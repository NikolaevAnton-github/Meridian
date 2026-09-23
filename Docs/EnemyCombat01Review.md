# EnemyCombat01 independent source review

Date: 2026-09-23. Task: **MSQ-70**. Reviewer: `/root/enemy_combat_source_review`.

**Verdict: PASS_SOURCE_ONLY** for `EnemyCombat01-Candidate01`, built by
`build03.log`. EC70-R1 is closed and no blocking source findings remain.
Gameplay, firing, navigation performance, physical handover and visual acceptance
remain pending owner testing under the
[explicit owner decision](Approvals/EnemyCombat01-OwnerStart02.json).

The review inspected the new combat/navigation/receiver code, the affected
fixture, rifle, projectile, HUD and module deltas, and the executor's build and
source evidence. It did not run a build, editor operation, Play session, shot,
gameplay probe, screenshot, recording, Multica dispatch or service change.
The controller's native execution record confirms Astra/max for this sole primary
reviewer and the executor, with no fast override requested.

## Candidate and build applicability

The candidate manifest is
`Saved/CombatSlice01/EnemyCombat01/Candidate01-identity.json`, SHA256
`819c58d5f9faf218c6667cc22d5887ee284ae4de2343e4c88dd8aa570843438b`.
All 14 reviewed native files and the resulting project DLL match that manifest.
The review records the individual comparisons and build-log identity in
`Saved/CombatSlice01/EnemyCombat01/Review/source-applicability.json`.

`build03.log` records a successful MeridianSquadEditor Win64 Development build
on UE 5.8.3 in 9.37 seconds and includes the final obstruction-budget correction.
`build01.log` retains the initial pointer-deduction and console-macro compilation
failure. `build02.log` is passing evidence for the compile correction before
EC70-R1; it is not used to establish the final corrected candidate's build.

## Source criteria

| Criterion | Review conclusion |
| --- | --- |
| Finite target knowledge | `ObservePlayer` updates target memory only after range, facing and scene-visibility checks. AI does not enable the follow-player rifle seam. Lost sight uses a fixed remembered position and finite search/return policy; `Fire` rechecks visibility at launch. |
| Bounded navigation and failure | The local A* uses grounded capsule clearance and swept edges against Pawn-blocking collision. Planning resumes across frames, with node, expansion, elapsed-time, retry and stuck bounds. Followed edges are checked again. The corrected muzzle-obstruction budget survives Aim/Pursue swaps. No teleport, navigation task queue or map mutation is introduced. |
| Weapon and damage path | Fire requires Locomotion, a held weapon, settled rifle/aim weights, low speed, actual local +Y barrel alignment and both launch-corridor checks. Accepted rounds use the existing finite-flight manager and cover/contact resolution. Fixture/foundation ownership supplies the instigator; own-body launch immunity is bounded by clearance and existing retirement rules. |
| World-time cadence and ammunition | Acquisition, aim, shot, reload, memory and failure deadlines use world time. One accepted round per update prevents accumulated catch-up bursts. Ammunition is debited only after accepted launch; the finite magazine has a full timed reload and explicitly unlimited reserve. |
| Physical authority, death and reset | Non-locomotion authority clears movement/path/burst/reload intent before the adopted physical response. Direct death and authority checks also gate firing. Recovery replans from the displaced pawn. Reset, mode changes and F10 clear rounds; foundation/controller destruction retains existing ownership. No timer-manager callbacks are added. Already emitted rounds may finish after death. |
| Player receiver and later scope | Existing `ApplyPointDamage` reaches one `TakeDamage` override, which calls `Super` once and records counters/feedback. No second damage application, player health, player death, disarming behavior or wound gesture system is added. Held-weapon and hand-occupancy interfaces are exposed. |
| Owner controls and preservation | One autonomous profile-1 opponent is the default; three passive original fixtures remain available. Manual rifle commands suspend AI; F6 resets according to the selected mode. The documented console controls and limits match source. Existing physical tuning and asset packages are outside the implementation delta; preservation evidence retains owner configuration/project/map hashes. |

These are source conclusions, not demonstrations that the runtime acceptance
rows in [the task](Tasks/EnemyCombat01.md) have passed.

## Finding and closure

**EC70-R1, medium — unbounded close-cover Aim/Pursue loop.** With a visible
target already inside the 85 cm reposition radius and a blocked muzzle, the
original implementation entered Aim immediately from Pursue, then returned to
Pursue on the next obstructed attempt. Each swap restarted its state timeout;
no path attempt ran inside that radius. This could repeat indefinitely.

The correction keeps `ObstructionAttempts` and `ObstructedSince` across
`ClearIntent` and the Aim/Pursue transitions. A third failed corridor, or a
repeated failure more than six world seconds after the first, starts return
with the existing sight-suppression cooldown. Explicit enable/reset, a fresh
visible acquisition or an accepted shot resets the budget. The source flow
closes the reported cycle; build03 compiles that correction.

Original finding and closure are preserved separately under
`Saved/CombatSlice01/EnemyCombat01/Review/EC70-R1-source-finding.json` and
`EC70-R1-source-closure.json`. No open review finding remains.

## Evidence limits and handoff

The [implementation handoff](EnemyCombat01.md) accurately states the local
single-layer navigation envelope, conservative grid clearance, frame-quantized
enemy cadence, unlimited reserve, Ready-pose reload and prototype muzzle offset.
The 1.5 ms planning boundary is soft; runtime cost is unmeasured. Rubble, moving
support, player survival, packaging and networking remain separate scope.

The executor's `source-self-check.json`, `editor-after.json`,
`editor-load-check.json` and `preservation-after.json` support the stated build,
load, stopped-Play and preservation claims. They are not gameplay evidence.
The owner retains actual acquisition, pursuit, cover/damage timing, recovery,
death/reset, aim and motion evaluation. The controller owns scope/evidence
acceptance and the task-scoped local closure commit.
