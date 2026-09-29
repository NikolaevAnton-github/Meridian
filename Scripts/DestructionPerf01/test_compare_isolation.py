#!/usr/bin/env python3
"""DP-02 exact-evidence, pairing and false-attribution regression checks."""

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
import compare_isolation as isolation
from test_analyze import metadata, sample


class IsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        analyze.SAVED_ROOT.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="dp02-compare-test-", dir=analyze.SAVED_ROOT)
        self.directory = Path(self.temporary.name)
        self.captures = []
        self.manifests = []
        for name, mode, durations in (("control", "reference", (100, 9, 10, 11)),
                                      ("candidate", "profile_observe", (200, 7, 8, 9))):
            for index, duration in enumerate(durations, 1):
                content = metadata(name, index)
                content["isolation_mode"] = mode
                content["diagnostics_enabled"] = True
                hooked = mode == "profile_observe"
                content["isolation_before"] = {"mode": mode, "native_hook_installed": hooked,
                                                "configured_props": 26, "pending_transactions": 0,
                                                "suppressed_vendor_collision_bindings": 0,
                                                **{key: 0 for key in isolation.ISOLATION_COUNTERS}}
                content["isolation_after"] = {"mode": mode, "native_hook_installed": hooked,
                                               "configured_props": 26, "pending_transactions": 0,
                                               "suppressed_vendor_collision_bindings": 0,
                                               **{key: 25 if hooked else 0 for key in isolation.ISOLATION_COUNTERS}}
                rows = [sample(timestamp, duration, diagnostic_sample=flag, gc_active_transforms=10,
                               observed_transform_activations=5, audio_active_sources=1)
                        for timestamp, flag in ((-4, 1), (0.1, 1), (0.2, 0), (0.6, 1), (3.1, 1), (10.1, 1))]
                path = self.directory / f"{name}{index}.csv"
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                path.with_suffix(".json").write_text(json.dumps(content), encoding="utf-8")
                self.captures.append(analyze.analyze_capture(path))
            path = self.directory / f"{name}-launch.json"
            launch = {
                "name": name, "isolation_mode": mode, "candidate_commit": "fixed", "workload_identity": "fixed",
                "source_hashes": {"code.cpp": "same-source", "other.cpp": "same-other"},
                "dll_sha256": "same-dll", "asset_config_hashes": {"map.umap": "same-map"},
                "map_sha256": "same-map", "engine_build": {"major": 5, "minor": 8}, "executable": "UnrealEditor.exe",
                "trace": False, "named_events": False, "diagnostics": True,
                "arguments": ["MeridianSquad.uproject", "-game", f"-DestructionPerfAuto={name}",
                              f"-abslog=Saved/{name}.log", "-DestructionPerfCommit=fixed",
                              "-DestructionPerfEvidence=DP-02", f"-DestructionPerfIsolation={mode}"],
            }
            path.write_text(json.dumps(launch), encoding="utf-8")
            self.manifests.append(isolation.read_manifest(path))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def compare(self, **kwargs: object) -> dict:
        options = {"allowed_metadata_fields": ("isolation_mode",),
                   "allowed_launch_arguments": ("-DestructionPerfIsolation=reference",
                                                "-DestructionPerfIsolation=profile_observe")}
        options.update(kwargs)
        return isolation.compare_isolation(self.captures, self.manifests, "control", "candidate",
                                           "profile-call observation", **options)

    def test_warm_pairs_do_not_pool_cold_or_frames_or_claim_equivalence(self) -> None:
        report = self.compare()
        self.assertEqual(report["problems"], [])
        self.assertEqual(report["status"], "identity_verified")
        metric = report["warm_phase_differences"]["burst"]["frame_ms"]["p95_ms"]
        self.assertEqual(metric["control"]["values_in_run_order"], [9, 10, 11])
        self.assertEqual(metric["candidate"]["values_in_run_order"], [7, 8, 9])
        self.assertEqual(metric["candidate_minus_control_median_ms"], -2)
        self.assertEqual(metric["paired_delta_variability_ms"]["values_in_run_order"], [-2, -2, -2])
        self.assertFalse(metric["absolute_median_shift_exceeds_larger_observed_run_range"])
        self.assertFalse(metric["observed_ranges_do_not_overlap"])
        self.assertFalse(report["equivalent_destruction_verified"])
        self.assertFalse(report["causal_improvement_verified"])
        self.assertEqual(report["series"]["control"]["first_process_blast"]["phase_metrics_ms"]
                         ["burst"]["frame_ms"]["p95_ms"]["median_of_run_values"], 100)

    def test_damage_and_diagnostic_samples_are_independent_observations(self) -> None:
        report = self.compare()
        observed = report["series"]["candidate"]["warm_observations"]
        self.assertEqual(observed["damaged_actor_observations"]["newly_root_broken_props"]["values_in_run_order"], [1, 1, 1])
        self.assertEqual(observed["damaged_actor_observations"]["props_with_break_notifications"]["values_in_run_order"], [1, 1, 1])
        self.assertEqual(observed["phase_diagnostic_observation_counts"]["burst"]["values_in_run_order"], [1, 1, 1])
        self.assertEqual(self.captures[-1]["dp01_phases"]["burst"]["frame_count"], 2)

    def test_fewer_damaged_actors_remains_an_explicit_unverified_outcome(self) -> None:
        changed = self.captures[-1]
        content = changed["metadata"]["content"]
        content["props_after"][0].update({"root_broken": False, "break_events": 0})
        changed["prop_workload"] = analyze.prop_workload(content)
        report = self.compare()
        self.assertEqual(report["status"], "identity_verified")
        self.assertEqual(report["series"]["candidate"]["warm_observations"]["damaged_actor_observations"]
                         ["newly_root_broken_props"]["values_in_run_order"], [1, 1, 0])
        self.assertFalse(report["equivalent_destruction_verified"])

    def test_missing_phase_is_not_silently_dropped(self) -> None:
        self.captures[-1]["comparison_eligible"] = False
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertNotIn("warm_phase_differences", report)
        self.assertIn("candidate: incomplete/invalid captures cannot be silently excluded", report["problems"])

    def test_two_warm_runs_do_not_pass_three_run_requirement(self) -> None:
        self.captures = [c for c in self.captures if c["metadata"]["content"]["run_index"] != 4]
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertFalse(report["has_at_least_three_warmed_runs_per_series"])

    def test_duplicate_and_mismatched_ordinals_are_rejected(self) -> None:
        self.captures[-1]["metadata"]["content"]["run_index"] = 3
        report = self.compare()
        self.assertIn("candidate: duplicate run indices", report["problems"])
        self.assertIn("Warm repeat ordinals differ; exact ordinal pairing is required", report["problems"])

    def test_smaller_blast_and_changed_layout_cannot_be_exempted(self) -> None:
        self.captures[-1]["metadata"]["content"]["blast_radius_cm"] = 1
        self.captures[-1]["metadata"]["content"]["props_before"][0]["data_asset"] = "SmallerDerivative"
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertFalse(report["intended_prop_layout_matches"])
        with self.assertRaises(ValueError):
            self.compare(allowed_metadata_fields=("isolation_mode", "blast_radius_cm"))

    def test_dirty_dll_at_same_commit_invalidates_runtime_comparison(self) -> None:
        self.manifests[-1]["content"]["dll_sha256"] = "other-dll"
        report = self.compare()
        self.assertIn("Undeclared launch identity difference: dll_sha256", report["problems"])

    def test_declared_derivative_records_exact_source_and_binary_changes(self) -> None:
        launch = self.manifests[-1]["content"]
        launch["source_hashes"]["code.cpp"] = "other-source"
        launch["dll_sha256"] = "other-dll"
        report = self.compare(allowed_source_files=("code.cpp",))
        self.assertEqual(report["status"], "identity_verified")
        self.assertEqual(report["source_changes"]["code.cpp"], {"control": "same-source", "candidate": "other-source"})
        launch["source_hashes"]["other.cpp"] = "undeclared-source"
        self.assertEqual(self.compare(allowed_source_files=("code.cpp",))["status"], "not_comparable")

    def test_declarations_must_describe_actual_changes(self) -> None:
        report = self.compare(allowed_source_files=("code.cpp",))
        self.assertEqual(report["status"], "not_comparable")
        report = self.compare(allowed_metadata_fields=("isolation_mode", "unused_diagnostic_flag"))
        self.assertIn("Declared metadata factor did not differ: unused_diagnostic_flag", report["problems"])

    def test_unknown_launch_flag_cannot_silently_change_work(self) -> None:
        self.manifests[-1]["content"]["arguments"].append("-nosound")
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertIn("-nosound", report["launch_argument_changes"]["added"])

    def test_reordered_flags_are_not_assumed_semantically_equivalent(self) -> None:
        arguments = self.manifests[-1]["content"]["arguments"]
        arguments[0], arguments[1] = arguments[1], arguments[0]
        self.assertIn("Unchanged launch arguments must retain exact order and multiplicity", self.compare()["problems"])

    def test_unhooked_reference_counters_are_unavailable_not_zero(self) -> None:
        report = self.compare()
        observed = report["series"]["control"]["warm_observations"]["isolation_counter_deltas"]["profile_calls"]
        self.assertEqual(observed["run_count"], 0)
        self.assertIsNone(observed["median_of_run_values"])
        candidate = report["series"]["candidate"]["warm_observations"]["isolation_counter_deltas"]["profile_calls"]
        self.assertEqual(candidate["values_in_run_order"], [25, 25, 25])

    def test_launcher_capture_factor_mismatch_and_missing_manifest_fail(self) -> None:
        self.manifests[-1]["content"]["isolation_mode"] = "reference"
        report = self.compare()
        self.assertIn("candidate: capture/launcher mismatch for isolation_mode", report["problems"])
        self.manifests.pop()
        self.assertIn("Missing launch manifest: candidate", self.compare()["problems"])

    def test_instrumentation_must_be_identical(self) -> None:
        for capture in self.captures[4:]:
            capture["metadata"]["content"]["trace_enabled"] = True
        self.manifests[-1]["content"]["trace"] = True
        report = self.compare()
        self.assertIn("Undeclared metadata identity difference: trace_enabled", report["problems"])

    def test_missing_gpu_pairs_do_not_emit_above_noise_flags(self) -> None:
        self.captures[-1]["dp01_phases"]["burst"]["coarse_non_additive_counters"]["gpu_ms"] = analyze.distribution([])
        report = self.compare()
        metric = report["warm_phase_differences"]["burst"]["gpu_ms"]["p95_ms"]
        self.assertFalse(metric["complete_warm_metric_pairs"])
        self.assertIsNone(metric["absolute_median_shift_exceeds_larger_observed_run_range"])
        self.assertEqual(metric["paired_delta_variability_ms"]["run_count"], 2)

    def test_unrequested_capture_cannot_be_silently_ignored(self) -> None:
        extra = copy.deepcopy(self.captures[-1])
        extra["metadata"]["content"]["run_name"] = "other"
        self.captures.append(extra)
        self.assertIn("Captures outside the requested pair were supplied", self.compare()["problems"])

    def test_rejected_observe01_installed_hook_with_zero_calls_is_not_exercised(self) -> None:
        # Preserve the relevant failed dp02_observe01 metadata pattern without
        # depending on local Saved evidence being present on another checkout.
        for capture in self.captures[4:]:
            snapshot = capture["metadata"]["content"]["isolation_after"]
            snapshot.update({"native_hook_installed": True, "configured_props": 26,
                             "profile_calls": 0, "requested_bone_ids": 0})
        report = self.compare()
        self.assertEqual(report["status"], "not_comparable")
        self.assertIn("diagnostic_switch_not_exercised", report["problems"])
        self.assertNotIn("warm_phase_differences", report)
        self.assertEqual([item["status"] for item in report["diagnostic_switch_liveness"]],
                         ["verified"] * 4 + ["not_exercised"] * 4)

    def test_known_mode_requires_native_snapshots_and_expected_hook_state(self) -> None:
        del self.captures[-1]["metadata"]["content"]["isolation_after"]
        self.captures[0]["metadata"]["content"]["isolation_before"]["native_hook_installed"] = True
        report = self.compare()
        self.assertIn("diagnostic_switch_not_exercised", report["problems"])
        self.assertIn("Missing isolation_after snapshot", report["diagnostic_switch_liveness"][-1]["problems"])
        self.assertEqual(report["diagnostic_switch_liveness"][0]["status"], "not_exercised")

    def test_old_positive_counts_without_new_target_work_do_not_prove_liveness(self) -> None:
        content = self.captures[-1]["metadata"]["content"]
        content["isolation_before"]["profile_calls"] = content["isolation_after"]["profile_calls"]
        self.assertIn("diagnostic_switch_not_exercised", self.compare()["problems"])

    def test_batch_requires_transactions_and_drained_boundaries(self) -> None:
        capture = copy.deepcopy(self.captures[-1])
        content = capture["metadata"]["content"]
        content["isolation_mode"] = "profile_batch"
        for key in ("isolation_before", "isolation_after"):
            content[key]["mode"] = "profile_batch"
        self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "verified")
        for key, value in (("profile_transactions", 0), ("committed_transactions", 0), ("pending_transactions", 1)):
            failed = copy.deepcopy(capture)
            failed["metadata"]["content"]["isolation_after"][key] = value
            with self.subTest(field=key):
                self.assertEqual(isolation.diagnostic_switch_liveness(failed)["status"], "not_exercised")
        content["isolation_before"]["pending_transactions"] = 1
        self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "not_exercised")

    def test_collision_suppression_must_be_observed_with_no_profile_hook(self) -> None:
        capture = copy.deepcopy(self.captures[0])
        content = capture["metadata"]["content"]
        content["isolation_mode"] = "collision_off"
        for key in ("isolation_before", "isolation_after"):
            content[key]["mode"] = "collision_off"
            content[key]["suppressed_vendor_collision_bindings"] = 26
        self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "verified")
        content["isolation_after"]["suppressed_vendor_collision_bindings"] = 0
        self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "not_exercised")
        content["isolation_after"]["suppressed_vendor_collision_bindings"] = 26
        content["isolation_after"]["native_hook_installed"] = True
        self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "not_exercised")

    def bridge_capture(self, mode: str) -> dict:
        capture = copy.deepcopy(self.captures[0])
        content = capture["metadata"]["content"]
        content["isolation_mode"] = mode
        relayed = mode in ("profile_observe", "profile_batch")
        for field, events in (("isolation_before", 0), ("isolation_after", 25)):
            content[field] = {
                "mode": mode, "diagnostic_implementation": isolation.BRIDGE_IMPLEMENTATION,
                "configured_props": 26, "setup_failed": False, "setup_failures": 0,
                "prop_bindings": [{"component": f"GC{index}", "break_bridge_installed": relayed}
                                  for index in range(26)],
                "break_events_received": events if relayed else 0,
                "break_events_forwarded": events if relayed else 0,
                "break_events_queued": events if mode == "profile_batch" else 0,
                "pending_break_events": 0, "flushes_with_work": 1 if events else 0,
                "profile_batch_calls": 1 if mode == "profile_batch" and events else 0,
                "profile_batch_bone_ids": events if mode == "profile_batch" else 0,
                "suppressed_vendor_collision_bindings": 26 if mode == "collision_off" else 0,
            }
        return capture

    def test_versioned_bridge_modes_have_independent_liveness(self) -> None:
        for mode in isolation.KNOWN_ISOLATION_MODES:
            with self.subTest(mode=mode):
                result = isolation.diagnostic_switch_liveness(self.bridge_capture(mode))
                self.assertEqual(result["status"], "verified", result["problems"])
                self.assertEqual(result["diagnostic_implementation"], isolation.BRIDGE_IMPLEMENTATION)

    def test_bridge_observe_requires_complete_forwarding_without_batching(self) -> None:
        for key, value in (("break_events_received", 0), ("break_events_forwarded", 24),
                           ("break_events_queued", 1), ("profile_batch_calls", 1), ("pending_break_events", 1)):
            capture = self.bridge_capture("profile_observe")
            capture["metadata"]["content"]["isolation_after"][key] = value
            with self.subTest(field=key):
                self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "not_exercised")

    def test_bridge_batch_requires_preapply_counts_and_drained_forwarding(self) -> None:
        for key, value in (("break_events_queued", 0), ("break_events_forwarded", 24),
                           ("profile_batch_calls", 0), ("profile_batch_bone_ids", 0), ("pending_break_events", 1)):
            capture = self.bridge_capture("profile_batch")
            capture["metadata"]["content"]["isolation_after"][key] = value
            with self.subTest(field=key):
                self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "not_exercised")

    def test_bridge_setup_requires_all_props_and_matching_known_version(self) -> None:
        for mutation in ("setup", "missing_prop", "unbridged_prop", "unknown_tag", "mismatched_tag"):
            capture = self.bridge_capture("profile_observe")
            content = capture["metadata"]["content"]
            after = content["isolation_after"]
            if mutation == "setup":
                after["setup_failed"], after["setup_failures"] = True, 1
            elif mutation == "missing_prop":
                after["prop_bindings"].pop()
            elif mutation == "unbridged_prop":
                after["prop_bindings"][0]["break_bridge_installed"] = False
            elif mutation == "unknown_tag":
                for field in ("isolation_before", "isolation_after"):
                    content[field]["diagnostic_implementation"] = "unknown_v2"
            else:
                del after["diagnostic_implementation"]
            with self.subTest(mutation=mutation):
                self.assertEqual(isolation.diagnostic_switch_liveness(capture)["status"], "not_exercised")

    def test_bridge_counters_do_not_claim_original_native_profile_calls(self) -> None:
        content = self.bridge_capture("profile_batch")["metadata"]["content"]
        counters = isolation.isolation_observations(content)["counters"]
        self.assertEqual(counters["break_events_forwarded"]["observed_delta"], 25)
        self.assertEqual(counters["profile_batch_calls"]["observed_delta"], 1)
        self.assertEqual(counters["profile_batch_bone_ids"]["observed_delta"], 25)
        self.assertFalse(counters["profile_calls"]["available"])
        reference = self.bridge_capture("reference")["metadata"]["content"]
        self.assertFalse(isolation.isolation_observations(reference)["counters"]["break_events_received"]["available"])

    def test_cli_keeps_exact_evidence_hashes_and_refuses_overwrite(self) -> None:
        output = self.directory / "report.json"
        command = [sys.executable, str(Path(isolation.__file__)),
                   *(capture["capture_path"] for capture in self.captures),
                   "--control-run", "control", "--candidate-run", "candidate", "--factor", "profile observation",
                   "--allow-metadata-field", "isolation_mode",
                   "--allow-launch-argument=-DestructionPerfIsolation=reference",
                   "--allow-launch-argument=-DestructionPerfIsolation=profile_observe",
                   "--launch-manifest", self.manifests[0]["path"],
                   "--launch-manifest", self.manifests[1]["path"], "--output", str(output)]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["comparison"]["status"], "identity_verified")
        self.assertEqual([capture["capture_sha256"] for capture in report["captures"]],
                         [capture["capture_sha256"] for capture in self.captures])
        original = output.read_bytes()
        repeated = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(repeated.returncode, 2)
        self.assertIn("Refusing to overwrite", repeated.stderr)
        self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
