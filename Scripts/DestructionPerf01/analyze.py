#!/usr/bin/env python3
"""Summarize native DestructionPerf01 frame captures without modifying evidence.

Example:
    python Scripts/DestructionPerf01/analyze.py Saved/run01.csv Saved/run02.csv \
        --output Saved/DestructionPerf01/analysis01.json
    python Scripts/DestructionPerf01/analyze.py --self-test

Time zero is the actual destruction-field spawn. Thread/GPU counters can be
delayed and are coarse diagnostic signals; they are neither additive nor a
replacement for an Unreal Insights trace.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAVED_ROOT = (PROJECT_ROOT / "Saved").resolve()
REQUIRED_COLUMNS = (
    "relative_seconds", "frame_ms", "game_ms", "render_ms", "rhi_ms", "gpu_ms"
)
THREAD_COLUMNS = ("game_ms", "render_ms", "rhi_ms", "gpu_ms")
THRESHOLDS_MS = (8.33, 16.67, 33.33, 50.0, 100.0)
MAX_CSV_BYTES = 64 * 1024 * 1024
MAX_METADATA_BYTES = 4 * 1024 * 1024
MAX_ROWS = 500_000
PHASES = (
    ("prebaseline", -5.0, -0.1, True),
    ("immediate", 0.0, 1.0, False),
    ("active", 1.0, 5.0, False),
    ("recovery", 5.0, 15.0, True),
)
DP01_PHASE_VERSION = "DestructionPerf01.DP-01.phases.v1"
DP01_PHASES = (
    ("intact", -5.0, -0.1, False),
    ("burst", 0.0, 0.5, False),
    ("early", 0.5, 3.0, False),
    ("active", 3.0, 10.0, False),
    ("settled", 10.0, 15.0, False),
)
OPTIONAL_COLUMNS = (
    "engine_frame", "simulation_seconds", "diagnostic_sample", "break_events",
    "process_physical_bytes", "process_virtual_bytes", "process_peak_physical_bytes",
    "gc_active_transforms", "gc_sleeping_transforms", "gc_dynamic_transforms",
    "niagara_active_components", "observed_transform_activations", "audio_active_sources",
)
DIAGNOSTIC_COUNTERS = {
    "process_physical_bytes": ("bytes", "Sampled process physical memory, not allocation churn"),
    "process_virtual_bytes": ("bytes", "Sampled process virtual memory"),
    "process_peak_physical_bytes": ("bytes", "Process-lifetime high-water mark, not phase-local allocation peak"),
    "gc_active_transforms": ("transforms", "Game-thread Geometry Collection mirror; not exact solver-active rigid bodies"),
    "gc_sleeping_transforms": ("transforms", "Game-thread Geometry Collection mirror; not exact solver-sleeping rigid bodies"),
    "gc_dynamic_transforms": ("transforms", "Game-thread Geometry Collection mirror dynamic state; not newly released bodies"),
    "niagara_active_components": ("components", "Sampled active Niagara components, not particle or emitter count"),
    "observed_transform_activations": (
        "observed transform transitions",
        "Cumulative sampled inactive-to-active GT transform transitions since reset; lower bound, not exact solver body releases",
    ),
    "audio_active_sources": (
        "sources", "Audio-thread GetNumActiveSources; asynchronous observation delayed by at least one diagnostic interval, not logical voice count",
    ),
}
IDENTITY_FIELDS = (
    "workload_identity", "candidate_commit", "engine", "world", "cpu", "gpu", "blast_location",
    "blast_radius_cm", "viewport_width", "viewport_height", "camera_location", "camera_rotation",
    "t.MaxFPS", "r.VSync", "r.ScreenPercentage", "sg.EffectsQuality", "sg.ShadowQuality",
    "r.Nanite", "fx.NiagaraComponentsEnabled",
    "sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.PostProcessQuality",
    "sg.GlobalIlluminationQuality", "sg.ReflectionQuality", "sg.TextureQuality",
    "sg.FoliageQuality", "sg.ShadingQuality",
)
INSTRUMENTATION_FIELDS = ("trace_enabled", "trace_channels", "named_events_enabled", "diagnostics_enabled")
TIMING_METRICS = ("arithmetic_mean_ms", "p50_ms", "p95_ms", "p99_ms", "max_ms")
CAMERA_TOLERANCE = 0.05
EXPECTED_CAMERA_LOCATION = {"X": -550.0, "Y": -600.0, "Z": 172.0}
EXPECTED_CAMERA_ROTATION = {"P": -2.0, "Y": 90.0, "R": 0.0}


def percentile(sorted_values: list[float], percent: float) -> float | None:
    """Linear interpolation between adjacent ranks, equivalent to R type 7."""
    if not sorted_values:
        return None
    index = (len(sorted_values) - 1) * percent / 100.0
    lower = math.floor(index)
    upper = math.ceil(index)
    fraction = index - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def phase_name(timestamp: float, phases: tuple = PHASES) -> str | None:
    for name, start, end, inclusive_end in phases:
        if start <= timestamp and (timestamp <= end if inclusive_end else timestamp < end):
            return name
    return None


def distribution(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "sample_count": len(ordered),
        "arithmetic_mean_ms": math.fsum(ordered) / len(ordered) if ordered else None,
        "p50_ms": percentile(ordered, 50),
        "p95_ms": percentile(ordered, 95),
        "p99_ms": percentile(ordered, 99),
        "max_ms": ordered[-1] if ordered else None,
    }


def summarize_phase(rows: list[dict[str, float]]) -> dict[str, Any]:
    frame_times = [row["frame_ms"] for row in rows]
    elapsed_ms = math.fsum(frame_times)
    frame_stats = distribution(frame_times)
    counters: dict[str, Any] = {}
    for column in THREAD_COLUMNS:
        all_values = [row[column] for row in rows]
        # A zero GPU counter commonly means that timing is unavailable. Do not
        # allow missing measurements to make the GPU appear artificially fast.
        usable = [value for value in all_values if value > 0] if column == "gpu_ms" else all_values
        counters[column] = distribution(usable)
        if column == "gpu_ms":
            counters[column]["zero_or_unavailable_samples"] = len(all_values) - len(usable)
            counters[column]["available"] = bool(usable)

    return {
        "frame_count": len(rows),
        "elapsed_from_frame_times_seconds": elapsed_ms / 1000.0,
        "first_sample_relative_seconds": rows[0]["relative_seconds"] if rows else None,
        "last_sample_relative_seconds": rows[-1]["relative_seconds"] if rows else None,
        "sample_timestamp_span_seconds": (
            rows[-1]["relative_seconds"] - rows[0]["relative_seconds"] if rows else None
        ),
        "time_weighted_average_fps": len(rows) * 1000.0 / elapsed_ms if rows else None,
        "minimum_instantaneous_fps": 1000.0 / frame_stats["max_ms"] if rows else None,
        "frame_time": frame_stats,
        "thresholds": [
            {
                "strictly_greater_than_ms": threshold,
                "frame_count": sum(value > threshold for value in frame_times),
                "total_frame_time_seconds": math.fsum(
                    value for value in frame_times if value > threshold
                ) / 1000.0,
                "excess_over_threshold_seconds": math.fsum(
                    value - threshold for value in frame_times if value > threshold
                ) / 1000.0,
            }
            for threshold in THRESHOLDS_MS
        ],
        "coarse_non_additive_counters": counters,
    }


def sample_record(row: dict[str, float]) -> dict[str, float]:
    """Keep frame position and coarse timings together for auditable excursions."""
    return {key: row[key] for key in (
        "sample_index", "engine_frame", "relative_seconds", "simulation_seconds",
        *REQUIRED_COLUMNS[1:],
    ) if key in row}


def blast_summary(rows: list[dict[str, float]], metadata: dict[str, Any]) -> dict[str, Any]:
    post_blast = [row for row in rows if 0 <= row["relative_seconds"] < 0.5]
    origin_frame = metadata.get("detonation_engine_frame")
    identified = [row for row in rows if origin_frame is not None and row.get("engine_frame") == origin_frame]
    return {
        "detonation_observed": metadata.get("detonation_observed"),
        "detonation_engine_frame": origin_frame,
        "engine_frame_match": sample_record(identified[0]) if len(identified) == 1 else None,
        "engine_frame_match_count": len(identified),
        "sample_after_engine_frame_match": (
            sample_record(rows[int(identified[0]["sample_index"]) + 1])
            if len(identified) == 1 and int(identified[0]["sample_index"]) + 1 < len(rows) else None
        ),
        "first_sample_at_or_after_blast": sample_record(post_blast[0]) if post_blast else None,
        "worst_sample_in_burst": sample_record(max(post_blast, key=lambda row: row["frame_ms"])) if post_blast else None,
        "limitation": (
            "Frame duration is the interval between fixture ticks, not an engine frame-boundary measurement. "
            "A matching engine_frame locates the fixture sample in the field-spawn engine frame; its duration "
            "can precede some blast work. The following sample can include remaining blast-frame work. "
            "Game/Render/RHI/GPU counters may be delayed. Use the frame trace for exact blast-frame cost; "
            "the first post-blast sample or burst maximum is not asserted to be that cost."
        ),
    }


def summarize_dp01_phase(rows: list[dict[str, float]]) -> dict[str, Any]:
    result = summarize_phase(rows)
    result["excursions_over_8_33_ms"] = [
        {**sample_record(row), "also_over_16_67_ms": row["frame_ms"] > 16.67}
        for row in rows if row["frame_ms"] > 8.33
    ]
    counters = {}
    diagnostic_rows = [row for row in rows if row.get("diagnostic_sample") == 1]
    for column, (unit, note) in DIAGNOSTIC_COUNTERS.items():
        values = [row[column] for row in diagnostic_rows if row.get(column, -1) >= 0]
        counters[column] = {"unit": unit, "note": note, **value_summary(values)}
        if column == "observed_transform_activations":
            increments = [row["observed_transform_activation_delta"] for row in diagnostic_rows
                          if row.get("observed_transform_activation_delta", -1) >= 0]
            counters[column]["observed_increment_total"] = sum(increments) if increments else None
            counters[column]["increment_sample_count"] = len(increments)
    break_rows = [row for row in rows if row.get("break_events", -1) >= 0]
    increments = [row["break_event_delta"] for row in rows if row.get("break_event_delta", -1) >= 0]
    counters["break_events"] = {
        "unit": "cumulative adapter break notifications since reset; not rigid bodies",
        "available": bool(break_rows),
        "sample_count": len(break_rows),
        "first_cumulative": break_rows[0]["break_events"] if break_rows else None,
        "last_cumulative": break_rows[-1]["break_events"] if break_rows else None,
        "observed_increment_total": sum(increments) if increments else None,
        "increment_sample_count": len(increments),
        "note": "Adjacent-sample count differences assigned to the later sample's phase; boundary intervals can cross phases",
    }
    result["workload_counters"] = counters
    result["diagnostic_sample_count"] = len(diagnostic_rows)
    return result


def value_summary(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "available": bool(ordered), "sample_count": len(ordered),
        "minimum": ordered[0] if ordered else None,
        "median": percentile(ordered, 50), "p95": percentile(ordered, 95),
        "maximum": ordered[-1] if ordered else None,
    }


def prop_workload(metadata: dict[str, Any]) -> dict[str, Any]:
    """Summarize observed outcomes without conflating events with rigid bodies."""
    snapshots: dict[str, dict[tuple[str, str], dict[str, Any]]] = {}
    problems: list[str] = []
    for name in ("props_before", "props_after"):
        indexed: dict[tuple[str, str], dict[str, Any]] = {}
        values = metadata.get(name)
        if not isinstance(values, list):
            problems.append(f"{name} is unavailable")
            values = []
        for prop in values:
            if not isinstance(prop, dict) or not prop.get("actor") or not prop.get("id"):
                problems.append(f"{name} contains a prop without actor path plus adapter ID")
                continue
            key = (prop["actor"], prop["id"])
            if key in indexed:
                problems.append(f"{name} duplicates actor path plus adapter ID: {key}")
            indexed[key] = prop
        snapshots[name] = indexed
    before, after = snapshots["props_before"], snapshots["props_after"]
    if set(before) != set(after):
        problems.append("Before/after actor path plus adapter ID sets differ")
    actors = []
    for key in sorted(before.keys() & after.keys()):
        left, right = before[key], after[key]
        start, end = left.get("break_events"), right.get("break_events")
        valid_counts = all(isinstance(value, (int, float)) and not isinstance(value, bool)
                           and math.isfinite(value) and value >= 0 for value in (start, end))
        delta = end - start if valid_counts and end >= start else None
        if delta is None:
            problems.append(f"Unavailable or nonmonotonic break event counts: {key}")
        actors.append({
            "actor": key[0], "adapter_id": key[1], "break_notification_delta": delta,
            "root_broken_before": left.get("root_broken"),
            "root_broken_after": right.get("root_broken"),
            "reset_generation_before": left.get("reset_generation"),
            "reset_generation_after": right.get("reset_generation"),
        })
    complete = bool(before) and not problems
    return {
        "available": complete,
        "identity": "actor path plus project adapter ID; copied vendor ObjectId is not an identity",
        "event_unit": "adapter break notifications, not released or simultaneously active rigid bodies",
        "managed_props_before": len(before), "managed_props_after": len(after),
        "break_notification_delta": sum(actor["break_notification_delta"] for actor in actors) if complete else None,
        "newly_root_broken_props": sum(
            actor["root_broken_before"] is False and actor["root_broken_after"] is True for actor in actors
        ) if complete and all(isinstance(actor["root_broken_before"], bool)
                              and isinstance(actor["root_broken_after"], bool) for actor in actors) else None,
        "actors": actors,
        "problems": problems,
    }


def read_capture(path: Path) -> tuple[list[dict[str, float]], str]:
    if path.stat().st_size > MAX_CSV_BYTES:
        raise ValueError(f"Capture exceeds the {MAX_CSV_BYTES}-byte limit: {path}")
    rows: list[dict[str, float]] = []
    previous_timestamp: float | None = None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Missing or duplicate CSV headers: {path}")
        missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing CSV columns {sorted(missing)}: {path}")
        optional_columns = set(OPTIONAL_COLUMNS) & set(reader.fieldnames)
        for line_number, raw in enumerate(reader, start=2):
            if len(rows) >= MAX_ROWS:
                raise ValueError(f"Capture exceeds the {MAX_ROWS}-row limit: {path}")
            if None in raw:
                raise ValueError(f"Extra unlabelled CSV values at {path}:{line_number}")
            try:
                row = {column: float(raw[column]) for column in REQUIRED_COLUMNS}
                row.update({column: int(raw[column]) if column == "engine_frame" else float(raw[column])
                            for column in optional_columns})
            except (ValueError, TypeError) as error:
                raise ValueError(f"Invalid numeric sample at {path}:{line_number}") from error
            if not all(math.isfinite(value) for value in row.values()):
                raise ValueError(f"Non-finite sample at {path}:{line_number}")
            if row["frame_ms"] <= 0 or any(row[column] < 0 for column in THREAD_COLUMNS):
                raise ValueError(f"Invalid negative/zero duration at {path}:{line_number}")
            if "engine_frame" in row and row["engine_frame"] < 0:
                raise ValueError(f"Invalid engine frame at {path}:{line_number}")
            if "diagnostic_sample" in row and row["diagnostic_sample"] not in (0, 1):
                raise ValueError(f"Invalid diagnostic sample flag at {path}:{line_number}")
            for column in optional_columns - {"engine_frame", "simulation_seconds", "diagnostic_sample"}:
                if not row[column].is_integer() or row[column] < -1:
                    raise ValueError(f"Invalid counter {column} at {path}:{line_number}; expected integer >= 0 or -1")
            timestamp = row["relative_seconds"]
            if previous_timestamp is not None and timestamp < previous_timestamp:
                raise ValueError(f"Time moved backwards at {path}:{line_number}")
            previous_timestamp = timestamp
            row["sample_index"] = len(rows)
            if "break_events" in row:
                previous = rows[-1].get("break_events", -1) if rows else -1
                row["break_event_delta"] = row["break_events"] - previous if 0 <= previous <= row["break_events"] else -1
            if "observed_transform_activations" in row:
                previous = rows[-1].get("observed_transform_activations", -1) if rows else -1
                current = row["observed_transform_activations"]
                row["observed_transform_activation_delta"] = current - previous if 0 <= previous <= current else -1
            rows.append(row)
    if not rows:
        raise ValueError(f"Capture contains no frame samples: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return rows, digest.hexdigest()


def read_metadata(capture_path: Path) -> dict[str, Any]:
    metadata_path = capture_path.with_suffix(".json")
    if not metadata_path.exists():
        return {"present": False, "expected_path": str(metadata_path)}
    if metadata_path.stat().st_size > MAX_METADATA_BYTES:
        raise ValueError(f"Metadata exceeds the {MAX_METADATA_BYTES}-byte limit: {metadata_path}")
    raw = metadata_path.read_bytes()
    return {
        "present": True,
        "path": str(metadata_path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "content": json.loads(raw.decode("utf-8-sig")),
    }


def parse_camera_components(value: Any, expected: dict[str, float]) -> dict[str, float] | None:
    if not isinstance(value, str):
        return None
    result: dict[str, float] = {}
    try:
        for token in value.split():
            key, separator, number = token.partition("=")
            if not separator or key not in expected or key in result:
                return None
            result[key] = float(number)
    except ValueError:
        return None
    return result if result.keys() == expected.keys() and all(math.isfinite(number) for number in result.values()) else None


def camera_validity(metadata: dict[str, Any]) -> dict[str, Any]:
    automatic_v2 = metadata.get("schema") == "DestructionPerf01-v2" and bool(metadata.get("run_name"))
    issues = []
    observations = {}
    for kind, expected in (("location", EXPECTED_CAMERA_LOCATION), ("rotation", EXPECTED_CAMERA_ROTATION)):
        for suffix in ("", "_after"):
            key = f"camera_{kind}{suffix}"
            observations[key] = parse_camera_components(metadata.get(key), expected)
            if automatic_v2:
                if observations[key] is None:
                    issues.append(f"Missing or malformed {key}")
                else:
                    for axis, target in expected.items():
                        delta = observations[key][axis] - target
                        error = abs((delta + 180.0) % 360.0 - 180.0) if kind == "rotation" else abs(delta)
                        if error > CAMERA_TOLERANCE + 1e-9:
                            issues.append(f"{key}.{axis} differs from intended camera by {error:.6f}")
        before, after = observations[f"camera_{kind}"], observations[f"camera_{kind}_after"]
        if automatic_v2 and before is not None and after is not None:
            for axis in expected:
                delta = after[axis] - before[axis]
                error = abs((delta + 180.0) % 360.0 - 180.0) if kind == "rotation" else abs(delta)
                if error > CAMERA_TOLERANCE + 1e-9:
                    issues.append(f"camera_{kind}.{axis} drifted by {error:.6f} during capture")
    return {
        "automatic_v2_contract_applies": automatic_v2,
        "status": ("invalid" if issues else "valid") if automatic_v2 else "unverified_legacy_or_manual",
        "expected_location_cm": EXPECTED_CAMERA_LOCATION,
        "expected_rotation_degrees": EXPECTED_CAMERA_ROTATION,
        "per_component_tolerance": CAMERA_TOLERANCE,
        "observations": observations,
        "issues": issues,
        "limitation": (
            "Automatic v2 captures require before/after camera position and rotation within the intended camera "
            "and each other by 0.05 cm/degrees per component. Endpoint checks do not prove no transient movement "
            "between observations. Legacy/manual captures without this contract remain unverified, not retroactively invalidated."
        ),
    }


def analyze_capture(path: Path) -> dict[str, Any]:
    rows, digest = read_capture(path)
    metadata = read_metadata(path)
    content = metadata.get("content", {})
    if not isinstance(content, dict):
        raise ValueError(f"Capture metadata must be a JSON object: {path.with_suffix('.json')}")
    buckets: dict[str, list[dict[str, float]]] = {phase[0]: [] for phase in PHASES}
    dp01_buckets: dict[str, list[dict[str, float]]] = {phase[0]: [] for phase in DP01_PHASES}
    excluded: list[dict[str, float]] = []
    for row in rows:
        phase = phase_name(row["relative_seconds"])
        (buckets[phase] if phase is not None else excluded).append(row)
        dp01_phase = phase_name(row["relative_seconds"], DP01_PHASES)
        if dp01_phase is not None:
            dp01_buckets[dp01_phase].append(row)
    camera = camera_validity(content)
    validity_problems = []
    if content.get("outcome") != "complete":
        validity_problems.append("Capture outcome is not complete")
    if content.get("detonation_observed") is not True:
        validity_problems.append("Detonation was not confirmed")
    if not all(dp01_buckets.values()):
        validity_problems.append("At least one DP-01 phase has no samples")
    if camera["status"] == "invalid":
        validity_problems.append("Automatic v2 camera does not satisfy the fixed-camera contract")
    return {
        "capture_path": str(path),
        "capture_sha256": digest,
        "metadata": metadata,
        "total_input_frames": len(rows),
        "excluded_frame_count": len(excluded),
        "excluded_frame_time_seconds": math.fsum(row["frame_ms"] for row in excluded) / 1000.0,
        "duplicate_timestamp_count": sum(
            left["relative_seconds"] == right["relative_seconds"]
            for left, right in zip(rows, rows[1:])
        ),
        "phases": {name: summarize_phase(samples) for name, samples in buckets.items()},
        "dp01_phase_version": DP01_PHASE_VERSION,
        "dp01_phases": {name: summarize_dp01_phase(samples) for name, samples in dp01_buckets.items()},
        "dp01_excluded_frame_count": len(rows) - sum(len(samples) for samples in dp01_buckets.values()),
        "blast": blast_summary(rows, content),
        "prop_workload": prop_workload(content),
        "unavailable_counters": {
            "newly_released_solver_bodies": "Not exported by the fixture; break notifications and dynamic transforms are not substitutes",
            "exact_active_and_sleeping_solver_bodies": "GT transform mirrors are proxy observations only; requires supported solver diagnostics",
            "solver_contacts": "Not exported by the fixture",
            "collision_events": "Not exported per frame; use separately attributed trace call counts where available",
            "audio_voices": "Logical voices are not exported; audio_active_sources is a delayed audio-device source observation",
            "phase_allocation_peak": "Sampled process memory and process-lifetime high-water mark are not phase allocation peaks",
        },
        "validity": {"camera": camera, "comparison_exclusion_reasons": validity_problems},
        "comparison_eligible": not validity_problems,
    }


def repeated_metric(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "run_count": len(values),
        "minimum_run_value": ordered[0] if ordered else None,
        "median_of_run_values": percentile(ordered, 50),
        "maximum_run_value": ordered[-1] if ordered else None,
        "run_value_range": ordered[-1] - ordered[0] if ordered else None,
        "values_in_run_order": values,
    }


def aggregate_runs(captures: list[dict[str, Any]]) -> dict[str, Any]:
    phases = {}
    for name, *_ in DP01_PHASES:
        counters = {}
        for column in ("frame_ms", *THREAD_COLUMNS):
            counters[column] = {}
            for metric in TIMING_METRICS:
                values = []
                for capture in captures:
                    phase = capture["dp01_phases"][name]
                    distribution_value = phase["frame_time"] if column == "frame_ms" else phase["coarse_non_additive_counters"][column]
                    if distribution_value[metric] is not None:
                        values.append(distribution_value[metric])
                counters[column][metric] = repeated_metric(values)
        phases[name] = counters
    return {
        "run_count": len(captures),
        "run_indices": [capture["metadata"]["content"].get("run_index") for capture in captures],
        "capture_paths_in_run_order": [capture["capture_path"] for capture in captures],
        "phase_metrics_ms": phases,
        "break_notification_delta": repeated_metric([
            capture["prop_workload"]["break_notification_delta"] for capture in captures
            if capture["prop_workload"]["break_notification_delta"] is not None
        ]),
        "newly_root_broken_props": repeated_metric([
            capture["prop_workload"]["newly_root_broken_props"] for capture in captures
            if capture["prop_workload"]["newly_root_broken_props"] is not None
        ]),
    }


def series_runs(captures: list[dict[str, Any]], run_name: str) -> tuple[list, list, list]:
    selected = [capture for capture in captures if capture["metadata"].get("content", {}).get("run_name") == run_name]
    eligible = [capture for capture in selected if capture["comparison_eligible"] and
                isinstance(capture["metadata"]["content"].get("run_index"), (int, float)) and
                not isinstance(capture["metadata"]["content"]["run_index"], bool) and
                float(capture["metadata"]["content"]["run_index"]).is_integer()]
    eligible.sort(key=lambda capture: capture["metadata"]["content"].get("run_index", 0))
    cold = [capture for capture in eligible if capture["metadata"]["content"].get("run_index") == 1]
    warm = [capture for capture in eligible if isinstance(capture["metadata"]["content"].get("run_index"), (int, float))
            and capture["metadata"]["content"]["run_index"] > 1]
    return selected, cold, warm


def series_summaries(captures: list[dict[str, Any]]) -> dict[str, Any]:
    names = sorted({capture["metadata"].get("content", {}).get("run_name") for capture in captures
                    if capture["metadata"].get("content", {}).get("run_name")})
    result = {}
    for name in names:
        selected, cold, warm = series_runs(captures, name)
        indices = [capture["metadata"]["content"].get("run_index") for capture in cold + warm]
        result[name] = {
            "selected_capture_count": len(selected),
            "excluded_capture_paths": [capture["capture_path"] for capture in selected if capture not in cold + warm],
            "first_blast_after_process_start": aggregate_runs(cold),
            "warmed_repetitions": aggregate_runs(warm),
            "duplicate_run_indices": sorted({index for index in indices if indices.count(index) > 1}),
            "has_at_least_three_distinct_warmed_runs": len({index for index in indices if index > 1}) >= 3,
            "classification_note": (
                "Native run_index 1 is the first blast in this process after fixture warmup; this does not verify cold OS, "
                "driver, shader or DDC caches. run_index > 1 is a repeat after the fixture reset/warmup; confirm reset "
                "and intended destruction from per-capture metadata and outcome evidence. Aborted/unverified captures are excluded."
            ),
        }
    return result


def intended_props(metadata: dict[str, Any]) -> str:
    """Compare the full intended layout; runtime actor names change after reset.

    This multiset is not an actor identity. Exact actor path plus adapter ID is
    retained separately by prop_workload for before/after outcome correlation.
    """
    keys = ("id", "data_asset", "location", "rotation", "scale", "materials",
            "material_overrides", "collision_profile", "ready", "root_broken")
    raw_props = metadata.get("props_before", [])
    props = [{key: prop.get(key) for key in keys} for prop in raw_props if isinstance(prop, dict)] if isinstance(raw_props, list) else []
    props.sort(key=lambda prop: json.dumps(prop, sort_keys=True))
    return json.dumps(props, sort_keys=True, ensure_ascii=False)


def compare_launch_manifests(manifests: list[dict[str, Any]], captures: list[dict[str, Any]],
                             names: tuple[str, str]) -> dict[str, Any]:
    """Verify runtime bytes as well as commit identity when launch evidence is supplied."""
    if not manifests:
        return {"status": "not_supplied", "problems": [],
                "limitation": "Capture metadata identifies commit and workload but not dirty runtime source/DLL bytes; verify launcher manifests separately"}
    indexed = {}
    problems = []
    for manifest in manifests:
        name = manifest["content"].get("name")
        if name in indexed:
            problems.append(f"Duplicate launch manifest for {name}")
        indexed[name] = manifest
    for name in names:
        if name not in indexed:
            problems.append(f"Missing launch manifest for {name}")
    selected = [indexed[name] for name in names if name in indexed]
    for field in ("candidate_commit", "workload_identity", "dll_sha256", "source_hashes",
                  "asset_config_hashes", "map_sha256", "engine_build"):
        values = [manifest["content"].get(field) for manifest in selected]
        if not values or any(value is None or value == {} or value == "" for value in values):
            problems.append(f"Launch manifests lack {field}")
        elif len({json.dumps(value, sort_keys=True) for value in values}) != 1:
            problems.append(f"Launch manifests disagree on {field}")
    for capture in captures:
        content = capture["metadata"]["content"]
        manifest = indexed.get(content.get("run_name"), {}).get("content", {})
        for key, launch_key in (("candidate_commit", "candidate_commit"), ("workload_identity", "workload_identity"),
                                ("trace_enabled", "trace"), ("named_events_enabled", "named_events"),
                                ("diagnostics_enabled", "diagnostics")):
            if content.get(key) != manifest.get(launch_key):
                problems.append(f"{content.get('run_name')}: capture {key} disagrees with launch manifest")
    return {"status": "verified" if not problems else "invalid", "problems": sorted(set(problems)),
            "manifest_paths": [manifest["path"] for manifest in selected],
            "limitation": "Hashes identify captured launch evidence; they do not prove deterministic destruction outcomes"}


def compare_runs(captures: list[dict[str, Any]], control_name: str, traced_name: str,
                 comparison_kind: str = "tracing", launch_manifests: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if comparison_kind not in ("tracing", "diagnostics"):
        raise ValueError("Comparison kind must be tracing or diagnostics")
    if control_name == traced_name:
        raise ValueError("Control and traced run names must differ")
    control_selected, control_cold, control = series_runs(captures, control_name)
    traced_selected, traced_cold, traced = series_runs(captures, traced_name)
    problems = []
    if not control_selected or not traced_selected:
        problems.append("A requested run_name has no supplied captures")
    if not control or not traced:
        problems.append("Both series need complete, observed-blast warm captures with every phase")
    camera_failures = []
    for capture in control_selected + traced_selected:
        camera = camera_validity(capture["metadata"]["content"])
        if camera["status"] == "invalid":
            camera_failures.append({"capture_path": capture["capture_path"], "issues": camera["issues"]})
    if camera_failures:
        problems.append("Selected automatic v2 captures fail the fixed-camera contract; invalid runs cannot be silently dropped")
    all_runs = control_cold + control + traced_cold + traced
    launch_verification = compare_launch_manifests(launch_manifests or [], all_runs, (control_name, traced_name))
    if launch_verification["status"] == "invalid":
        problems.append("Launch build/workload evidence is missing or inconsistent")
    validated_fixed_cameras = bool(all_runs) and all(camera_validity(capture["metadata"]["content"])["status"] == "valid"
                                                   for capture in all_runs)
    identity_variations = {}
    for field in IDENTITY_FIELDS:
        if field in ("camera_location", "camera_rotation") and validated_fixed_cameras:
            continue  # The explicit fixed-camera tolerance supersedes exact float-string equality.
        values = {json.dumps(capture["metadata"]["content"].get(field), sort_keys=True) for capture in all_runs}
        if len(values) != 1 or "null" in values:
            identity_variations[field] = sorted(values)
    if identity_variations:
        problems.append("Missing or inconsistent workload/build/hardware/camera/graphics identity")
    prop_signatures = {intended_props(capture["metadata"]["content"]) for capture in all_runs}
    if len(prop_signatures) != 1 or prop_signatures == {"[]"}:
        problems.append("Missing or inconsistent intended prop state before blast")
    if any(not capture["prop_workload"]["available"] for capture in all_runs):
        problems.append("Incomplete actor path plus adapter ID outcome identity")
    changed_flag = "trace_enabled" if comparison_kind == "tracing" else "diagnostics_enabled"
    for name, expected, selected in ((control_name, False, control_cold + control), (traced_name, True, traced_cold + traced)):
        if any(capture["metadata"]["content"].get(changed_flag) is not expected for capture in selected):
            problems.append(f"{name}: {changed_flag} must be {expected}")
        for field in INSTRUMENTATION_FIELDS:
            values = {json.dumps(capture["metadata"]["content"].get(field), sort_keys=True) for capture in selected}
            if len(values) != 1 or "null" in values:
                problems.append(f"{name}: missing or inconsistent {field} within the series")
    if comparison_kind == "diagnostics":
        for field in INSTRUMENTATION_FIELDS[:-1]:
            if len({json.dumps(capture["metadata"]["content"].get(field), sort_keys=True) for capture in all_runs}) != 1:
                problems.append(f"Diagnostics comparison must keep {field} unchanged")
    for name, selected in ((control_name, control_cold + control), (traced_name, traced_cold + traced)):
        indices = [capture["metadata"]["content"].get("run_index") for capture in selected]
        if len(indices) != len(set(indices)):
            problems.append(f"{name}: duplicate run indices")
    control_indices = [capture["metadata"]["content"]["run_index"] for capture in control]
    traced_indices = [capture["metadata"]["content"]["run_index"] for capture in traced]
    if control_indices != traced_indices:
        problems.append("Warm run ordinals differ; supply matching repeat sets")
    result = {
        "control_run_name": control_name, "traced_run_name": traced_name,
        "comparison_kind": comparison_kind,
        "launch_verification": launch_verification,
        "intended_prop_comparison": (
            "Exact multiset of adapter ID, asset, pose, materials, collision and pre-blast state, preserving multiplicity. "
            "Runtime actor names change on reset and are excluded only from cross-run layout comparison; "
            "each capture's before/after outcome identity remains exact actor path plus adapter ID."
        ),
        "status": "comparable" if not problems else "not_comparable",
        "problems": problems, "identity_variations": identity_variations, "camera_failures": camera_failures,
        "has_at_least_three_warmed_runs_per_series": len(control) >= 3 and len(traced) >= 3,
        "instrumentation": {
            name: {key: sorted({str(capture["metadata"]["content"].get(key)) for capture in selected})
                   for key in INSTRUMENTATION_FIELDS}
            for name, selected in ((control_name, control_cold + control), (traced_name, traced_cold + traced))
        },
        "method": (
            "Compare medians of each run's phase statistics; do not pool frames. The observed candidate-minus-control "
            "delta includes all instrumentation differences plus stochastic outcome and session variation; it is not "
            "a causal estimate or confidence interval. The candidate retains the traced label in metric keys for "
            "schema compatibility. Report per-run ranges and damage outcomes alongside deltas."
        ),
    }
    if problems:
        return result
    controls, traces = aggregate_runs(control), aggregate_runs(traced)
    overhead = {}
    for phase, *_ in DP01_PHASES:
        overhead[phase] = {}
        for column in ("frame_ms", *THREAD_COLUMNS):
            overhead[phase][column] = {}
            for metric in TIMING_METRICS:
                left = controls["phase_metrics_ms"][phase][column][metric]
                right = traces["phase_metrics_ms"][phase][column][metric]
                control_value, traced_value = left["median_of_run_values"], right["median_of_run_values"]
                delta = traced_value - control_value if control_value is not None and traced_value is not None else None
                overhead[phase][column][metric] = {
                    "control": left, "traced": right, "traced_minus_control_ms": delta,
                    "relative_delta_percent": 100 * delta / control_value if delta is not None and control_value else None,
                }
    result["warmed_phase_overhead"] = overhead
    result["control_outcomes"] = {key: controls[key] for key in ("break_notification_delta", "newly_root_broken_props")}
    result["traced_outcomes"] = {key: traces[key] for key in ("break_notification_delta", "newly_root_broken_props")}
    return result


def output_path_checked(value: str) -> Path:
    path = Path(value).resolve()
    if not path.is_relative_to(SAVED_ROOT) or path == SAVED_ROOT:
        raise ValueError(f"Analysis output must be a file under {SAVED_ROOT}")
    if path.suffix.lower() != ".json":
        raise ValueError("Analysis output must use a .json extension")
    if path.exists():
        raise ValueError(f"Refusing to overwrite existing output: {path}")
    return path


def self_test() -> None:
    rows = [
        {"relative_seconds": -4.0 + index, "frame_ms": duration,
         "game_ms": 2.0, "render_ms": 3.0, "rhi_ms": 1.0,
         "gpu_ms": 0.0 if index < 3 else 8.0}
        for index, duration in enumerate((5.0, 10.0, 20.0, 100.0))
    ]
    summary = summarize_phase(rows)
    assert summary["frame_count"] == 4
    assert math.isclose(summary["elapsed_from_frame_times_seconds"], 0.135)
    assert math.isclose(summary["time_weighted_average_fps"], 4000.0 / 135.0)
    assert summary["minimum_instantaneous_fps"] == 10.0
    assert summary["frame_time"]["p50_ms"] == 15.0
    assert math.isclose(summary["frame_time"]["p95_ms"], 88.0)
    assert math.isclose(summary["frame_time"]["p99_ms"], 97.6)
    assert [item["frame_count"] for item in summary["thresholds"]] == [3, 2, 1, 1, 0]
    assert math.isclose(summary["thresholds"][1]["total_frame_time_seconds"], 0.12)
    assert math.isclose(summary["thresholds"][1]["excess_over_threshold_seconds"], 0.08666)
    assert summary["coarse_non_additive_counters"]["gpu_ms"]["sample_count"] == 1
    assert summary["coarse_non_additive_counters"]["gpu_ms"]["arithmetic_mean_ms"] == 8.0
    assert summary["coarse_non_additive_counters"]["gpu_ms"]["zero_or_unavailable_samples"] == 3
    assert summarize_phase([])["time_weighted_average_fps"] is None
    assert summarize_phase([])["minimum_instantaneous_fps"] is None
    assert summarize_phase([])["coarse_non_additive_counters"]["gpu_ms"]["available"] is False
    expected_boundaries = {
        -5.01: None, -5.0: "prebaseline", -0.1: "prebaseline", -0.099: None,
        0.0: "immediate", 0.999: "immediate", 1.0: "active", 4.999: "active",
        5.0: "recovery", 15.0: "recovery", 15.001: None,
    }
    assert all(phase_name(timestamp) == expected for timestamp, expected in expected_boundaries.items())
    print("DestructionPerf01 analyzer self-test passed (metrics, thresholds, GPU availability, phase boundaries).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("captures", nargs="*", help="One or more native frame CSV captures")
    parser.add_argument("--output", help="Required fresh JSON output path under the project's Saved directory")
    parser.add_argument("--self-test", action="store_true", help="Run built-in synthetic checks without writing files")
    parser.add_argument("--control-run", help="Control run_name: untraced for tracing, diagnostics disabled for diagnostics")
    parser.add_argument("--traced-run", help="Candidate run_name: traced for tracing, diagnostics enabled for diagnostics")
    parser.add_argument("--comparison-kind", choices=("tracing", "diagnostics"), default="tracing",
                        help="Diagnostics compares disabled/enabled diagnostics while holding trace settings fixed")
    parser.add_argument("--launch-manifest", action="append", default=[],
                        help="Launcher JSON evidence; repeat for each series to verify dirty source/DLL and asset hashes")
    arguments = parser.parse_args()
    if arguments.self_test:
        if (arguments.captures or arguments.output or arguments.control_run or arguments.traced_run
                or arguments.comparison_kind != "tracing" or arguments.launch_manifest):
            parser.error("--self-test cannot be combined with captures or --output")
        self_test()
        return
    if not arguments.captures or not arguments.output:
        parser.error("one or more capture paths and --output are required")
    if bool(arguments.control_run) != bool(arguments.traced_run):
        parser.error("--control-run and --traced-run must be supplied together")
    if arguments.comparison_kind != "tracing" and not arguments.control_run:
        parser.error("--comparison-kind requires --control-run and --traced-run")
    try:
        output_path = output_path_checked(arguments.output)
        capture_paths = [Path(value).resolve() for value in arguments.captures]
        if len(capture_paths) != len(set(capture_paths)):
            raise ValueError("Duplicate capture paths are not allowed")
        captures = [analyze_capture(path) for path in capture_paths]
        launch_manifests = []
        for value in arguments.launch_manifest:
            path = Path(value).resolve()
            if path.stat().st_size > MAX_METADATA_BYTES:
                raise ValueError(f"Launch manifest exceeds the {MAX_METADATA_BYTES}-byte limit: {path}")
            raw = path.read_bytes()
            content = json.loads(raw.decode("utf-8-sig"))
            if not isinstance(content, dict):
                raise ValueError(f"Launch manifest must be a JSON object: {path}")
            launch_manifests.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "content": content})
        report = {
            "schema": "DestructionPerf01.analysis.v2",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "method": {
                "time_origin": "Actual destruction-field spawn (relative_seconds = 0)",
                "phase_assignment": "Whole frame assigned by its recorded relative_seconds; no boundary interpolation",
                "phase_intervals_seconds": {
                    name: {"start_inclusive": start, "end": end, "end_inclusive": inclusive_end}
                    for name, start, end, inclusive_end in PHASES
                },
                "baseline_guard_gap": "Samples strictly between -0.1 and 0 seconds are excluded",
                "legacy_results": "The phases key retains the original v1 intervals, boundary behavior and calculations",
                "dp01_phase_version": DP01_PHASE_VERSION,
                "dp01_phase_intervals_seconds": {
                    name: {"start_inclusive": start, "end": end, "end_inclusive": inclusive_end}
                    for name, start, end, inclusive_end in DP01_PHASES
                },
                "dp01_guard_and_tail": "DP-01 excludes [-0.1, 0) and samples at or after 15 seconds; no boundary interpolation",
                "average_fps": "frame_count / sum(frame_ms / 1000); never mean(1000 / frame_ms)",
                "minimum_instantaneous_fps": "1000 / max(frame_ms); distinct from phase-average FPS",
                "percentiles": "Linear interpolation between adjacent ranks (R type 7)",
                "thresholds": "Strict >; total_frame_time_seconds sums complete violating frames; thresholds overlap",
                "counters": "Game/render/RHI/GPU timings may be delayed. Coarse diagnostics only; never sum them.",
                "gpu_zeros": "Zero GPU samples are excluded as unavailable/zero; availability counts are reported",
                "metadata": "Adjacent same-stem .json is retained verbatim as decoded content with its raw-byte SHA-256",
                "comparisons": "Each capture is summarized independently; repeated summaries use per-run metric medians/ranges, never pooled frames",
                "diagnostics": "Only diagnostic_sample=1 rows are independent observations; held values are not resampled; -1 is unavailable",
                "time_domains": "relative_seconds is platform real time; simulation_seconds is world time relative to the same blast",
                "proposed_target": "8.33 ms / 120 FPS is proposed only; excursions are reported without production acceptance claims",
            },
            "captures": captures,
            "series": series_summaries(captures),
            "launch_manifests": launch_manifests,
        }
        if arguments.control_run:
            key = "trace_overhead" if arguments.comparison_kind == "tracing" else "diagnostic_overhead"
            report[key] = compare_runs(captures, arguments.control_run, arguments.traced_run,
                                       arguments.comparison_kind, launch_manifests)
        serialized = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        parser.error(str(error))
    print(f"Analyzed {len(capture_paths)} capture(s): {output_path}")


if __name__ == "__main__":
    main()
