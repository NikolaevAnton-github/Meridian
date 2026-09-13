"""One fresh, subscription-authenticated Codex app-server benchmark turn.

Run only while the operator holds the DCC lease. This client never retries or
resumes a turn. All detailed records stay in the ignored output directory.
Protocol: https://learn.chatgpt.com/docs/app-server, codex-cli 0.153.4 schema.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import tomllib
import traceback


PROJECT = Path(__file__).resolve().parents[3]
BASE = PROJECT / 'Saved/AgentSetup/OrchestrationAB'
CODEX = Path(os.environ.get("LOCALAPPDATA", "")) / (
    "JetBrains/Rider2026.2/acp-agents/codex-acp/1.11.0/node_modules/"
    "@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe"
)
MODEL = "gpt-6-astra"
EXPECTED_VERSION = "codex-cli 0.153.4"

# Pass this exact list as the Multica Codex agent's custom_args. Keep its
# mcp_config absent so the native user/project MCP configuration is inherited.
COMMON_ARGS = [
    "-c",
    "forced_login_method=\"chatgpt\"",
    "-c",
    "model_provider=\"openai\"",
    "-c",
    "model=\"gpt-6-astra\"",
    "-c",
    "model_reasoning_effort=\"medium\"",
    "-c",
    "service_tier=\"default\"",
    "-c",
    "approval_policy=\"never\"",
    "-c",
    "sandbox_mode=\"danger-full-access\"",
    "--disable",
    "fast_mode",
    "-c",
    "features.multi_agent=false",
    "-c",
    "features.memories=false",
    "-c",
    "memories.generate_memories=false",
    "-c",
    "memories.use_memories=false",
    "-c",
    "mcp_servers.node_repl.enabled=false",
    "-c",
    "mcp_servers.blender.enabled=true",
    "-c",
    "mcp_servers.substance_painter.enabled=true",
    "-c",
    "mcp_servers.unreal_epic.enabled=true",
    "-c",
    "mcp_servers.cua_repl.command=\"C:\\\\Users\\\\Origa\\\\AppData\\\\Local\\\\OpenAI\\\\Codex\\\\runtimes\\\\cua_node\\\\a708e72b10c27b59\\\\bin\\\\node.exe\"",
    "-c",
    "mcp_servers.cua_repl.enabled=false"
]
# codex_apps is absent from native MCP configuration. Defining only enabled=false
# creates an invalid server without a transport in Codex 0.153.4; do not add it.
QUOTA_CAVEATS = [
    "Account rate-limit snapshots are shared-account, rounded window measurements; "
    "other sessions, delayed updates and window resets can affect their difference.",
    "Native token counts are model activity, not subscription dollars or an exact "
    "conversion into remaining subscription quota. No API price calculation is made.",
    "A sequential single pair cannot separate orchestration effects from model "
    "variation, prompt-cache warmth, DCC/cache state and execution order.",
    "TTFT here means the first agentMessage text delta; tools or reasoning may "
    "precede it. Tool counts are app-server items, not every nested DCC operation.",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_relative(path, root):
    path = path.resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Output and task home must be inside the benchmark Saved directory.")
    return path


def prepare_home(source, target):
    """Match Multica's fresh-home seed; no shared session or memory history."""
    if target.exists():
        raise FileExistsError("Task CODEX_HOME already exists; refusing reuse or overwrite.")
    auth = source / "auth.json"
    if not auth.is_file():
        raise FileNotFoundError("Source CODEX_HOME has no auth.json; use the same ChatGPT home as Multica.")
    target.mkdir(parents=True)
    (target / "sessions").mkdir()
    # A private copy also works without Windows symlink privileges. Token refresh
    # remains task-local; the shared login and configuration are never modified.
    shutil.copy2(auth, target / "auth.json")
    manifest = {"source": str(source), "auth_mode": "private_copy", "files": []}
    for name in ("config.json", "config.toml", "instructions.md", "models_cache.json"):
        src = source / name
        if src.is_file():
            shutil.copy2(src, target / name)
            manifest["files"].append({"name": name, "source_sha256": sha256(src)})
    config = target / "config.toml"
    if config.exists():
        raw = config.read_text(encoding="utf-8-sig")
        # Same narrow compatibility transformation as Multica codex_skill_strip.go.
        lines, skipping, removed = [], False, 0
        for line in raw.splitlines(keepends=True):
            if line.lstrip().startswith("["):
                skipping = bool(re.match(r"^\s*\[\[skills\.config\]\]\s*(?:#.*)?$", line))
                removed += int(skipping)
            if not skipping:
                lines.append(line)
        config.write_text("".join(lines), encoding="utf-8")
        parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        manifest["removed_skills_config_entries"] = removed
        # Absolute paths continue to point at the same files. Relative model
        # instruction/catalog files must resolve identically in the task home.
        for key in ("model_instructions_file", "experimental_instructions_file", "model_catalog_json"):
            value = parsed.get(key)
            if not value:
                continue
            path = Path(value).expanduser()
            if path.is_absolute():
                if not path.is_file():
                    raise FileNotFoundError("An inherited model instruction/catalog file is missing.")
                continue
            dst = (target / path).resolve()
            if not dst.is_relative_to(target):
                raise ValueError("An inherited relative model file escapes the task home.")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / path, dst)
            manifest["files"].append({"name": str(path), "source_sha256": sha256(source / path)})
        manifest["task_config_sha256"] = sha256(config)
    cache = source / "plugins" / "cache"
    if cache.is_dir():
        dst = target / "plugins" / "cache"
        dst.parent.mkdir(parents=True)
        if os.name == "nt":
            # PowerShell literal quoting: no command interpolation or cmd.exe.
            quote = lambda p: "'" + str(p).replace("'", "''") + "'"
            command = "New-Item -ItemType Junction -Path " + quote(dst) + " -Target " + quote(cache) + " | Out-Null"
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode:
                raise RuntimeError("Could not expose the shared plugin cache as a junction.")
        else:
            dst.symlink_to(cache, target_is_directory=True)
        manifest["plugin_cache"] = "shared_directory_link"
    manifest["sessions"] = "fresh_empty_directory"
    manifest["global_AGENTS_and_user_skills"] = "not_copied_same_as_multica_home_seed"
    return manifest


class RPCError(RuntimeError):
    pass


class AppServer:
    def __init__(self, command, cwd, env, output, metadata, timeout):
        self.output, self.metadata = output, metadata
        self.start = time.monotonic()
        self.deadline = self.start + timeout
        self.events = (output / "rpc.jsonl").open("x", encoding="utf-8", buffering=1)
        self.stderr = (output / "stderr.log").open("xb")
        self.lock = threading.Lock()
        self.incoming = queue.Queue()
        self.responses = {}
        self.request_id = 0
        self.turn_sent_at = None
        self.first_text_at = None
        self.first_activity_at = None
        self.turn_completed_at = None
        self.completed_turn = None
        self.active_thread = None
        self.active_turn = None
        self.items = {}
        self.text_deltas = {}
        self.usage_updates = []
        self.notification_counts = Counter()
        self.proc = subprocess.Popen(
            command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.stderr, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.reader = threading.Thread(target=self._read_stdout, daemon=True)
        self.reader.start()

    def _record(self, direction, message):
        with self.lock:
            self.events.write(json.dumps({"at": utc_now(), "elapsed_seconds": time.monotonic() - self.start,
                                          "direction": direction, "message": message}, ensure_ascii=False) + "\n")

    def _read_stdout(self):
        try:
            for line in self.proc.stdout:
                stamp = time.monotonic()
                try:
                    message = json.loads(line)
                    self._record("server", message)
                    self.incoming.put((stamp, message))
                except (ValueError, UnicodeError):
                    self._record("non_json_stdout", line.decode("utf-8", errors="replace"))
        except Exception:
            self.incoming.put((time.monotonic(), {"localReaderError": True}))
        finally:
            self.incoming.put((time.monotonic(), None))

    def send(self, message):
        self._record("client", message)
        self.proc.stdin.write((json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8"))
        self.proc.stdin.flush()

    def request(self, method, params=None, timeout=60):
        self.request_id += 1
        request_id = self.request_id
        message = {"id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)
        deadline = min(self.deadline, time.monotonic() + timeout)
        while request_id not in self.responses:
            self.pump(deadline)
        response = self.responses.pop(request_id)
        if "error" in response:
            # The raw error stays in rpc.jsonl; never reflect server text/secrets.
            raise RPCError(method + " failed; inspect the private rpc.jsonl error response.")
        return response.get("result")

    def optional_read(self, method, params=None):
        try:
            return {"captured_at": utc_now(), "result": self.request(method, params, timeout=30)}
        except (RPCError, TimeoutError) as exc:
            return {"captured_at": utc_now(), "unavailable": str(exc)}

    def pump(self, deadline):
        remaining = min(deadline, self.deadline) - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Benchmark/RPC time limit reached; no automatic retry.")
        try:
            stamp, message = self.incoming.get(timeout=min(remaining, 1.0))
        except queue.Empty:
            return
        if message is None:
            raise RuntimeError("App-server stdout closed before all requested work completed.")
        if message.get("localReaderError"):
            raise RuntimeError("Could not capture the app-server output stream.")
        if "id" in message and "method" not in message:
            self.responses[message["id"]] = message
            return
        if "id" in message:
            # With never/full-access there should be no host approvals. Do not
            # invent user input, OAuth credentials or DCC elicitation answers.
            self.send({"id": message["id"], "error": {"code": -32601,
                       "message": "Finite benchmark cannot answer interactive server requests."}})
            raise RuntimeError("Unexpected interactive server request; benchmark stopped without retry.")
        method, params = message.get("method", ""), message.get("params") or {}
        self.notification_counts[method] += 1
        if self.active_thread and params.get("threadId") not in (None, self.active_thread):
            return
        if method == "turn/started":
            self.active_turn = params["turn"]["id"]
        if method.startswith("item/") and self.turn_sent_at is not None:
            self.first_activity_at = self.first_activity_at or stamp
        if method == "item/agentMessage/delta":
            self.first_text_at = self.first_text_at or stamp
            item_id = params.get("itemId", "unknown")
            self.text_deltas[item_id] = self.text_deltas.get(item_id, "") + params.get("delta", "")
        if method in ("item/started", "item/completed"):
            item = params.get("item") or {}
            if item.get("id"):
                self.items[item["id"]] = item
        if method == "thread/tokenUsage/updated":
            self.usage_updates.append(params)
        if method == "turn/completed":
            self.completed_turn = params.get("turn")
            self.turn_completed_at = stamp

    def close(self):
        if self.proc.poll() is None:
            try:
                self.proc.stdin.close()
                self.proc.wait(timeout=10)
            except (BrokenPipeError, subprocess.TimeoutExpired):
                # Only the benchmark-owned process tree; never search by DCC name.
                if os.name == "nt":
                    subprocess.run(["taskkill.exe", "/PID", str(self.proc.pid), "/T", "/F"],
                                   capture_output=True, timeout=20)
                else:
                    self.proc.terminate()
                try:
                    self.proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=10)
        self.reader.join(timeout=5)
        self.stderr.close()
        if not self.reader.is_alive():
            self.events.close()

    def results(self):
        completed = self.completed_turn or {}
        native = self.usage_updates[-1]["tokenUsage"]["total"] if self.usage_updates else None
        compatible = None
        if native is not None:
            compatible = {
                "input_tokens": max(0, native["inputTokens"] - native["cachedInputTokens"] - native.get("cacheWriteInputTokens", 0)),
                "cache_read_tokens": native["cachedInputTokens"],
                "cache_write_tokens": native.get("cacheWriteInputTokens", 0),
                "output_tokens": native["outputTokens"] + native["reasoningOutputTokens"],
            }
        tool_types = {"commandExecution", "mcpToolCall", "dynamicToolCall", "fileChange", "webSearch", "imageGeneration", "collabAgentToolCall"}
        tool_items = [item for item in self.items.values() if item.get("type") in tool_types]
        messages = [item for item in self.items.values() if item.get("type") == "agentMessage"]
        finals = [item.get("text", "") for item in messages if item.get("phase") == "final_answer"]
        final_source = "final_answer_items"
        if not finals and messages:
            finals = [messages[-1].get("text", "")]
            final_source = "last_agent_message_fallback"
        if not finals and self.text_deltas:
            finals = [next(reversed(self.text_deltas.values()))]
            final_source = "last_streamed_agent_message_fallback"
        final_text = "\n\n".join(finals)
        (self.output / "final_output.md").write_text(final_text, encoding="utf-8")
        save_json(self.output / "items.json", list(self.items.values()))
        save_json(self.output / "native_usage_updates.json", self.usage_updates)
        delta = lambda end, start: round(end - start, 3) if end is not None and start is not None else None
        return {
            "thread_id": self.active_thread, "turn_id": self.active_turn,
            "turn_status": completed.get("status"), "turn_error": completed.get("error"),
            "native_usage_total": native,
            "native_usage_semantics": "Final cumulative total of a fresh thread, not a sum of cumulative notifications; input includes cached input. Raw output and reasoning remain separate.",
            "multica_normalized_usage": compatible,
            "multica_normalization": "Pinned Multica codex.go subtracts cached/read+write from native input, and adds native output+reasoning for its output_tokens field.",
            "usage_notification_count": len(self.usage_updates),
            "timing": {"launch_to_turn_sent_seconds": delta(self.turn_sent_at, self.start),
                       "turn_elapsed_seconds": delta(self.turn_completed_at, self.turn_sent_at),
                       "launch_to_turn_completed_seconds": delta(self.turn_completed_at, self.start),
                       "turn_to_first_agent_text_seconds": delta(self.first_text_at, self.turn_sent_at),
                       "launch_to_first_agent_text_seconds": delta(self.first_text_at, self.start),
                       "turn_to_first_item_event_seconds": delta(self.first_activity_at, self.turn_sent_at)},
            "notification_counts": dict(self.notification_counts),
            "tool_item_counts": dict(Counter(item["type"] for item in tool_items)),
            "mcp_tool_counts": dict(Counter(str(item.get("server")) + "/" + str(item.get("tool")) for item in tool_items if item["type"] == "mcpToolCall")),
            "tool_item_count_total": len(tool_items),
            "final_output_file": "final_output.md", "final_output_source": final_source,
            "final_output_characters": len(final_text),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=BASE / "DirectRun")
    parser.add_argument("--codex-home", type=Path, default=BASE / "DirectCodexHome")
    parser.add_argument("--source-codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--codex", type=Path, default=CODEX)
    parser.add_argument("--cwd", type=Path, default=PROJECT)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    args = parser.parse_args()
    output = checked_relative(args.output_dir, BASE)
    home = checked_relative(args.codex_home, BASE)
    if output == home or output.is_relative_to(home) or home.is_relative_to(output):
        raise ValueError("Output directory and task home must be separate sibling directories.")
    if output.exists() or home.exists():
        raise FileExistsError("A prior result/task home exists; refusing reuse or overwrite.")
    if not 60 <= args.timeout_seconds <= 14400:
        raise ValueError("Timeout must be between 60 and 14400 seconds.")
    cwd, source, binary = args.cwd.resolve(strict=True), args.source_codex_home.resolve(strict=True), args.codex.resolve(strict=True)
    prompt_bytes = args.prompt_file.read_bytes()
    prompt = prompt_bytes.decode("utf-8-sig")
    if not prompt.strip():
        raise ValueError("Prompt file is empty.")
    version = subprocess.run([str(binary), "--version"], capture_output=True, text=True, timeout=15, check=True).stdout.strip()
    if version != EXPECTED_VERSION:
        raise RuntimeError("Native Codex version differs from the pinned benchmark version.")
    output.mkdir(parents=True, exist_ok=False)
    (output / "prompt.txt").write_bytes(prompt_bytes)
    save_json(output / "common_codex_args.json", COMMON_ARGS)
    metadata = {"schema_version": 1, "mode": "direct", "started_at": utc_now(), "status": "starting",
                "native_binary": str(binary), "native_binary_sha256": sha256(binary), "native_version": version,
                "cwd": str(cwd), "codex_home": str(home), "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
                "prompt_bytes": len(prompt_bytes), "requested_model": MODEL, "requested_reasoning": "medium",
                "requested_service_tier": "default", "approval_policy": "never", "sandbox": "danger-full-access",
                "common_codex_args": COMMON_ARGS, "turn_start_requests": 0, "quota_caveats": QUOTA_CAVEATS}
    save_json(output / "run.json", metadata)
    client = None
    started = time.monotonic()
    try:
        metadata["home_seed"] = prepare_home(source, home)
        metadata["instruction_files_before"] = [
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (cwd / "AGENTS.md", cwd / ".codex" / "config.toml") if path.is_file()
        ]
        env = os.environ.copy()
        excluded = []
        for key in list(env):
            if key.upper().startswith("MULTICA_") or key.upper() in {"OPENAI_API_KEY", "AZURE_OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL", "OPENAI_API_BASE"}:
                excluded.append(key)
                del env[key]
        env["CODEX_HOME"] = str(home)
        metadata["excluded_environment_names"] = sorted(excluded)
        command = [str(binary), "app-server", "--listen", "stdio://", *COMMON_ARGS]
        client = AppServer(command, str(cwd), env, output, metadata, args.timeout_seconds)
        metadata["initialize"] = client.request("initialize", {
            "clientInfo": {"name": "meridiansquad-direct-benchmark", "title": "MeridianSquad Direct Benchmark", "version": "1.0.0"},
            "capabilities": {"experimentalApi": True},
        })
        client.send({"method": "initialized"})
        account = client.request("account/read", {"refreshToken": False})
        save_json(output / "account_before.json", account)
        account_type = (account.get("account") or {}).get("type")
        if account_type != "chatgpt":
            raise RuntimeError("Account is not the expected ChatGPT subscription login; no model turn started.")
        metadata["account_auth_type"] = account_type
        catalog, cursor, selected = [], None, None
        for _ in range(10):
            page = client.request("model/list", {"includeHidden": True, "limit": 100, "cursor": cursor})
            catalog.extend(page.get("data", []))
            selected = next((m for m in catalog if m.get("model") == MODEL), None)
            cursor = page.get("nextCursor")
            if selected or not cursor:
                break
        save_json(output / "model_catalog.json", catalog)
        if not selected or "medium" not in [x.get("reasoningEffort") for x in selected.get("supportedReasoningEfforts", [])]:
            raise RuntimeError("Runtime did not advertise gpt-6-astra with medium reasoning; no model turn started.")
        metadata["advertised_model"] = selected
        save_json(output / "effective_config.json", client.optional_read("config/read", {"cwd": str(cwd), "includeLayers": True}))
        save_json(output / "rate_limits_before.json", client.optional_read("account/rateLimits/read"))
        result = client.request("thread/start", {
            "model": MODEL, "modelProvider": "openai", "profile": None, "cwd": str(cwd),
            "approvalPolicy": "never", "sandbox": "danger-full-access",
            "config": {"model_reasoning_effort": "medium"}, "serviceTier": "default",
            "baseInstructions": None, "developerInstructions": None,
            "experimentalRawEvents": False, "persistExtendedHistory": True,
            "allowProviderModelFallback": False,
        }, timeout=180)
        save_json(output / "thread_start.json", result)
        thread = result["thread"]
        client.active_thread = thread["id"]
        metadata["thread_id"] = thread["id"]
        metadata["session_id"] = thread.get("sessionId")
        metadata["rollout_path"] = thread.get("path")
        metadata["effective_thread_config"] = {key: result.get(key) for key in (
            "model", "modelProvider", "reasoningEffort", "serviceTier", "approvalPolicy", "sandbox", "cwd", "instructionSources")}
        if result.get("model") != MODEL or result.get("modelProvider") != "openai" or result.get("approvalPolicy") != "never" or result.get("sandbox", {}).get("type") != "dangerFullAccess":
            raise RuntimeError("Effective thread configuration differs from the benchmark; no model turn started.")
        if result.get("reasoningEffort") not in (None, "medium") or result.get("serviceTier") not in (None, "default"):
            raise RuntimeError("Effective model effort/tier differs from the benchmark; no model turn started.")
        metadata["status"] = "running"
        # Persist before sending: any ambiguous transport failure consumes this
        # one-run marker; a restart never silently replays the asset operation.
        metadata["turn_start_requests"] = 1
        metadata["turn_sent_at"] = utc_now()
        save_json(output / "run.json", metadata)
        client.turn_sent_at = time.monotonic()
        result = client.request("turn/start", {"threadId": thread["id"], "input": [{"type": "text", "text": prompt}],
                                                 "effort": "medium", "serviceTier": "default"}, timeout=180)
        client.active_turn = result["turn"]["id"]
        save_json(output / "turn_start.json", result)
        while client.completed_turn is None:
            client.pump(client.deadline)
        metadata["status"] = client.completed_turn.get("status", "unknown")
        save_json(output / "rate_limits_after.json", client.optional_read("account/rateLimits/read"))
        save_json(output / "account_after.json", client.optional_read("account/read", {"refreshToken": False}))
        save_json(output / "thread_after.json", client.optional_read("thread/read", {"threadId": thread["id"], "includeTurns": True}))
        save_json(output / "mcp_status_after.json", client.optional_read("mcpServer/status/list", {"threadId": thread["id"], "limit": 100}))
    except BaseException as exc:
        metadata["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        metadata["error_type"] = type(exc).__name__
        (output / "failure.log").write_text(traceback.format_exc(), encoding="utf-8")
        if client and client.active_thread and client.active_turn and not client.completed_turn:
            try:
                # Best effort interruption of this turn only, never a second turn.
                client.deadline = max(client.deadline, time.monotonic() + 12)
                client.request("turn/interrupt", {"threadId": client.active_thread, "turnId": client.active_turn}, timeout=10)
                until = time.monotonic() + 2
                while client.completed_turn is None and time.monotonic() < until:
                    client.pump(until)
            except Exception:
                pass
    finally:
        if client:
            client.close()
            metadata.update(client.results())
            metadata["app_server_exit_code"] = client.proc.returncode
        metadata["finished_at"] = utc_now()
        metadata["client_wall_seconds"] = round(time.monotonic() - started, 3)
        save_json(output / "run.json", metadata)
    # No model output, server error body, account identity or credentials on stdout.
    print(json.dumps({key: metadata.get(key) for key in (
        "status", "thread_id", "session_id", "turn_status", "native_usage_total",
        "multica_normalized_usage", "timing", "tool_item_counts", "client_wall_seconds")}, indent=2))
    print("Private benchmark artifacts: " + str(output))
    return 0 if metadata["status"] == "completed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("Benchmark setup refused (" + type(exc).__name__ + "). Check paths, prior output/home, prompt and pinned native binary.", file=sys.stderr)
        raise SystemExit(2)
