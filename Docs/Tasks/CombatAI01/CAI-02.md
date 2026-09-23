# CAI-02: Footsteps, incoming fire and evidence memory

Multica issue: **MSQ-104**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Authorized 2026-09-23 after the owner's MSQ-118 playtest under the
[owner follow-up](../../Approvals/CombatAI01-CAI02-OwnerStart01.json).

Delivered 2026-09-24: **Candidate03/build01**, accepted for owner testing within
build/source scope. Native builds, focused checks and the sole primary reviewer's
finding closure pass. See [controller acceptance](../../CombatAI01-CAI02Acceptance.md),
[base handoff](../../CombatAI01-CAI02.md),
[navigation correction](../../CombatAI01-CAI02Navigation01.md),
[R1/R2 correction](../../CombatAI01-CAI02Correction01.md) and
[finding closure](../../CombatAI01-CAI02Correction01Review.md).
Gameplay, motion, audibility, position usefulness, difficulty and performance remain
pending owner. Successors are undispatched.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-103, MSQ-118.

The later [early tactical delivery](../../CombatAI01-Tactical01Acceptance.md)
provides the current sight-based policy. Preserve its protected-position,
reacquisition, weapon-gate and action contracts while adding sensory evidence.
The later owner follow-up now authorizes this package and the bounded corrections
below. Historical MSQ-118 evidence remains preserved.

## Owner follow-up: capable hunter and useful protection

The owner confirms more column use but rejects exposed positions toward the
center and weak tracking. Incorporate these corrections in the one-enemy policy:

1. Prefer low exposure to multiple plausible firing approaches. A column behind
   the enemy alone must not outweigh broad exposure from the center and sides.
   Use static geometry and permitted threat evidence; no hidden-player transform.
   Include a bounded way to consider the protected side of a column and a feasible
   short route around it rather than accepting only scanner-visible/direct points.
2. Choose a nearby reachable point among comparably safe choices. Open view and
   escape count must not outweigh safety. Keep useful facing, clearance, actual-feet
   arrival validation, finite retries and switch hysteresis.
3. Use actual GASP crouch locomotion for cautious protected repositioning and
   observation, with quiet footstep presentation. Audit the audible enemy step
   path and connect stance to volume/emission; a boolean or speed change alone
   is insufficient. Urgent exposed crossing may retain running if safer.
4. Give sight sufficient range for the retained location, justified by static
   dimensions. Use body visibility samples and bounded contact hysteresis so a
   blocked camera sample or brief column crossing does not erase tracking.
   Actual launch remains gated by current sight and muzzle safety, not memory.
5. Connect hearing to prompt attention, investigation and protected repositioning.
   Retain evidence, uncertainty and alert through occlusion/physical recovery.
   Silent hidden relocation must not update position, velocity or aim secretly.
6. Keep reactions/retention on world time so existing slowdown supplies its player
   advantage. No damage, cadence or player-movement tuning for difficulty.
7. Check the existing 28 m home navigation cap against the retained 60.8 x 24.8 m
   floor. If it prevents useful pursuit of fresh evidence across the room, make a
   bounded adjustment to the existing navigator and verify its work limits. Full
   topology/Recast remains deferred; long sight alone is not full-room pursuit.

Additional focused acceptance: safer point beats an exposed column-back point;
nearest comparably safe point wins; crouch locomotion and quiet step wiring agree;
location-scale sight and brief-loss retention coexist with blocked-shot rejection;
fresh sound updates intent without exact hidden-player tracking. Test production
policy and producers/consumers with adversarial pure/source fixtures. Include
blocked/stationary/airborne/reset motion and stale sound. Complement S02-S05 and
affected S06/S10/S11. Actual gameplay remains pending owner testing.

## Package work and acceptance
**Purpose:** give the hunter multiple honest sources of information.
Size/risk: medium/high because movement audio and projectile clocks meet here.
Depends on CAI-01. Near-miss sensing can be completed in CAI-04 if not yet needed.

Work:

1. Add the normalized immutable stimulus record and per-enemy hypothesis memory.
   Separate attribution/lifecycle actor handles from permitted targeting information.
2. Route current sight through the same memory path. Add bounded retention/hysteresis
   and body samples where needed without allowing obstructed shots.
3. Audit existing player step audio/contact events. Choose one authoritative event
   producer, or a grounded-distance fallback, and prevent dual emissions.
4. Add walk/run intensity, actual-ground-travel gating and one landing event. Provide
   distance/occlusion attenuation and uncertain localization; document acoustic limits.
5. Emit accepted-shot noise from `LaunchTimed`'s accepted branch. Emit impact/damage
   evidence at resolved contact and before physical interruption discards tactical intent.
6. Preserve projectile simulation/contact time and world receipt/occurrence time as
   distinct fields until a tested conversion exists. Never substitute real-time impact
   presentation timestamps for AI reaction deadlines.
7. Queue delivery outside projectile collision iteration. Preserve ordered contact and
   reset-generation protection; deduplicate shot/listener and hit events.
8. Add category/team filtering, event merging, bounded listeners and debug regions.
   A heard source actor does not automatically reveal identity or current location.
9. Inspect engine AI Perception only as an optional sensor/event transport adapter.
   Use one authoritative hearing route and retain project memory/uncertainty contracts.

Acceptance: S02-S05 plus affected S06/S10/S11. Identical unseen positions cannot change
memory absent new evidence. Incoming damage supplies a bearing, not a live exact target.
Footstep cadence agrees with actual motion; muted audio does not disable gameplay hearing.

Fallback: first ship a declared distance/occlusion model for the current open lobby.
Doorway-aware propagation is a later extension if representative geometry needs it.
Do not invent rooms/portals or advertise physically accurate sound.

Owner route: hide from sight, walk then run, stop, jump/land, fire from a new angle and
relocate quietly. Observe how the enemy searches the old sound/shot region.

## Execution and verification contract

The linked owner follow-up authorizes execution through Multica. Read
`Docs/ProjectState.md` first,
then this task, the linked plan/design and only relevant prerequisite decisions.

- One production writer and one Unreal writer; max reasoning at standard speed,
  verified in configured and native execution.
- Executor implements and self-checks; one primary independent reviewer owns
  substantive technical review. Controller owns scoped acceptance and local commit.
- State the applicable verification mode at dispatch. The continuing MSQ-70
  owner-test reservation is not silently revoked. Under owner-only gameplay testing,
  provide build/source evidence and the owner route; leave runtime rows pending.
- Run only affected scenarios and related transitions; reuse applicable evidence.
  Owner retains motion, readability, surprise and combat-feel acceptance.
- Preserve GASP/Mover physical authority, finite bullets and current time policy:
  world/bullets/rifle cadence 0.25, hero movement 0.65 during slowdown.
- Preserve owner edits, current map, asset sources and historical evidence. No new
  paid services, duplicate project or unapproved art/architecture production.

## Required handoff

Provide scope, candidate identity, changed files/assets, tuning, build result,
applicable focused evidence, review findings/closure, owner controls/route and known
limits. Keep generated evidence in `Saved/CombatAI01/<package>/<candidate>/`.
Executor delivers `Docs/CombatAI01-CAI02.md`, immutable candidate identity including
the DLL, and `Saved/CombatAI01/CAI-02/Worker/Candidate01/` evidence. Controller owns
primary-review dispatch and the verified local MSQ-104 closure commit.
