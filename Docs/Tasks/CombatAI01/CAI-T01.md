# CAI-T01: Situational single-enemy tactics and coordinator foundation

Multica issue: **MSQ-118**. Parent: MSQ-101. Authorized 2026-09-23 under the
[owner start](../../Approvals/CombatAI01-Tactical01-OwnerStart01.json).
Delivered **Candidate02/build01** for owner testing. Native build, affected checks
and the same primary review's CAIT-R1/R2 closure pass; see
[controller acceptance](../../CombatAI01-Tactical01Acceptance.md) and
[final review](../../CombatAI01-Tactical01Correction01Review.md).
Actual movement, position quality, performance and combat feel remain pending owner.
Read [ProjectState](../../ProjectState.md), the
[tactical refinement](../../Design/CombatAI01TacticalCoordinator01.md) and the
[MSQ-103 handoff](../../CombatAI01-CAI01.md).

Prerequisite: delivered MSQ-103 / Candidate01/build05 and current tracked source.
This early bounded slice uses current sight evidence and local navigation. It
does not mark full CAI-03/04/05 complete. MSQ-104 remains the separate hearing/fire
evidence package, to consume this revised policy when later dispatched.

## Implementation

1. Add a small explicit tactical objective/selection seam that can represent a
   one-member coordinator now and accept later group assignments. Keep personal
   knowledge and local action execution separate. Do not add a parallel planner.
2. Correct redundant response waits for an already known threat. Distinguish
   initial contact, brief reacquisition and a substantially new threat direction.
   Preserve ordinary turn/aim and stationary launch safety, physical recovery,
   weapon readiness and current world clocks. New visible evidence interrupts an
   obsolete observation/position action without waiting for its ordinary dwell.
3. Generate a bounded set of tactical positions from actual retained collision
   geometry, using local surface-derived candidates or removable annotations as
   appropriate. Validate standing capsule/support and route feasibility. Include
   current position and useful neighboring observation opportunities.
4. Rank real rear/side protection, approach visibility, exposure relative to the
   last observed threat region, travel cost, useful weapon space and escape
   options. Reject unsupported/blocked candidates. Never label a mere coordinate
   offset as cover or consult the concealed player's transform for scoring.
5. On lost contact, select and move to useful protection when available, then
   face plausible open approaches. Revalidate arrival and held geometry. Do not
   face into the protective wall or keep aiming at the actor's own feet.
6. Hold actively: examine useful sectors, re-evaluate periodically and take a
   safer informative adjacent observation opportunity when worthwhile. Use
   commitment/switching margin to prevent oscillation. Do not make every enemy
   camp forever, or force exposed wandering when no useful alternative exists.
7. Bound candidate work, navigation attempts, rejection history and retries.
   Unreachable/no-cover situations retain useful alert observation and an honest
   fallback reason. Avoid repeated selection of the same failed destination.
8. Cleanly cancel/rebuild tactical intents on reset, death, disable, living
   physics interruption and recovery at displaced feet. Preserve CAI-01 action
   tokens/generations and finite projectile/time policies.
9. Extend existing status/trace output with objective, selected position/facing,
   reason, candidate/rejection counts, evidence age and pending decision/action
   gates. Keep enough timestamps to diagnose decision versus execution delay.

First scope is a single enemy using available sight/last-sight evidence. Do not
claim auditory reactions, ally-loss knowledge, full room topology or validated
group behavior. Use the existing map and locomotion; no new art or geometry.

## Acceptance and review

The executor implements and self-checks. One primary independent source reviewer
owns substantive technical review; the controller accepts scope, identity,
evidence applicability and finding closure without repeating that full review.

- T01: protected geometry scores better than exposed alternatives in applicable
  inputs; invalid floor/capsule/route/facing candidates cannot be accepted.
- T02: lost-contact movement and held facing derive only from permitted evidence
  and geometry. Identical evidence with different concealed player positions
  yields identical tactical proposals before physical safety vetoes.
- T03: fresh known contact interrupts ordinary hold/search waits; initial contact
  and aim/launch constraints retain explicit bounded semantics.
- T04: stable holds do not thrash; a useful better probe can replace a stale hold;
  no-cover and unreachable positions cannot cause unbounded retries or queues.
- T05: physics/death/reset invalidate old intents and callbacks; living recovery
  replans from actual feet while retaining encounter awareness.
- T06: native Development Editor build passes; focused pure/source checks exercise
  the above contracts with edge/adversarial inputs rather than source strings alone.

All actual movement, map-position usefulness, visible responsiveness, firing,
physics transitions, performance and combat feel remain **pending owner testing**.
No agent PIE, simulated combat, firing probes or screenshots of gameplay. Inspect
editor geometry read-only when useful. Reuse unaffected passing evidence.

Owner route: establish contact, briefly hide and reappear; then disappear longer
behind retained geometry and approach visibly from another direction. Inspect
whether the enemy chooses protection, watches approaches and changes decisions.
Use F6 and the existing `msq.EnemyCombat status`/`trace` controls as documented in
the final handoff. Do not describe unobserved silent movement as a heard clue.

## Execution and handoff

One production/editor writer and one heavy workload. Astra/max at standard speed,
verified in profile/native arguments and native run context. Preserve owner edits,
map, assets and historical evidence. Necessary guarded native rebuild/reload is
authorized; preserve any newly active owner Play session and unsaved packages.

Evidence: `Saved/CombatAI01/CAI-T01/Worker/Candidate01/`, with a new candidate name
for substantive post-freeze changes. Deliver `Docs/CombatAI01-Tactical01.md`,
focused evidence, exact PASS versus pending-owner rows, changed files/tuning,
controls, limits and an immutable candidate manifest including the built DLL.
Controller owns approvals/task/index/ProjectState updates, registry if applicable,
independent review dispatch and a local closure commit with the real MSQ task ID.
