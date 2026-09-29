#!/usr/bin/env python3
"""Compare one explicitly declared DP-02 diagnostic factor using exact captures.

Example (quote launch arguments containing a leading dash using '=' syntax):
    python Scripts/DestructionPerf01/compare_isolation.py <exact-csv-paths> \
        --control-run control --candidate-run candidate \
        --factor profile-call-observation --allow-metadata-field isolation_mode \
        --allow-launch-argument=-DestructionPerfIsolation=reference \
        --allow-launch-argument=-DestructionPerfIsolation=profile_observe \
        --launch-manifest Saved/control-launch.json \
        --launch-manifest Saved/candidate-launch.json --output Saved/pair01.json

Pass exact file paths; the script does not expand globs. First-process blasts
remain separate from at least three warm ordinal pairs. This report identifies
observed differences, not accepted optimizations or equivalent damage outcomes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import analyze


MAX_CAPTURES = 16
MAX_INPUT_BYTES = 128 * 1024 * 1024
LAUNCH_IDENTITY_FIELDS = (
    "candidate_commit", "workload_identity", "dll_sha256", "source_hashes",
    "asset_config_hashes", "map_sha256", "engine_build", "executable",
)
IMMUTABLE_METADATA_FIELDS = set(analyze.IDENTITY_FIELDS + analyze.INSTRUMENTATION_FIELDS) - {
    "fx.NiagaraComponentsEnabled",
}
VARIABLE_ARGUMENT_PREFIXES = (
    "-DestructionPerfAuto=", "-abslog=", "-tracefile=", "-DestructionPerfCommit=",
)
ISOLATION_COUNTERS = (
    "profile_calls", "requested_bone_ids", "profile_transactions", "committed_transactions",
    "flushes_with_work", "same_frame_repeated_id_requests", "same_frame_changed_profile_requests",
)
BRIDGE_IMPLEMENTATION = "vendor_break_event_bridge_v1"
BRIDGE_COUNTERS = ("break_events_received", "break_events_forwarded", "break_events_queued",
                   "profile_batch_calls", "profile_batch_bone_ids", "flushes_with_work")
ALL_ISOLATION_COUNTERS = tuple(dict.fromkeys((*ISOLATION_COUNTERS, *BRIDGE_COUNTERS)))
KNOWN_ISOLATION_MODES = {"reference", "profile_observe", "profile_batch", "collision_off"}


def diagnostic_switch_liveness(capture: dict[str, Any]) -> dict[str, Any]:
    """Validate versioned native-hook or delegate-bridge exposure before timing deltas."""
    metadata = capture["metadata"]["content"]
    mode = metadata.get("isolation_mode")
    result = {"capture_path": capture["capture_path"], "run_name": metadata.get("run_name"),
              "run_index": metadata.get("run_index"), "isolation_mode": mode,
              "status": "not_applicable", "problems": []}
    if mode not in KNOWN_ISOLATION_MODES:
        return result
    problems = result["problems"]
    snapshots = {}
    for field in ("isolation_before", "isolation_after"):
        snapshot = metadata.get(field)
        if not isinstance(snapshot, dict):
            problems.append(f"Missing {field} snapshot")
            snapshot = {}
        elif snapshot.get("mode") != mode:
            problems.append(f"{field} mode does not match isolation_mode")
        snapshots[field] = snapshot
    before, after = snapshots.values()

    def count(value: Any) -> bool:
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value >= 0 and float(value).is_integer())

    def positive_delta(key: str) -> None:
        left, right = before.get(key), after.get(key)
        if not count(left) or not count(right) or right <= left:
            problems.append(f"{key} must have a positive observed before/after delta")

    tags = [snapshot.get("diagnostic_implementation") for snapshot in snapshots.values()]
    implementation = "legacy_native_hook" if tags == [None, None] else tags[-1]
    bridge = tags == [BRIDGE_IMPLEMENTATION, BRIDGE_IMPLEMENTATION]
    if tags != [None, None] and not bridge:
        problems.append("Unsupported or mismatched diagnostic_implementation tags")
    elif bridge:
        relayed = mode in ("profile_observe", "profile_batch")
        for field, snapshot in snapshots.items():
            if snapshot.get("setup_failed") is not False or snapshot.get("setup_failures") != 0:
                problems.append(f"{field} must confirm successful bridge setup")
            configured = snapshot.get("configured_props")
            bindings = snapshot.get("prop_bindings")
            if (not count(configured) or configured <= 0 or not isinstance(bindings, list)
                    or len(bindings) != configured):
                problems.append(f"{field} must identify all configured prop bindings")
            elif any(not isinstance(binding, dict) or binding.get("break_bridge_installed") is not relayed
                     for binding in bindings):
                problems.append(f"{field} expected break_bridge_installed={relayed} for every configured prop")
            if not count(snapshot.get("pending_break_events")) or snapshot.get("pending_break_events") != 0:
                problems.append(f"{field} pending_break_events must be zero")
            if relayed:
                received, forwarded = snapshot.get("break_events_received"), snapshot.get("break_events_forwarded")
                if not count(received) or not count(forwarded) or received != forwarded:
                    problems.append(f"{field} received and forwarded break counts must be equal")
                queued = snapshot.get("break_events_queued")
                if not count(queued) or queued != (received if mode == "profile_batch" else 0):
                    problems.append(f"{field} queued break count does not match the selected bridge mode")
            if mode != "profile_batch":
                for key in ("profile_batch_calls", "profile_batch_bone_ids"):
                    if not count(snapshot.get(key)) or snapshot.get(key) != 0:
                        problems.append(f"{field} {key} must be zero outside profile_batch")
        if relayed:
            positive_delta("break_events_received")
            positive_delta("break_events_forwarded")
        if mode == "profile_batch":
            positive_delta("profile_batch_calls")
            positive_delta("profile_batch_bone_ids")
        if mode == "collision_off":
            suppressed = after.get("suppressed_vendor_collision_bindings")
            if not count(suppressed) or suppressed <= 0:
                problems.append("After snapshot must record positive suppressed_vendor_collision_bindings")
    elif mode in ("profile_observe", "profile_batch"):
        if after.get("native_hook_installed") is not True:
            problems.append("After snapshot must confirm native_hook_installed=true")
        positive_delta("profile_calls")
        positive_delta("requested_bone_ids")
        if mode == "profile_batch":
            positive_delta("profile_transactions")
            positive_delta("committed_transactions")
            for field, snapshot in snapshots.items():
                pending = snapshot.get("pending_transactions")
                if not count(pending) or pending != 0:
                    problems.append(f"{field} pending_transactions must be zero")
    else:
        for field, snapshot in snapshots.items():
            if snapshot.get("native_hook_installed") is not False:
                problems.append(f"{field} must confirm native_hook_installed=false")
        if mode == "collision_off":
            suppressed = after.get("suppressed_vendor_collision_bindings")
            if not count(suppressed) or suppressed <= 0:
                problems.append("After snapshot must record positive suppressed_vendor_collision_bindings")
    observation_fields = ("mode", "diagnostic_implementation", "native_hook_installed", "configured_props", "suppressed_vendor_collision_bindings",
                          "profile_calls", "requested_bone_ids", "profile_transactions", "committed_transactions",
                          "pending_transactions", "setup_failed", "setup_failures", "pending_break_events", *BRIDGE_COUNTERS)
    result.update({"status": "not_exercised" if problems else "verified",
                   "diagnostic_implementation": implementation,
                   "observed": {field: {key: snapshot.get(key) for key in observation_fields}
                                for field, snapshot in snapshots.items()}})
    return result


def isolation_observations(metadata: dict[str, Any]) -> dict[str, Any]:
    before, after = (metadata.get(key, {}) for key in ("isolation_before", "isolation_after"))
    hooked = isinstance(before, dict) and isinstance(after, dict) and all(
        snapshot.get("native_hook_installed") is True for snapshot in (before, after))
    bridged = isinstance(before, dict) and isinstance(after, dict) and all(
        snapshot.get("diagnostic_implementation") == BRIDGE_IMPLEMENTATION
        and snapshot.get("mode") in ("profile_observe", "profile_batch") for snapshot in (before, after))
    counters = {}
    for key in ALL_ISOLATION_COUNTERS:
        values = [snapshot.get(key) if isinstance(snapshot, dict) else None for snapshot in (before, after)]
        observed = (hooked and key in ISOLATION_COUNTERS) or (bridged and key in BRIDGE_COUNTERS)
        valid = observed and all(isinstance(value, (int, float)) and not isinstance(value, bool)
                               and math.isfinite(value) and value >= 0 for value in values)
        counters[key] = {"available": valid and values[1] >= values[0],
                         "before": values[0], "after": values[1],
                         "observed_delta": values[1] - values[0] if valid and values[1] >= values[0] else None}
    snapshots = {}
    for phase in ("DP01_Intact", "DP01_Burst", "DP01_Early", "DP01_Active", "DP01_Settled", "complete"):
        snapshot = metadata.get(f"isolation_phase_{phase}", {})
        actors = snapshot.get("actors") if isinstance(snapshot, dict) else None
        snapshots[phase] = {
            "available": isinstance(actors, list),
            "actor_observation_count": len(actors) if isinstance(actors, list) else None,
            "major_transform_position_observation_count": sum(
                len(actor.get("largest32_index_active_rest_bbox_volume_state_world_xyz", []))
                for actor in actors if isinstance(actor, dict)) if isinstance(actors, list) else None,
        }
    return {"counters": counters, "phase_snapshot_observation_counts": snapshots,
            "note": "Before/after deltas include pre-blast work. Legacy profile observations require the native hook; bridge event and explicit preapply counters require the versioned break bridge. Unobserved reference/collision_off fields are unavailable, not zero native calls. Bridge profile_batch_calls are explicit preapply operations, not measured original native profile calls or actual physics proxy writes. Phase positions are sampled GT mirrors, not solver trajectories or proof of equivalent openings."}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def read_manifest(path: Path) -> dict[str, Any]:
    if path.stat().st_size > analyze.MAX_METADATA_BYTES:
        raise ValueError(f"Launch manifest exceeds {analyze.MAX_METADATA_BYTES} bytes: {path}")
    raw = path.read_bytes()
    content = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(content, dict):
        raise ValueError(f"Launch manifest must be a JSON object: {path}")
    canonical(content)  # Reject non-finite JSON constants even in unused evidence.
    return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "content": content}


def normalized_arguments(manifest: dict[str, Any]) -> list[str] | None:
    arguments = manifest.get("arguments")
    if not isinstance(arguments, list) or not all(isinstance(value, str) for value in arguments):
        return None
    return [argument for argument in arguments if not argument.startswith(VARIABLE_ARGUMENT_PREFIXES)]


def run_observations(capture: dict[str, Any]) -> dict[str, Any]:
    content = capture["metadata"]["content"]
    workload = capture["prop_workload"]
    return {
        "run_index": content.get("run_index"), "capture_path": capture["capture_path"],
        "damaged_actor_observations": {
            "newly_root_broken_props": workload["newly_root_broken_props"],
            "props_with_break_notifications": sum(actor["break_notification_delta"] > 0
                for actor in workload["actors"]) if workload["available"] else None,
            "break_notification_delta": workload["break_notification_delta"],
        },
        "phase_diagnostic_observation_counts": {
            phase: value["diagnostic_sample_count"] for phase, value in capture["dp01_phases"].items()
        },
        "isolation": isolation_observations(content),
        "outcome_limit": "Root-break flags and break notifications do not measure openings or major chunk trajectories.",
    }


def aggregate_observations(captures: list[dict[str, Any]]) -> dict[str, Any]:
    observations = [run_observations(capture) for capture in captures]
    return {
        "per_run": observations,
        "damaged_actor_observations": {
            key: analyze.repeated_metric([item["damaged_actor_observations"][key] for item in observations
                                         if item["damaged_actor_observations"][key] is not None])
            for key in ("newly_root_broken_props", "props_with_break_notifications", "break_notification_delta")
        },
        "phase_diagnostic_observation_counts": {
            phase: analyze.repeated_metric([item["phase_diagnostic_observation_counts"][phase]
                                           for item in observations])
            for phase, *_ in analyze.DP01_PHASES
        },
        "isolation_counter_deltas": {
            key: analyze.repeated_metric([item["isolation"]["counters"][key]["observed_delta"]
                                         for item in observations if item["isolation"]["counters"][key]["available"]])
            for key in ALL_ISOLATION_COUNTERS
        },
    }


def phase_differences(control: list[dict[str, Any]], candidate: list[dict[str, Any]]) -> dict[str, Any]:
    """Pair by validated repeat ordinal; never pool frames across repetitions."""
    left, right = analyze.aggregate_runs(control), analyze.aggregate_runs(candidate)
    result = {}
    for phase, *_ in analyze.DP01_PHASES:
        result[phase] = {}
        for column in ("frame_ms", *analyze.THREAD_COLUMNS):
            result[phase][column] = {}
            for metric in analyze.TIMING_METRICS:
                baseline = left["phase_metrics_ms"][phase][column][metric]
                changed = right["phase_metrics_ms"][phase][column][metric]
                pairs = []
                for a, b in zip(control, candidate):
                    def value(capture: dict[str, Any]) -> float | None:
                        stats = capture["dp01_phases"][phase]
                        return (stats["frame_time"] if column == "frame_ms" else
                                stats["coarse_non_additive_counters"][column])[metric]
                    a_value, b_value = value(a), value(b)
                    pairs.append({"run_index": a["metadata"]["content"]["run_index"],
                                  "candidate_minus_control_ms": b_value - a_value
                                  if a_value is not None and b_value is not None else None})
                deltas = [pair["candidate_minus_control_ms"] for pair in pairs
                          if pair["candidate_minus_control_ms"] is not None]
                a_median, b_median = baseline["median_of_run_values"], changed["median_of_run_values"]
                delta = b_median - a_median if a_median is not None and b_median is not None else None
                ranges_available = baseline["run_value_range"] is not None and changed["run_value_range"] is not None
                largest_range = max(baseline["run_value_range"], changed["run_value_range"]) if ranges_available else None
                complete = len(deltas) == len(control) and len(deltas) >= 3
                result[phase][column][metric] = {
                    "control": baseline, "candidate": changed,
                    "candidate_minus_control_median_ms": delta,
                    "relative_delta_percent": 100 * delta / a_median if delta is not None and a_median else None,
                    "paired_run_deltas": pairs, "paired_delta_variability_ms": analyze.repeated_metric(deltas),
                    "complete_warm_metric_pairs": complete,
                    "observed_ranges_do_not_overlap": (changed["maximum_run_value"] < baseline["minimum_run_value"]
                        or baseline["maximum_run_value"] < changed["minimum_run_value"])
                        if complete and ranges_available else None,
                    "absolute_median_shift_exceeds_larger_observed_run_range": abs(delta) > largest_range
                        if complete and delta is not None and largest_range is not None else None,
                }
    return result


def compare_isolation(captures: list[dict[str, Any]], manifests: list[dict[str, Any]],
                      control_name: str, candidate_name: str, factor: str,
                      allowed_metadata_fields: tuple[str, ...] = (),
                      allowed_source_files: tuple[str, ...] = (),
                      allowed_launch_arguments: tuple[str, ...] = ()) -> dict[str, Any]:
    if not factor.strip() or control_name == candidate_name:
        raise ValueError("A nonempty factor label and two distinct run names are required")
    if set(allowed_metadata_fields) & IMMUTABLE_METADATA_FIELDS:
        raise ValueError("Blast, workload, hardware, camera, graphics and instrumentation identity cannot be exempted")
    forbidden = {"props_before", "props_after", "run_name", "run_index", "outcome", "detonation_observed"}
    if set(allowed_metadata_fields) & forbidden:
        raise ValueError("Run and damage evidence cannot be declared a diagnostic factor")
    problems: list[str] = []
    variations: dict[str, Any] = {}
    names = (control_name, candidate_name)
    series = {name: analyze.series_runs(captures, name) for name in names}
    if any(capture["metadata"]["content"].get("run_name") not in names for capture in captures):
        problems.append("Captures outside the requested pair were supplied")
    for name, (selected, cold, warm) in series.items():
        if len(cold) != 1 or len(warm) < 3:
            problems.append(f"{name}: require one first-process blast and at least three warmed repetitions")
        if len(selected) != len(cold) + len(warm):
            problems.append(f"{name}: incomplete/invalid captures cannot be silently excluded")
        indices = [capture["metadata"]["content"].get("run_index") for capture in selected]
        if len(indices) != len({canonical(index) for index in indices}):
            problems.append(f"{name}: duplicate run indices")
        if any(not capture["prop_workload"]["available"] or
               capture["prop_workload"]["newly_root_broken_props"] is None for capture in selected):
            problems.append(f"{name}: incomplete exact actor/adapter damage evidence")
    control, candidate = series[control_name][2], series[candidate_name][2]
    if [c["metadata"]["content"]["run_index"] for c in control] != [c["metadata"]["content"]["run_index"] for c in candidate]:
        problems.append("Warm repeat ordinals differ; exact ordinal pairing is required")
    prop_signatures = {analyze.intended_props(capture["metadata"]["content"]) for capture in captures}
    layout_matches = len(prop_signatures) == 1 and prop_signatures != {"[]"}
    if not layout_matches:
        problems.append("Intended prop layout/state differs or is unavailable")

    indexed: dict[str, dict[str, Any]] = {}
    for manifest in manifests:
        name = manifest["content"].get("name")
        if name not in names or name in indexed:
            problems.append(f"Unexpected or duplicate launch manifest: {name}")
        indexed[name] = manifest["content"]
    for name in names:
        if name not in indexed:
            problems.append(f"Missing launch manifest: {name}")
    launch_left, launch_right = (indexed.get(name, {}) for name in names)
    source_left, source_right = (item.get("source_hashes") for item in (launch_left, launch_right))
    source_changes = {}
    if isinstance(source_left, dict) and isinstance(source_right, dict):
        source_changes = {key: {"control": source_left.get(key), "candidate": source_right.get(key)}
                          for key in sorted(source_left.keys() | source_right.keys())
                          if source_left.get(key) != source_right.get(key)}
    if set(source_changes) != set(allowed_source_files):
        problems.append("Changed source_hashes keys must exactly match declared --allow-source-file values")
    derivative = bool(source_changes) and set(source_changes) == set(allowed_source_files)
    for field in LAUNCH_IDENTITY_FIELDS:
        a, b = launch_left.get(field), launch_right.get(field)
        if a in (None, "", {}) or b in (None, "", {}):
            problems.append(f"Launch manifests lack {field}")
        elif canonical(a) != canonical(b):
            allowed = derivative and field in ("source_hashes", "dll_sha256", "candidate_commit")
            variations[f"launch.{field}"] = {"control": a, "candidate": b, "declared": allowed}
            if not allowed:
                problems.append(f"Undeclared launch identity difference: {field}")

    fields = set(analyze.IDENTITY_FIELDS + analyze.INSTRUMENTATION_FIELDS) | set(allowed_metadata_fields)
    # New native diagnostic identity must be present in both groups, even if omitted from CLI declarations.
    fields.update(key for key in ("isolation_mode", "isolation_factor")
                  if any(key in c["metadata"]["content"] for c in captures))
    all_cameras_valid = bool(captures) and all(analyze.camera_validity(c["metadata"]["content"])["status"] == "valid"
                                             for c in captures)
    observed_metadata_changes = set()
    for field in sorted(fields):
        if field in ("camera_location", "camera_rotation") and all_cameras_valid:
            continue
        values = {name: {canonical(c["metadata"]["content"].get(field)) for c in series[name][0]} for name in names}
        if any(len(values[name]) != 1 or "null" in values[name] for name in names):
            problems.append(f"Missing or varying metadata identity within a series: {field}")
            continue
        a, b = (json.loads(next(iter(values[name]))) for name in names)
        if a != b:
            observed_metadata_changes.add(field)
            allowed = field in allowed_metadata_fields or (field == "candidate_commit" and derivative)
            variations[f"metadata.{field}"] = {"control": a, "candidate": b, "declared": allowed}
            if not allowed:
                problems.append(f"Undeclared metadata identity difference: {field}")
    for field in set(allowed_metadata_fields) - observed_metadata_changes:
        problems.append(f"Declared metadata factor did not differ: {field}")
    for capture in captures:
        metadata = capture["metadata"]["content"]
        launch = indexed.get(metadata.get("run_name"), {})
        bindings = [("candidate_commit", "candidate_commit"), ("workload_identity", "workload_identity"),
                    ("trace_enabled", "trace"), ("named_events_enabled", "named_events"), ("diagnostics_enabled", "diagnostics")]
        bindings.extend((field, field) for field in allowed_metadata_fields
                        if field in launch or field in ("isolation_mode", "isolation_factor"))
        for key, launch_key in bindings:
            if metadata.get(key) != launch.get(launch_key):
                problems.append(f"{metadata.get('run_name')}: capture/launcher mismatch for {key}")
        for field in ("isolation_before", "isolation_after"):
            if field in metadata and (not isinstance(metadata[field], dict) or
                                      metadata[field].get("mode") != metadata.get("isolation_mode")):
                problems.append(f"{metadata.get('run_name')}: {field} mode disagrees with capture isolation_mode")
    arguments = [normalized_arguments(launch) for launch in (launch_left, launch_right)]
    argument_changes: dict[str, Any] = {}
    if any(value is None for value in arguments):
        problems.append("Launch manifests lack an exact arguments array")
    else:
        left_counts, right_counts = (Counter(value) for value in arguments)
        removed, added = list((left_counts - right_counts).elements()), list((right_counts - left_counts).elements())
        argument_changes = {"removed": removed, "added": added}
        if set(removed + added) != set(allowed_launch_arguments):
            problems.append("Changed launch arguments must exactly match declared --allow-launch-argument values")
        if ([value for value in arguments[0] if value not in allowed_launch_arguments] !=
                [value for value in arguments[1] if value not in allowed_launch_arguments]):
            problems.append("Unchanged launch arguments must retain exact order and multiplicity")
    if not observed_metadata_changes and not source_changes and not any(argument_changes.values()):
        problems.append("No recorded diagnostic factor changed")
    liveness = [diagnostic_switch_liveness(capture) for capture in captures]
    if any(item["status"] == "not_exercised" for item in liveness):
        problems.append("diagnostic_switch_not_exercised")
    result = {
        "status": "identity_verified" if not problems else "not_comparable",
        "factor": factor, "control_run_name": control_name, "candidate_run_name": candidate_name,
        "problems": sorted(set(problems)), "identity_variations": variations,
        "source_changes": source_changes, "launch_argument_changes": argument_changes,
        "diagnostic_switch_liveness": liveness,
        "intended_prop_layout_matches": layout_matches,
        "has_at_least_three_warmed_runs_per_series": len(control) >= 3 and len(candidate) >= 3,
        "equivalent_destruction_verified": False, "causal_improvement_verified": False,
        "damage_acceptance": "Unverified: inspect damaged actors, openings, substantial chunk trajectories and presentation. Equal root-break counts do not prove equivalent destruction.",
        "method": "Per-run statistics and ordinal-paired warm differences; never pooled frames. Observed range separation is descriptive, not a confidence interval or causal proof. Process order, stochastic outcomes and presentation changes still require interpretation.",
        "series": {name: {
            "first_process_blast": analyze.aggregate_runs(cold),
            "warm": analyze.aggregate_runs(warm), "warm_observations": aggregate_observations(warm),
            "excluded_capture_paths": [c["capture_path"] for c in selected if c not in cold + warm],
        } for name, (selected, cold, warm) in series.items()},
    }
    if not problems:
        result["warm_phase_differences"] = phase_differences(control, candidate)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("captures", nargs="+", help="Exact native CSV paths; adjacent JSON is required")
    parser.add_argument("--control-run", required=True)
    parser.add_argument("--candidate-run", required=True)
    parser.add_argument("--factor", required=True, help="Single causal hypothesis being isolated; not an acceptance label")
    parser.add_argument("--launch-manifest", action="append", required=True)
    parser.add_argument("--allow-metadata-field", action="append", default=[])
    parser.add_argument("--allow-source-file", action="append", default=[])
    parser.add_argument("--allow-launch-argument", action="append", default=[])
    parser.add_argument("--output", required=True, help="Fresh JSON path under Saved/")
    args = parser.parse_args()
    try:
        output = analyze.output_path_checked(args.output)
        paths = [Path(value).resolve() for value in args.captures]
        manifest_paths = [Path(value).resolve() for value in args.launch_manifest]
        if len(paths) > MAX_CAPTURES or len(paths) != len(set(paths)) or len(manifest_paths) != 2:
            raise ValueError(f"Supply at most {MAX_CAPTURES} unique captures and exactly two launch manifests")
        evidence_paths = paths + [path.with_suffix(".json") for path in paths] + manifest_paths
        if sum(path.stat().st_size for path in evidence_paths) > MAX_INPUT_BYTES:
            raise ValueError(f"Total evidence input exceeds {MAX_INPUT_BYTES} bytes")
        captures = [analyze.analyze_capture(path) for path in paths]
        manifests = [read_manifest(path) for path in manifest_paths]
        result = compare_isolation(captures, manifests, args.control_run, args.candidate_run, args.factor,
                                   tuple(args.allow_metadata_field), tuple(args.allow_source_file),
                                   tuple(args.allow_launch_argument))
        report = {"schema": "DestructionPerf01.DP-02.isolation.v1",
                  "created_utc": datetime.now(timezone.utc).isoformat(),
                  "phase_version": analyze.DP01_PHASE_VERSION,
                  "phase_intervals_seconds": {
                      name: {"start_inclusive": start, "end_exclusive": end}
                      for name, start, end, _ in analyze.DP01_PHASES},
                  "comparison": result, "captures": captures, "launch_manifests": manifests}
        encoded = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        parser.error(str(error))
    print(f"DP-02 {result['status']}: {output}")
    if result["problems"]:
        parser.exit(2)


if __name__ == "__main__":
    main()
