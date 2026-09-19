"""Download only pinned official inference files into the single local HF cache."""
import json
import os
from pathlib import Path

from filelock import FileLock, Timeout
from huggingface_hub import HfApi, get_hf_file_metadata, hf_hub_url, snapshot_download
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError

ROOT = Path("D:/devgames/Kimodo")
LIMIT = 45_000_000_000


def disk_bytes():
    # Count logical bytes conservatively, including hardlinks and local history.
    total = 0
    directories = [ROOT]
    while directories:
        with os.scandir(directories.pop()) as entries:
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        directories.append(entry.path)
                    elif entry.is_file():
                        total += entry.stat().st_size
                except FileNotFoundError:
                    pass  # A temporary build file can disappear during inspection.
    return total


def main():
    os.environ.pop("HF_HUB_OFFLINE", None)
    models = json.loads(Path(__file__).with_name("models.json").read_text())
    results = []
    for model in models:
        repo, revision = model["repo"], model["revision"]
        if model["gated"]:
            try:
                # HF handles authentication locally. Never print the token or raw HTTP headers.
                get_hf_file_metadata(hf_hub_url(repo, "config.json", revision=revision))
            except (GatedRepoError, HfHubHTTPError) as exc:
                code = getattr(exc.response, "status_code", None)
                if code not in (401, 403):
                    raise
                results.append({**model, "status": "pending_owner_authentication", "http_status": code})
                print("Llama access is pending. Run Login-HuggingFace.cmd locally after account approval.")
                continue
        info = HfApi().model_info(repo, revision=revision, files_metadata=True)
        files = [f for f in info.siblings if not f.rfilename.startswith("original/")
                 and not f.rfilename.endswith((".bin", ".pth", ".pt"))]
        expected = sum(f.size or 0 for f in files)
        used = disk_bytes()
        cache_repo = Path(os.environ["HF_HUB_CACHE"]) / ("models--" + repo.replace("/", "--"))
        snapshot = cache_repo / "snapshots" / revision
        missing = sum(f.size or 0 for f in files if not (snapshot / f.rfilename).is_file())
        if used + missing + 1_000_000_000 > LIMIT:
            raise RuntimeError("45 GB installation budget would be exceeded. No owner files were removed.")
        print(f"Preparing {repo}@{revision}: {expected} bytes, at most {missing} new bytes", flush=True)
        location = snapshot_download(repo, revision=revision, allow_patterns=[f.rfilename for f in files], max_workers=1)
        # Upstream resolves 'main'. Freeze that cache alias to our pinned revision for offline runtime.
        (cache_repo / "refs").mkdir(exist_ok=True)
        (cache_repo / "refs" / "main").write_text(revision, encoding="utf-8")
        results.append({**model, "status": "cached", "path": location,
                        "download_bytes": expected, "files": [f.rfilename for f in files]})
    report = {"models": results, "installation_logical_bytes": disk_bytes(), "cap_bytes": LIMIT,
              "generation_verified": False}
    (ROOT / "runtime" / "models-status.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"statuses": {m["repo"]: m["status"] for m in results},
                      "installation_logical_bytes": report["installation_logical_bytes"]}, indent=2))


if __name__ == "__main__":
    try:
        with FileLock(str(ROOT / "runtime" / "workload.lock"), timeout=0):
            main()
    except Timeout:
        raise SystemExit("Kimodo is already running or preparing models. Stop it before preparing models.")
