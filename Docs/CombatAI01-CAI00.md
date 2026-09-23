# MSQ-102 / CAI-00: baseline, contracts and observability

Prepared 2026-09-23. Executor candidate **Candidate01/build02**. Verification is
native Development Editor build, focused source comparison and pure C++ value-contract
checks. Gameplay, motion, audibility and performance remain **PENDING OWNER**.
Independent technical review and controller acceptance/closure are separate.

## Baseline and preservation

The incoming source HEAD is `288f44d3a313a9d6801c858ac74076d2cd6c7fd9`.
All 14 native source files and the DLL matched MSQ-70 Candidate01/build03's manifest
`Saved/CombatSlice01/EnemyCombat01/Candidate01-identity.json`, whose SHA256 is
`819c58d5f9faf218c6667cc22d5887ee284ae4de2343e4c88dd8aa570843438b`.
Incoming DLL SHA256: `708488a78ab329bba2ac444a17972b85c533dd162dc6249dc8984783b1b1e95e`.
Candidate output identities are in `Worker/Candidate01/candidate-manifest.json` under
`Saved/CombatAI01/CAI-00/` (the evidence root used throughout this report).

UE **5.8.3-58210709**, Win64 Development Editor, retained map
`/Game/Maps/L_OpeningLobby_PainterStone01`. The live pre-build check found no PIE and
no dirty packages. Default Play mode is one profile-1 GASP opponent; three passive
profiles remain an explicit console option. There was no active gameplay test mode
because no Play session ran. No FPS limit, performance sample or run gait was measured.

Pre-existing owner edits to `Config/DefaultEngine.ini`, `MeridianSquad.uproject` and
the retained map match the controller preservation hashes. Controller edits in
AGENTS, ProjectState, task/index and approval files were left to the controller.
No content assets or sources were changed. Native execution is Astra/high/default,
fast mode disabled, as recorded in the controller's native process and turn-context
evidence. No delegates were dispatched and no commit/status administration was performed.

## What exists and what the owner reported

| Observed source fact | Consequence / boundary |
| --- | --- |
| Sight range 2400 cm, half-angle 100 degrees, interval .12 world s; successful range/FOV/occlusion query alone updates remembered ground/aim | No hearing, damage awareness or near-miss knowledge producer exists in this policy |
| Navigation follower calls `SetMovementCommand(..., true)` | Requests walking; non-walk bridge capability is not proof of a demonstrated run gait |
| Last sight expires after 4 world s; pursuit/return have 12 s bounds | Finite search and return, not persistent hunting |
| `StartReturn` clears memory and applies 5 s sight suppression; obstruction budget is 3 attempts / 6 s, unsettled aim bound 6 s | Source-backed routes by which the enemy can stop pursuing despite recent contact |
| Local navigation uses one floor layer, 2800 cm home radius, 80 cm cells, 1200 expansions, at most 16 nodes per frame and a 1.5 ms boundary between nodes | Bounded algorithm, not measured frame cost or demonstrated reachability; query work per node can exceed the boundary |
| 12-round enemy magazine, 3-round bursts, .18 s shot interval, 1.1 s burst pause, 2.6 s timed reload, unlimited reserve, Ready reload pose | Existing weapon policy retained; no moving-fire or reload-animation claim |
| Bullet speed 14000 cm/s, damage 10, spread .6 degrees; acquire/aim .65 s, attack range 1000 cm | Values unchanged; the requested per-agent seeding changes the spread sequence |

The owner reported weakness, no running and easy loss of the player. Walking and
memory-clearing return are supported explanations from source. The exact trigger in
the owner's session (memory expiry, path failure, obstruction or unsettled aim) was
not captured, so selecting one as the observed cause would be a hypothesis. The new
trace distinguishes these paths on the next owner run. Group lanes, multi-enemy
combat/performance, persistent search and hearing remain later packages.

## Interface inventory and ownership

| Interface | Actual contract |
| --- | --- |
| `UEnemyCombatComponent::AdvanceCombat` | Called by fixture tick before foundation input; component has no independent tick, timer/controller or alternate pawn |
| `AGASPEnemyFixture::SetMovementCommand`, `StopMovementCommand`, `GetMovementIntent` | Normalized direction and explicit walk flag; intent suppressed outside ready, living Locomotion |
| `AGASPEnemyFixture::ProduceInput_Implementation` / `UpdateRifleInput` | Single fixture bridge registered with Mover, delegates adopted GASP input producers and repairs physical handover; AI supplies commands through this bridge, never actor teleport/movement |
| `SetRifleStance`, `SetRifleAimTarget`, `SetRifleFollowPlayer`, `SetCrouchCommand`, `SetHandOccupancy` | Relax/Ready/Aim, independent aim, actual crouch and hand capability seams; autonomous combat disables privileged follow-player aim |
| `SetAuthority`, `SuspendForPhysics`, `StopCombat`, `ResetCombat` | Death and physical authority cancel movement/fire first. Recovery/Falling/Down/GettingUp own physical motion. Locomotion return clears old path and reacquires from actual feet. Ordinary recovery retains valid sight memory; death clears it |
| `CanShoot`, `Fire` | Living Locomotion, held/right-hand weapon, settled aim animation, low movement alpha, alignment and two swept muzzle corridors; fresh sight rechecked at birth |
| `ACombatProjectileWorld::Launch`, `BuildQuery`, `ResolveHit`, `OnBulletHit` | Finite-flight shared collision/contact ordering; point damage or physical target `ReceiveBullet`; character collision uses custom sweeps. Current corridor query does not prove safe teammate lanes |
| `AGASPEnemyFixture::ReceiveBullet` / `APhysicsControlDummy::ReceiveBullet` | Physical hit/death/recovery authority; does not update tactical awareness |
| `AOpeningLobbyCharacter::TakeDamage`, `ResetCombatReceiver` | Player hit/damage counters; no player health/death acceptance |
| `UCombatRifleComponent` / `ClearTransientFeedback` | Owns player ammunition/cadence/reload transaction; F6 binding reaches manager reset, which clears feedback without ammunition assignment |
| `ResetTargets`, `SetEnemyCombatMode`, `SetPhysicsDummyEnabled` | Retained lifecycle and passive-mode toggle; reset advances encounter generation before resetting fixtures |

Time remains world/bullets/rifle cadence **0.25**, hero movement **0.65** during
slowdown. The new capture uses world time; CPU path budgeting remains wall-clock.
This package adds no clock, authority, movement, projectile or damage-policy writer.

## Delivered capture and lifecycle contract

`CombatAIObservation.h` defines schema 1, a plain value `InputSnapshot`, typed events,
a fixed `TraceRing`, the seed function and a separately typed future fairness record.
`EnemyCombatObservation.cpp` adapts current component state to JSON. Snapshots own
their numbers and fixed reason text; they contain no actor handles, target getters,
paths to actors or privileged fairness transforms.

The snapshot includes encounter generation, seed/spawn index/agent seed, world time
and frame delta, own feet/home, last legitimately observed ground/aim/time/event ID,
legacy state/physical authority, memory/visibility, readiness/weapon capabilities,
magazine/shots/spread-stream state, deadlines and path outcome/counts. Without memory,
the new snapshot zeroes known positions and hides old sight metadata. Successful sight
event IDs are local to `(generation, spawn_index)`; event occurrence and receipt are
the same synchronous `world_time`. `last_seen_world_time` preserves observation age.
Sight and failed-query event types declare provenance; a failed query is not a new
target-position observation. No hidden player transform is read by the capture adapter.

The status fields `alert=legacy_memory_present|legacy_no_memory` deliberately describe
the current finite-memory policy. They are not the proposed independent persistent
encounter alert. `evidence=direct_sight|last_sight|none`, `intent`, `physical_authority`
and `path_outcome` remain separate dimensions in `decision_input` and each trace row.
Path events report planning, ready, following_walk, arrived, failed or canceled, with
bounded failure reasons. Physical authority transitions and state reasons are recorded.

There are **64 entries**, **96 bytes maximum reason storage**, about **21,024 bytes**
of ring storage with the installed compiler. Oldest entries are overwritten; sequence
numbers retain total count. Entries are sampled after perception at its current .12 s
interval and on sight, state, path, shot, stop and physical handover events. Normal
unchanged movement does not append every frame. Continuous sight supplies about
16.7 rows/world second before other events, so this is a short tail, not a full-session
recorder. State/shot messages now go to this ring rather than automatic log output.

`GetCombatState`/`msq.EnemyCombat status` extends the existing JSON with the current
snapshot, bounded tail, seed identity and `tuning_at_status_request`. Tuning is a
status-time snapshot, not historical per-event tuning; keep tuning constant for a
comparison or record each tuning boundary. Existing top-level fields remain legacy
debug data, not the pure decision-input contract.

`msq.EnemyCombat trace` explicitly writes one bounded JSON file per existing fixture
under `Saved/CombatAI01/CAI-00/Traces/`, named by generation, spawn slot and UTC ticks.
There is no automatic disk recorder. Status/export are owner controls; neither was
executed in gameplay by this worker. Manually requested files accumulate until managed
by the owner/controller. The contract does not claim full legacy-policy replay: unsampled
frames, collision/animation inputs and the navigation frontier are not reconstructed.
Identical supplied snapshots/events/seeds reproduce value capture and seed selection;
Chaos, animation and runtime encounter replay are not deterministic claims.

The encounter manager starts at generation 1. F6/`reset` increments it before fixture
reset; old trace storage is cleared and a fresh reset event begins at sequence 1.
The pure ring refuses stale-generation records. Mode changes use the same reset path.
Projectile cancellation keeps its separate existing generation. There is no async AI
event queue in CAI-00; future ingress must additionally reject stale/duplicate evidence
before beliefs change. Direct individual fixture resets clear their ring but are not
a new encounter; successors should use manager reset for encounter lifecycle.

Seed v1 is the fixed integer mix `AgentSeed(encounter_seed, stable_spawn_index)`, with
a 31-bit result for `FRandomStream`. Default encounter seed is **102**; placement loop
slots are **0, 1, 2**, assigned before deferred `FinishSpawning`, independent of actor
names, allocation order, live-actor iteration and generation. Their seeds are
**930522253, 1447358377, 298751569**. F6 retains the configured seed and restarts the
per-agent stream. `msq.EnemyCombat seed N` sets a nonnegative signed-32-bit seed and
resets the current mode. No claim of mathematical collision freedom for all possible
seed/index pairs is made; the actual requested slots and 1024 test slots differ.

`PrivilegedFairnessTrace` is **proposed/unwired**: generation, proposal ID, world time,
actual player/camera transforms, grant/reconsider deadline and debug-only reason.
It is neither a member of decision snapshots/entries nor a policy input; nothing in
CAI-00 produces or consumes it. Later pressure code must use a separate bounded
channel and return only a grant or generic wait deadline to the executor. It must
not turn hidden coordinates or detailed denial reasons into beliefs/routes/aim.
Sound, reports, evidence deduplication, action lifecycles and pressure are not implemented.

## Reusable audio inventory

Read-only asset-registry enumeration found **160 `/Game` audio assets**: 134 SoundWaves
and 26 SoundCues. Full paths are in `audio-inventory.json`. Presence is not proof of
playback, audibility, attenuation quality or event binding; plugin-mounted audio was
not comprehensively enumerated.

| Existing asset under `/Game/InfimaGames/TacticalFPSAnimations/` | Evidence / possible reuse |
| --- | --- |
| `Weapons/AssaultRifle/Audio/Firing/A_TFA_AR_Fire_Single_Cue` | Native enemy `Fire` already plays this at the muzzle, volume .45, pitch follows clamped world dilation |
| `Common/Audio/Foley/A_TFA_Foley_Footsteps_Cue` | Candidate movement cue; asset exists, no native hearing-event connection; current Blueprint playback/audibility not verified |
| `.../Audio/Handling/Foley/A_TFA_AR_AimIn_Cue`, `A_TFA_AR_Handling_Cue`, `A_TFA_AR_Click_Cue` | Existing weapon handling candidates; enemy usage not established |
| `.../Audio/Handling/Magazine/A_TFA_AR_Mag_Insert_Cue`, `A_TFA_AR_Mag_Remove_Full_Cue`, `A_TFA_AR_Mag_Remove_Empty_Cue` and `.../Handling/Bolt/A_TFA_AR_Bolt_Open_Cue`, `A_TFA_AR_Bolt_Close_Cue` | Reload/handling candidates; current enemy timed Ready reload does not bind them |
| `.../Audio/Firing/A_TFA_AR_Fire_Empty_Cue`, `A_TFA_AR_EmptyCasing_Cue`, `A_TFA_AR_Fire_Tail_Long_Cue` | Weapon feedback candidates, not tactical speech |
| `Common/Audio/Foley/A_TFA_Foley_Cloth_Cue` and existing impact cues | Possible physical readability cues; no tactical event contract yet |

No tactical contact/search/reload/ally-response voice set was identified in the
enumerated `/Game` inventory. Existing heal/melee assets do not authorize those enemy
actions. Debug status cannot close the later audible-warning/readability gate.

## Verification and owner route

| Criterion | Result / evidence under `Worker/Candidate01/` |
| --- | --- |
| Incoming source/DLL and exact historical manifest identity | PASS, `baseline-identity.json` |
| Native module compile/link | PASS, `build02.log` (build01 also passed before final capture metadata/export additions) |
| Pure seed stability/distinct test slots, identical full input records, ordered eviction after 1000 events, owned values, reset, stale generation rejection, reason bounds | PASS, actual production header compiled with MSVC C++20 `/W4 /WX`; `pure-test-build.log`, `pure-test.log` |
| Sight query, launch gates, decision policy, finite return and reset behavior preserved except declared instrumentation | PASS, focused source comparisons in `self-check.json` |
| Player rifle/ammo code, physical foundation, rifle animation and slowdown bodies preserved | PASS, `self-check.json` |
| Owner config/project/map bytes | PASS, `preservation-after.json` |
| Fresh native editor load, retained map and no PIE/dirty packages | Recorded in `editor-after.json` and `editor-load-check.json`; no gameplay execution |
| Actual F6 generation/ring/ammo behavior, in-engine trace/export/replay, motion, audio/readability and cost | PENDING OWNER; no runtime or performance PASS inferred from source/build |
| Primary independent review and controller acceptance/commit | Pending controller workflow |

The reusable focused check is `Scripts/CombatAI01/CAI00/check.py`; run from the project
root using the installed UE Python. It compiles/runs `observation_test.cpp` against the
actual production header and performs scoped source/preservation comparisons. It never
starts PIE. `editor_tools.py` registers read-only inventory and guarded lifecycle tools
with official Epic MCP; Rider was used only to bootstrap that registration when the
running editor exposed no generic Python MCP tool. Earlier MSQ-70 lifecycle evidence
was not rewritten. The first reload with `-ExecutePythonScript` exited after running
the script; ordinary startup in `editor-launch02.json`/`editor02.log` is the retained load.

Owner route: Play on the retained lobby; keep default one-enemy mode (or use
`msq.EnemyCombat one`). Obtain `status`/`trace`, break sight behind existing cover,
allow/inflict one hit, then obtain another trace. Press F6 and inspect a final status:
generation must advance, old tail disappear, seed stay constant, and player ammo stay
at its pre-reset amount. `seed 102` restores this candidate's seed and resets; `fixtures`
selects the passive trio. This route diagnoses the reported loss-of-contact problem;
it does not require manually proving source facts or running a variant/benchmark matrix.

Changed native files: `CombatAIObservation.h`, `EnemyCombatObservation.cpp`,
`EnemyCombatComponent.h/.cpp`, `EnemyCombatNavigation.cpp`, `CombatProjectileWorld.h/.cpp`,
`PhysicsControlDummyWorld.cpp`. Added supporting files: this report and
`Scripts/CombatAI01/CAI00/{check.py,observation_test.cpp,editor_tools.py}`. No assets changed.
CAI-01 can consume the snapshot/seed/reset/status seams while replacing the documented
finite-memory policy. It must still implement its own intent/action/running semantics;
this handoff does not dispatch it.
