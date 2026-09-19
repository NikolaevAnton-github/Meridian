"""Small local service wrapper. Upstream inference remains unchanged."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import psutil
from filelock import FileLock, Timeout
from prepare_models import disk_bytes

ROOT = Path("D:/devgames/Kimodo")
STATE = ROOT / "runtime" / "server.json"
SCRIPT = Path(__file__).resolve()
URL = "http://127.0.0.1:7860"
MODEL = "Kimodo-SOMA-RP-v1.1"
GIB = 1024**3


def owned_process():
    if not STATE.exists():
        return None
    state = json.loads(STATE.read_text())
    try:
        process = psutil.Process(state["pid"])
        if abs(process.create_time() - state["create_time"]) > 0.01:
            return None
        if not Path(process.exe()).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError("Recorded PID belongs to an external executable; refusing to control it.")
        args = process.cmdline()
        if str(SCRIPT) not in args or "_serve" not in args:
            raise RuntimeError("Recorded PID command does not match this Kimodo launcher.")
        return process
    except psutil.NoSuchProcess:
        return None


def readiness():
    status_file = ROOT / "runtime" / "models-status.json"
    missing = []
    records = json.loads(status_file.read_text()) if status_file.exists() else {"models": []}
    models = json.loads(SCRIPT.with_name("models.json").read_text())
    by_repo = {m["repo"]: m for m in records["models"]}
    for model in models:
        record = by_repo.get(model["repo"], {})
        cache = Path(os.environ["HF_HUB_CACHE"]) / ("models--" + model["repo"].replace("/", "--"))
        snapshot = cache / "snapshots" / model["revision"]
        ref = cache / "refs" / "main"
        if (record.get("status") != "cached" or record.get("revision") != model["revision"]
                or not ref.exists() or ref.read_text().strip() != model["revision"]
                or not record.get("files")
                or any(not (snapshot / f).is_file() for f in record.get("files", []))):
            missing.append(model["repo"])
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, check=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
    ram = psutil.virtual_memory().available
    vram = int(gpu.stdout.splitlines()[0]) * 1024**2
    used = disk_bytes()
    report = {"missing_models": missing, "free_ram_gib": round(ram/GIB, 2),
              "free_vram_gib": round(vram/GIB, 2), "installation_logical_bytes": used,
              "required_free_ram_gib": 20, "required_free_vram_gib": 20}
    print(json.dumps(report, indent=2), flush=True)
    problems = []
    if missing:
        problems.append("Run Login-HuggingFace.cmd locally with approved Llama access, then Prepare-Models.cmd.")
    if ram < 20*GIB or vram < 20*GIB:
        problems.append("Close other heavy applications yourself until at least 20 GiB RAM and 20 GiB VRAM are free.")
    if used > 44_000_000_000:
        problems.append("Installation is near the 45 GB cap. Review local generated data before starting.")
    if problems:
        raise RuntimeError(" ".join(problems))
    return report


def runtime_environment():
    # The explicitly prepared cache is reused. Runtime cannot fetch another model variant.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["LOCAL_CACHE"] = "True"
    os.environ["SERVER_NAME"] = "127.0.0.1"
    os.environ["SERVER_PORT"] = "7860"
    os.environ["TEXT_ENCODER_MODE"] = "local"
    os.environ["TEXT_ENCODER_DEVICE"] = "cuda"
    os.chdir(ROOT / "outputs")


def serve():
    with FileLock(str(ROOT / "runtime" / "workload.lock"), timeout=0):
        current = psutil.Process()
        pending = STATE.with_suffix(".tmp")
        pending.write_text(json.dumps({"pid": current.pid, "create_time": current.create_time(),
                                       "script": str(SCRIPT), "url": URL}, indent=2))
        pending.replace(STATE)
        try:
            readiness()
            runtime_environment()
            from kimodo.demo.app import Demo
            demo = Demo(default_model_name=MODEL)
            print(f"Kimodo ready: {URL}", flush=True)
            demo.run()
        finally:
            STATE.unlink(missing_ok=True)


def start():
    existing = owned_process()
    if existing:
        print(f"Kimodo is already starting/running (PID {existing.pid}): {URL}")
        return
    # Test the workload lock before spawning; the worker acquires it for its whole lifetime.
    with FileLock(str(ROOT / "runtime" / "workload.lock"), timeout=0):
        readiness()
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 7860))
    log_path = ROOT / "logs" / f"demo-{time.strftime('%Y%m%d-%H%M%S')}.log"
    with log_path.open("w", encoding="utf-8") as log:
        child = subprocess.Popen([sys.executable, str(SCRIPT), "_serve"], cwd=ROOT / "outputs",
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=log, close_fds=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
    launched = psutil.Process(child.pid)
    for _ in range(30):
        if child.poll() is not None:
            raise RuntimeError(f"Kimodo startup failed. See {log_path}")
        if owned_process():
            print(f"Kimodo is starting: {URL}\nLog: {log_path}\nStop: Stop-Kimodo.cmd")
            return
        time.sleep(0.5)
    # Do not leave an unrecorded start in the background.
    terminate_tree(launched)
    raise RuntimeError(f"No owned PID was registered. See {log_path}")


def terminate_tree(process):
    children = process.children(recursive=True)
    # Stop only this verified process and descendants created by this process tree.
    for child in reversed(children):
        try:
            child.terminate()
        except psutil.NoSuchProcess:
            pass
    process.terminate()
    _, alive = psutil.wait_procs(children + [process], timeout=10)
    for proc in alive:
        proc.kill()
    psutil.wait_procs(alive, timeout=5)


def stop():
    process = owned_process()
    if process is None:
        print("No owned Kimodo server is running.")
        return
    terminate_tree(process)
    STATE.unlink(missing_ok=True)
    print("Owned Kimodo server stopped.")


def smoke():
    with FileLock(str(ROOT / "runtime" / "workload.lock"), timeout=0):
        readiness()
        runtime_environment()
        output = ROOT / "outputs" / f"smoke-{time.strftime('%Y%m%d-%H%M%S')}.npz"
        sys.argv = ["kimodo_gen", "A person walks forward.", "--model", MODEL,
                    "--duration", "2", "--num_samples", "1", "--diffusion_steps", "20",
                    "--seed", "42", "--output", str(output)]
        from kimodo.scripts.generate import main
        main()
        import numpy as np
        with np.load(output, allow_pickle=False) as motion:
            joints = motion["posed_joints"]
            assert joints.size > 0 and np.isfinite(joints).all()
            for key in ("global_rot_mats", "local_rot_mats", "root_positions"):
                assert np.isfinite(motion[key]).all()
            print(json.dumps({"output": str(output), "finite": True, "shape": list(joints.shape)}))


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    if action == "_serve":
        serve()
        return
    with FileLock(str(ROOT / "runtime" / "control.lock"), timeout=0):
        if action == "start":
            start()
        elif action == "stop":
            stop()
        elif action == "smoke":
            smoke()
        elif action == "check":
            readiness()
        else:
            raise ValueError(f"Unknown action: {action}")


if __name__ == "__main__":
    try:
        main()
    except Timeout:
        print("Another Kimodo operation is active. Stop/wait for it before retrying.", file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
