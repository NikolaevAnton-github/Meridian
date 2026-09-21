# GASPEnemyFoundation01: migrate enemies to GASP with retained balance

Multica issue: **MSQ-98**.
High-priority unstaged child of [CombatSlice01 / MSQ-67](CombatSlice01Plan.md).
Predecessor: delivered [MSQ-92](PhysicsControlAdaptiveSteps01.md), consuming the
current baseline including the later [cadence correction](../CombatSlowdownCadence01.md).
The owner places this work first, ahead of the remaining physical refinements
and MSQ-70; see [the exact planning decision](../Approvals/GASPEnemyFoundation01-TaskCreation01.json).
The later [owner start and review waiver](../Approvals/GASPEnemyFoundation01-OwnerStart01.json)
authorizes this implementation without an independent reviewer for now. Executor
focused self-checks and controller acceptance remain required; owner motion/play
judgement stays separate.
The [later editor-lifecycle approval](../Approvals/GASPEnemyFoundation01-OwnerEditor01.json)
permits stopping the existing Play session and necessary controlled Unreal restarts
for this task, preserving owner changes and unsaved assets first.

Delivered Candidate01 on 2026-09-21: all three fixtures migrated; build and six
focused executor criteria pass. Controller scope/evidence acceptance and registry
validation pass. See the [immutable handoff](../GASPEnemyFoundation01Handoff.md)
and [controller acceptance](../GASPEnemyFoundation01Acceptance.md). Independent
review was waived; owner motion/play judgment and successor dispatch remain separate.

## Outcome

Use the configured UE 5.8 GASP physical character as the enemy foundation while
retaining our damage, balance, recoverability and adaptive stepping behavior.
Start with one isolated pilot, then migrate the current three active fixtures
after the affected checks pass. Preserve the old implementation and evidence.
A pilot alone does not complete the migration task.

## Scope

- Audit the local source at `D:/devgames/GameAnimationSample`, its actual engine
  version and dependency footprint. Use `SandboxCharacter_Mover_Ragdoll`, its
  required animation/PhysicsControl setup and motion-matched get-up as the starting
  point. Selectively migrate the needed assets into a task-scoped project namespace;
  preserve the source project. Record exact source/derived asset identities, skeleton
  mapping, retargeting choices and changed physics tuning. Keep within the 250 GB cap.
- Adapt the existing support/contact measurements, physical recoverability estimate,
  bounded actuator effort, leg replanting and disturbance-driven step length/lift/time.
  Preserve successive feasible steps and real falling when support or recovery fails.
  Preserve the configurable recovery tempo and bounded Ctrl+F9 assistance behavior.
- Establish one authority for PhysicsControl targets, modifiers and profiles. Define
  ownership of animation, physical bodies, root/capsule and Mover during locomotion,
  disturbed balance, stepping, falling, down, get-up and terminal death. Do not run
  our old world-space drives and GASP's drives as competing controllers. Recalibrate
  contact, sole clearance and effort against the actual adopted body/Physics Asset.
- Use GASP's pose selection and get-up transitions where applicable; retire the
  active two-clip Mixamo selection and its specific timing adjustments from this
  path without deleting original sources. Retain supported-space checks, safe
  blocked behavior and interruption from the current physical pose.
- Connect real rifle impacts and the existing authoritative projectile/damage path
  to the new enemy type. Account for the present direct `APhysicsControlDummy`
  coupling. Preserve regional contact data, impulse, health, death, corpse hits,
  reset and fixture controls. Do not introduce a second hit or damage event.
- Demonstrate commanded flat-floor walking/running, stopping and resuming solely
  to prove the locomotion-to-balance handover. Supply the movement and combat
  interfaces for MSQ-70, with an extension point for hand/weapon occupancy;
  perception, pursuit and autonomous firing stay in that task.
- Preserve the three current fixture slots/profile distinctions at final rollout.
  Keep purchased first-person arms, player movement/camera, retained lobby and
  owner edits. Enemy-side Mover integration does not migrate the player.

## Focused acceptance

1. The final three GASP-based fixtures render in the retained lobby. Verify shared
   behavior on one representative, without a per-profile comparison matrix.
2. Show a continuous movement -> real rifle hit -> feasible recovery step/settling
   -> resumed movement sequence, and an infeasible disturbance -> physical fall
   -> supported living get-up -> resumed movement sequence. No root/capsule jump,
   competing targets, forced support or loss of the actual recovery location.
3. Demonstrate the retained displaced-leg and successive torso-hit recovery behavior
   on flat support. Reuse applicable MSQ-92 evidence; recheck criteria invalidated
   by the new body, controller or animation integration. Record tuning and limits.
4. Check the newly coupled get-up interruption, terminal death/corpse impact and
   blocked/unsupported recovery paths. Preserve calibrated sole contact and effective
   arm/body collision; record any remaining motion limitations honestly.
5. Check affected reset/recreation and relative slowdown transitions: world, bullets
   and rifle cadence at 0.25; player movement at 0.65. Retain F6/F10 and Ctrl+F7/F8/F9
   behavior, including reset without ammunition refill and no stale actor references.
6. Provide ordinary-speed continuous footage, candidate/file identities, a focused
   result table and an ownership/interface handoff for MSQ-70 and MSQ-93 through 96.

## Boundaries and execution

MSQ-93 retains expanded torso/arm counterbalance, MSQ-94 obstacle-aware recovery
improvements, and MSQ-95/96 uneven/moving support. Preserve current safety behavior
without claiming those future criteria pass. Parkour gameplay, disarming, wound
gestures, AnimGen experiments, AI combat, new character art, player replacement
and migration of the whole sample are excluded. These planning boundaries supersede
earlier enemy-side Mover/locomotion exclusions only within this task's future scope.

On execution, use one Multica Unreal writer at verified native Astra/max/standard.
Follow executor focused self-checks and controller acceptance under the task-specific
[owner review waiver](../Approvals/GASPEnemyFoundation01-OwnerStart01.json). Do not
dispatch an independent reviewer for this execution; owner motion/play judgement
remains separate. Confirm live editor/project/map/PIE
and dirty state through Epic MCP before mutations. Preserve owner sessions, source
assets, old candidates and exact historical manifests. Track binary derivatives in
LFS and register new fingerprints without overwriting accepted registry records.

Deliver `Docs/GASPEnemyFoundation01.md`, its controller handoff and focused evidence
under `Saved/CombatSlice01/GASPEnemyFoundation01/`. The controller makes the verified
task-scoped local closure commit. Do not automatically dispatch successor tasks.
