# Gameplay policy and baseline routes

Read only for AI/combat/movement/physics work. Current scope is in
[ProjectState](../ProjectState.md); historical starts are not new authorization.
Use [GameBrief](../Design/GameBrief.md) when defining game/level requirements,
including AI/combat behavior; read the sections relevant to the active task.
For code navigation, open only the relevant [subsystem map](../Subsystems/README.md):
AI, navigation, weapons or animation. Maps identify entrypoints and boundaries;
the active task and owner decisions still determine authorized changes.

## AI and locomotion

Read the relevant [UtilityGOAP01 child](../Tasks/UtilityGOAP01.md), replacement-plan
sections and its scoped decisions before AI work. Preserve canonical GASPALS/CMC
and justified primitives; no selectable legacy AI/navigation fallback.
The current correction is [GASPALSAIFix01](../GASPALSAIFix01.md), Build07.
The preceding [GASPALS migration](../Tasks/GASPALSLocomotion01.md) explains the source
adapter and ownership. Source Masculine/Rifle gait and aim movement supersede the
older 360 cm/s enemy override and active custom balance/recovery requirements.
Physical hit reactions, ragdoll/get-up, death and corpse impulses remain bounded
adapters. Old GASP/Mover deliveries and evidence stay preserved.

## Combat and time

[CombatSlice01](../Tasks/CombatSlice01Plan.md) indexes combat dependencies. MSQ-68,
69 and 82 are verified prerequisites; [timing review](../CombatTiming01Review.md)
retains the low-FPS recoil limitation. Manny is a technical placeholder.
[MSQ-70 direct start](../Approvals/EnemyCombat01-OwnerStart02.json) permits direct
implementation and build/source checks with owner gameplay testing for that task;
it does not dispatch successors or waive their review requirements.

Slowdown: rifle cadence, bullets and world are **0.25**, hero movement **0.65**.
This supersedes the old normal-player rule. Read
[cadence authority](../Approvals/CombatSlowdownCadence01-OwnerScope01.json) and,
if needed, [relative-slowdown authority](../Approvals/PhysicsControlVariants01-OwnerScope01.json).
Full stop remains later scope. PurchasedArms06 is the rifle presentation baseline.

## Earlier physics work

[MSQ-90 plan](../Tasks/PhysicsControlRefinement01Plan.md) indexes MSQ-91..96.
The [MSQ-97 insertion](../Approvals/PhysicsControlRecoverability01-NextTask01.json)
places recoverability after 91 and before 92. Delivered: MSQ-91 Candidate07 stance,
MSQ-97 Candidate07 recoverability, MSQ-92 Candidate06 adaptive steps (approximately
25% faster recovery). MSQ-93..96 are undispatched. Candidate-specific evidence is in
the respective task/handoff, not a mandate to retest the historical matrix.
MSQ-91/97 review waivers are task-scoped; owner motion judgement is separate.

[MSQ-98 migration](../Tasks/GASPEnemyFoundation01.md) followed MSQ-92 before 93/70;
its Candidate01 technical acceptance and task-scoped review waiver remain historical.
MSQ-99 disarming and MSQ-100 wound gestures are prepared only. Preserve MSQ-89
Candidate05 and all later candidate evidence. Current GASPALS source locomotion
supersedes old active-enemy custom-balance requirements.

## Focused verification

Check only changed animation/gameplay behavior and related transitions under
[FocusedVerification01](../Approvals/FocusedVerification01.json).
For owner experimentation, verify the requested variant set renders and shared
functionality works on one representative instance. Subjective comparison stays
with the owner; a per-variant matrix or independent visual comparison needs an
explicit request or concrete distinct defect. See
[OwnerVariantTesting01](../Approvals/OwnerVariantTesting01.json).
