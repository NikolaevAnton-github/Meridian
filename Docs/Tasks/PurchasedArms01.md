# Purchased arms lobby walkthrough

Authorized by the owner's direct request on 2026-09-18. This new scope supersedes
the original-protagonist execution plan: pause that work, roll its changes out of
the active game, and use the purchased arms and animations for a simple lobby
walkthrough. Preserve original character sources, experiments and review evidence
as inactive history. Do not continue BodyRepair01 or its successors.

## Required result

- Keep `/Game/Maps/L_OpeningLobby_PainterStone01` and its current owner geometry,
  materials, lighting, atmosphere and collisions. Existing native on-foot pawn
  and game mode are the starting point.
- Show the owner's purchased first-person arms and one compatible rifle with
  their supplied animations. Reuse the audited subset already under
  `Content/InfimaGames/TacticalFPSAnimations` and untouched source project
  `D:/devgames/Weapon`. This explicitly authorizes stock arms for this temporary
  scope; previous original-art gates do not block it.
- Retain basic walking/looking and appropriate locomotion animation. Keep aiming
  and reloads with synchronized hands, rifle and magazine. Existing jump may stay
  if it remains simple and correctly presented. Exclude shooting, damage, targets,
  inventory, pickups, weapon switching, showcase HUD, demo level, special movement
  and other vendor systems. Use only the asset dependency closure needed here.
- Arms, rifle and magazine cast no dynamic, static, hidden or contact shadows.
  No body or detached-body shadow is present. Apply this to runtime components,
  rather than disabling lobby shadows globally.
- Move unused original protagonist native development assets and unused migrated
  pack assets outside active `Content` into a bounded, hash-manifested archive
  under `Assets/Archive/PurchasedArms01/`. Preserve their bytes and relative paths;
  do not delete original sources, owner changes, history, or the vendor project.
  Inspect references before moving; retain required dependencies. Remove only
  original-character-specific startup/config/plugin hooks after inspecting their
  actual use. Avoid bulk Git reset, clean or reverting unrelated config edits.

## Implementation and verification

One production writer through the existing Multica Unreal executor, verified
Astra/max/standard. Read ProjectState, this task, the scoped owner record and the
existing animation audit/harness. Read the inventory supplied by the controller.
The canceled MSQ-54 run is historical context, never a continuation instruction.
No new paid service, new asset generation, original-character repair or lobby
architecture work. Keep the project below 250 GB and avoid duplicate worktrees.

Before changes, record relevant current hashes and Git status. Preserve a bounded
rollback snapshot of any changed binary map/assets. Keep the current map bytes
unchanged if native pawn changes suffice. Use official Epic MCP for editor work;
start the existing UE 5.8 editor if necessary and verify live project/PIE state.

Compile the changed game code. Test actual PIE spawn, normal WASD/mouse input,
walking and collision, idle/movement animation, aim press/release, reload completion
and return to locomotion, aiming reload behavior and repeated action recovery.
Verify evaluated component transforms/animation states and no-shadow flags in PIE.
Capture comparable actual first-person idle, movement, aim and reload views and
inspect them for camera framing, visible wrists, rifle alignment and magazine
synchronization. Check unsupported keys do not trigger vendor gameplay. Check
active dependency closure and missing references after pruning; reopening the
project must start the retained lobby and use the new pawn presentation.

Deliver `Docs/PurchasedArms01.md`, exact controls, scoped file list, preservation
and pruning manifests, test results and screenshots under `Saved/PurchasedArms01/`.
Leave the retained lobby ready for owner Play. Controller owns independent review,
Multica administration, final local task-scoped commit and owner handoff. Worker
must not commit or change unrelated documentation/configuration. A diagnostic-only
handoff is insufficient; complete and verify the playable result.
