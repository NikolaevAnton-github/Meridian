# LobbyPlaytestFix01: rifle interruption and complete demo assortment

2026-09-25. Authority: [owner playtest request](../Approvals/LobbyPlaytestFix01-OwnerStart01.json).
Candidate01 builds on MSQ-149 Candidate01 / Build03 in the retained lobby.
Multica owns current task status and issue identity.

## Objective and scope

Fix the owner's intermittent loss of firing in automatic and semiautomatic modes.
Establish the real cause before changing behavior: check held/released input,
cadence, finite ammunition, reload/mode transitions, launch safety, focus and UI
capture as evidence warrants. A normal blocked muzzle or empty magazine must remain
safe; fixing a latch must not bypass collision or grant ammunition. Use the
debugging-code skill when source/logs cannot establish actual runtime state.

Expand `/Game/Maps/L_OpeningLobby_PainterStone01` from its three NGD specimens to
the distinct ready-made destructible objects in the actual vendor demo. Inventory
the demo-map instances and their configured data assets/overrides, reconcile with
the catalog, and state explicitly what constitutes complete coverage. Reuse vendor
behavior and existing adapters. Do not copy every duplicate demo instance or demo
lighting/architecture. Include meaningful material/breakable variants. Preserve
scale and use available side bays/space without blocking the retained central route.

## Sources and boundaries

- `Docs/Subsystems/Weapons.md`: weapon entrypoints and timing contracts.
- `Docs/NextGenDestructionIntegration01NGD01.md`: current integration and evidence.
- `Docs/Approvals/NextGenDestruction01-LobbyScope01.json`: preservation boundary.
- `Docs/OpeningLobbyDeferred01.md`: retained owner architecture where needed.
- Source assets: `/Game/NextGenDestruction`; current lobby only for delivery.
- Existing harness: `Scripts/NextGenDestructionIntegration01/`.

Before mutation, verify live project/editor/bridge, record dirty packages and
capture recoverable current lobby state, original actor properties and protected
owner-file hashes. Pre-existing owner changes: `Config/DefaultEngine.ini`,
`MeridianSquad.uproject`, untracked `Docs/EnvironmentDestruction01ED02.md`.
Preserve their exact current bytes and all vendor originals. Never load a historical
map over live owner edits. One editor writer and one heavy build at a time.

Allowed production writes: relevant weapon/input code and minimal NGD integration
corrections under `Source/MeridianSquad`, current lobby map, focused scripts under
`Scripts/LobbyPlaytestFix01`, this task, `Docs/LobbyPlaytestFix01.md`, and generated
evidence under `Saved/LobbyPlaytestFix01/Candidate01`. Necessary shared-script edits
must be justified and bounded. Controller owns approvals, ProjectState and commits.
No vendor package edits or successor-task implementation.

## Acceptance and delivery

1. Evidence identifies the interrupted-fire cause, with a before/after reproduction
   of the actual input path where possible; public API-only tests do not prove input.
2. Sustained auto, repeated semiauto, release/repress, empty/reload, mode switching
   and relevant obstruction recovery work at normal time and affected slowdown
   transitions (world/bullets/rifle 0.25; player movement 0.65). Keep normal cadence,
   ammunition and blocking safety. Check focused affected behavior, not old matrices.
3. Source-demo inventory maps every distinct requested specimen to a saved lobby
   instance, source/configuration, scale and transform. All render in the lobby;
   representative rifle/destruction and F6 reset work, with variant-specific checks
   only for distinct integration risks. No overlaps or obstruction of circulation.
4. Build and focused checks pass; preserve vendor and original owner state. Record
   exact candidate/map/build fingerprints, warnings, limits and pending owner play.
5. Stop PIE after verification and leave the saved expanded lobby open. Provide
   concise handoff, evidence index and local change list; do not commit. The later
   [owner waiver](../Approvals/LobbyPlaytestFix01-ReviewWaiver01.json) removes the
   independent technical review for this task; controller closes verified delivery.

## Executor delivery

Candidate01 / Build02 is implemented and self-checked on 2026-09-25. The firing
interruptions are reproduced and corrected; all 14 distinct default-demo specimens
are saved in the retained lobby. Exact results, preservation evidence, warnings,
fingerprints and review scope: [candidate handoff](../LobbyPlaytestFix01.md).
Controller scope/evidence acceptance passed. MSQ-153 was cancelled before execution
under the owner waiver. Owner play/layout acceptance remains pending. The controller
owns the local closure commit and task status; no successor task is dispatched.
