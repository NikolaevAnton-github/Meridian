#!/usr/bin/env python3
"""Focused DP-03 identity, counter-conservation and false-attribution checks."""

from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import analyze
import compare_dp03 as dp03
import compare_isolation as isolation
from test_analyze import metadata, sample


class DP03Tests(unittest.TestCase):
    def setUp(self) -> None:
        evidence = analyze.SAVED_ROOT / "DestructionPerf01" / "DP-03"
        evidence.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="compare-test-", dir=evidence)
        self.directory = Path(self.temporary.name)
        self.captures, self.manifests = [], []
        for name, mode, durations in (("control", "observe", (100, 9, 10, 11)),
                                      ("candidate", "native", (200, 7, 8, 9))):
            for index, duration in enumerate(durations, 1):
                content = metadata(name, index)
                content.update({"collision_mode": mode, "notification_mode": "immediate",
                                "dp03_first_five_counter_end_seconds": 5.012})
                content["props_before"] = [self.prop(mode, index, actor, 0) for actor in (0, 1)]
                content["props_after"] = [self.prop(mode, index, actor, 25) for actor in (0, 1)]
                content["dp03_detonation_props"] = copy.deepcopy(content["props_before"])
                content["dp03_first_five_props"] = [self.prop(mode, index, actor, 20) for actor in (0, 1)]
                rows = [sample(timestamp, duration if timestamp < 5 else 1000)
                        for timestamp in (-4, 0, 0.49, 0.5, 2.99, 3, 4.999, 5, 10.1)]
                path = self.directory / f"{name}{index}.csv"
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                path.with_suffix(".json").write_text(json.dumps(content), encoding="utf-8")
                self.captures.append(dp03.analyze_capture(path))
            path = self.directory / f"{name}-launch.json"
            launch = {"name": name, "candidate_commit": "fixed", "workload_identity": "fixed",
                      "source_hashes": {"code.cpp": "same-source"}, "dll_sha256": "same-dll",
                      "asset_config_hashes": {"map.umap": "same-map"}, "map_sha256": "same-map",
                      "engine_build": {"major": 5, "minor": 8}, "executable": "UnrealEditor.exe",
                      "trace": False, "named_events": False, "diagnostics": False,
                      "collision_mode": mode, "notification_mode": "immediate",
                      "arguments": ["MeridianSquad.uproject", "-game", f"-DestructionPerfAuto={name}",
                                    f"-DestructionCollisionMode={mode}", "-DestructionNotificationMode=immediate"]}
            path.write_text(json.dumps(launch), encoding="utf-8")
            self.manifests.append(isolation.read_manifest(path))

    @staticmethod
    def prop(mode: str, index: int, actor: int, breaks: int) -> dict:
        path = f"/Game/Test.Actor{actor}_Generation{index}"
        collection = path + ".GeometryCollection"
        collision = {"mode": mode, "actor": path, "component": collection, "installed": mode != "vendor",
                     "validated": mode != "vendor", "counters_available": mode != "vendor",
                     "validation_reason": "synthetic validated schema", **{key: 0 for key in dp03.COLLISION_COUNTERS}}
        if breaks and mode != "vendor":
            collision.update({"raw_callbacks": breaks * 4, "forwarded_callbacks": breaks * 4 if mode == "observe" else 0,
                              "native_callbacks": breaks * 4 if mode == "native" else 0,
                              "fast_handled_callbacks": breaks * 4 if mode == "native" else 0,
                              "profile_requested": breaks * 3, "profile_applied": breaks,
                              "profile_skipped_identical": breaks * 2,
                              "profile_skipped_setter": breaks * 2 if mode == "native" else 0,
                              "profile_native_calls": breaks if mode == "native" else breaks * 3})
        return {"actor": path, "id": "CopiedVendorId", "data_asset": "/Game/Test.Asset", "ready": True,
                "root_broken": breaks > 0, "break_events": breaks, "reset_generation": index - 1,
                "collision_revision": (index - 1) * 25 + breaks, "collision_policy": collision,
                "notifications": {"mode": "immediate", "actor_path": path, "adapter_path": path + ".NGDIntegration",
                                  "collection_path": collection, "adapter_lifetime_id": index * 2 + actor,
                                  **{key: 0 for key in dp03.NOTIFICATION_COUNTERS}, "raw_break_callbacks": breaks,
                                  "physics_recreating": False,
                                  "published_changes": breaks + 1, "published_batches": breaks + 1, "pending_changes": 0}}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def compare(self, factor: str = "collision") -> dict:
        return dp03.compare_dp03(self.captures, self.manifests, "control", "candidate", factor)

    def modify_mode(self, name: str, kind: str, mode: str) -> None:
        key, flag, _ = dp03.MODES[kind]
        for manifest in self.manifests:
            launch = manifest["content"]
            if launch["name"] == name:
                launch[key] = mode
                launch["arguments"] = [f"-{flag}={mode}" if value.startswith(f"-{flag}=") else value
                                       for value in launch["arguments"]]
        for capture in self.captures:
            content = capture["metadata"]["content"]
            if content["run_name"] != name:
                continue
            content[key] = mode
            for endpoint in ("props_before", "props_after", "dp03_detonation_props", "dp03_first_five_props"):
                for prop in content[endpoint]:
                    if kind == "notification":
                        stats = prop["notifications"]
                        stats["mode"] = mode
                        stats["queued_changes"] = stats["raw_break_callbacks"] if mode == "batch" else 0
                        stats["published_batches"] = 1 + (1 if stats["raw_break_callbacks"] else 0) if mode == "batch" else stats["published_changes"]
                    else:
                        prop["collision_policy"] = self.prop(mode, content["run_index"],
                            prop["notifications"]["adapter_lifetime_id"] % 2, prop["break_events"])["collision_policy"]

    def test_warm_first_five_are_half_open_and_cold_is_separate(self) -> None:
        report = self.compare()
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["status"], "identity_verified")
        metric = report["warm_first_five_differences"]["frame_ms"]["p95_ms"]
        self.assertEqual(metric["control"]["values_in_run_order"], [9, 10, 11])
        self.assertEqual(metric["candidate"]["values_in_run_order"], [7, 8, 9])
        self.assertEqual(metric["candidate_minus_control_median_ms"], -2)
        self.assertFalse(metric["observed_ranges_do_not_overlap"])
        self.assertFalse(metric["absolute_median_shift_exceeds_larger_observed_run_range"])
        self.assertEqual(self.captures[-1]["first_five_seconds"]["frame_count"], 6)
        self.assertEqual(report["series"]["candidate"]["first_five_seconds"]["first_process_blast"]
                         ["metrics_ms"]["frame_ms"]["p95_ms"]["median_of_run_values"], 200)
        self.assertIn("warm_phase_differences", report)
        self.assertFalse(report["equivalent_destruction_verified"])
        self.assertFalse(report["causal_improvement_verified"])

    def test_causal_counts_are_separate_from_noisy_timing_and_exact_window(self) -> None:
        report = self.compare()
        counters = report["series"]["candidate"]["dp03_warm_counter_deltas"]
        self.assertEqual(counters["whole_capture"]["collision_policy.profile_native_calls"]["values_in_run_order"], [50, 50, 50])
        self.assertEqual(counters["first_five_counter_window"]["collision_policy.profile_native_calls"]["values_in_run_order"], [40, 40, 40])
        self.assertEqual(report["dp03_actor_evidence"][-1]["actor_count"], 2)
        self.assertEqual(report["dp03_actor_evidence"][-1]["first_five_counter_window"]["observed_end_seconds"], 5.012)

    def test_notification_single_factor_preserves_required_changes(self) -> None:
        self.modify_mode("candidate", "collision", "observe")
        self.modify_mode("candidate", "notification", "batch")
        report = self.compare("notification")
        self.assertEqual(report["problems"], [])
        counters = report["series"]["candidate"]["dp03_warm_counter_deltas"]["whole_capture"]
        self.assertEqual(counters["notifications.published_changes"]["values_in_run_order"], [50, 50, 50])
        self.assertEqual(counters["notifications.published_batches"]["values_in_run_order"], [2, 2, 2])

    def test_vendor_counters_are_unavailable_not_zero_observations(self) -> None:
        self.modify_mode("control", "collision", "vendor")
        report = self.compare()
        self.assertEqual(report["problems"], [])
        stats = report["series"]["control"]["dp03_warm_counter_deltas"]["whole_capture"]["collision_policy.raw_callbacks"]
        self.assertEqual(stats["run_count"], 0)
        self.assertIsNone(stats["median_of_run_values"])

    def test_mixed_modes_and_undeclared_identity_changes_fail_closed(self) -> None:
        self.modify_mode("candidate", "notification", "batch")
        self.manifests[-1]["content"]["dll_sha256"] = "changed-binary"
        self.captures[-1]["metadata"]["content"]["blast_radius_cm"] = 1
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertNotIn("warm_first_five_differences", report)
        self.assertNotIn("warm_phase_differences", report)
        self.assertTrue(any("notification_mode changed=True" in value for value in report["problems"]))
        self.assertIn("Undeclared launch identity difference: dll_sha256", report["problems"])

    def test_missing_warm_repeat_and_camera_drift_are_rejected(self) -> None:
        self.captures = self.captures[:-1]
        self.assertEqual(self.compare()["status"], "not_comparable")
        content = self.captures[-1]["metadata"]["content"]
        content["camera_location_after"] = "X=0 Y=0 Z=0"
        path = Path(self.captures[-1]["capture_path"])
        path.with_suffix(".json").write_text(json.dumps(content), encoding="utf-8")
        self.captures[-1] = dp03.analyze_capture(path)
        self.assertIn("candidate: incomplete/invalid captures cannot be silently excluded", self.compare()["problems"])

    def test_missing_required_changes_pending_queue_and_callback_drop_are_rejected(self) -> None:
        prop = self.captures[-1]["metadata"]["content"]["props_after"][0]
        prop["notifications"]["published_changes"] -= 1
        prop["notifications"]["pending_changes"] = 1
        prop["collision_policy"]["native_callbacks"] -= 1
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertTrue(any("pending notifications" in value for value in report["problems"]))
        self.assertTrue(any("callback accounting" in value for value in report["problems"]))
        prop["notifications"]["pending_changes"] = 0
        self.assertTrue(any("missing or duplicated" in value for value in self.compare()["problems"]))

    def test_copied_vendor_ids_are_valid_but_lifetime_alias_and_reuse_are_not(self) -> None:
        self.assertEqual(self.compare()["problems"], [])
        props = self.captures[-1]["metadata"]["content"]["props_before"]
        props[1]["notifications"]["adapter_lifetime_id"] = props[0]["notifications"]["adapter_lifetime_id"]
        props[0]["reset_generation"] -= 1
        problems = self.compare()["problems"]
        self.assertTrue(any("duplicate notification lifetime" in value for value in problems))
        self.assertTrue(any("generations did not advance" in value for value in problems))

    def test_missing_counter_and_fallback_are_not_silently_accepted(self) -> None:
        stats = self.captures[-1]["metadata"]["content"]["props_after"][0]["collision_policy"]
        stats.pop("profile_requested")
        self.assertEqual(self.compare()["status"], "not_comparable")
        stats["profile_requested"] = 75
        stats["fallback_callbacks"] = 1
        self.assertTrue(any("fallback or unapplied" in value for value in self.compare()["problems"]))

    def test_native_high_speed_forwarding_is_retained_alongside_fast_path(self) -> None:
        for capture in self.captures:
            content = capture["metadata"]["content"]
            if content["run_name"] != "candidate":
                continue
            for endpoint in ("props_after", "dp03_first_five_props"):
                for prop in content[endpoint]:
                    stats = prop["collision_policy"]
                    forwarded = prop["break_events"]
                    stats["forwarded_callbacks"] = forwarded
                    stats["native_callbacks"] -= forwarded
                    stats["fast_handled_callbacks"] -= forwarded
                    stats["profile_skipped_setter"] -= forwarded
                    stats["profile_native_calls"] += forwarded
        self.assertEqual(self.compare()["problems"], [])

    def test_pending_at_five_seconds_is_accounted_without_faking_a_drained_endpoint(self) -> None:
        self.modify_mode("candidate", "collision", "observe")
        self.modify_mode("candidate", "notification", "batch")
        prop = self.captures[-1]["metadata"]["content"]["dp03_first_five_props"][0]
        prop["notifications"]["published_changes"] -= 2
        prop["notifications"]["pending_changes"] = 2
        self.assertEqual(self.compare("notification")["problems"], [])
        prop["notifications"]["pending_changes"] = 1
        self.assertTrue(any("missing or duplicated" in value for value in self.compare("notification")["problems"]))

    def test_intermediate_counter_window_cannot_use_another_actor_lifetime(self) -> None:
        prop = self.captures[-1]["metadata"]["content"]["dp03_first_five_props"][0]
        prop["notifications"]["adapter_lifetime_id"] += 100
        prop["notifications"]["physics_recreating"] = True
        self.assertTrue(any("lifetime/reset identity" in value for value in self.compare()["problems"]))

    def test_cli_writes_once_and_retains_exact_evidence(self) -> None:
        output = self.directory / "comparison.json"
        args = [sys.executable, str(Path(dp03.__file__)), *(capture["capture_path"] for capture in self.captures),
                "--control-run", "control", "--candidate-run", "candidate", "--factor", "collision",
                "--output", str(output)]
        for manifest in self.manifests:
            args.extend(("--launch-manifest", manifest["path"]))
        completed = subprocess.run(args, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["comparison"]["status"], "identity_verified")
        self.assertEqual(len(report["captures"]), 8)
        self.assertEqual(subprocess.run(args, capture_output=True, text=True, check=False).returncode, 2)


if __name__ == "__main__":
    unittest.main()
