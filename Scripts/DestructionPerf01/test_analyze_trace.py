"""Numerical checks for clipping/nesting and explicit task-graph attribution."""
import json
import tempfile
import unittest
from pathlib import Path

from analyze import SAVED_ROOT
from analyze_trace import (aggregate_thread, summarize_counters, summarize_dependencies,
                           summarize_events, summarize_frame_phases, summarize_frames,
                           summarize_task_interiors, summarize_wait_phases)


class TraceAttributionTests(unittest.TestCase):
    def temporary(self):
        return tempfile.TemporaryDirectory(prefix="dp01-trace-test-", dir=SAVED_ROOT)

    def test_clipping_children_and_sibling_self_time(self):
        events = [(0, 10, 0, "1", "root"), (1, 4, 1, "2", "child"),
                  (2, 3, 2, "3", "leaf"), (5, 8, 1, "2", "child")]
        values, invalid = aggregate_thread(events, 2.5, 6)
        by_name = {row["name"]: row for row in values}
        self.assertEqual(invalid, 0)
        self.assertAlmostEqual(by_name["root"]["inclusive_ms"], 3500)
        self.assertAlmostEqual(by_name["root"]["exclusive_ms"], 1000)
        self.assertAlmostEqual(by_name["child"]["exclusive_ms"], 2000)
        self.assertAlmostEqual(sum(row["exclusive_ms"] for row in values), 3500)

    def test_missing_child_depth_suppresses_self_time(self):
        values, invalid = aggregate_thread([(0, 3, 0, "1", "root"),
                                            (1, 2, 2, "2", "gap")], 0, 3)
        self.assertEqual(invalid, 1)
        self.assertTrue(all(row["exclusive_ms"] is None for row in values))

    def test_overlapping_siblings_and_missing_root_suppress_self_time(self):
        for events in ([(0, 3, 0, "1", "root"), (0.5, 2, 1, "2", "child"),
                        (1, 2.5, 1, "3", "sibling")], [(0, 3, 1, "2", "missing root")]):
            values, invalid = aggregate_thread(events, 0, 3)
            self.assertEqual(invalid, 1)
            self.assertTrue(all(row["exclusive_ms"] is None for row in values))

    def test_gpu_and_game_same_timer_name_stay_separate(self):
        with self.temporary() as temp:
            path = Path(temp) / "events.csv"
            path.write_text("ThreadId,ThreadName,TimerId,TimerName,StartTime,EndTime,Depth\n"
                            "1,GameThread,10,Frame,0,1,0\n"
                            "2,GPU0-Graphics0,20,Frame,0,2,0\n"
                            "3,Game Frames,0,Frame,0,2,0\n", encoding="utf-8")
            result = summarize_events(path, {"start_seconds": 0, "end_seconds": 2, "region": "test"},
                                      {"1": {"Group": ""}, "2": {"Group": "GPU"},
                                       "3": {"Group": "Frame Tracks"}}, {}, 10)
            self.assertEqual([row["timeline_type"] for row in result["threads"]], ["CPU", "GPU"])
            self.assertEqual([row["top_inclusive"][0]["inclusive_ms"] for row in result["threads"]], [1000, 2000])
            self.assertEqual([row["instrumented_scope_coverage_ms"] for row in result["threads"]], [1000, 2000])

    def test_counter_boundaries_prior_value_and_filename_collision(self):
        with self.temporary() as temp:
            directory = Path(temp)
            (directory / "counters.csv").write_text("Id,Type,Name\n1,Int64,Chaos/Active\n", encoding="utf-8")
            (directory / "counter-Chaos_Active.csv").write_text("Time,Value\n0,8\n1,3\n2,5\n3,11\n", encoding="utf-8")
            bounds = [{"region": "test", "start_seconds": 1, "end_seconds": 3}]
            result = summarize_counters(directory, bounds)[0]["phases"][0]
            self.assertEqual((result["prior_value"], result["sample_count"], result["min"], result["max"], result["last"]),
                             (8, 2, 3, 5, 5))
            (directory / "counters.csv").write_text("Id,Type,Name\n1,Int64,Chaos/Active\n2,Int64,Chaos_Active\n", encoding="utf-8")
            self.assertTrue(all(not row["available"] for row in summarize_counters(directory, bounds)))

    def test_nonmonotonic_counter_is_rejected(self):
        with self.temporary() as temp:
            directory = Path(temp)
            (directory / "counters.csv").write_text("Id,Type,Name\n1,Int64,Count\n", encoding="utf-8")
            (directory / "counter-Count.csv").write_text("Time,Value\n2,8\n1,3\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                summarize_counters(directory, [{"region": "test", "start_seconds": 0, "end_seconds": 3}])

    def test_counter_prefix_does_not_read_excluded_sample_files(self):
        with self.temporary() as temp:
            directory = Path(temp)
            (directory / "counters.csv").write_text("Id,Type,Name\n1,Int64,Chaos/Count\n2,Int64,Tasks::Running\n", encoding="utf-8")
            (directory / "counter-Chaos_Count.csv").write_text("Time,Value\n1,8\n", encoding="utf-8")
            (directory / "counter-Tasks__Running.csv").write_text("Time,Value\ninvalid,NaN\n", encoding="utf-8")
            bounds = [{"region": "test", "start_seconds": 0, "end_seconds": 3}]
            selected = summarize_counters(directory, bounds, ["Chaos/"])
            self.assertEqual([counter["name"] for counter in selected], ["Chaos/Count"])
            with self.assertRaises(ValueError):
                summarize_counters(directory, bounds)

    def test_engine_frames_use_start_assignment_and_full_duration(self):
        result = summarize_frames({"interval_start_seconds": 1, "interval_end_seconds": 2,
                                   "game_frames_overlapping_interval": [
                                       {"index": "5", "start": 0.5, "end": 1.1},
                                       {"index": "6", "start": 1.1, "end": 1.9},
                                       {"index": "7", "start": 1.9, "end": 2.2}]})
        self.assertEqual(result["overlapping_frame_count"], 3)
        self.assertEqual(result["frame_time"]["sample_count"], 2)
        self.assertAlmostEqual(result["frame_time"]["max_ms"], 800)
        self.assertEqual(result["start_assigned_crossing_end_count"], 1)
        self.assertEqual(result["fully_contained_frame_time"]["sample_count"], 1)
        self.assertTrue(result["excursions_over_8_33_ms"][-1]["crosses_selected_interval_end"])
        self.assertEqual([row["index"] for row in result["excursions_over_8_33_ms"]], ["6", "7"])

    def test_partial_frame_phase_keeps_native_region_and_clip(self):
        result = summarize_frame_phases({"interval_start_seconds": 1.1, "interval_end_seconds": 2.5,
                                        "regions": [{"name": "DP01_Burst", "begin": 1, "end": 2},
                                                    {"name": "DP01_Early", "begin": 2, "end": 3},
                                                    {"name": "DestructionPerfBlast", "begin": 1, "end": 16}],
                                        "game_frames_overlapping_interval": [
                                            {"index": "6", "start": 1.05, "end": 1.2},
                                            {"index": "7", "start": 1.2, "end": 2.1},
                                            {"index": "8", "start": 2.1, "end": 2.6}]})
        self.assertEqual(len(result), 2)
        self.assertTrue(all(phase["partial_region"] for phase in result))
        self.assertEqual(result[0]["region_start_seconds"], 1)
        self.assertEqual(result[0]["selected_start_seconds"], 1.1)
        self.assertEqual(result[0]["overlapping_frame_count"], 2)
        self.assertEqual(result[1]["overlapping_frame_count"], 2)
        self.assertEqual([phase["frame_time"]["sample_count"] for phase in result], [1, 1])

    def test_wait_phase_union_does_not_add_nested_scopes_or_threads(self):
        def wait(begin, end, matched, thread=1):
            return {"event_start": begin, "event_end": end, "awaited_task_ids": ["task"] if matched else [],
                    "thread_id": thread, "thread_name": "GameThread" if thread == 1 else "Worker", "timer": "Wait"}
        result = summarize_wait_phases({"interval_start_seconds": 0, "interval_end_seconds": 1,
                                       "regions": [{"name": "DP01_Burst", "begin": 0, "end": 1}],
                                       "waits": [wait(-1, 2, False), wait(0.1, 0.9, True),
                                                 wait(0.2, 0.8, True), wait(0, 1, True, thread=2)]})
        threads = {row["thread_name"]: row for row in result["phases"][0]["threads"]}
        self.assertEqual(threads["GameThread"]["all_wait_union_ms"], 1000)
        self.assertEqual(threads["GameThread"]["matched_wait_union_ms"], 800)
        self.assertEqual(threads["GameThread"]["unmatched_wait_union_ms"], 1000)
        self.assertEqual(threads["Worker"]["all_wait_union_ms"], 1000)

    def test_task_interiors_require_recorded_thread_and_execution_span(self):
        events = [(0, 10, 0, "1", "Enclosing"), (1, 4, 1, "2", "Physics"),
                  (2, 3, 2, "3", "Collision"), (5, 6, 1, "4", "Unrelated")]
        target = {"task_id": "123", "thread_id": 7, "start": 1, "finish": 3.5}
        bounds = {"start_seconds": 0, "end_seconds": 10}
        self.assertEqual(summarize_task_interiors(events, bounds, 8, [target], {}, 10), [])
        result = summarize_task_interiors(events, bounds, "7", [target], {}, 10)[0]
        self.assertEqual([scope["name"] for scope in result["top_inclusive_interiors"]], ["Physics", "Collision"])
        self.assertEqual(result["interior_scope_coverage_ms"], 2500)
        self.assertEqual(result["top_inclusive_interiors"][0]["crosses_task_end_count"], 1)

    def test_wait_only_follows_recorded_graph_with_cycle(self):
        with self.temporary() as temp:
            path = Path(temp) / "dependencies.json"
            task = {"id": "9007199254740993", "name": "Physics", "started": 1,
                    "finished": 2, "completed": 2.1, "started_thread_id": 7,
                    "started_thread_name": "Worker", "nested_tasks": [],
                    "prerequisites": [{"task_id": "9007199254740993"}]}
            source = {"interval_start_seconds": 1, "interval_end_seconds": 3,
                      "truncated": False, "matched_wait_count": 1, "unmatched_wait_count": 0,
                      "tasks": [task, {**task, "id": "unrelated", "name": "Not a blocker"}],
                      "waits": [{"event_start": 1.5, "event_end": 2.5,
                                 "interval_overlap_ms": 1000, "awaited_task_ids": [task["id"]]}]}
            path.write_text(json.dumps(source), encoding="utf-8")
            wait = summarize_dependencies(path, 10)["top_waits"][0]
            self.assertEqual(wait["blocking_graph_task_count"], 1)
            self.assertEqual(wait["overlapping_executions"][0]["task_id"], task["id"])
            self.assertEqual(wait["overlapping_executions"][0]["wait_overlap_ms"], 500)


if __name__ == "__main__":
    unittest.main()
