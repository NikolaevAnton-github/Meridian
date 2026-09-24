"""Snapshot controller/helper usage after the benchmark instruction, no services.

Only session metadata and token_usage_record fields are inspected. No auth,
account records, model output, encrypted reasoning or tool results are extracted.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[3] / 'Saved/AgentSetup/OrchestrationAB/Controller'
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens", "total_tokens")
ROOT_THREAD = "01a09a0f-3b99-78e3-8f66-ba447979da35"
THIS_HELPER = "01a09a79-3eac-7173-adc5-d59ac90afc31"
BOUNDARY = "2026-09-13T11:45:22.582Z"


def lines(path):
    with path.open("rb") as stream:
        remaining = path.stat().st_size
        while remaining > 0:
            raw = stream.readline(remaining)
            remaining -= len(raw)
            if not raw:
                break
            try:
                yield json.loads(raw)
            except (ValueError, UnicodeError):
                continue


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def collect_native_usage(path, since, thread_id=None, until=None):
    """Reusable metadata-only run slice; never sum cumulative native counters.

    First/second/peak inputs describe observed requests after the boundary. The
    second request is NOT asserted to be a universal bootstrap-complete event.
    Output includes reasoning and input includes cached input.
    """
    cutoff = timestamp(since)
    end = timestamp(until) if until else float('inf')
    meta, contexts, responses = {}, [], {}
    for row in lines(Path(path)):
        kind, payload = row.get('type'), row.get('payload') or {}
        if kind == 'session_meta':
            meta = {k: payload.get(k) for k in ('id', 'session_id', 'cli_version', 'source', 'model_provider')}
            if thread_id and meta['id'] != thread_id:
                raise ValueError('Native thread identity mismatch')
        if kind not in ('turn_context', 'token_usage_record'):
            continue
        try:
            at = timestamp(row.get('timestamp', '1970-01-01T00:00:00Z'))
        except (ValueError, TypeError):
            continue
        if at < cutoff or at > end:
            continue
        if kind == 'turn_context':
            contexts.append({k: payload.get(k) for k in ('model', 'effort', 'service_tier', 'turn_id')})
            continue
        if payload.get('thread_id') not in (None, thread_id or meta.get('id')):
            continue
        response_id = payload.get('response_id')
        if not response_id:
            # A timestamp fallback cannot prove unique response accounting.
            continue
        usage = payload.get('usage') or {}
        if not all(isinstance(usage.get(k, 0), int) and usage.get(k, 0) >= 0 for k in FIELDS):
            raise ValueError('Invalid native usage record')
        responses[response_id] = {'at': row.get('timestamp'), 'usage': {k: usage.get(k, 0) for k in FIELDS}}
    ordered = sorted(responses.values(), key=lambda x: x['at'])
    totals = {k: sum(r['usage'][k] for r in ordered) for k in FIELDS}
    inputs = [r['usage']['input_tokens'] for r in ordered]
    return {'native': meta, 'contexts': contexts, 'unique_response_count': len(ordered),
            'first_response_at': ordered[0]['at'] if ordered else None,
            'last_response_at': ordered[-1]['at'] if ordered else None,
            'first_input_tokens': inputs[0] if inputs else None,
            'input_after_first_response_tokens': inputs[1] if len(inputs) > 1 else None,
            'peak_input_tokens': max(inputs) if inputs else None,
            'last_input_tokens': inputs[-1] if inputs else None,
            'observed_growth_tokens': max(inputs) - inputs[0] if inputs else None,
            'native_usage': totals,
            'output_includes_reasoning_check': all(r['usage']['total_tokens'] == r['usage']['input_tokens'] + r['usage']['output_tokens'] for r in ordered),
            'responses': ordered}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-dir", type=Path, default=Path.home() / ".codex/sessions/2026/09/13")
    parser.add_argument("--root-thread-id", default=ROOT_THREAD)
    parser.add_argument("--since", default=BOUNDARY)
    parser.add_argument("--output", type=Path, default=BASE / "controller_usage_snapshot.json")
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(BASE):
        raise ValueError("Usage snapshots must remain under Controller.")
    cutoff = timestamp(args.since)
    selected = []
    # Only this date directory is scanned; unrelated files get one metadata read.
    for path in args.sessions_dir.glob("*.jsonl"):
        try:
            with path.open("rb") as stream:
                first = json.loads(stream.readline())
        except (OSError, ValueError):
            continue
        meta = first.get("payload") or {}
        if first.get("type") != "session_meta" or meta.get("session_id") != args.root_thread_id:
            continue
        thread = meta.get("id")
        responses = {}
        for row in lines(path):
            if row.get("type") != "token_usage_record" or timestamp(row.get("timestamp", "1970-01-01T00:00:00Z")) < cutoff:
                continue
            payload = row.get("payload") or {}
            if payload.get("thread_id") not in (None, thread):
                continue
            responses[payload.get("response_id") or row.get("timestamp")] = {
                "at": row.get("timestamp"), "usage": payload.get("usage") or {}}
        totals = {key: sum(int(row["usage"].get(key, 0) or 0) for row in responses.values()) for key in FIELDS}
        selected.append({"role": "controller" if thread == args.root_thread_id else "helper",
                         "helper_label": "multica_codex_pilot" if thread == THIS_HELPER else None,
                         "thread_id": thread, "session_id": meta.get("session_id"), "source_path": str(path),
                         "native_source": meta.get("source"), "unique_response_count": len(responses),
                         "first_response_at": min((r["at"] for r in responses.values()), default=None),
                         "last_response_at": max((r["at"] for r in responses.values()), default=None),
                         "native_usage": totals,
                         "output_includes_reasoning_check": totals["total_tokens"] == totals["input_tokens"] + totals["output_tokens"]})
    aggregate = {key: sum(row["native_usage"][key] for row in selected) for key in FIELDS}
    result = {"schema_version": 1, "snapshot_at": datetime.now(timezone.utc).isoformat(),
              "instruction_boundary_at": args.since,
              "boundary_evidence": "Root user message containing the full-asset benchmark instruction was observed at this exact timestamp; prompt content is not copied.",
              "root_thread_id": args.root_thread_id, "threads": selected,
              "shared_controller_and_helpers_native_usage": aggregate,
              "worker_usage_included": False,
              "limits": ["This is shared preparation, control and verification work, separate from both worker runs.",
                         "The snapshot is partial while controller/helper turns continue; refresh after final measurement/report preparation.",
                         "Only root-session threads stored in the selected date directory are included. Missing or remote traces remain unmeasured.",
                         "Per-response usage is counted once by response ID within each native thread; cumulative usage is not summed.",
                         "Output includes reasoning. Cached input remains part of native input. No dollar or subscription-quota conversion is inferred."]}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(args.output), "thread_count": len(selected),
                      "response_count": sum(r["unique_response_count"] for r in selected),
                      "worker_usage_included": False}, indent=2))


if __name__ == "__main__":
    main()
