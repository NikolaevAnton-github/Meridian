# NGD-01: MeridianSquad rifle and first toolkit object

Multica issue: **MSQ-149**. Parent: [MSQ-74](../EnvironmentDestruction01.md).
Prepared 2026-09-25; unassigned backlog, no execution authorized.
Authority and shared rules: [toolkit integration plan](../EnvironmentDestruction01Plan.md)
and [owner task rewrite](../../Approvals/NextGenDestruction01-TaskRewrite01.json).
Prerequisites: MSQ-68, MSQ-82, [accepted migration](../../NextGenDestruction01.md).

## Work

Select one existing imported toolkit object/material, identify its package and
supported break states, and create a bounded task-owned derivative fixture. Preserve
vendor originals and original lobby/shared assets. Use the current MeridianSquad
player/rifle, not the vendor pawn/rifle as integration evidence. Confirm live engine,
project and bridge before edits; inspect actual vendor damage entrypoints first.

Connect the existing projectile/hit path through a narrow adapter to toolkit damage.
Record damage/impulse/anchoring choices and prevent duplicate damage for one hit.
Declare localization and fracture granularity; extend only a demonstrated gap.
Keep finite-projectile launch safety and existing self-hit/timing behavior.
Begin object identity, changed bounds, collision revision and reset-generation
notifications; NGD-02 finalizes the gameplay/support contract.

## Acceptance

- In the identified fixture, actual MeridianSquad shots reach the chosen object,
  cause the declared damage/break state and agree with the visible hit position.
- Intact geometry blocks a witness target. After a declared opening, a subsequent
  shot whose real sweep fits reaches it; a shot at remaining solid geometry stops.
  If the selected source cannot support this bounded test, select a suitable
  existing vendor source and record why, without inventing accepted new art.
- The breaking bullet is consumed by the intact obstacle; no double hit/damage or
  unintended intact-material penetration. Visual state and blocking collision agree.
- A bounded repeat/reset returns the initial object and clears stale blockers and
  callbacks. Basic significant-fragment collision works; detailed lifecycle is NGD-02.
- Handoff records exact source/derivative, fixture path, controls, candidate,
  observed states, adapter entrypoint, limitations and reusable evidence for NGD-02.

Use the plan's independent review and owner acceptance gates; old ED waivers do not
apply. No new AI, lobby placement, layered-column reconstruction or population pass.
Evidence: `Saved/NextGenDestructionIntegration01/NGD-01/<candidate>/`.
