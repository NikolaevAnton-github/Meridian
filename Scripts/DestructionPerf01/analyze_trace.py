"""DP-01 thread-resolved timing, counter and exact task-wait summaries.

Run after export_trace.ps1 -IncludeTimingEvents -IncludeCounterValues.
All timer events are required to reconstruct exclusive time; no timer filtering.
Only stdlib is used. Output must be new and below project Saved.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

from analyze import distribution

COUNTER_NOTES = {
    "Chaos/Solver/Bodies/Num": "NonDisabledView particle count",
    "Chaos/Solver/Bodies/NumDisabled": "AllParticlesView minus NonDisabledView particle count",
    "Chaos/Solver/Bodies/NumDynamic": "NonDisabledDynamicView particle count; not newly released bodies",
    "Chaos/Solver/Bodies/NumMoving": "ActiveDynamicMovingKinematicParticlesView count; not exact awake dynamic bodies",
    "Chaos/Solver/Bodies/NumGC": "Geometry Collection particle storage size, including disabled particles",
    "Chaos/Solver/Collisions/NumConstraints": "Collision constraint count; not contact manifold point count",
}


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        yield from csv.DictReader(source)


def aggregate_thread(events, begin, end):
    """Clip all scopes, subtract union of direct children, retain exact timer IDs."""
    events.sort(key=lambda e: (e[0], e[2], -e[1]))
    stats = defaultdict(lambda: {"count": 0, "inclusive_ms": 0.0,
                                 "exclusive_ms": 0.0, "max_overlap_ms": 0.0})
    stack = []
    invalid_nesting = 0
    sibling_ends = {}

    def finish():
        item = stack.pop()
        start, stop, depth, timer_id, name, covered, last_child_end = item
        duration = max(0.0, stop - start)
        value = stats[(timer_id, name)]
        value["count"] += 1
        value["inclusive_ms"] += duration * 1000.0
        value["exclusive_ms"] += max(0.0, duration - covered) * 1000.0
        value["max_overlap_ms"] = max(value["max_overlap_ms"], duration * 1000.0)
        if stack:
            parent = stack[-1]
            a, b = max(start, parent[0]), min(stop, parent[1])
            parent[5] += max(0.0, b - max(a, parent[6]))
            parent[6] = max(parent[6], b)

    for start, stop, depth, timer_id, name in events:
        start, stop = max(start, begin), min(stop, end)
        if stop <= start:
            continue
        if depth < 0:
            raise ValueError("Timing event depth must be nonnegative")
        while stack and depth <= stack[-1][2]:
            finish()
        # Same-depth scopes cannot overlap, even if each fits inside its parent.
        # Missing ancestors also mean that exported scopes were not complete.
        if (start < sibling_ends.get(depth, -math.inf) - 1e-6
                or (not stack and depth != 0)
                or (stack and (depth != stack[-1][2] + 1 or start < stack[-1][0] - 1e-6
                               or stop > stack[-1][1] + 1e-6))):
            invalid_nesting += 1
        sibling_ends[depth] = max(stop, sibling_ends.get(depth, -math.inf))
        stack.append([start, stop, depth, timer_id, name, 0.0, start])
    while stack:
        finish()
    result = []
    for (timer_id, name), values in stats.items():
        result.append({"timer_id": timer_id, "name": name, **values})
    # Do not present unreliable reconstructed self time as measured attribution.
    if invalid_nesting:
        for value in result:
            value["exclusive_ms"] = None
    return result, invalid_nesting


def summarize_task_interiors(events, bound, thread_id, targets, timers, top):
    """Join recorded awaited task execution to same-thread scope starts, once loaded."""
    begins = [event[0] for event in events]
    output = []
    for target in targets:
        if str(target["thread_id"]) != str(thread_id):
            continue
        begin = max(target["start"], bound["start_seconds"])
        end = min(target["finish"], bound["end_seconds"])
        if end <= begin:
            continue
        first = bisect.bisect_left(begins, target["start"])
        last = bisect.bisect_left(begins, end)
        stats = defaultdict(lambda: {"count": 0, "inclusive_overlap_ms": 0.0, "max_overlap_ms": 0.0,
                                     "minimum_depth": None, "crosses_task_end_count": 0})
        intervals = []
        for index in range(first, last):
            start, stop, depth, timer_id, name = events[index]
            overlap = min(stop, end) - max(start, begin)
            if overlap <= 0:
                continue
            intervals.append((start, stop))
            value = stats[(timer_id, name)]
            value["count"] += 1
            value["inclusive_overlap_ms"] += overlap * 1000.0
            value["max_overlap_ms"] = max(value["max_overlap_ms"], overlap * 1000.0)
            value["minimum_depth"] = depth if value["minimum_depth"] is None else min(value["minimum_depth"], depth)
            value["crosses_task_end_count"] += stop > target["finish"]
        values = [{"timer_id": timer_id, "name": name, **value,
                   "source_file": timers.get(timer_id, {}).get("File", ""),
                   "source_line": timers.get(timer_id, {}).get("Line", "")}
                  for (timer_id, name), value in stats.items()]
        values.sort(key=lambda value: value["inclusive_overlap_ms"], reverse=True)
        output.append({**target, "phase_overlap_ms": (end - begin) * 1000.0,
                       "interior_scope_coverage_ms": interval_union_ms(intervals, begin, end),
                       "interior_scope_count": sum(value["count"] for value in values),
                       "top_inclusive_interiors": values[:top]})
    return output


def summarize_events(path, bound, threads, timers, top, task_targets=()):
    begin, end = bound["start_seconds"], bound["end_seconds"]
    if not all(map(math.isfinite, (begin, end))) or end <= begin:
        raise ValueError(f"Invalid region interval: {bound}")
    output = []
    interiors = []
    seen = set()
    for thread_id, group in itertools.groupby(rows(path), lambda row: row["ThreadId"]):
        if thread_id in seen:
            raise ValueError(f"Noncontiguous thread export in {path}: {thread_id}")
        seen.add(thread_id)
        thread = threads.get(thread_id, {})
        # Unreal exports virtual frame and Verse tracks alongside actual CPU/GPU.
        if thread.get("Group") in {"Frame Tracks", "Verse"}:
            continue
        events = []
        thread_name = thread.get("Name", "")
        for row in group:
            thread_name = thread_name or row["ThreadName"]
            a, b = float(row["StartTime"]), float(row["EndTime"])
            if not all(map(math.isfinite, (a, b))) or b < a:
                raise ValueError(f"Invalid event interval in {path}")
            events.append((a, b, int(row["Depth"]), row["TimerId"], row["TimerName"]))
        values, invalid = aggregate_thread(events, begin, end)
        if thread.get("Group") != "GPU":
            interiors.extend(summarize_task_interiors(events, bound, thread_id, task_targets, timers, top))
        coverage = 0.0
        last_end = begin
        overlapping = 0
        for a, b, *_ in events:
            a, b = max(a, begin), min(b, end)
            if b > a:
                overlapping += 1
                coverage += max(0.0, b - max(a, last_end))
                last_end = max(last_end, b)
        for value in values:
            source = timers.get(value["timer_id"], {})
            value["timer_type"] = source.get("Type", "unknown")
            value["source_file"] = source.get("File", "")
            value["source_line"] = source.get("Line", "")
        values.sort(key=lambda x: x["inclusive_ms"], reverse=True)
        exclusive = sorted(values, key=lambda x: x["exclusive_ms"] or 0.0, reverse=True)
        output.append({"thread_id": thread_id, "thread_name": thread_name,
                       "group": thread.get("Group", ""),
                       "timeline_type": "GPU" if thread.get("Group") == "GPU" else "CPU",
                       "event_count": len(events), "invalid_nesting_count": invalid,
                       "overlapping_event_count": overlapping,
                       "instrumented_scope_coverage_ms": coverage * 1000.0,
                       "exclusive_scope_total_ms": sum(value["exclusive_ms"] for value in values) if not invalid else None,
                       "top_inclusive": values[:top], "top_exclusive": exclusive[:top]})
    return {"region": bound["region"], "region_index": bound.get("region_index"),
            "start_seconds": begin, "end_seconds": end,
            "duration_seconds": end - begin, "events_file": str(path), "threads": output,
            "awaited_task_interiors": interiors}


def summarize_counters(directory, bounds, prefixes=()):
    inventory = list(rows(directory / "counters.csv"))
    output = []
    invalid_chars = '<>:"/\\|?*'
    filenames = defaultdict(list)
    for counter in inventory:
        filename = "".join("_" if char in invalid_chars else char for char in counter["Name"]).strip()
        filenames[filename.casefold()].append(counter["Id"])
    for counter in inventory:
        if prefixes and not any(counter["Name"].startswith(prefix) for prefix in prefixes):
            continue
        filename = "".join("_" if char in invalid_chars else char for char in counter["Name"]).strip()
        path = directory / f"counter-{filename}.csv"
        if not path.exists():
            continue
        if len(filenames[filename.casefold()]) > 1:
            output.append({"id": counter["Id"], "name": counter["Name"], "type": counter["Type"],
                           "available": False, "problem": "Multiple counter IDs map to the same export filename",
                           "conflicting_counter_ids": filenames[filename.casefold()], "phases": []})
            continue
        phase = [{"region": bound["region"], "region_index": bound.get("region_index"),
                  "start_seconds": bound["start_seconds"],
                  "end_seconds": bound["end_seconds"], "sample_count": 0,
                  "prior_value": None, "min": None, "max": None, "last": None} for bound in bounds]
        count = 0
        prior_time = -math.inf
        for row in rows(path):
            time, value = float(row["Time"]), float(row["Value"])
            if not all(map(math.isfinite, (time, value))) or time < prior_time:
                raise ValueError(f"Invalid or nonmonotonic counter sample in {path}")
            prior_time = time
            count += 1
            for result in phase:
                if time < result["start_seconds"]:
                    result["prior_value"] = value
                elif time < result["end_seconds"]:
                    result["sample_count"] += 1
                    result["min"] = value if result["min"] is None else min(result["min"], value)
                    result["max"] = value if result["max"] is None else max(result["max"], value)
                    result["last"] = value
        output.append({"id": counter["Id"], "name": counter["Name"], "type": counter["Type"], "available": count > 0,
                       "semantics": COUNTER_NOTES.get(counter["Name"], "Native counter values; units require provider/source interpretation"),
                       "sample_count": count, "phases": phase})
    return output


def summarize_frames(source):
    """Full engine-frame durations, assigned by frame start, separate from ticks."""
    begin, end = source["interval_start_seconds"], source["interval_end_seconds"]
    frames = source.get("game_frames_overlapping_interval", [])
    selected = []
    overlapping = 0
    incomplete = 0
    for frame in frames:
        a, b = frame.get("start"), frame.get("end")
        if a is None or b is None:
            incomplete += 1
            continue
        if not all(map(math.isfinite, (a, b))) or b < a:
            raise ValueError("Invalid engine frame interval")
        if begin <= a < end:
            selected.append({**frame, "duration_ms": (b - a) * 1000.0,
                             "crosses_selected_interval_end": b > end})
        if a < end and b > begin:
            overlapping += 1
    return {"available": bool(selected), "overlapping_frame_count": overlapping,
            "incomplete_frame_count": incomplete,
            "frame_time": distribution([frame["duration_ms"] for frame in selected]),
            "start_assigned_crossing_end_count": sum(frame["crosses_selected_interval_end"] for frame in selected),
            "fully_contained_frame_time": distribution([frame["duration_ms"] for frame in selected
                                                          if not frame["crosses_selected_interval_end"]]),
            "excursions_over_8_33_ms": [frame for frame in selected if frame["duration_ms"] > 8.33],
            "assignment": "Full engine-frame durations whose starts lie in the half-open trace interval; not clipped. Crossing-end frames are flagged and fully-contained statistics are separate: a capture-tail frame can include excluded screenshot/save work. Fixture CSV uses tick-end timestamps and different boundaries."}


def summarize_frame_phases(source):
    result = []
    occurrences = defaultdict(int)
    for region in sorted(source.get("regions", []), key=lambda item: item.get("begin", 0)):
        name = region["name"]
        if not name.startswith("DP01_"):
            continue
        index = occurrences[name]
        occurrences[name] += 1
        a, b = region.get("begin"), region.get("end")
        if a is None or b is None:
            continue
        begin = max(a, source["interval_start_seconds"])
        end = min(b, source["interval_end_seconds"])
        if end <= begin:
            continue
        result.append({"region": name, "region_index": index, "region_start_seconds": a,
                       "region_end_seconds": b, "selected_start_seconds": begin, "selected_end_seconds": end,
                       "partial_region": begin != a or end != b,
                       **summarize_frames({**source, "interval_start_seconds": begin, "interval_end_seconds": end})})
    return result


def interval_union_ms(intervals, begin, end):
    total, last_end = 0.0, begin
    for start, stop in sorted(intervals):
        start, stop = max(begin, start), min(end, stop)
        if stop > start:
            total += max(0.0, stop - max(start, last_end))
            last_end = max(last_end, stop)
    return total * 1000.0


def summarize_wait_phases(source):
    """Union recorded wait scopes within each thread; do not sum nested waits."""
    result = []
    occurrences = defaultdict(int)
    for region in sorted(source.get("regions", []), key=lambda item: item.get("begin", 0)):
        name = region["name"]
        if not name.startswith("DP01_"):
            continue
        index = occurrences[name]
        occurrences[name] += 1
        if region.get("begin") is None or region.get("end") is None:
            continue
        begin = max(region["begin"], source["interval_start_seconds"])
        end = min(region["end"], source["interval_end_seconds"])
        if end <= begin:
            continue
        by_thread = defaultdict(list)
        for wait in source["waits"]:
            if wait["event_start"] < end and wait["event_end"] > begin:
                by_thread[(wait["thread_id"], wait["thread_name"])].append(wait)
        threads = []
        for (thread_id, thread_name), waits in by_thread.items():
            matched = [wait for wait in waits if wait["awaited_task_ids"]]
            unmatched = [wait for wait in waits if not wait["awaited_task_ids"]]
            intervals = lambda selected: [(wait["event_start"], wait["event_end"]) for wait in selected]
            timer_groups = defaultdict(list)
            for wait in waits:
                timer_groups[wait["timer"]].append(wait)
            threads.append({"thread_id": thread_id, "thread_name": thread_name, "wait_scope_count": len(waits),
                            "matched_wait_scope_count": len(matched),
                            "all_wait_union_ms": interval_union_ms(intervals(waits), begin, end),
                            "matched_wait_union_ms": interval_union_ms(intervals(matched), begin, end),
                            "unmatched_wait_union_ms": interval_union_ms(intervals(unmatched), begin, end),
                            "by_timer": [{"timer": timer, "wait_scope_count": len(group),
                                          "union_ms": interval_union_ms(intervals(group), begin, end)}
                                         for timer, group in sorted(timer_groups.items())]})
        result.append({"region": name, "region_index": index, "start_seconds": begin, "end_seconds": end,
                       "threads": sorted(threads, key=lambda thread: thread["all_wait_union_ms"], reverse=True)})
    return {"minimum_exported_wait_ms": source.get("minimum_wait_ms"), "phases": result,
            "limitation": "Union within each thread of exported wait scopes only. Matched/unmatched subsets and individual timer unions may overlap; do not add them. Wait scope wall time can include processing work, not pure idle. Generic task names do not establish subsystem attribution."}


def summarize_dependencies(path, top):
    source = json.loads(path.read_text(encoding="utf-8-sig"))
    tasks = {task["id"]: task for task in source["tasks"]}
    output = []
    waits = sorted(source["waits"], key=lambda item: item["interval_overlap_ms"], reverse=True)
    for wait in waits[:top]:
        begin = max(wait["event_start"], source["interval_start_seconds"])
        end = min(wait["event_end"], source["interval_end_seconds"])
        pending = list(wait["awaited_task_ids"])
        seen = set()
        missing = set()
        executions = []
        while pending:
            task_id = pending.pop()
            if task_id in seen:
                continue
            seen.add(task_id)
            task = tasks.get(task_id)
            if not task:
                missing.add(task_id)
                continue
            for relation in task["prerequisites"] + task["nested_tasks"]:
                pending.append(relation["task_id"])
            a, b = task.get("started"), task.get("finished")
            if a is not None and b is not None and min(b, end) > max(a, begin):
                executions.append({"task_id": task_id, "name": task["name"],
                                   "thread_id": task["started_thread_id"],
                                   "thread_name": task["started_thread_name"],
                                   "start": a, "finish": b, "completed": task.get("completed"),
                                   "wait_overlap_ms": (min(b, end) - max(a, begin)) * 1000.0})
        executions.sort(key=lambda item: item["wait_overlap_ms"], reverse=True)
        output.append({**wait, "blocking_graph_task_count": len(seen),
                       "missing_graph_task_ids": sorted(missing),
                       "overlapping_executions": executions[:top]})
    return {"source": str(path), "truncated": source["truncated"],
            "trace_file": source.get("trace_file"),
            "region": source.get("region"), "region_index": source.get("region_index"),
            "interval_start_seconds": source["interval_start_seconds"],
            "interval_end_seconds": source["interval_end_seconds"],
            "matched_wait_count": source["matched_wait_count"],
            "unmatched_wait_count": source["unmatched_wait_count"],
            "missing_task_ids": source.get("missing_task_ids", []),
            "game_frames": summarize_frames(source),
            "game_frame_phases": summarize_frame_phases(source),
            "wait_phase_unions": summarize_wait_phases(source),
            "blast_frame": source.get("blast_frame"), "top_waits": output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exports", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dependencies", type=Path, action="append", default=[])
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--counter-prefix", action="append", default=[],
                        help="Only read sample files for counter names with this prefix; repeat as needed (default: all)")
    args = parser.parse_args()
    saved = Path(__file__).resolve().parents[2] / "Saved"
    output = args.output.resolve()
    if not output.is_relative_to(saved.resolve()) or output.exists():
        parser.error("--output must be a new path beneath project Saved")
    if not 1 <= args.top <= 100:
        parser.error("--top must be between 1 and 100")
    directory = args.exports.resolve()
    bounds = json.loads((directory / "region-bounds.json").read_text(encoding="utf-8-sig"))
    if isinstance(bounds, dict):
        bounds = [bounds]
    if not bounds:
        parser.error("No timing event region bounds; export with -IncludeTimingEvents")
    occurrences = defaultdict(int)
    for bound in sorted(bounds, key=lambda value: (value["region"], value["start_seconds"])):
        if "region_index" not in bound:
            bound["region_index"] = occurrences[bound["region"]]
        occurrences[bound["region"]] += 1
    threads = {item["Id"]: item for item in rows(directory / "threads.csv")}
    timers = {item["Id"]: item for item in rows(directory / "timers.csv")}
    dependencies = [summarize_dependencies(path, args.top) for path in args.dependencies]
    targets = {}
    for dependency in dependencies:
        for wait in dependency["top_waits"]:
            if wait["thread_name"] != "GameThread" or not wait["awaited_task_ids"]:
                continue
            for task in wait["overlapping_executions"]:
                key = (dependency["source"], task["task_id"])
                if key not in targets:
                    targets[key] = {**task, "dependency_source": dependency["source"], "awaited_from_waits": []}
                targets[key]["awaited_from_waits"].append({key: wait.get(key) for key in
                    ("timer", "event_start", "event_end", "relation_source", "provider_lookup_timer")})
    manifest_path = directory / "launch.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        trace_file = manifest.get("trace_path")
        if trace_file and any(dependency["trace_file"] and Path(dependency["trace_file"]).resolve() != Path(trace_file).resolve()
                              for dependency in dependencies):
            parser.error("Dependency exports must reference the same trace as the event-export launch manifest")
    result = {"schema": "DP01-trace-attribution-v1", "units": "seconds for origins; milliseconds for timings",
              "limits": [
                  "Inclusive nested scopes and parallel worker/GPU times overlap; totals are not frame time.",
                  "Timer names are exact evidence, not an automatic assignment of generic work to Chaos or Blueprint.",
                  "Exclusive time uses all event scopes, clipped to region boundaries; invalid nesting suppresses self time.",
                  "Instrumented scope coverage is the union of recorded scope intervals, including waits; it is not CPU utilization.",
                  "Legacy logged region bounds have microsecond precision; bounded native-provider exports retain source precision. Both reflect observed phase transition ticks.",
                  "Counter min/max use samples within the half-open phase; prior_value is separate. Missing samples are not zero.",
                  "Chaos/Solver counters are global trace counters updated by each solver, not per actor or additive across solvers (UE 5.8 PBDRigidsSolver.cpp UpdateStatCounters).",
                  "Task dependencies are provider edges. Execution overlaps are correlated only within that dependency graph; do not sum them.",
                  "Awaited-task interiors cover top GameThread waits only, joining exact recorded task thread/span to scope starts within that execution. Earlier-starting enclosing scopes are excluded; clipped/nested interior inclusive times are non-additive.",
                  "Frame/GPU availability and owner acceptance must be checked separately."],
              "phases": [], "counters": [], "dependencies": []}
    for bound in bounds:
        path = directory / Path(bound["path"].replace("\\", "/")).name
        result["phases"].append(summarize_events(path, bound, threads, timers, args.top, targets.values()))
    excluded = [counter["Name"] for counter in rows(directory / "counters.csv")
                if args.counter_prefix and not any(counter["Name"].startswith(prefix) for prefix in args.counter_prefix)]
    result["counter_selection"] = {"prefixes": args.counter_prefix, "excluded_counter_names": excluded,
                                   "note": "Excluded counters were deliberately not read; exclusion does not mean unavailable"}
    result["counters"] = summarize_counters(directory, bounds, args.counter_prefix)
    result["dependencies"] = dependencies
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as destination:
        json.dump(result, destination, indent=2, allow_nan=False)
    print(json.dumps({"output": str(output), "phases": len(result["phases"]),
                      "counters_with_exports": len(result["counters"]),
                      "dependency_exports": len(result["dependencies"])}))


if __name__ == "__main__":
    main()
