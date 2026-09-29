#!/usr/bin/env python3
"""Compare one DP-03 runtime factor using exact CSV and launch-manifest evidence.

    python Scripts/DestructionPerf01/compare_dp03.py <exact-csv-paths> \
        --control-run vendor --candidate-run native --factor collision \
        --launch-manifest Saved/vendor-launch.json \
        --launch-manifest Saved/native-launch.json \
        --output Saved/DestructionPerf01/DP-03/collision-pair.json

The collision or notification switch is the only permitted identity difference.
Keep one first-process blast separate from at least three warmed ordinal pairs.
Counter reductions and timing variation are independent evidence, not acceptance.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

import analyze
import compare_isolation as isolation


MODES = {"collision": ("collision_mode", "DestructionCollisionMode", {"vendor", "observe", "native"}),
         "notification": ("notification_mode", "DestructionNotificationMode", {"immediate", "batch"})}
COLLISION_COUNTERS = (
    "raw_callbacks", "forwarded_callbacks", "native_callbacks", "fast_handled_callbacks", "fallback_callbacks",
    "profile_requested", "profile_applied", "profile_skipped_identical", "profile_skipped_setter",
    "profile_unapplied", "profile_native_calls", "sleep_retriggers", "reset_invalidations",
)
NOTIFICATION_COUNTERS = (
    "raw_break_callbacks", "queued_changes", "published_batches", "published_changes", "legacy_publications",
    "reset_invalidations", "invalidated_changes", "lifetime_invalidated_changes", "physics_recreations",
)
LIFETIME_FIELDS = ("actor_path", "adapter_path", "collection_path", "adapter_lifetime_id")


def count(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0 and float(value).is_integer())


def analyze_capture(path: Path) -> dict[str, Any]:
    capture = analyze.analyze_capture(path)
    rows, digest = analyze.read_capture(path)
    if digest != capture["capture_sha256"]:
        raise ValueError(f"Capture changed while being analyzed: {path}")
    capture["first_five_seconds"] = analyze.summarize_dp01_phase(
        [row for row in rows if 0 <= row["relative_seconds"] < 5])
    return capture


def timing_values(captures: list[dict[str, Any]], column: str, metric: str) -> list[float | None]:
    return [(capture["first_five_seconds"]["frame_time"] if column == "frame_ms" else
             capture["first_five_seconds"]["coarse_non_additive_counters"][column])[metric]
            for capture in captures]


def first_five_summary(captures: list[dict[str, Any]]) -> dict[str, Any]:
    return {"run_count": len(captures), "metrics_ms": {
        column: {metric: analyze.repeated_metric([value for value in timing_values(captures, column, metric)
                                                if value is not None]) for metric in analyze.TIMING_METRICS}
        for column in ("frame_ms", *analyze.THREAD_COLUMNS)}}


def first_five_differences(control: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for column in ("frame_ms", *analyze.THREAD_COLUMNS):
        result[column] = {}
        for metric in analyze.TIMING_METRICS:
            left, right = (timing_values(group, column, metric) for group in (control, candidate))
            a, b = (analyze.repeated_metric([value for value in values if value is not None])
                    for values in (left, right))
            pairs = [{"run_index": capture["metadata"]["content"]["run_index"],
                      "candidate_minus_control_ms": y - x if x is not None and y is not None else None}
                     for capture, x, y in zip(control, left, right)]
            deltas = [pair["candidate_minus_control_ms"] for pair in pairs
                      if pair["candidate_minus_control_ms"] is not None]
            complete = len(deltas) == len(control) == len(candidate) and len(deltas) >= 3
            delta = (b["median_of_run_values"] - a["median_of_run_values"]
                     if a["run_count"] and b["run_count"] else None)
            result[column][metric] = {
                "control": a, "candidate": b, "candidate_minus_control_median_ms": delta,
                "paired_run_deltas": pairs, "paired_delta_variability_ms": analyze.repeated_metric(deltas),
                "complete_warm_metric_pairs": complete,
                "observed_ranges_do_not_overlap": (b["maximum_run_value"] < a["minimum_run_value"]
                    or a["maximum_run_value"] < b["minimum_run_value"]) if complete else None,
                "absolute_median_shift_exceeds_larger_observed_run_range":
                    abs(delta) > max(a["run_value_range"], b["run_value_range"]) if complete else None,
            }
    return result


def snapshot_evidence(values: Any, metadata: dict[str, Any], endpoint: str,
                      problems: list[str]) -> dict[tuple[str, str], dict[str, Any]]:
    if not isinstance(values, list) or not values:
        problems.append(f"{endpoint}: nonempty actor snapshot required")
        return {}
    indexed = {}
    lifetimes = set()
    for prop in values:
        if not isinstance(prop, dict) or not all(isinstance(prop.get(key), str) and prop[key] for key in ("actor", "id")):
            problems.append(f"{endpoint}: actor path plus adapter ID required")
            continue
        key = (prop["actor"], prop["id"])
        label = f"{endpoint}/{prop['actor']}"
        if key in indexed:
            problems.append(f"{label}: duplicate actor identity")
        indexed[key] = prop
        for field in ("reset_generation", "collision_revision", "break_events"):
            if not count(prop.get(field)):
                problems.append(f"{label}: missing/invalid {field}")
        notification = prop.get("notifications")
        collision = prop.get("collision_policy")
        for group, stats, fields in (("notifications", notification, NOTIFICATION_COUNTERS + ("pending_changes",)),
                                     ("collision_policy", collision, COLLISION_COUNTERS)):
            if not isinstance(stats, dict):
                problems.append(f"{label}: missing {group}")
                continue
            missing = [field for field in fields if not count(stats.get(field))]
            if missing:
                problems.append(f"{label}: missing/invalid {group} counters: {', '.join(missing)}")
        if isinstance(notification, dict):
            valid_identity = (all(isinstance(notification.get(field), str) and notification[field]
                                  for field in LIFETIME_FIELDS[:-1])
                              and count(notification.get("adapter_lifetime_id"))
                              and notification["adapter_lifetime_id"] > 0)
            if not valid_identity or notification.get("actor_path") != prop["actor"]:
                problems.append(f"{label}: complete matching notification lifetime identity required")
            elif notification["adapter_lifetime_id"] in lifetimes:
                problems.append(f"{label}: duplicate notification lifetime ID")
            else:
                lifetimes.add(notification["adapter_lifetime_id"])
            mode = notification.get("mode")
            if mode != metadata.get("notification_mode"):
                problems.append(f"{label}: notification mode mismatch")
            if notification.get("physics_recreating") is not False:
                problems.append(f"{label}: notification physics lifetime is unavailable/recreating")
            if all(count(notification.get(field)) for field in NOTIFICATION_COUNTERS + ("pending_changes",)):
                raw, pending = notification["raw_break_callbacks"], notification["pending_changes"]
                if raw != prop.get("break_events"):
                    problems.append(f"{label}: raw callbacks disagree with break_events")
                if (notification["published_changes"] + pending + notification["lifetime_invalidated_changes"] !=
                        raw + 1 + notification["physics_recreations"]):
                    problems.append(f"{label}: required changes are missing or duplicated")
                if notification["published_batches"] > notification["published_changes"]:
                    problems.append(f"{label}: published batches exceed changes")
                if endpoint in ("props_before", "props_after") and pending:
                    problems.append(f"{label}: complete capture boundary has pending notifications")
                if mode == "immediate" and (pending or notification["queued_changes"]
                        or notification["published_batches"] != notification["published_changes"]):
                    problems.append(f"{label}: immediate notification accounting mismatch")
                if mode == "batch" and notification["queued_changes"] != raw:
                    problems.append(f"{label}: batch queue must contain every raw break change")
        if isinstance(collision, dict):
            mode = collision.get("mode")
            observed = mode in ("observe", "native")
            if mode != metadata.get("collision_mode"):
                problems.append(f"{label}: collision mode mismatch")
            if collision.get("counters_available") is not observed or collision.get("installed") is not observed:
                problems.append(f"{label}: collision installation/counter availability mismatch")
            if observed and collision.get("validated") is not True:
                problems.append(f"{label}: collision policy validation failed")
            if collision.get("actor") != prop["actor"] or not collision.get("component"):
                problems.append(f"{label}: matching collision actor/component identity required")
            if isinstance(notification, dict) and collision.get("component") != notification.get("collection_path"):
                problems.append(f"{label}: collision and notification collection identities differ")
            if all(count(collision.get(field)) for field in COLLISION_COUNTERS):
                if not observed and any(collision[field] for field in COLLISION_COUNTERS):
                    problems.append(f"{label}: vendor counters are unavailable and must remain zero")
                if observed:
                    if collision["profile_requested"] != sum(collision[field] for field in
                            ("profile_applied", "profile_skipped_identical", "profile_unapplied")):
                        problems.append(f"{label}: requested profile accounting mismatch")
                    skipped = collision["profile_skipped_setter"]
                    if skipped > collision["profile_skipped_identical"] or mode == "observe" and skipped:
                        problems.append(f"{label}: skipped setter accounting mismatch")
                    expected_calls = collision["profile_requested"] - skipped
                    if collision["profile_native_calls"] != expected_calls:
                        problems.append(f"{label}: native profile call accounting mismatch")
                    if (collision["raw_callbacks"] != collision["native_callbacks"] + collision["forwarded_callbacks"]
                            or collision["fast_handled_callbacks"] != collision["native_callbacks"]
                            or mode == "observe" and collision["native_callbacks"]):
                        problems.append(f"{label}: required collision callback accounting mismatch")
                    if collision["fallback_callbacks"] or collision["profile_unapplied"]:
                        problems.append(f"{label}: collision fallback or unapplied profile requests occurred")
    return indexed


def delta_evidence(before: dict, after: dict, label: str, problems: list[str]) -> list[dict[str, Any]]:
    if set(before) != set(after):
        problems.append(f"{label}: actor sets differ")
    actors = []
    for key in sorted(before.keys() & after.keys()):
        a, b = before[key], after[key]
        left, right = a.get("notifications", {}), b.get("notifications", {})
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        if any(left.get(field) != right.get(field) for field in LIFETIME_FIELDS) or a.get("reset_generation") != b.get("reset_generation"):
            problems.append(f"{label}/{key[0]}: actor lifetime/reset identity changed inside the capture")
        counters = {}
        for group, fields in (("collision_policy", COLLISION_COUNTERS), ("notifications", NOTIFICATION_COUNTERS)):
            start, end = a.get(group, {}), b.get(group, {})
            if not isinstance(start, dict) or not isinstance(end, dict):
                continue
            for field in fields:
                x, y = start.get(field), end.get(field)
                valid = count(x) and count(y) and y >= x
                if not valid:
                    problems.append(f"{label}/{key[0]}: nonmonotonic or missing {group}.{field}")
                available = valid and (group != "collision_policy" or start.get("counters_available") is True
                                       and end.get("counters_available") is True)
                counters[f"{group}.{field}"] = y - x if available else None
        revision_delta = b["collision_revision"] - a["collision_revision"] if all(count(p.get("collision_revision")) for p in (a, b)) else None
        if revision_delta != counters.get("notifications.raw_break_callbacks"):
            problems.append(f"{label}/{key[0]}: required collision revisions do not match raw callbacks")
        actors.append({"actor": key[0], "adapter_id": key[1],
                       "lifetime": {field: left.get(field) for field in LIFETIME_FIELDS},
                       "reset_generation": a.get("reset_generation"), "collision_revision_delta": revision_delta,
                       "pending_notifications_before": left.get("pending_changes"),
                       "pending_notifications_after": right.get("pending_changes"), "counter_deltas": counters})
    return actors


def prop_evidence(capture: dict[str, Any]) -> dict[str, Any]:
    metadata = capture["metadata"]["content"]
    problems: list[str] = []
    snapshots = {endpoint: snapshot_evidence(metadata.get(endpoint), metadata, endpoint, problems)
                 for endpoint in ("props_before", "props_after", "dp03_detonation_props", "dp03_first_five_props")}
    actors = delta_evidence(snapshots["props_before"], snapshots["props_after"], "whole_capture", problems)
    early = delta_evidence(snapshots["dp03_detonation_props"], snapshots["dp03_first_five_props"], "first_five_counter_window", problems)
    for endpoint in ("dp03_detonation_props", "dp03_first_five_props"):
        if set(snapshots[endpoint]) != set(snapshots["props_before"]):
            problems.append(f"{endpoint}: actor set differs from capture boundaries")
        # Also bind intermediate windows to this capture's exact lifetime and counters.
        delta_evidence(snapshots["props_before"], snapshots[endpoint], f"capture_start_to_{endpoint}", problems)
        delta_evidence(snapshots[endpoint], snapshots["props_after"], f"{endpoint}_to_capture_end", problems)
    end = metadata.get("dp03_first_five_counter_end_seconds")
    if not isinstance(end, (int, float)) or isinstance(end, bool) or not math.isfinite(end) or end < 5:
        problems.append("Missing/invalid first-five counter window end time")
    if metadata.get("collision_mode") in ("observe", "native"):
        required = ("raw_callbacks", "profile_requested") + (("fast_handled_callbacks",) if metadata["collision_mode"] == "native" else ())
        for field in required:
            if not any((actor["counter_deltas"].get(f"collision_policy.{field}") or 0) > 0 for actor in actors):
                problems.append(f"Collision mode was not exercised: {field}")
    if not any((actor["counter_deltas"].get("notifications.raw_break_callbacks") or 0) > 0 for actor in actors):
        problems.append("Notification mode was not exercised: no raw break callbacks")
    return {"run_name": metadata.get("run_name"), "run_index": metadata.get("run_index"),
            "actor_count": len(actors), "actors": actors,
            "first_five_counter_window": {"start_seconds": 0, "observed_end_seconds": end,
                                          "actors": early, "note": "End snapshot is the first fixture tick >=5 seconds; includes overshoot."},
            "problems": problems}


def counter_summary(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for window in ("whole_capture", "first_five_counter_window"):
        actors_by_run = [item["actors"] if window == "whole_capture" else item[window]["actors"] for item in evidence]
        fields = [f"{group}.{field}" for group, counters in (("collision_policy", COLLISION_COUNTERS),
                                                             ("notifications", NOTIFICATION_COUNTERS)) for field in counters]
        result[window] = {field: analyze.repeated_metric([
            sum(actor["counter_deltas"][field] for actor in actors) for actors in actors_by_run
            if actors and all(actor["counter_deltas"].get(field) is not None for actor in actors)]) for field in fields}
    return result


def reset_series_evidence(captures: list[dict[str, Any]], name: str) -> dict[str, Any]:
    _, cold, warm = analyze.series_runs(captures, name)
    previous_generations: list[int] | None = None
    seen_lifetimes = set()
    observations, problems = [], []
    for capture in cold + warm:
        metadata = capture["metadata"]["content"]
        props = metadata.get("props_before", [])
        props = props if isinstance(props, list) else []
        props = [prop for prop in props if isinstance(prop, dict)]
        lifetimes = [prop.get("notifications", {}).get("adapter_lifetime_id") for prop in props
                     if isinstance(prop.get("notifications"), dict)]
        generations = sorted(prop["reset_generation"] for prop in props if count(prop.get("reset_generation")))
        valid_lifetimes = {value for value in lifetimes if count(value)}
        if seen_lifetimes & valid_lifetimes:
            problems.append(f"{name}: reset reused a prior adapter lifetime")
        if previous_generations is not None and (len(generations) != len(previous_generations)
                or any(current <= previous for current, previous in zip(generations, previous_generations))):
            problems.append(f"{name}: reset generations did not advance between repetitions")
        seen_lifetimes.update(valid_lifetimes)
        observations.append({"run_index": metadata.get("run_index"), "adapter_lifetime_ids": lifetimes,
                             "sorted_reset_generations": generations})
        previous_generations = generations
    return {"per_run": observations, "problems": problems,
            "limit": "Distinct lifetimes and advancing generations are reset evidence, not proof of pending-reset bounds or gameplay correctness."}


def compare_dp03(captures: list[dict[str, Any]], manifests: list[dict[str, Any]],
                 control_name: str, candidate_name: str, factor: str) -> dict[str, Any]:
    if factor not in MODES:
        raise ValueError("DP-03 factor must be collision or notification")
    field, switch, _ = MODES[factor]
    launches = {manifest["content"].get("name"): manifest["content"] for manifest in manifests}
    arguments = tuple(f"-{switch}={launches.get(name, {}).get(field)}" for name in (control_name, candidate_name))
    result = isolation.compare_isolation(captures, manifests, control_name, candidate_name, factor,
                                         allowed_metadata_fields=(field,), allowed_launch_arguments=arguments)
    problems = result["problems"]
    for kind, (key, flag, known) in MODES.items():
        values = {}
        for name in (control_name, candidate_name):
            launch = launches.get(name, {})
            mode = launch.get(key)
            values[name] = mode
            if not isinstance(mode, str) or mode not in known:
                problems.append(f"{name}: missing or unknown {key}")
            expected = f"-{flag}={mode}"
            raw_arguments = launch.get("arguments")
            observed = [value for value in (raw_arguments if isinstance(raw_arguments, list) else [])
                        if isinstance(value, str) and value.lower().startswith(f"-{flag}=".lower())]
            if observed != [expected]:
                problems.append(f"{name}: exact single {flag} argument must match the manifest")
            for capture in captures:
                metadata = capture["metadata"]["content"]
                if metadata.get("run_name") == name and metadata.get(key) != mode:
                    problems.append(f"{name}: capture/launcher mismatch for {key}")
        changed = values[control_name] != values[candidate_name]
        if changed != (kind == factor):
            problems.append(f"Exactly the declared {factor} mode must change; found {key} changed={changed}")
    evidence = [prop_evidence(capture) for capture in captures]
    for item in evidence:
        problems.extend(f"{item['run_name']}[{item['run_index']}]: {problem}" for problem in item["problems"])
    result["dp03_actor_evidence"] = evidence
    for name in (control_name, candidate_name):
        selected, cold, warm = analyze.series_runs(captures, name)
        resets = reset_series_evidence(captures, name)
        result["series"][name]["dp03_resets"] = resets
        problems.extend(resets["problems"])
        if any(not capture.get("first_five_seconds", {}).get("frame_count") for capture in selected):
            problems.append(f"{name}: first-five-second frame evidence missing")
            continue
        result["series"][name]["first_five_seconds"] = {
            "first_process_blast": first_five_summary(cold), "warm": first_five_summary(warm)}
        result["series"][name]["dp03_warm_counter_deltas"] = counter_summary(
            sorted([item for item in evidence if item["run_name"] == name and item["run_index"] in
                    [capture["metadata"]["content"]["run_index"] for capture in warm]], key=lambda item: item["run_index"]))
    result["problems"] = sorted(set(problems))
    result["status"] = "identity_verified" if not problems else "not_comparable"
    result["counter_interpretation"] = (
        "Whole-capture counter deltas include pre-blast work; first-five counter endpoints retain their measured overshoot. "
        "profile_applied counts changed authoritative override names; profile_native_calls counts setter invocations; "
        "profile_skipped_setter counts native fast-path omissions. Counters do not measure CPU time, active bodies or "
        "physics-proxy writes. Frame/thread metrics use [0,5) real "
        "seconds after blast. Fewer redundant operations may coexist with overlapping/noisy frame-time distributions. "
        "Equal actor counts do not establish equivalent openings, cover, bullet collision or traversal.")
    if problems:
        result.pop("warm_phase_differences", None)
    else:
        result["warm_first_five_differences"] = first_five_differences(
            analyze.series_runs(captures, control_name)[2], analyze.series_runs(captures, candidate_name)[2])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("captures", nargs="+", help="Exact native CSV paths; adjacent JSON required")
    parser.add_argument("--control-run", required=True)
    parser.add_argument("--candidate-run", required=True)
    parser.add_argument("--factor", choices=sorted(MODES), required=True)
    parser.add_argument("--launch-manifest", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        paths = [Path(value).resolve() for value in args.captures]
        manifest_paths = [Path(value).resolve() for value in args.launch_manifest]
        output = analyze.output_path_checked(args.output)
        if len(paths) > isolation.MAX_CAPTURES or len(set(paths)) != len(paths) or len(manifest_paths) != 2:
            raise ValueError(f"Supply at most {isolation.MAX_CAPTURES} unique captures and exactly two launch manifests")
        evidence_paths = paths + [path.with_suffix(".json") for path in paths] + manifest_paths
        if sum(path.stat().st_size for path in evidence_paths) > isolation.MAX_INPUT_BYTES:
            raise ValueError(f"Total evidence input exceeds {isolation.MAX_INPUT_BYTES} bytes")
        captures = [analyze_capture(path) for path in paths]
        manifests = [isolation.read_manifest(path) for path in manifest_paths]
        result = compare_dp03(captures, manifests, args.control_run, args.candidate_run, args.factor)
        report = {"schema": "DestructionPerf01.DP-03.comparison.v1",
                  "created_utc": datetime.now(timezone.utc).isoformat(),
                  "phase_version": analyze.DP01_PHASE_VERSION,
                  "phase_intervals_seconds": {name: {"start_inclusive": start, "end_exclusive": end}
                                              for name, start, end, _ in analyze.DP01_PHASES},
                  "first_five_seconds_interval": {"start_inclusive": 0, "end_exclusive": 5},
                  "comparison": result, "captures": captures, "launch_manifests": manifests}
        encoded = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        parser.error(str(error))
    print(f"DP-03 {result['status']}: {output}")
    if result["problems"]:
        parser.exit(2)


if __name__ == "__main__":
    main()
