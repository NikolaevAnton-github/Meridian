# Next Gen Destruction Toolkit: UE 5.8 migration

Owner direction, 2026-09-25: remove the custom destruction work before migrating
the purchased toolkit directly, without creating a Multica task. This supersedes
the previous MSQ-74 / MSQ-140..147 custom laboratory implementation plan.

Source: [Next Gen Destruction Toolkit on Fab](https://www.fab.com/listings/9990252b-cfef-4b64-b99e-89e489e5b16b),
local Epic VaultCache `NextGenD10664f7c91efV3/data`, authored for UE 5.4.
Destination: `/Game/NextGenDestruction` in the existing UE 5.8 project.

## Scope

The custom laboratory map, ED-01/ED-02 content, geometry sources, authoring scripts,
`ADestructibleCladding` and `UED02LabTools` are removed from the active project.
Exact retired bytes and hashes remain outside Git under
`Saved/NextGenDestruction01/RetiredImplementation` and `removal-manifest.json`.
Existing historical reports/approvals and evidence remain historical records.
Original lobby, shared assets, gameplay and unrelated owner edits are preserved.

The vendor content keeps its original package paths. Only its named collision
channel/profiles, seven physical surfaces, demo input mappings and Niagara static
mesh distance-field setting are merged. Project startup map/game mode, renderer,
physics solver iteration counts and owner plugin choices remain unchanged.
Five stale vendor soft self-references under `/Game/ChaosSetup` were repaired
through Unreal's `rename_referencing_soft_object_paths`; no binary patching or
placeholder assets were used.

No placement in the lobby or connection to the MeridianSquad weapon damage path
is included in this migration. The vendor demo maps provide the initial handoff.

## Validation

Evidence: `Saved/NextGenDestruction01/`. The source build passed after removal.
UE **5.8.3-58210709** loaded and resaved all **481 assets**, compiled all
**24 Blueprints** to up-to-date status and opened all **four maps**. The initial
conversion report records five stale soft references; the subsequent
`dependencies-after-resave.json` closes those findings with zero missing hard or
soft dependencies.

The default demo entered PIE with its vendor pawn, 21 breakable actors and a
successful rifle pickup. Automated firing verification was interrupted by the
owner's Escape key before the shot; no measured break/fragment result is claimed.
The owner subsequently inspected the demo and accepted the migration on
2026-09-25: "I looked, everything is good." This is acceptance of the imported
package, not approval of future lobby destruction design or integration.

Independent technical review: `Saved/NextGenDestruction01/review-notes.md`.
It verified the retired implementation's 539 files and preservation of 5,874
existing project files except the intended config additions. The measured local
project footprint was 58.1 GiB, excluding reparse-point aliases.
Reproducible editor conversion/check: `Scripts/NextGenDestruction01/validate.py`.
Open `/Game/NextGenDestruction/Maps/DemoMap` to use the vendor demonstration.

## Subsequent planning

The owner subsequently authorized a [task rewrite](Approvals/NextGenDestruction01-TaskRewrite01.json).
The [MSQ-74 integration plan](Tasks/EnvironmentDestruction01Plan.md) prepares fresh
MSQ-149..151 for weapon integration, gameplay debris/reset and measured slowdown/load.
The later [lobby clarification](Approvals/NextGenDestruction01-LobbyScope01.json)
places ready-made demo breakables directly in `/Game/Maps/L_OpeningLobby_PainterStone01`
from the first task; all stages use that existing lobby. This does not change the
accepted migration's historical scope or dispatch future implementation.
