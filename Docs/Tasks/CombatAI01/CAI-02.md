# CAI-02: Footsteps, incoming fire and evidence memory

Multica issue: **MSQ-104**.
Parent: [MSQ-101 / CombatAI01](../CombatAI01.md), under MSQ-67.
Prepared 2026-09-23; no implementation started.

Authority: [task preparation](../../Approvals/CombatAI01-TaskCreation01.json).
Read the [implementation plan](../CombatAI01Plan.md) and [design](../../Design/CombatAI01.md).

Hard prerequisites: MSQ-103, MSQ-118.

The later [early tactical delivery](../../CombatAI01-Tactical01Acceptance.md)
provides the current sight-based policy. Preserve its protected-position,
reacquisition, weapon-gate and action contracts while adding sensory evidence.
This prerequisite update does not dispatch MSQ-104.

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
