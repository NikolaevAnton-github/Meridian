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


def percentile(sorted_values: list[float], percent: float) -> float | None:
    """Linear interpolation between adjacent ranks, equivalent to R type 7."""
    if not sorted_values:
        return None
    index = (len(sorted_values) - 1) * percent / 100.0
    lower = math.floor(index)
    upper = math.ceil(index)
    fraction = index - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def phase_name(timestamp: float) -> str | None:
    for name, start, end, inclusive_end in PHASES:
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
        for line_number, raw in enumerate(reader, start=2):
            if len(rows) >= MAX_ROWS:
                raise ValueError(f"Capture exceeds the {MAX_ROWS}-row limit: {path}")
            if None in raw:
                raise ValueError(f"Extra unlabelled CSV values at {path}:{line_number}")
            try:
                row = {column: float(raw[column]) for column in REQUIRED_COLUMNS}
            except (ValueError, TypeError) as error:
                raise ValueError(f"Invalid numeric sample at {path}:{line_number}") from error
            if not all(math.isfinite(value) for value in row.values()):
                raise ValueError(f"Non-finite sample at {path}:{line_number}")
            if row["frame_ms"] <= 0 or any(row[column] < 0 for column in THREAD_COLUMNS):
                raise ValueError(f"Invalid negative/zero duration at {path}:{line_number}")
            timestamp = row["relative_seconds"]
            if previous_timestamp is not None and timestamp < previous_timestamp:
                raise ValueError(f"Time moved backwards at {path}:{line_number}")
            previous_timestamp = timestamp
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


def analyze_capture(path: Path) -> dict[str, Any]:
    rows, digest = read_capture(path)
    buckets: dict[str, list[dict[str, float]]] = {phase[0]: [] for phase in PHASES}
    excluded: list[dict[str, float]] = []
    for row in rows:
        phase = phase_name(row["relative_seconds"])
        (buckets[phase] if phase is not None else excluded).append(row)
    return {
        "capture_path": str(path),
        "capture_sha256": digest,
        "metadata": read_metadata(path),
        "total_input_frames": len(rows),
        "excluded_frame_count": len(excluded),
        "excluded_frame_time_seconds": math.fsum(row["frame_ms"] for row in excluded) / 1000.0,
        "duplicate_timestamp_count": sum(
            left["relative_seconds"] == right["relative_seconds"]
            for left, right in zip(rows, rows[1:])
        ),
        "phases": {name: summarize_phase(samples) for name, samples in buckets.items()},
    }


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
    arguments = parser.parse_args()
    if arguments.self_test:
        if arguments.captures or arguments.output:
            parser.error("--self-test cannot be combined with captures or --output")
        self_test()
        return
    if not arguments.captures or not arguments.output:
        parser.error("one or more capture paths and --output are required")
    try:
        output_path = output_path_checked(arguments.output)
        capture_paths = [Path(value).resolve() for value in arguments.captures]
        if len(capture_paths) != len(set(capture_paths)):
            raise ValueError("Duplicate capture paths are not allowed")
        report = {
            "schema": "DestructionPerf01.analysis.v1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "method": {
                "time_origin": "Actual destruction-field spawn (relative_seconds = 0)",
                "phase_assignment": "Whole frame assigned by its recorded relative_seconds; no boundary interpolation",
                "phase_intervals_seconds": {
                    name: {"start_inclusive": start, "end": end, "end_inclusive": inclusive_end}
                    for name, start, end, inclusive_end in PHASES
                },
                "baseline_guard_gap": "Samples strictly between -0.1 and 0 seconds are excluded",
                "average_fps": "frame_count / sum(frame_ms / 1000); never mean(1000 / frame_ms)",
                "minimum_instantaneous_fps": "1000 / max(frame_ms); distinct from phase-average FPS",
                "percentiles": "Linear interpolation between adjacent ranks (R type 7)",
                "thresholds": "Strict >; total_frame_time_seconds sums complete violating frames; thresholds overlap",
                "counters": "Game/render/RHI/GPU timings may be delayed. Coarse diagnostics only; never sum them.",
                "gpu_zeros": "Zero GPU samples are excluded as unavailable/zero; availability counts are reported",
                "metadata": "Adjacent same-stem .json is preserved without assuming a schema",
                "comparisons": "Each capture is summarized independently; no implicit pooling of runs",
            },
            "captures": [analyze_capture(path) for path in capture_paths],
        }
        serialized = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
    except (OSError, ValueError, csv.Error, UnicodeError) as error:
        parser.error(str(error))
    print(f"Analyzed {len(capture_paths)} capture(s): {output_path}")


if __name__ == "__main__":
    main()
