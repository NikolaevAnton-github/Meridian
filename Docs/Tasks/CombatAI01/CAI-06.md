# CAI-06: Arcade pressure and player-facing cues

Multica issue: **MSQ-108**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-107.

## Package work and acceptance
**Purpose:** make group aggression readable and sustainable before richer maneuvers.
Size/risk: medium implementation, high subjective tuning. Depends on CAI-05.

Work:

1. Define observable pressure inputs and a small grant/delay policy for new fire and
   aggressive-movement commitments. Keep existing bullets and immediate safety intact.
2. Add start-of-fight lead-in, limited simultaneous dangerous directions and a useful
   cue/reaction interval for a newly appearing offscreen threat.
3. Implement camera-based fairness restriction as a post-selection start gate. Its
   true player position cannot enter enemy memory, utility scores, proposed routes or
   aim points. Expose only grant/wait to the executor, with a useful waiting fallback
   selected from permitted evidence. Detailed gate reasons remain debug-only.
4. Stagger bursts, reloads and maneuvers through real commitments. Agents waiting for
   permission still search, improve position or observe a useful sector.
5. Add event-bound cue records for contact, search, move, reload and interruption.
   Reuse suitable existing audio where available; attach barks only to actual states.
6. Bound repetitions/overlap, cancel stale cues and preserve source location. If voice
   assets are unavailable, prioritize audible movement/weapon cues and record the
   missing voice-production requirement separately.
7. Expose a compact tuning profile: reaction, burst rhythm, pressure overlap, cue lead-in
   and maneuver frequency. Physical recovery profile remains independently tunable.

Acceptance: S15/S16 plus affected S09/S11/S23. An attack permit cannot force a shot
without its mode-specific sight or evidence-region authorization and shared physical,
weapon, muzzle, friendly-lane and geometry gates. Revocation prevents new launches without
canceling existing bullets. The player gets observable counterplay for a new threat.

Owner route: fight the three-enemy encounter, turn away from a relocating enemy, reload
and move during a pressure transition. Record whether the openings feel natural and
whether danger was understandable. Debug captions cannot prove final cue quality.

## Execution and verification contract

Prepared only: backlog, unassigned, no run. Dispatch requires a later execution
instruction under the standing project workflow. Read `Docs/ProjectState.md` first,
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
Commit verified task-scoped changes locally with the real MSQ task ID before handoff.
