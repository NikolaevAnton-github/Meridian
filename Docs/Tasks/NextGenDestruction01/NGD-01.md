# NGD-01: Demo breakable props in the lobby with our rifle

Multica issue: **MSQ-149**. Parent: [MSQ-74](../EnvironmentDestruction01.md).
Updated 2026-09-25; Candidate01 / Build03 technically complete under
[NGD-01 start and review waiver](../../Approvals/NextGenDestructionIntegration01-NGD01-OwnerStart01.json).
Controller scope/evidence acceptance passed; see the
[delivery and controls](../../NextGenDestructionIntegration01NGD01.md).
Owner visual/play acceptance remains separate; successors are not dispatched.
Authority and shared rules: [toolkit integration plan](../EnvironmentDestruction01Plan.md)
and the later [owner lobby scope](../../Approvals/NextGenDestruction01-LobbyScope01.json).
Prerequisites: MSQ-68, MSQ-82, [accepted migration](../../NextGenDestruction01.md).

## Work

Deliver a small playable set of ready-made breakable props from the imported demo
directly in `/Game/Maps/L_OpeningLobby_PainterStone01`. Start with one source to
verify the weapon connection, then place approximately three to five existing props
in available lobby space during this same task. Record the chosen packages,
materials, supported break states and instance transforms. Reuse existing behavior;
custom asset production and a separate test/laboratory map are not first-pass work.

Use the current MeridianSquad player/rifle. Confirm live engine/project/bridge and
the actual current lobby before edits; inspect vendor damage entrypoints. Capture
the saved/unsaved owner state and a recoverable pre-change map snapshot under Saved.
Preserve architecture, materials, lighting, existing actors, routes and player start.
Add identifiable removable instances in a dedicated folder or equivalent grouping.
Keep vendor originals unchanged; make task-owned asset derivatives only where a
required integration edit would otherwise modify them. Never restore old map bytes
over current owner work. No new or duplicate gameplay map is the handoff target.

Connect the existing projectile/hit path through a narrow adapter to toolkit damage.
Record damage/impulse/anchoring choices and prevent duplicate damage for one hit.
Declare localization and fracture granularity; extend only a demonstrated gap.
Keep finite-projectile launch safety and existing self-hit/timing behavior.
Begin object identity, changed bounds, collision revision and reset-generation
notifications; NGD-02 finalizes the gameplay/support contract.

## Acceptance

- Opening the actual lobby with the MeridianSquad player lets the owner reach and
  shoot the placed demo props. Each selected prop type breaks through the real
  rifle path; demonstrate the full shot/blocking loop on one representative source.
- Intact geometry blocks a witness target. After a declared opening, a subsequent
  shot whose real sweep fits reaches it; a shot at remaining solid geometry stops.
  If the selected source cannot support this bounded test, select a suitable
  existing vendor source and record why, without inventing accepted new art.
- The breaking bullet is consumed by the intact obstacle; no double hit/damage or
  unintended intact-material penetration. Visual state and blocking collision agree.
- A bounded repeat/reset returns the initial object and clears stale blockers and
  callbacks. Basic significant-fragment collision works; detailed lifecycle is NGD-02.
- The lobby keeps its existing architecture and usable circulation. Record added
  actors/transforms and before/after views; the placement is removable without
  rebuilding or rolling back owner work. The placed props remain available to play.
- Handoff names the actual lobby, source/derivative and actor set, controls,
  candidate, observed states, adapter entrypoint, limits and evidence for NGD-02.

The owner waived independent review for MSQ-149 in its new task-scoped start.
Executor self-checks and controller scope/evidence acceptance apply; owner visual/play
acceptance remains separate. This placement is gameplay testing, not final dressing acceptance.
No new AI, layered-column reconstruction or broad density/performance pass.
Evidence: `Saved/NextGenDestructionIntegration01/NGD-01/<candidate>/`.
