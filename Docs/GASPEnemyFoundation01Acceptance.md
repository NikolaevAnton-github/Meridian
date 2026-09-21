# MSQ-98 Candidate01 controller acceptance

Accepted for the authorized migration scope on 2026-09-21. All three enemy
fixtures now use the GASP physical character with the retained damage, balance,
adaptive steps, physical falling, supported get-up and terminal death paths.
The Development Editor build and six focused executor criteria pass. Independent
review was not dispatched under the [task-specific owner waiver](Approvals/GASPEnemyFoundation01-OwnerStart01.json).
Owner motion/play judgment remains separate.

The immutable [implementation report](GASPEnemyFoundation01.md) and
[executor handoff](GASPEnemyFoundation01Handoff.md) contain the authority table,
interface contract, footage index and detailed evidence applicability. This
separate document records controller acceptance without modifying those frozen
reports. No successor task is dispatched by this acceptance.

## Candidate and evidence acceptance

Evidence root: `Saved/CombatSlice01/GASPEnemyFoundation01/`.

- `Worker/Candidate01/manifest.json`, frozen at 2026-09-21 19:22:35 UTC, SHA-256
  `e08a49765331eb7aa2632ae4261e7ead8fe905121072f93b434d8b47160405ff`.
- `Controller/identity-check01.json` passes all 3,236 identity records: 3,094
  production entries, 141 evidence entries and one implementation ZIP. No manifest
  hash was replaced or rebaselined.
- `Worker/build10.log` records UE 5.8.1 CL 56057345 Development Editor success
  in 14.04 seconds. The controller reuses that build, executor runtime self-checks
  and ZIP integrity result; no duplicate runtime matrix or technical review ran.
- `Worker/final-analysis02.json` covers 13 applicable recordings;
  `Worker/controls-analysis02.json` covers controls and relative slowdown.
  The controller also inspected the final three-fixture frame to confirm rollout
  scope. This is not owner motion acceptance.

| Task criterion | Controller acceptance of executor evidence |
| --- | --- |
| Three-fixture rollout | Final01 shows all three GASP bodies and retained profile slots. Shared behavior is checked on one representative. |
| Movement, hit, recovery and resume | Final01 real rifle hit produces one step and resumed locomotion. Final fall recording includes two interrupted get-ups and 288.9 cm of resumed travel. Pilot09 supplies an unobstructed view of the unchanged upright handover. |
| Displaced leg and successive torso hits | Only the completed 0-3.2 s leg segment of Final01-LegArm is accepted. Pilot08 supplies three successive real torso hits and two steps; the report identifies later changes and the corresponding final coverage. |
| Safety, death and contact | Final fall, death/corpse and blocked recordings plus applicable Pilot11 support-removal evidence cover the affected transitions. Positive arm/trunk Chaos contacts and calibrated foot shapes are recorded. Sampled rows show no competing or uncapped controls. |
| Reset, recreation and slowdown | Final02 establishes 0.085/0.340 s rifle cadence, world/bullets 0.25, net player movement 0.65, F6 ammunition preservation, F10 recreation without orphan pawns, and Ctrl+F7/F8/F9 toggles. |
| Provenance and handoff | Frozen identities, ordinary-speed continuous footage, ownership/interface documentation, source preservation and the scoped registry inventory are present. |

Earlier failed recordings remain preserved and do not count as passing evidence.
In particular, Final01-ControlsSlow does not establish cadence; Final02 does.
The later unfinished hand-disturbance segment of Final01-LegArm does not establish
successful get-up. Reuse of Pilot05/08/09/11 is bounded to the unchanged behavior
identified in the implementation report. Old Manny footage does not verify the
new GASP body. No per-profile comparison matrix was required.

## Asset registry and preservation

The existing `register`, `inspect` and `validate` commands all pass for
`GASPEnemyFoundation01`: **3,018 artifacts, zero asserted dependency edges**.
The asset ID is `e26bdf77-554c-5440-a031-16a471fa1e3d`.
The accepted input is [the tracked registry manifest](../Scripts/AssetRegistry/manifests/GASPEnemyFoundation01.json).
Results are retained as `Controller/registry-register01.json`,
`registry-inspect01.json`, `registry-validate01.json` and `registry-acceptance01.json`.

The existing registry only supports structured `/Game/` package paths. Plugin
artifacts therefore use `unreal_package: null`; exact `/GASPEnemyFoundation01/`
names are retained in each evidence note and in
`Controller/Registry-Candidate01-01/package-inventory.json`. This is file-level
registration, without inferred verified dependency edges or a schema change.
All 3,017 mapped external sources match their migration fingerprints. The new
`PA_MSQ98_Recovery` has no fabricated external-source relationship. Registration
does not independently establish behavior or visual acceptance.

Executor preservation evidence verifies all 3,906 original GASP files unchanged,
the retained map unchanged, the owner's engine-config prefix unchanged and the
owner's project descriptor semantics preserved. Mover is the sole appended
project-level plugin. The source sample, earlier candidates, old Manny/Mixamo
assets and failed probes remain available. The project measured about 45 GB
before the small candidate snapshot, within the 250 GB limit.

The closure commit includes only MSQ-98 changes. The controller stages the scoped
engine-config suffix and Mover addition separately; pre-existing owner config
and plugin edits remain in the working tree. Local index/commit receipts are
retained under `Controller/`. The frozen working candidate intentionally includes
those preserved owner settings; it is not represented as a clean checkout of the
task-only commit.

## Execution and owner handoff

One Multica Unreal execution completed:
`01a0c500-58f1-7069-92fb-14fff8db52c5`. Saved profile and actual native context
confirm Astra/max; native launch arguments set the default service tier and disable
fast mode. The context's null service-tier field alone is not speed evidence.
Profiles were not changed. `Controller/execution-receipt01.json` retains the checks.
A redundant queued run created by the editor-approval comment was cancelled before
execution. The administrative registry helper did not review or edit production.

All capture-owned Play sessions ended and temporary performance settings were
restored. A new active Play session was preserved. The final read-only executor
snapshot records three wrappers/three GASP pawns, no dirty packages, background
throttling true, MaxFPS 0 and no pending harness override. Controller closure does
not stop that Play session or edit the running scene.

Owner controls remain F6 reset without ammunition refill, F10 fixture toggle,
Y relative slowdown, Ctrl+F7 immortality, Ctrl+F8 infinite reserve and Ctrl+F9
bounded recovery assistance. Walking/running uses the command API prepared for
MSQ-70; autonomous perception, pursuit and firing remain later scope.

Recorded limits remain visible: about 0.5-1.3 cm of sole compliance penetration
under disturbance; severe impacts can cause falls; tight lobby walls can stop
resumed movement. The support-loss probe does not accept moving-platform behavior.
Optional MovieSceneAnimMixer remains excluded because of its incompatibility with
the retained purchased-arm AnimBP. WGC footage is approximately 15 FPS with
timestamps preserved. Owner motion/play judgment, MSQ-93 through MSQ-96, MSQ-70,
MSQ-99 and MSQ-100 remain separate.
