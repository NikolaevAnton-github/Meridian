# CAI-T02: Weapon-aware cover peeking and prompt fire

Multica issue: **MSQ-119**. Parent: MSQ-101. Authorized 2026-09-24 by the
[owner follow-up](../../Approvals/CombatAI01-CoverFire01-OwnerStart01.json).
Read [ProjectState](../../ProjectState.md) first. Prerequisite: delivered MSQ-104
Candidate03/build01 and current source. This bounded early slice consumes current
senses/navigation and does not complete or dispatch full CAI-03/04/05.

Delivered **Candidate02/build01** for owner testing. Native build, 71 original
and 44 affected assertions, and the sole primary review's CFT02-R1/R2 closure
pass. See [controller acceptance](../../CombatAI01-CoverFire01Acceptance.md),
[base handoff](../../CombatAI01-CoverFire01.md),
[correction](../../CombatAI01-CoverFire01Correction01.md) and
[finding closure](../../CombatAI01-CoverFire01Correction01Review.md).
Gameplay, motion, usefulness and feel remain pending owner testing.

## Behavior and implementation

1. Replace rifle rush-to-short-range behavior with an explicit weapon engagement
   profile: effective/preferred range, reaction/aim timing, burst/rest behavior and
   movement intent. Fire from a useful existing range; advance cautiously only
   when useful. A blocked muzzle must select a bounded alternate firing pose or
   cover position, never pursue the player's feet at an 85 cm acceptance radius.
2. Build cover actions from actual static collision geometry and permitted threat
   evidence: a protected anchor, left/right exposure poses and a safe return path.
   Both sides must be evaluated independently and selected by feasibility/usefulness;
   a blocked side cannot disable the valid side. Use actual movement via GASP/Mover.
3. At low cover validate crouched protection and standing fire space, request actual
   stand, wait for achieved stance/stationary aim/muzzle safety, fire a finite burst,
   then crouch into protection. Lateral peeks likewise return after burst, loss of
   useful contact, interruption or timeout. Do not shoot through the cover or fake
   posture via a flag. Gracefully handle a refused stand and invalidated return.
4. Make cover fire usable while engaged, not only when searching. Own loss of sight
   while ducking must not destroy a valid peek plan or create Acquire/Search loops.
   Hidden target movement cannot update proposals/aim. Exposure may seek fresh sight;
   direct launch always requires fresh current visibility and all existing safety.
5. Remove redundant long contact/aim waits. Tune for prompt initial and repeat fire,
   preserve turning, achieved locomotion/stance, reload, ammo, burst pause, physical
   authority and finite-flight launch. Keep clocks in world time. State a source-level
   eligible-shot latency target and distinguish physical/geometry delays from it.
6. Add a compact typed tactical context consumed by the existing selector: weapon
   capability, actual self-health, optional evidence-backed target health, and
   available ally count/composition/capability summaries. Unknown health/support
   must be explicit; no invented omniscient values. Use lower self-health to favor
   protection; known health advantage may favor cautious attack without charging.
   Provide meaningful eligibility/score seams and examples/tests for future inputs,
   not a second planner or a hardcoded branch per weapon/ally combination.
7. Keep bounded geometry work, per-action deadlines, history/backoff and stable
   commitment. Handle no cover, one blocked side, no firing lane, stale evidence,
   stand refusal, route failure and moving threat with useful fallback reasons.
8. Reset/death/disable/weapon loss/living physics interruption invalidate action
   ownership, pending bursts and pose requests. Recovery replans from actual feet.
   Extend existing status/trace with cover phase/side, range/context decisions and
   timing/gate reason, without introducing a parallel observability system.

Player health/death, new weapons/assets, group gameplay/cooperation, suppression,
full navigation, map remodeling and paused art remain outside this slice. The
health extension input must remain honest while player health is absent. Existing
owner edits in Config/DefaultEngine.ini and MeridianSquad.uproject are preserved.

## Acceptance and evidence

The executor implements/self-checks; one primary independent technical reviewer
owns the substantive review. Controller accepts scope, identity and finding closure.

- CF01: valid left and right peeks work as independent choices; the alternate side
  remains eligible when one is blocked. Validate capsule/support/route/return,
  achieved position and current muzzle before a shot. No teleport/physics override.
- CF02: low cover has a real crouch -> achieved stand -> burst -> crouch lifecycle;
  stand refusal/occlusion/no contact cannot fire blindly or wait forever.
- CF03: a visible in-range rifle target does not cause a short-range rush; muzzle
  obstruction cannot become a charge. Out-of-range movement is bounded/cautious.
- CF04: contact and known reacquisition have short explicit eligible-fire deadlines
  without bypassing cadence/reload/turn/stance/stationary safety or slowdown clocks.
- CF05: current sight is mandatory at launch; hidden target relocation cannot alter
  cover choices absent new evidence. Duck/peek visibility transitions preserve
  useful action progress and stale plans expire/revalidate honestly.
- CF06: actual low self-health changes risk preference; unknown target health stays
  unknown. Weapon ranges and injected known health/support contexts have deterministic
  extensible policy effects with capability validation, without spawning allies.
- CF07: reset/death/recovery and geometry/weapon failure clear obsolete ownership;
  work/retry limits and no-cover fallback are finite and diagnostic.
- CF08: native Development Editor build and focused production pure/source fixtures
  pass. Exercise adversarial transitions and actual producer/consumer wiring, not
  only mirrored toy predicates or string-presence assertions. Reuse unchanged evidence.

No agent gameplay, PIE, firing, simulation, gameplay screenshots or performance
probes. Actual cover usefulness, motion, reaction feel and difficulty remain pending
owner play. Read-only geometry/editor checks and guarded build/reload are authorized.
Use official Epic MCP and verify project/map/PIE/dirty state before lifecycle changes;
preserve unsaved assets and a newly active owner session.

## Execution and handoff

One Multica production writer and one editor writer/heavy build at a time.
Astra/max/default, fast disabled, verified in configured and native execution.
Do not dispatch subexecutors or reviewers, change shared profiles/status or commit.
Controller handles those operations and the local verified task commit.

Deliver Docs/CombatAI01-CoverFire01.md with concrete behavior/tuning, changed files,
build/check evidence, limits and owner test route. Store bounded generated evidence
and an immutable candidate manifest (source, DLL, checks; preserved inputs) under
Saved/CombatAI01/CAI-T02/Worker/Candidate01/. Preserve earlier candidates unchanged.
Leave ordinary editor ready on retained lobby with matching DLL when safe, PIE stopped;
report a newly active/dirty owner session rather than disrupting it.
