# GASPALS AI correction: primary technical review

Date: 2026-09-24. Existing work reference: MSQ-121.
Reviewer: the sole primary independent technical reviewer.
Scope: [owner correction request](Approvals/GASPALSAIFix01-OwnerStart01.json), covering audit F1-F5, movement independent of the first shot, firing and reload, and the measured cover-anatomy integration risk.

**Final verdict: PASS for the scoped technical correction, Build07.** GAF-R1 and GAF-R2 are closed. No technical finding remains open. Owner judgment of motion, hit feel and combat quality remains separate.

## Review method and candidate applicability

The reviewer inspected the fourteen changed/new production files and relevant installed UE 5.8 PhysicsControl, skeletal-animation, physics-blend and tick code. Runtime captures were supplied by the controller; the reviewer inspected their contents and independently recomputed the principal movement and barrel metrics. The reviewer did not build, operate the editor, run gameplay, edit production, create tasks, dispatch another reviewer or commit.

Build07 completed successfully in 8.469 seconds. Comparing the current source with the frozen Build06 patch and new source file confirms only two subsequent changes: a `!Points.IsEmpty()` guard preserves the legacy fixture's cover probes, and a comment links the tracked anatomy calibration. The guard does not change the active source path: unavailable source anatomy already rejects the query, and available source anatomy has four points. Build06 runtime evidence therefore applies to the final source. Applicable earlier checks are reused below.

The frozen Build06 DLL SHA-256 is `fda1ce8d4fe5fdc6aa6dd3fe8e7014a30e4715e2073bd8d2c81a570f7bf01906`. Final source/DLL identity is recorded in `Saved/GASPALSAIFix01/final-identity.json`. Controller identity, preservation and closure-commit acceptance remain separate from this technical review.

## Findings and closure

### GAF-R1 - P2: moving cover selection used stale travel distance - CLOSED

The Build02 candidate allowed a scan to finish after moving away from its origin, but still authorized cover transfer using the old `ScanOrigin` distance. Its final route query returned current route length without applying that length to the transfer policy. A candidate originally 300 cm away could therefore remain eligible when its current route exceeded the healthy rifle policy's 450 cm limit.

The correction computes assessment and candidate filtering/scoring distance from current feet. After validating the winning route, it saves actual route length, recomputes the score and rechecks `CoverTransferEligible` before committing the transfer. Source inspection closes the stale-distance authorization defect.

### GAF-R2 - P1: Build02 never primed the localized-hit cache - CLOSED

Build01 still produced four invalid-buffer frames and 120 missing-bone warnings during one localized hit. Build02 rejected all 46 hit frames: body/helper actual tick group was `TG_DuringPhysics`, and cache age reached 35.340862 seconds. Its zero warnings resulted from disabled controls, so that candidate failed review. These failed captures remain preserved.

Installed PhysicsControl reads editable component-space transforms when updating its skeletal cache. UE's parallel evaluation/physics-blend work can temporarily swap that buffer. The source `PreCMCTick` was configured for DuringPhysics and was a prerequisite of CMC, promoting the downstream mesh/helper despite their PrePhysics settings. Pinning only downstream configured groups was insufficient.

The correction pins the input producer before physics and preserves the source producer/CMC/mesh order. The helper samples only a complete, freshly evaluated, nonparallel pose in its actual PrePhysics phase, using the public manual `UpdateTargetCaches`/`UpdateControls` API. Cache elapsed time is accumulated; an unavailable pose may retain the last cache for at most 0.1 world seconds. Beyond that, controls are explicitly disabled and updated to zero their drives. Only still-live local controls can be re-enabled. No global animation CVar or engine modification is used.

Build03 records 47 local-pose frames, zero invalid/deferred frames, a primed cache in all 20 samples and a peak of 15 active drives. The log reports actual body, body-end and helper group 0, fresh evaluation, no parallel evaluation, and 95/95 readable/editable bones. The two-second capture includes five shots; it ends with zero local regions/drives and continued locomotion.

The separate physical capture confirms actual `spine_03` simulation in 17 samples, from 145.323 to 145.813 world seconds, with a changed physical velocity after the impulse. By 146.312 seconds simulation is false, regions/drives are zero and CMC is moving at approximately 180 cm/s. This closes both cache correctness and the earlier risk of a false pass with disabled physical reactions.

## Audit acceptance

| Criterion | Reviewed result |
| --- | --- |
| F1: physical rifle alignment | The existing final spine control applies a bounded correction after removing the previously evaluated additive rotation. It preserves the source graph and both hands, fades for large source turns, and freezes recalibration during local physics. Build06's real `Muzzle` socket capture has 11 shots over 3.004 seconds, 29/29 moving commands, and 0.005997-0.255081 degree barrel error across 26 full-aim samples. The native six-degree launch gate remains. |
| F2: first shot and moving weapon actions | The shot-count gate and weapon-owned stops are removed from direct acquisition, fire and reload. Movement eligibility uses achieved grounding and authority independently of temporary weapon-pose readiness. Build03 records 26 shots and two complete reloads over 12.002 seconds, with 115/115 nonzero movement commands. Its two samples before the first shot already strafe at 43.69 and 137.63 cm/s. All 50 reload samples retain movement commands and positive actual speed. Build05 repeats the chain with 26 shots and two reloads. |
| Reload ownership and loss of sight | The central reload clock advances before cover/evidence policy. Tactical replacement preserves its token/deadline; genuine death, weapon loss, reset and physical-authority handover cancel it. The Build02 occlusion capture preserves action 103 and completes reload 10 to 11 with a 12-round refill after losing sight. Cover/search transitions cannot silently relabel an unfinished reload as a new weapon action. |
| Turn and bounded aim failure | Persistent failed aim now ends the action with a timeout and requests reorientation/retry while useful movement remains eligible. The Build05 changed-target capture records 24 shots and two reloads over 12.020 seconds. It does not establish a cover/lean cycle. |
| F3: enemy footsteps | Active CMC grounding and achieved displacement feed the existing producer. The native world capture records 78 enemy step stimuli. Hearing is queued before the CMC audio early return; source animation retains audible foley ownership without duplicate fallback steps. |
| F4: control lifetime | Control names are copied before destruction, eliminating the owning-array alias. Build06 reset returns ready with zero active local drives/regions and cleared anatomy/cache state. Its log contains no missing-bone, control-destruction or ranged-for ensure messages through teardown. |
| F5: localized physics | Closed by GAF-R2 evidence above. The resulting pose-cache cadence and explicit stale-drive cutoff are reviewed against the installed engine implementation. |
| Launch safety and preservation | Actual current sight, achieved pose/barrel, muzzle corridors, authority, grounded motion, finite magazine/burst/cadence and projectile ownership remain authoritative. No binary asset is changed. Current owner config/project SHA-256 values match `owner-before.json`. |

Historical moving series used the audit sampler's local fallback muzzle point, even though the source rifle has a `Muzzle` socket. Their shot, movement and reload observations remain applicable. The final numerical alignment result above uses the corrected sampler in the new correction script and the real socket; earlier captures and the original audit script remain unchanged.

## Cover anatomy correction

The initial measurement confirmed a source standing head around 134 cm rather than the legacy 170 cm proposal, with corresponding chest/pivot/weapon differences. The intermediate capsule-only crouch estimate also failed comparison: CMC shrinks by 26 cm while the source ready crouch lowers the head by about 43 cm.

The final adapter records actual standing-aim and crouched-ready points in a feet-relative yaw frame after completed source evaluation. Capture excludes lean, local physics and non-locomotion authority; it does not require standing still. Caches survive ordinary weapon transitions and clear on source reset. An unmeasured stance uses the paired source-specific per-point delta documented in the tracked [calibration](../Scripts/CombatAI01/GASPALSFix01/source-anatomy-calibration.json). Once achieved, the live measured stance replaces that estimate. If neither stance is available, source proposals wait for a valid cache.

Protection, firing-lane, lean-proposal and edge-height queries now use these source points. Achieved crouched protection uses current actual bones. Actual lean sweep, socket displacement and launch checks remain required; proposal geometry cannot authorize a shot. Legacy fixtures retain their original fallback proposals.

Build06's five standing points project back to their actual positions within 4.4e-8 cm. The initial crouch estimate differs from the subsequently achieved pose by 0.980-1.294 cm; estimated/actual head heights are 90.421/89.844 cm. The measured crouch flag changes from false to true. This is adequate bounded evidence for the anatomy integration correction, not a claim of exact prediction for every gait.

## Evidence and limits

Primary evidence is under `Saved/GASPALSAIFix01/`:

- `samples-build03-moving-combat.json`, `samples-build03-local-hit.json`, `physical-response-build03.json`, `world-build03-footsteps.json` and `editor-build03.log`.
- `reload-occlusion-build02.json` and `samples-build02-reload-occlusion.json`.
- `samples-build05-moving-combat.json`, `samples-build05-turned-cover.json`, `anatomy-build05-crouch-ready.json` and `anatomy-build05-lean.json`.
- `samples-build06-real-muzzle.json`, `anatomy-build06-standing.json`, `anatomy-build06-crouch-ready.json`, `anatomy-build06-comparison.json`, `reset-build06.json`, `editor-state-build06-after.json`, `editor-build06.log` and the frozen `Build06/` source/identity records.
- Build metadata/logs: `Saved/GASPALSLocomotion01/Worker/build-ai-fix01-build07.*`. Earlier failed hypotheses and captures remain under the same evidence root and `Review/source-investigation-01.md` / `source-investigation-02.md`.

The manual aimed-run capture validates the source running pose and supported ground-motion gate at 500 cm/s with AI disabled. It is not autonomous running-fire evidence. Autonomous moving fire/reload is established by the combat captures.

The lean watcher timed out because the corrected proposals did not offer a valid lean in that experiment. No completed final cover/lean cycle is claimed; the directly affected anatomy comparison passes and actual lean safety is reviewed in source. The wider navigation, dynamic-destruction, full ragdoll/death and performance matrices were not repeated. They are outside this focused correction acceptance.

The completed Build06 diagnostic session has no PIE worlds or dirty packages in its final editor-state record. A subsequently owner-opened editor is outside that capture and was not operated by the reviewer. Owner visual/play acceptance and controller final manifest/commit remain separate.
