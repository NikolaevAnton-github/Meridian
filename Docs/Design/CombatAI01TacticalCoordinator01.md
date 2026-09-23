# CombatAI01: situational tactics and squad coordination

Date: 2026-09-23. Parent: MSQ-101. Design refinement following the owner's
playtest of MSQ-103; this is not an implemented candidate or runtime acceptance.
Source: [exact owner feedback](../Approvals/CombatAI01-TacticalDirection01.json).
Read with the [main design](CombatAI01.md) and [package plan](../Tasks/CombatAI01Plan.md).

Later [owner start](../Approvals/CombatAI01-Tactical01-OwnerStart01.json) authorizes
[MSQ-118 / CAI-T01](../Tasks/CombatAI01/CAI-T01.md), the first single-enemy tactical
slice using current sight evidence/local navigation. This explicit early slice
precedes the full sensory/topology packages without claiming their completion.

## Required behavior

The owner reports visible running and continued search, but finds decisions slow
and the opponent mannequin-like. The requested direction is a tactical squad
coordinator that changes behavior with the combat situation. In particular, a
lone remaining enemy that loses contact should prefer a defensible observation
position over exposed wandering. Mines/traps and smoke for advance or withdrawal
are intended later mechanics that enemies actively use during combat.

Persistent search means continued effort to locate and contain the threat. It can
include listening, controlling plausible exits and repositioning. It does not
require continuous movement through an exposed room. This refines the earlier
search direction without restoring timed forgetting or an unaware return home.

## Current implementation evidence

Source inspection of `EnemyCombatComponent.h`, `EnemyCombatPolicy.cpp` and
`CombatAIAction.h` finds these defaults and branches:

- Sight is sampled every 0.12 world seconds. Acquisition and aiming each introduce
  a 0.65-second delay; eligible paths can pay both delays before firing.
- Search proposes last sight, four surrounding points and four nearby points.
  Reached points introduce a 2-second observation dwell; a completed proposal
  cycle uses a 5-second retry delay. Failed proposals have separate backoffs.
- There is no protected-position score, approach coverage or squad assignment in
  this policy. Merely reducing timers cannot supply those decisions.

These are source observations, not measurements of the owner's play session.
Movement, turning, physical recovery, shot eligibility and navigation can add
delay. Separate event-to-decision latency from movement onset and first valid
shot in existing traces before attributing the whole symptom to any one timer.
All tactical deadlines use world time under the retained slowdown policy.

## Coordinator and individual responsibilities

Use a logical **Squad Coordinator**, with no dependency on a visible commander
character. Its first useful scope can include one member. It consumes member
capabilities, available support, reported threat evidence and validated space;
it selects a combat objective and assigns feasible responsibilities. Each enemy
still handles immediate danger, movement, aim and physical interruptions locally.

Keep the encounter pressure policy as the existing separate permission stage.
It controls readable attack pressure; it must not supply secret player locations
to tactical selection. Use the same bounded utility/action architecture already
proposed in the main design, rather than introducing a second planner.

| Observed situation | Proposed objective and visible action |
| --- | --- |
| Alone, lost contact, exposed | Move to reachable protection; watch plausible approaches and listen |
| Two members, contact sufficiently localized | One controls the known threat angle while the other changes position |
| Group loses contact | Divide useful search/exit sectors and retain mutual support |
| Supporting member becomes unavailable | Cancel dependent maneuver; reassess actual available support |
| New evidence compromises a held position | Reorient, choose another protected position or take a supported opportunity |
| No safe position or alternate route exists | Select the best reachable fallback with an explicit risk reason |

Member death/reset immediately releases coordinator resources for correctness.
An individual enemy's knowledge of an unseen casualty still requires observation,
a delivered report or failed expected coordination. A missed acknowledgement
establishes uncertain unavailability, not confirmed death. Resource cleanup must not
silently provide a new target location or an instant unseen-casualty reaction.

## Protected positions and active search

Evaluate existing geometry for approach coverage, rear/side access, exposure to
the threat's possible region, movement cost, usable weapon space and an escape
route. A wall at the back is useful evidence, but a corner can also be a trap.
Score uncertainty across plausible approach routes, not just one last-seen point.
There is no promise of an unflankable position in every layout.

Use removable tactical anchors and bounded geometry checks on the retained map.
Revalidate arrival and abandon invalid or unreachable positions. The enemy must
face useful approaches while holding; facing is part of the action result.

Holding remains alert and interruptible. Fresh sight, sound, incoming danger,
lost support or invalid protection can change the decision. Periodic bounded
reassessment prevents a stale assignment from becoming permanent. If no new
evidence arrives, evaluate safe adjacent observation opportunities and coverage
gaps; do not force an arbitrary exposed march solely because a timer elapsed.
Owner testing must reject prolonged passive standoffs as well as foolish pursuit.
Repeated unchanged holds fail acceptance when a demonstrably better reachable
observation opportunity remains available.

## Decision responsiveness

Distinguish first awareness from reacquiring a known nearby threat. Do not restart
the full first-contact delay after every brief loss of sight. Let urgent valid
evidence interrupt observation dwells and invalidate obsolete plans promptly.
Preserve aiming/turning, projectile and physical-authority constraints.

Use event-driven invalidation plus bounded periodic selection. Apply commitment
and a switching margin to ordinary alternatives, with explicit interruption for
danger and lost action prerequisites. Trace the selected objective, reason,
rejected alternatives and pending gate so an idle-looking interval is explainable.
Reaction numbers are tuning proposals until measured and judged in owner play.

## Proposed delivery sequence

Default planning assumption: demonstrate situational decisions with one opponent,
then extend the same coordinator to two/three. This is the controller's recommendation,
accepted for the first slice by the later owner start linked above.

1. Retain CAI-02's real sound/fire evidence work. Use it to interrupt stale search
   and distinguish a located threat from an uncertain direction.
2. Build the smallest useful route/position subset of CAI-03/04: defensible
   observation, approach coverage, withdrawal and prompt reacquisition. Introduce
   the shared objective/coordinator interface here for one member. Do not wait
   for suppression, style variation or the full group maneuver repertoire to
   expose this behavior to the owner.
3. The first group delivery combines CAI-05 membership, reports, reservations,
   friendly launch safety and pressure permissions with minimum CAI-06 readability
   and one CAI-07 contract, such as hold-and-search or alternate-angle movement.
   Include interrupted cooperation and transition to lone-survivor behavior.
   Cover-and-cross still requires CAI-04's separately verified suppression contract;
   do not relax direct-fire visibility to deliver it early.
4. Add equipment only when its real mechanics and counterplay exist.

The later CAI-T01 task implements the bounded sight-based portion early; the
remaining sequence is proposed, not a claim that existing hard prerequisites
are satisfied. Player
health and encounter lifecycle still gate their respective full acceptance.

## Future equipment contract

Smoke is an action with a purpose: obscure a dangerous crossing, support an
advance, disengage or reposition. It needs finite inventory, throw/deployment
time, duration, interruption and real effects on sight for both sides. Visual
opacity alone is insufficient; smoke does not become bulletproof cover. An
enemy may exploit remembered information without precisely tracking through it.

Mines/traps can protect a vulnerable approach or a withdrawal route based on
known geometry and observed activity. Placement must occur through a real
interruptible action with inventory cost and readable player counterplay. No
invisible retroactive placement on the hidden player's route. Coordinate friendly
routes and hazards; do not deploy equipment automatically on cooldown.

Equipment eligibility belongs in the existing capability/action selection:
expected tactical benefit, deployment risk, resource cost and opportunity cost.
Its absence must leave a working base policy. Equipment mechanics, balance and
presentation remain later scope, as requested by the owner.

## Focused acceptance for the next tactical delivery

- An exposed lone enemy loses contact and selects/holds a useful reachable
  position with fewer uncontrolled approaches when the test geometry offers one.
- A new clue or a visible flank changes its observation/position; the enemy can
  still be deceived while the player stays unobserved.
- Known-threat reacquisition does not repeatedly pay unrelated first-contact or
  search delays. Record actual event-to-choice and choice-to-action timing.
- Holding does not forget the encounter or produce an indefinite stale action;
  unsafe/unreachable protection has a bounded, explainable fallback.
- When group scope is delivered, losing support cancels dependent maneuvers and
  changes the remaining enemy's policy using permitted knowledge.
- Physical recovery, death and reset still cancel intents and stale assignments.

Retain owner-only gameplay testing. Agents supply build/source and focused pure
checks plus one substantive technical review at implementation time. Runtime
position quality, reaction feel, readable cooperation and fun remain owner gates.
