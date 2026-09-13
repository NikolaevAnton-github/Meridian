"""Take one read-only snapshot of saved benchmark evidence; never call services.

Writes a derived report under Controller only. It does not read authentication,
account, effective-config or credential files. Incomplete JSONL tails are ignored.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[3]
BASE = PROJECT / 'Saved/AgentSetup/OrchestrationAB'
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens", "total_tokens")
CAMEL = ("inputTokens", "cachedInputTokens", "cacheWriteInputTokens",
         "outputTokens", "reasoningOutputTokens", "totalTokens")
TOOLS = {"commandexecution", "mcptoolcall", "dynamictoolcall", "filechange",
         "websearch", "imagegeneration", "collabagenttoolcall", "toolcall"}
LIMITS = [
    "This is a finite snapshot, not a polling loop. Pending runs have incomplete counts and no final verdict.",
    "Native response usage is summed once per response ID. Cumulative thread/turn snapshots are retained separately and never summed as response usage.",
    "Native input includes cached input; native output already includes its reasoning component. Multica's output adds reasoning again. Its adapter-compatible field is not the canonical native output or total.",
    "Model tool calls (including code-mode exec wrappers), native execution items and API message counts are different levels; do not add them together.",
    "FileChange items are file events, not apply_patch invocations. Static apply_patch call-site counts inside exec code are labeled separately and cannot prove loop/branch execution counts.",
    "Definite failures use structured failed status, nonzero command exit code or isError. Text error markers are candidates requiring review, not proven failures.",
    "Stage intervals are first/last observed tool timestamps, not exclusive stage durations. Keyword-derived stage labels are explicitly inferred.",
    "Worker reports are self-reported evidence. The controller's independent asset checks determine acceptance.",
    "Task wall time, native turn time and controller/setup time have different boundaries. Keep all attempts and controller preparation separate.",
    "A sequential single pair does not control model randomness, prompt-cache warmth, DCC caches or execution order. Tokens do not imply exact subscription dollars/quota.",
    "No auth/account/config files or service endpoints are read. Subscription rate-limit deltas are intentionally outside this report.",
    "Resource sample peaks require filtering to the worker/task time window. Whole-host Codex process totals include controller/helpers. No GPU/VRAM telemetry was collected.",
]


def stamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return None


def iso(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value is not None else None


def seconds(start, end):
    a, b = stamp(start), stamp(end)
    return round(b - a, 3) if a is not None and b is not None else None


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default


def json_lines(path):
    """Read only the bytes that existed at open time, including a live logfile."""
    if not path or not path.is_file():
        return
    with path.open("rb") as stream:
        remaining = path.stat().st_size
        while remaining > 0:
            line = stream.readline(remaining)
            remaining -= len(line)
            if not line:
                break
            try:
                yield json.loads(line)
            except (ValueError, UnicodeError):
                continue


def usage(raw):
    if not isinstance(raw, dict):
        return None
    return {key: int(raw.get(key, raw.get(camel, 0)) or 0) for key, camel in zip(FIELDS, CAMEL)}


def sum_usage(rows):
    rows = [r for r in rows if r is not None]
    return {key: sum(r[key] for r in rows) for key in FIELDS} if rows else None


def multica_usage(raw):
    if raw is None:
        return None
    return {"input_tokens": max(0, raw["input_tokens"] - raw["cached_input_tokens"] - raw["cache_write_input_tokens"]),
            "cache_read_tokens": raw["cached_input_tokens"], "cache_write_tokens": raw["cache_write_input_tokens"],
            "output_tokens": raw["output_tokens"] + raw["reasoning_output_tokens"]}


def texts(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(x.get("text", "") for x in content if isinstance(x, dict))
    return ""


def classify_stage(item):
    server = str(item.get("server", "")).lower()
    explicit = {"blender": "Blender", "substance_painter": "Painter", "unreal_epic": "Unreal"}
    if server in explicit:
        return [explicit[server]], "native_mcp_server"
    # Input is inspected locally; it is never reproduced in the report.
    candidate = " ".join(str(item.get(k, "")) for k in ("name", "tool", "command", "input", "arguments")).lower()
    labels = [label for label, pattern in (("Blender", r"blender|\.blend\b"),
              ("Painter", r"painter|\.spp\b"), ("Unreal", r"unreal|epic|/game/")) if re.search(pattern, candidate)]
    return labels, "keyword_inference" if labels else None


def failures(item):
    reasons = []
    if str(item.get("status", "")).lower() in {"failed", "errored", "declined"}:
        reasons.append("failed_status")
    code = item.get("exit_code", item.get("exitCode"))
    if isinstance(code, int) and code != 0:
        reasons.append("nonzero_exit_code")
    if item.get("error"):
        reasons.append("structured_error")
    for value in (item, item.get("result"), item.get("output")):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                value = None
        if isinstance(value, dict) and (value.get("isError") is True or value.get("is_error") is True):
            reasons.append("structured_is_error")
    body = " ".join(str(item.get(k, "")) for k in ("output", "aggregated_output", "aggregatedOutput", "stderr", "result"))
    candidate = bool(re.search(r"Traceback \(most recent call last\)|Tool execution failed|\"isError\"\s*:\s*true", body))
    return sorted(set(reasons)), candidate


def summarize_items(items):
    records, stages = [], {}
    patch_sites = sum(len(re.findall(r"\btools\.apply_patch\s*\(", str(item.get("input", "")))) for item in items.values())
    for item in items.values():
        labels, evidence = classify_stage(item)
        reasons, candidate = failures(item)
        row = {"id": item.get("id", item.get("call_id")), "type": item.get("type"),
               "name": item.get("name", item.get("tool")), "server": item.get("server"),
               "started_at": item.get("_started_at"), "completed_at": item.get("_completed_at"),
               "status": item.get("status"), "failure_reasons": reasons,
               "text_error_candidate": candidate, "stages": labels, "stage_evidence": evidence}
        records.append(row)
        for label in labels:
            stage = stages.setdefault(label, {"first_observed_at": None, "last_observed_at": None,
                                             "tool_count": 0, "evidence": set()})
            stage["tool_count"] += 1
            stage["evidence"].add(evidence)
            values = [stamp(row[k]) for k in ("started_at", "completed_at") if stamp(row[k]) is not None]
            if values:
                first, last = stamp(stage["first_observed_at"]), stamp(stage["last_observed_at"])
                stage["first_observed_at"] = iso(min(values + ([first] if first is not None else [])))
                stage["last_observed_at"] = iso(max(values + ([last] if last is not None else [])))
    for row in stages.values():
        row["evidence"] = sorted(row["evidence"])
    return {"count": len(records), "by_type": dict(Counter(str(r["type"]) for r in records)),
            "by_name": dict(Counter(str(r["name"]) for r in records if r["name"])),
            "file_change_item_count": sum(str(r["type"]).lower() == "filechange" for r in records),
            "non_file_change_item_count": sum(str(r["type"]).lower() != "filechange" for r in records),
            "apply_patch_model_call_count": sum(str(r["name"]).split(".")[-1] == "apply_patch" for r in records),
            "apply_patch_static_call_sites_inside_exec": patch_sites,
            "definite_failed_count": sum(bool(r["failure_reasons"]) for r in records),
            "text_error_candidate_count": sum(r["text_error_candidate"] for r in records),
            "records": records, "stage_observations": stages}


def native_rollout(path, started_at=None, completed_at=None):
    if not path or not path.is_file():
        return {"available": False, "path": str(path) if path else None}
    lower, upper = stamp(started_at), stamp(completed_at)
    turn, active, session = None, lower is None, {}
    calls, items, responses, turn_totals, snapshots = {}, {}, {}, {}, []
    final_messages, lifecycle, error_events = [], [], []
    latest_thread, first_at, last_at = None, None, None
    for number, row in enumerate(json_lines(path)):
        payload, kind, at = row.get("payload") or {}, row.get("type"), row.get("timestamp")
        event = payload.get("type")
        if kind == "session_meta":
            session = {key: payload.get(key) for key in ("id", "session_id", "cli_version", "cwd", "model_provider", "originator")}
        if kind == "event_msg" and event == "task_started":
            turn = payload.get("turn_id")
            ts = stamp(at)
            active = (lower is None or (ts is not None and ts >= lower - 5)) and (upper is None or (ts is not None and ts <= upper + 5))
        if not active:
            continue
        first_at, last_at = first_at or at, at
        if kind == "token_usage_record":
            key = payload.get("response_id") or "line-" + str(number)
            responses[key] = {"at": at, "turn_id": payload.get("turn_id"), "usage": usage(payload.get("usage"))}
            turn_totals[payload.get("turn_id") or turn or "unknown"] = usage(payload.get("turn_token_usage"))
            latest_thread = usage(payload.get("thread_token_usage"))
        if kind == "event_msg" and event == "token_count":
            info = payload.get("info") or {}
            snapshots.append({"at": at, "turn_id": turn, "cumulative_thread": usage(info.get("total_token_usage")),
                              "last_response": usage(info.get("last_token_usage"))})
        if kind == "event_msg" and event in {"task_started", "task_complete", "task_aborted"}:
            lifecycle.append({"event": event, "at": at, **{k: payload.get(k) for k in (
                "turn_id", "started_at", "completed_at", "duration_ms", "time_to_first_token_ms")}})
            if event == "task_complete" and payload.get("last_agent_message"):
                final_messages.append({"at": at, "text": payload["last_agent_message"], "source": "native_task_complete"})
        if kind == "event_msg" and event in {"error", "stream_error"}:
            error_events.append({"at": at, "event": event})
        if kind == "event_msg" and event == "item_completed":
            item = dict(payload.get("item") or {})
            item["_completed_at"] = iso(payload["completed_at_ms"] / 1000) if payload.get("completed_at_ms") is not None else at
            item["_started_at"] = iso(payload["started_at_ms"] / 1000) if payload.get("started_at_ms") is not None else None
            if str(item.get("type", "")).lower() in TOOLS:
                items[item.get("id") or "line-" + str(number)] = item
            if item.get("type") == "AgentMessage" and item.get("phase") == "final_answer":
                final_messages.append({"at": at, "text": texts(item.get("content")), "source": "native_final_answer_item"})
        if kind == "response_item" and event in {"function_call", "custom_tool_call"}:
            item = dict(payload)
            item["_started_at"] = at
            calls[item.get("call_id") or item.get("id") or "line-" + str(number)] = item
        if kind == "response_item" and event in {"function_call_output", "custom_tool_call_output"}:
            item = calls.get(payload.get("call_id"))
            if item is not None:
                item.update({"output": payload.get("output"), "_completed_at": at})
    native = sum_usage([row["usage"] for row in responses.values()])
    source = "sum_unique_native_response_usage"
    if native is None and snapshots and lower is None:
        native, source = snapshots[-1]["cumulative_thread"], "fresh_thread_cumulative_fallback"
    return {"available": True, "path": str(path), "session": session,
            "snapshot_first_event_at": first_at, "snapshot_last_event_at": last_at,
            "usage": native, "usage_source": source if native else None,
            "normalized_for_multica": multica_usage(native), "response_count": len(responses),
            "responses": list(responses.values()), "last_thread_cumulative": latest_thread,
            "last_cumulative_per_turn": turn_totals, "token_count_snapshots": snapshots,
            "lifecycle": lifecycle, "native_error_events": error_events,
            "model_tool_calls": summarize_items(calls), "execution_items": summarize_items(items),
            "final_messages": final_messages}


def direct_rpc(path):
    items, lifecycle, first_text, usage_total, methods, errors = {}, [], None, None, Counter(), []
    requests = {}
    for row in json_lines(path):
        message, at = row.get("message") or {}, row.get("at")
        if not isinstance(message, dict):
            continue
        method, params = message.get("method"), message.get("params") or {}
        if row.get("direction") == "client" and method and "id" in message:
            requests[message["id"]] = method
        if row.get("direction") != "server":
            continue
        if method:
            methods[method] += 1
        if method in {"turn/started", "turn/completed"}:
            lifecycle.append({"event": method, "at": at, "turn_id": (params.get("turn") or {}).get("id"),
                              "status": (params.get("turn") or {}).get("status")})
        if method == "item/agentMessage/delta":
            first_text = first_text or at
        if method == "thread/tokenUsage/updated":
            usage_total = usage((params.get("tokenUsage") or {}).get("total"))
        if method in {"item/started", "item/completed"}:
            item = dict(params.get("item") or {})
            if str(item.get("type", "")).lower() in TOOLS:
                old = items.get(item.get("id"), {})
                item["_started_at"] = old.get("_started_at") or (at if method == "item/started" else None)
                item["_completed_at"] = at if method == "item/completed" else None
                items[item.get("id")] = item
        if method == "error" or "error" in message:
            request_method = requests.get(message.get("id"))
            errors.append({"at": at, "method": method or request_method,
                           "scope": "worker_turn" if method == "error" or str(request_method).startswith("turn/") else "measurement_or_setup",
                           "code": (message.get("error") or {}).get("code"),
                           "will_retry": params.get("willRetry")})
    return {"lifecycle": lifecycle, "first_agent_text_at": first_text,
            "latest_native_usage_total": usage_total, "notification_counts": dict(methods),
            "rpc_errors": errors, "execution_items": summarize_items(items)}


def locate_multica_rollouts(task, workspaces, source_home):
    """Use Multica's stable task-root index, then its scoped per-issue sessions."""
    task_id, workspace, issue, agent = (task.get(k) for k in ("id", "workspace_id", "issue_id", "agent_id"))
    paths = []
    if task_id and workspace:
        identity = hashlib.sha256((workspace + "\0" + task_id).encode()).hexdigest()[:32]
        record = read_json(workspaces / ".task_roots" / identity / "root.json", {})
        if record.get("task_id") == task_id and record.get("workspace_id") == workspace:
            root = (workspaces / record.get("relative_path", "")).resolve()
            if root.is_relative_to(workspaces.resolve()):
                paths = list((root / "codex-home" / "sessions").rglob("*.jsonl"))
    if not paths and issue and agent:
        store = source_home / "multica-sessions"
        for scoped in store.glob("*/" + agent + "/" + issue):
            paths.extend(scoped.rglob("*.jsonl"))
    session = (task.get("result") or {}).get("session_id")
    if session:
        paths = [p for p in paths if session in p.name]
    return sorted(set(p.resolve() for p in paths))


def multica_attempt(task, directory, workspaces, source_home):
    result = task.get("result") or {}
    parsed = [native_rollout(p, task.get("started_at"), task.get("completed_at"))
              for p in locate_multica_rollouts(task, workspaces, source_home)]
    native = sum_usage([p.get("usage") for p in parsed])
    api = task.get("usage")
    rows = api if isinstance(api, list) else []
    aggregate = {k: sum(int(row.get(k, 0) or 0) for row in rows) for k in (
        "input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens")} if rows else None
    expected = multica_usage(native)
    return {"task_id": task.get("id"), "attempt": task.get("attempt"), "status": task.get("status"),
            "started_at": task.get("started_at"), "completed_at": task.get("completed_at"),
            "task_wall_seconds": seconds(task.get("started_at"), task.get("completed_at")),
            "session_id": result.get("session_id"), "task_has_error": bool(task.get("error")),
            "api_usage_rows": rows, "api_normalized_usage": aggregate,
            "native_usage": native, "native_normalized_usage": expected,
            "api_matches_native_normalization": aggregate == expected if aggregate is not None and expected is not None else None,
            "native_rollouts": parsed, "final_output": result.get("output")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--direct-dir", type=Path)
    parser.add_argument("--multica-dir", type=Path)
    parser.add_argument("--source-codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--multica-workspaces", type=Path, default=PROJECT / "Saved" / "Multica" / "workspaces")
    parser.add_argument("--output", type=Path, default=BASE / "Controller" / "measurement-summary.json")
    args = parser.parse_args()
    base = args.base.resolve()
    output = args.output.resolve()
    if not output.is_relative_to((BASE / "Controller").resolve()):
        raise ValueError("Derived reports must stay under Controller.")
    protocol = read_json(base / "controller-state.json", {})
    definitions = protocol.get("runs", [])
    direct_id = next((r.get("run_id") for r in definitions if r.get("route") == "direct"), "BenchA")
    multica_id = next((r.get("run_id") for r in definitions if r.get("route") == "multica"), "BenchB")
    direct_dir = args.direct_dir or base / "DirectRun"
    multica_dir = args.multica_dir or base / multica_id
    direct_meta = read_json(direct_dir / "run.json", {})
    rollout_path = direct_meta.get("rollout_path")
    direct = {"run_id": direct_id, "status": direct_meta.get("status", "pending"),
              "thread_id": direct_meta.get("thread_id"), "session_id": direct_meta.get("session_id"),
              "client_started_at": direct_meta.get("started_at"), "turn_sent_at": direct_meta.get("turn_sent_at"),
              "client_wall_seconds": direct_meta.get("client_wall_seconds"), "client_timing": direct_meta.get("timing"),
              "client_native_usage_total": usage(direct_meta.get("native_usage_total")),
              "native": native_rollout(Path(rollout_path) if rollout_path else None),
              "rpc": direct_rpc(direct_dir / "rpc.jsonl"),
              "worker_report": read_json(base / direct_id / "worker-report.json")}
    final_file = direct_dir / "final_output.md"
    direct["final_output"] = final_file.read_text(encoding="utf-8") if final_file.is_file() else None
    original_agents = next((x for x in direct_meta.get("instruction_files_before", [])
                            if Path(x.get("path", "")).name == "AGENTS.md"), {})
    injected = base / multica_id / "injected-AGENTS.md"
    instruction_size = {"direct_project_AGENTS": original_agents,
                        "multica_injected_AGENTS_bytes": injected.stat().st_size if injected.is_file() else None,
                        "byte_delta": injected.stat().st_size - original_agents["bytes"]
                        if injected.is_file() and original_agents.get("bytes") is not None else None,
                        "limit": "File byte delta is not a token estimate or the complete model prompt; it may include newline normalization."}
    tasks = read_json(multica_dir / "multica-task-runs.json", [])
    if not tasks:
        pending = read_json(multica_dir / "multica-run-request.json")
        tasks = [pending] if isinstance(pending, dict) and pending.get("id") else []
    tasks = sorted((task for task in tasks if isinstance(task, dict)),
                   key=lambda task: (int(task.get("attempt") or 0), task.get("created_at") or ""))
    attempts = [multica_attempt(task, multica_dir, args.multica_workspaces, args.source_codex_home) for task in tasks]
    raw_messages = read_json(multica_dir / "multica-messages.json", [])
    messages = raw_messages if isinstance(raw_messages, list) else raw_messages.get("messages", [])
    message_counts = Counter(row.get("type") for row in messages)
    summary = {"schema_version": 1, "snapshot_at": datetime.now(timezone.utc).isoformat(),
               "direct": direct,
               "multica": {"run_id": multica_id, "status": attempts[-1]["status"] if attempts else "pending",
                           "attempt_count": len(attempts), "attempts": attempts,
                           "all_attempts_native_usage": sum_usage([a["native_usage"] for a in attempts]),
                           "api_message_counts": dict(message_counts),
                           "api_message_task_ids": sorted({r["task_id"] for r in messages if r.get("task_id")}),
                           "api_message_file_limit": "Controller status currently stores only its last task's messages when several attempts exist; native evidence covers each discovered rollout.",
                           "worker_report": read_json(base / multica_id / "worker-report.json")},
               "shared_controller_preparation": {
                   "snapshot_file": str(BASE / "Controller" / "controller_usage_snapshot.json"),
                   "accounting": "Separate substantial shared preparation/control/verification cost; never included in either worker total. Refresh with snapshot_controller_usage.py."},
               "instruction_size_evidence": instruction_size,
               "measurement_limits": LIMITS}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Print only aggregate status/counts, never full tool output, auth or account data.
    print(json.dumps({"report": str(output), "direct_status": direct["status"],
                      "direct_native_response_count": direct["native"].get("response_count"),
                      "multica_status": summary["multica"]["status"], "multica_attempt_count": len(attempts)}, indent=2))


if __name__ == "__main__":
    main()
