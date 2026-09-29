#!/usr/bin/env python3
"""Focused DP-01 analysis checks; synthetic fixtures stay under Saved/."""

from __future__ import annotations

import copy
import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

import analyze


def sample(timestamp: float, frame_ms: float = 10.0, **extra: float) -> dict:
    return {"relative_seconds": timestamp, "frame_ms": frame_ms, "game_ms": 3.0,
            "render_ms": 2.0, "rhi_ms": 1.0, "gpu_ms": 4.0, **extra}


def metadata(name: str = "control", index: int = 1, traced: bool = False) -> dict:
    prop = {"actor": "/Game/Test.Actor1", "id": "CopiedVendorId", "data_asset": "/Game/Test.Asset",
            "root_broken": False, "break_events": 0, "ready": True, "reset_generation": index - 1}
    result = {key: "fixed" for key in analyze.IDENTITY_FIELDS}
    result.update({"schema": "DestructionPerf01-v2", "outcome": "complete", "detonation_observed": True,
                   "run_name": name, "run_index": index, "trace_enabled": traced,
                   "trace_channels": "cpu,frame,task,gpu" if traced else "none",
                   "diagnostics_enabled": False, "named_events_enabled": traced,
                   "camera_location": "X=-550.000 Y=-600.000 Z=172.000",
                   "camera_rotation": "P=-2.000 Y=90.000 R=0.000",
                   "camera_location_after": "X=-550.000 Y=-600.000 Z=172.000",
                   "camera_rotation_after": "P=-2.000 Y=90.000 R=0.000",
                   "props_before": [prop], "props_after": [{**prop, "root_broken": True, "break_events": 25}]})
    return result


class AnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        analyze.SAVED_ROOT.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="dp01-analyzer-test-", dir=analyze.SAVED_ROOT)
        self.directory = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def capture(self, name: str, rows: list[dict], content: dict | None = None) -> dict:
        path = self.directory / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        if content is not None:
            path.with_suffix(".json").write_text(json.dumps(content), encoding="utf-8")
        return analyze.analyze_capture(path)

    def paired(self) -> list[dict]:
        return [self.capture(f"{name}{index}", [sample(time, duration) for time in (-4, 0.1, 0.6, 3.1, 10.1)],
                             metadata(name, index, traced))
                for name, traced, durations in (("control", False, (100, 9, 10, 11)),
                                                ("traced", True, (200, 10, 11, 12)))
                for index, duration in enumerate(durations, 1)]

    def test_legacy_metrics_and_boundaries(self) -> None:
        analyze.self_test()
        self.assertEqual(analyze.phase_name(-0.1), "prebaseline")
        self.assertEqual(analyze.phase_name(15), "recovery")

    def test_dp01_half_open_boundaries(self) -> None:
        expected = {-5.001: None, -5: "intact", -0.100001: "intact", -0.1: None, -0.001: None,
                    0: "burst", 0.499999: "burst", 0.5: "early", 2.999999: "early",
                    3: "active", 9.999999: "active", 10: "settled", 14.999999: "settled", 15: None}
        for timestamp, name in expected.items():
            with self.subTest(timestamp=timestamp):
                self.assertEqual(analyze.phase_name(timestamp, analyze.DP01_PHASES), name)

    def test_legacy_and_new_buckets_are_separate(self) -> None:
        capture = self.capture("boundaries", [sample(time) for time in (-5, -0.1, 0, 0.5, 1, 3, 5, 10, 15)], metadata())
        self.assertEqual([phase["frame_count"] for phase in capture["phases"].values()], [2, 2, 2, 3])
        self.assertEqual([phase["frame_count"] for phase in capture["dp01_phases"].values()], [1, 1, 2, 2, 1])
        self.assertEqual(capture["dp01_excluded_frame_count"], 2)

    def test_excursions_are_strict_and_keep_position(self) -> None:
        capture = self.capture("thresholds", [sample(0.01 * index, duration) for index, duration in
                                               enumerate((8.33, 8.34, 16.67, 16.68))])
        phase = capture["dp01_phases"]["burst"]
        excursions = phase["excursions_over_8_33_ms"]
        self.assertEqual([row["sample_index"] for row in excursions], [1, 2, 3])
        self.assertEqual([row["also_over_16_67_ms"] for row in excursions], [False, False, True])
        self.assertEqual([row["frame_count"] for row in phase["thresholds"][:2]], [3, 1])
        self.assertAlmostEqual(phase["frame_time"]["p50_ms"], 12.505)

    def test_diagnostic_held_values_and_unavailable_are_not_samples(self) -> None:
        rows = [sample(0.01 * index, diagnostic_sample=flag, process_physical_bytes=value,
                       gc_active_transforms=-1, niagara_active_components=0)
                for index, (flag, value) in enumerate(((1, 1000), (0, 1000), (1, 3000), (1, -1)))]
        counters = self.capture("diagnostics", rows)["dp01_phases"]["burst"]["workload_counters"]
        self.assertEqual(counters["process_physical_bytes"]["sample_count"], 2)
        self.assertEqual(counters["process_physical_bytes"]["median"], 2000)
        self.assertEqual(counters["process_physical_bytes"]["unit"], "bytes")
        self.assertFalse(counters["gc_active_transforms"]["available"])
        self.assertTrue(counters["niagara_active_components"]["available"])
        self.assertEqual(counters["niagara_active_components"]["maximum"], 0)

    def test_cumulative_break_increment_includes_phase_entry(self) -> None:
        rows = [sample(-0.01, break_events=10), sample(0.1, break_events=14), sample(0.2, break_events=19)]
        counter = self.capture("breaks", rows)["dp01_phases"]["burst"]["workload_counters"]["break_events"]
        self.assertEqual(counter["first_cumulative"], 14)
        self.assertEqual(counter["observed_increment_total"], 9)
        self.assertEqual(counter["increment_sample_count"], 2)

    def test_cumulative_counter_reset_is_not_negative_work(self) -> None:
        rows = [sample(0.1, break_events=10), sample(0.2, break_events=0), sample(0.3, break_events=4)]
        counter = self.capture("reset", rows)["dp01_phases"]["burst"]["workload_counters"]["break_events"]
        self.assertEqual(counter["observed_increment_total"], 4)
        self.assertEqual(counter["increment_sample_count"], 1)

    def test_activation_and_audio_proxy_units_remain_explicit(self) -> None:
        rows = [sample(-0.01, diagnostic_sample=0, observed_transform_activations=10, audio_active_sources=-1),
                sample(0.1, diagnostic_sample=1, observed_transform_activations=14, audio_active_sources=3),
                sample(0.2, diagnostic_sample=0, observed_transform_activations=14, audio_active_sources=3),
                sample(0.3, diagnostic_sample=1, observed_transform_activations=19, audio_active_sources=7)]
        counters = self.capture("proxies", rows)["dp01_phases"]["burst"]["workload_counters"]
        self.assertEqual(counters["observed_transform_activations"]["observed_increment_total"], 9)
        self.assertEqual(counters["observed_transform_activations"]["sample_count"], 2)
        self.assertIn("not exact solver body releases", counters["observed_transform_activations"]["note"])
        self.assertEqual(counters["audio_active_sources"]["unit"], "sources")
        self.assertEqual(counters["audio_active_sources"]["sample_count"], 2)

    def test_blast_frame_candidate_and_following_sample(self) -> None:
        content = {**metadata(), "detonation_engine_frame": 101}
        rows = [sample(-0.001, 6, engine_frame=101), sample(0.03, 31, engine_frame=102),
                sample(0.07, 40, engine_frame=103)]
        blast = self.capture("blast", rows, content)["blast"]
        self.assertEqual(blast["engine_frame_match"]["frame_ms"], 6)
        self.assertEqual(blast["sample_after_engine_frame_match"]["frame_ms"], 31)
        self.assertEqual(blast["worst_sample_in_burst"]["frame_ms"], 40)
        self.assertIn("not an engine frame-boundary", blast["limitation"])

    def test_old_capture_does_not_invent_blast_identity(self) -> None:
        blast = self.capture("old", [sample(0.001), sample(0.1, 30)], metadata())["blast"]
        self.assertIsNone(blast["engine_frame_match"])
        self.assertIsNone(blast["detonation_engine_frame"])
        self.assertEqual(blast["worst_sample_in_burst"]["frame_ms"], 30)

    def test_engine_frame_integer_precision(self) -> None:
        capture = self.capture("integer", [sample(0, engine_frame=2**53 + 1)],
                               {**metadata(), "detonation_engine_frame": 2**53 + 1})
        self.assertEqual(capture["blast"]["engine_frame_match"]["engine_frame"], 2**53 + 1)

    def test_invalid_optional_counter_is_rejected(self) -> None:
        for index, invalid in enumerate((-2, 0.5, math.inf)):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.capture(f"invalid{index}", [sample(0, gc_active_transforms=invalid)])

    def test_prop_identity_uses_actor_and_adapter(self) -> None:
        content = metadata()
        content["props_before"].append({**content["props_before"][0], "actor": "/Game/Test.Actor2"})
        content["props_after"].append({**content["props_after"][0], "actor": "/Game/Test.Actor2", "break_events": 10})
        workload = analyze.prop_workload(content)
        self.assertTrue(workload["available"])
        self.assertEqual(workload["break_notification_delta"], 35)
        self.assertEqual(workload["newly_root_broken_props"], 2)
        content["props_before"].append(content["props_before"][0])
        self.assertFalse(analyze.prop_workload(content)["available"])

    def test_aborted_and_missing_metadata_captures_are_not_comparison_eligible(self) -> None:
        rows = [sample(time) for time in (-4, 0.1, 0.6, 3.1, 10.1)]
        self.assertFalse(self.capture("aborted", rows, {**metadata(), "outcome": "aborted_reset"})["comparison_eligible"])
        self.assertFalse(self.capture("no-metadata", rows)["comparison_eligible"])

    def test_cold_and_warm_are_not_pooled(self) -> None:
        captures = self.paired()
        series = analyze.series_summaries(captures)["control"]
        self.assertTrue(series["has_at_least_three_distinct_warmed_runs"])
        self.assertEqual(series["first_blast_after_process_start"]["run_indices"], [1])
        metric = series["warmed_repetitions"]["phase_metrics_ms"]["burst"]["frame_ms"]["p95_ms"]
        self.assertEqual(metric["median_of_run_values"], 10)
        self.assertEqual(metric["run_value_range"], 2)
        comparison = analyze.compare_runs(captures, "control", "traced")
        self.assertEqual(comparison["status"], "comparable")
        self.assertTrue(comparison["has_at_least_three_warmed_runs_per_series"])
        delta = comparison["warmed_phase_overhead"]["burst"]["frame_ms"]["p95_ms"]
        self.assertEqual(delta["traced_minus_control_ms"], 1)
        self.assertEqual(delta["relative_delta_percent"], 10)

    def test_mismatched_workload_and_ordinals_refuse_overhead(self) -> None:
        captures = self.paired()
        mismatch = copy.deepcopy(captures)
        mismatch[-1]["metadata"]["content"]["camera_rotation"] = "changed"
        result = analyze.compare_runs(mismatch, "control", "traced")
        self.assertEqual(result["status"], "not_comparable")
        self.assertNotIn("warmed_phase_overhead", result)
        self.assertIn("camera_rotation", result["identity_variations"])
        self.assertEqual(analyze.compare_runs(captures[:-1], "control", "traced")["status"], "not_comparable")

    def test_duplicate_ordinals_refuse_overhead(self) -> None:
        captures = self.paired()
        captures[-1]["metadata"]["content"]["run_index"] = 3
        result = analyze.compare_runs(captures, "control", "traced")
        self.assertEqual(result["status"], "not_comparable")
        self.assertIn("traced: duplicate run indices", result["problems"])

    def test_instrumentation_cannot_change_inside_one_series(self) -> None:
        captures = self.paired()
        captures[-1]["metadata"]["content"]["diagnostics_enabled"] = True
        result = analyze.compare_runs(captures, "control", "traced")
        self.assertEqual(result["status"], "not_comparable")
        self.assertIn("traced: missing or inconsistent diagnostics_enabled within the series", result["problems"])

    def test_diagnostic_overhead_holds_tracing_fixed(self) -> None:
        captures = self.paired()
        for capture in captures:
            content = capture["metadata"]["content"]
            content["diagnostics_enabled"] = content["run_name"] == "traced"
            content["trace_enabled"] = content["named_events_enabled"] = True
            content["trace_channels"] = "cpu,frame,task,gpu"
        comparison = analyze.compare_runs(captures, "control", "traced", "diagnostics")
        self.assertEqual(comparison["status"], "comparable")
        self.assertEqual(comparison["comparison_kind"], "diagnostics")
        self.assertEqual(comparison["warmed_phase_overhead"]["burst"]["frame_ms"]["p95_ms"]["traced_minus_control_ms"], 1)
        for capture in captures[4:]:
            capture["metadata"]["content"]["named_events_enabled"] = False
        comparison = analyze.compare_runs(captures, "control", "traced", "diagnostics")
        self.assertEqual(comparison["status"], "not_comparable")
        self.assertIn("Diagnostics comparison must keep named_events_enabled unchanged", comparison["problems"])

    def test_engine_graphics_and_prop_pose_are_comparison_identity(self) -> None:
        for key in ("engine", "sg.PostProcessQuality"):
            captures = self.paired()
            captures[-1]["metadata"]["content"][key] = "changed"
            self.assertEqual(analyze.compare_runs(captures, "control", "traced")["status"], "not_comparable")
        captures = self.paired()
        captures[-1]["metadata"]["content"]["props_before"][0]["scale"] = "X=2 Y=2 Z=2"
        self.assertEqual(analyze.compare_runs(captures, "control", "traced")["status"], "not_comparable")

    def test_launch_manifests_catch_dirty_runtime_difference_at_same_commit(self) -> None:
        captures = self.paired()
        manifests = []
        for name, traced in (("control", False), ("traced", True)):
            manifests.append({"path": f"{name}-launch.json", "content": {
                "name": name, "candidate_commit": "fixed", "workload_identity": "fixed",
                "dll_sha256": "same-dll", "source_hashes": {"code.cpp": "same-source"},
                "asset_config_hashes": {"map.umap": "same-map"}, "map_sha256": "same-map",
                "engine_build": {"version": "same-engine"}, "trace": traced,
                "named_events": traced, "diagnostics": False}})
        comparison = analyze.compare_runs(captures, "control", "traced", launch_manifests=manifests)
        self.assertEqual(comparison["launch_verification"]["status"], "verified")
        self.assertEqual(comparison["status"], "comparable")
        manifests[-1]["content"]["dll_sha256"] = "other-dll"
        comparison = analyze.compare_runs(captures, "control", "traced", launch_manifests=manifests)
        self.assertEqual(comparison["status"], "not_comparable")
        self.assertIn("Launch manifests disagree on dll_sha256", comparison["launch_verification"]["problems"])

    def test_reset_respawn_names_do_not_change_intended_layout(self) -> None:
        captures = self.paired()
        for capture in captures:
            content = capture["metadata"]["content"]
            for phase in ("props_before", "props_after"):
                content[phase][0]["actor"] = f"/Game/Test.RespawnedActor_{content['run_index']}"
            capture["prop_workload"] = analyze.prop_workload(content)
        self.assertEqual(analyze.compare_runs(captures, "control", "traced")["status"], "comparable")
        content = captures[-1]["metadata"]["content"]
        content["props_before"].append({**content["props_before"][0], "actor": "/Game/Test.ExtraActor"})
        self.assertEqual(analyze.compare_runs(captures, "control", "traced")["status"], "not_comparable")

    def test_camera_drift_invalidates_comparison_without_losing_phase_metrics(self) -> None:
        rows = [sample(time) for time in (-4, 0.1, 0.6, 3.1, 10.1)]
        valid = self.capture("camera-valid", rows, metadata())
        drifted = self.capture("camera-drifted", rows, {**metadata(), "camera_rotation_after": "P=-2 Y=120 R=0"})
        self.assertFalse(drifted["comparison_eligible"])
        self.assertEqual(drifted["validity"]["camera"]["status"], "invalid")
        self.assertEqual(drifted["phases"], valid["phases"])
        self.assertEqual(drifted["dp01_phases"], valid["dp01_phases"])
        self.assertTrue(any("drifted" in issue for issue in drifted["validity"]["camera"]["issues"]))
        captures = self.paired()
        captures[0] = drifted  # Three warm controls remain, but a rejected cold run must not be hidden.
        result = analyze.compare_runs(captures, "control", "traced")
        self.assertEqual(result["status"], "not_comparable")
        self.assertEqual(len(result["camera_failures"]), 1)

    def test_camera_tolerance_checks_intended_pose_and_endpoint_drift(self) -> None:
        content = metadata()
        content["camera_location_after"] = "X=-550.05 Y=-600 Z=172"
        content["camera_rotation_after"] = "P=-2 Y=450 R=0"
        self.assertEqual(analyze.camera_validity(content)["status"], "valid")
        content["camera_rotation"] = "P=-1.96 Y=90 R=0"
        content["camera_rotation_after"] = "P=-2.04 Y=90 R=0"
        self.assertEqual(analyze.camera_validity(content)["status"], "invalid")
        content["camera_rotation"] = content["camera_rotation_after"] = "P=-2 Y=0 R=0"
        self.assertTrue(any("intended camera" in issue for issue in analyze.camera_validity(content)["issues"]))

    def test_camera_missing_after_is_invalid_only_for_automatic_v2(self) -> None:
        rows = [sample(time) for time in (-4, 0.1, 0.6, 3.1, 10.1)]
        content = metadata()
        del content["camera_location_after"]
        del content["camera_rotation_after"]
        self.assertFalse(self.capture("v2-no-after", rows, content)["comparison_eligible"])
        legacy = self.capture("v1-no-after", rows, {**content, "schema": "DestructionPerf01-v1"})
        self.assertTrue(legacy["comparison_eligible"])
        self.assertEqual(legacy["validity"]["camera"]["status"], "unverified_legacy_or_manual")

    def test_comparison_uses_camera_tolerance_not_exact_float_strings(self) -> None:
        captures = self.paired()
        captures[-1]["metadata"]["content"]["camera_location"] = "X=-550.01 Y=-600 Z=172"
        captures[-1]["metadata"]["content"]["camera_rotation"] = "P=-2.01 Y=90 R=0"
        self.assertEqual(analyze.compare_runs(captures, "control", "traced")["status"], "comparable")

    def test_output_is_fresh_and_inside_saved(self) -> None:
        self.assertEqual(analyze.output_path_checked(str(self.directory / "new.json")), self.directory / "new.json")
        existing = self.directory / "existing.json"
        existing.write_text("{}", encoding="utf-8")
        for path in (existing, analyze.PROJECT_ROOT / "out.json", self.directory / "out.csv"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                analyze.output_path_checked(str(path))


if __name__ == "__main__":
    unittest.main()
