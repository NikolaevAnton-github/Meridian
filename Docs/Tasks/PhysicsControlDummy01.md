# PhysicsControlDummy01: second interactive mannequin experiment

Prepared 2026-09-19. Multica issue: **MSQ-84**.
An unstaged experimental child of [CombatSlice01 / MSQ-67](CombatSlice01Plan.md),
depending on verified [EnemyPrototype01 / MSQ-69](EnemyPrototype01.md), closure
commit `02fb313`. See the [owner request](../Approvals/PhysicsControlDummy01-TaskCreation01.json).
This preparation creates a plan and one unassigned backlog task; it starts no
production run and does not reorder or dispatch MSQ-70 and successors.

## Outcome and experiment boundary

Add one removable second Manny in the retained lobby to let the owner compare
Physics Control hit reactions with the existing enemy. The experimental dummy
maintains a powered living pose, reacts locally to rifle hits, transitions to
passive ragdoll on death, and continues receiving physical bullet impacts while
falling or resting. Preserve the first enemy as the comparison baseline,
including its existing post-death pass-through behavior for this experiment.
Adoption of the new behavior by the baseline enemy is a later owner choice.

Use one task with sequential implementation, verification and review steps.
The first result is a stationary shooting fixture, not a complete Euphoria-style
behavior system. Autonomous balance/stepping, get-up, AI, navigation, Mover
migration, dismemberment, new art and full Game Animation Sample integration are
outside this experiment. The player-facing slowdown/stop ability remains MSQ-75.

## Baseline and technical direction

- Installed engine: UE 5.8.1, changelist 56057345. PhysicsControl is installed and
  its descriptor is neither Beta nor Experimental. The current enemy uses
  ordinary skeletal physics; plugin availability does not mean integration.
- Reuse the audited Manny mesh, skeleton, animations and physics asset from
  [EnemyPrototype01](../EnemyPrototype01.md). Keep source packages unchanged;
  store any required editable experimental copies/profiles separately under
  `/Game/Development/PhysicsControlDummy01/` and retain binary assets in LFS.
- Prefer the Physics Control Component for this gameplay experiment. Document
  the chosen bone/body mapping, living drive strengths/damping, root or pelvis
  support, death drive release, impulse limits and sleep policy. A supported
  standing fixture must be described honestly; it does not prove self-balancing.
- The current projectile world ignores characters in world sweeps and gates its
  custom character/aim queries on capsule collision; dead enemies also stop
  supplying hit spheres. Separate physical hit eligibility from health/death
  eligibility for the second dummy. Its movement capsule must not become an
  invisible standing bullet blocker after death. A collision-channel change
  alone is insufficient.
- Preserve one authoritative rifle/finite-flight hit path. Use actual current
  physical body poses for contacts, with explicit time/history limits. Keep the
  baseline enemy's corrected exclusion of obsolete living aim spheres.

## Sequential plan

1. **Confirm the implementation seam.** Inspect installed PhysicsControl APIs and
   relevant Epic examples. Establish the body/drive and projectile-contact
   contract before editing gameplay. Use the August 2026 GASP powered-ragdoll
   example as a reference; importing its Mover pawn or full sample is not a
   prerequisite. Any needed official free reference download must have verified
   terms, measured size and bounded storage; no purchases or duplicate project.
2. **Create the second fixture.** Spawn one transient Manny beside the baseline
   with a clear experimental identity and unobstructed firing space, without
   editing lobby geometry. Use the same initial health and rifle damage for
   comparison. Implement a stable powered idle pose with visibly local physical
   response to torso, arm and leg hits and bounded recovery. Tune one initial
   profile; expose necessary values instead of creating a tuning campaign.
3. **Connect death and corpse contacts.** Release living drives once and preserve
   the current pose and physical momentum. Apply the lethal hit and later hits
   once, at the struck body/contact location, along the incoming bullet direction.
   Keep health at zero and the death event single. Consume bullets under the
   retained nonpenetrating policy. Use natural/inactivity-based sleep and wake
   on new impacts; do not inherit the old actor's repeated six-second forced sleep.
4. **Make the experiment repeatable.** Integrate reset with F6 without ammunition
   refill, clean teardown and an explicit way to disable the second fixture.
   Preserve F7's current baseline movement behavior. Add a bounded development
   preview at normal time and 0.25 world speed: body physics and bullets must
   slow coherently while player movement remains normal. Record the clock policy
   and restore all overrides on exit/reset/PIE teardown. This is not a new ability
   binding, resource system, or full exact-stop implementation.
5. **Verify and review.** Use the existing probes/transport and short comparable
   gameplay captures. One primary independent reviewer owns the focused technical
   and prototype visual criteria below; the controller accepts scope, applicable
   evidence and finding closure. Deliver the experiment for owner play comparison.

## Focused acceptance

| Criterion | Required evidence |
| --- | --- |
| Two distinct fixtures | Both load in the retained lobby; the original enemy's assets/tuning and current behavior are preserved. The second fixture can be disabled without changing the baseline. Record spawn positions and any support constraints. |
| Living physical response | Rifle hits to torso, one arm and one leg visibly affect the corresponding physical region and settle/recover without sustained jitter, joint explosions or an unreported world anchor. Candidate telemetry confirms Physics Control drives, not only animation playback. |
| Death continuity | One lethal event releases drives and continues from the current physical pose/velocity without reset-to-idle, a pose snap, duplicate lethal impulse or renewed living control. |
| Repeated corpse hits | The actual finite-flight rifle hits both a falling corpse and a settled/sleeping corpse. Each bullet produces one local impulse/contact; direction and resulting motion are coherent, the bullet is consumed, health remains zero and death count remains one. A later hit wakes the body and is not immediately canceled by a sleep timer. |
| Contact and birth timing | One focused case kills the dummy and emits a later scheduled shot in the same processing interval. Preserve 85 ms births/residual flight, nearest obstruction and valid corpse convergence; no stale standing proxy or pre-birth contact. Record the transition/history approximation: frame-end Chaos poses cannot establish exact historical subframe motion. Cover the touched near-cover path and baseline Correction01 guard only. |
| Slow preview | Actual body and bullet movement are measured at scales 1 and 0.25 with no double scaling, repeated impulse or restoration burst; player movement stays normal. A projectile-only scale change or slow video playback is insufficient. Full world stop remains MSQ-75; reuse existing zero-scale/self-hit evidence unless the changed seam requires a focused recheck. |
| Reset and bounded cost | F6 restores both fixtures and clears experimental velocities, controls, contact history and time overrides without refilling ammo. Reset during active ragdoll and one fresh PIE session pass, with no leaked actors or unbounded work. Record incremental frame cost and disk growth, not a new benchmark suite. |
| Preservation and handoff | Appropriate native build/fresh load and experimental asset reload succeed. Owner configuration, lobby, purchased arms, historical sources/evidence and baseline enemy behavior remain preserved. Short actual comparable clips support visual claims; technical verification and owner play acceptance remain distinct. |

The slow-preview criterion must be reported explicitly if incomplete; do not
label projectile-only timing as full physical slow motion or silently expand
this task into MSQ-75. Numerical tolerances and any approximation must be chosen
from the implementation and recorded before claiming a pass.

## Execution, evidence and review ownership

Use one existing Multica Unreal executor at **Astra/max/standard**, production
concurrency one and one editor writer. Verify configured profiles, native
arguments and actual execution, then restore task-local settings while retaining
the standing max requirement. Confirm live project, map, PIE and dirty packages
through official Epic MCP before mutation; preserve any owner session/edits.

The executor implements and self-checks. One primary independent reviewer at
max/standard owns all eight acceptance rows, including direct inspection of the
relevant implementation and actual gameplay views. Name that reviewer at dispatch;
no second overlapping technical review is required. Reuse applicable MSQ-69 and
MSQ-82 evidence and run only directly affected checks/related transitions under
[FocusedVerification01](../Approvals/FocusedVerification01.json). Corrections
return to the same reviewer and affected criteria. The controller owns acceptance,
administrative closure, a verified task-scoped local commit and the owner handoff.

Deliver `Docs/PhysicsControlDummy01.md` with setup/controls, tuning and support
contract, collision/time policy, results and limits; retain candidate identities,
probes, concise telemetry, comparable clips, source inventory and preservation
records under `Saved/CombatSlice01/PhysicsControlDummy01/`. Register new accepted
assets with the existing registry workflow without replacing baseline fingerprints.
Keep the total project within 250 GB and preserve sources and failed candidates.

## Sources and preparation record

- [Epic: GASP for UE 5.8, 2026-08-12](https://www.unrealengine.com/tech-blog/download-the-latest-game-animation-sample-project-now-updated-for-ue-5-8): Physics Control drives and the powered-ragdoll sample.
- [Epic: UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes): PhysicsControl production readiness; Control Rig Physics and Dynamics have distinct roles/status.
- [Fixed projectile/time/self-hit policy](../Approvals/CombatFoundation01-OwnerScope01.json), [baseline correction](../EnemyPrototype01Correction01.md) and [review responsibilities](../AgentDevelopment.md#review-responsibilities).

Task preparation is an administrative change, using controller self-checks and
bounded read-only planning advice rather than a production review. Creation and
readback evidence belongs in `Saved/CombatSlice01/PhysicsControlDummy01/Planning/`.
No implementation, runtime capability or owner visual acceptance is claimed by
creating this task. Routine implementation choices within the eventual task scope
do not require separate owner confirmations.
