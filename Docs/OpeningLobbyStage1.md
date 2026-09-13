# Opening lobby: Stage 1 handoff

MSQ-5 provides a saved spatial prototype for the owner's layout and movement
review. Stages 2 and 3, final materials, combat and narrative events are outside
this handoff.

## Open and play

Open `/Game/Maps/L_OpeningLobby` and use **Play > Selected Viewport** with
**Default Player Start**. Click the game viewport to capture input. WASD walks,
the mouse looks, Space jumps, Escape ends PIE, and Shift+F1 releases the cursor.
The map sets `OpeningLobbyGameMode`, which possesses `OpeningLobbyCharacter`.
Both the game default map and editor startup map point to this lobby.

The interior is 36 m along X, 22 m along Y, and 8 m high. The entrance is at
negative X and the three closed prototype elevator doors are at positive X.
Eight columns have 1 m shafts, 1.5 m bases and 7 m longitudinal spacing.
The central aisle is 8.5 m clear between column bases, with approximately
5 m side aisles. Security pedestals flank the entrance axis; reception is on
the positive-Y entrance side. All upper-floor and entrance boundaries are
closed prototype geometry, without a narrative explanation.

The capsule radius is 34 cm and half-height is 88 cm. The camera is 170 cm
above the capsule bottom, approximately 172.15 cm above a flat floor because
CharacterMovement maintains a 2.15 cm floor gap. Horizontal FOV is 90 degrees,
walking speed is 360 cm/s, step height is 35 cm, and gravity is -980 cm/s².
Jump velocity is 320 cm/s. The camera has no head bob or motion blur.

## Implementation

- `Source/MeridianSquad/OpeningLobbyCharacter.{h,cpp}`: capsule, camera,
  movement, input bindings and PIE-only key injection for verification.
- `Source/MeridianSquad/OpeningLobbyGameMode.{h,cpp}`: the default pawn.
- `Config/DefaultInput.ini`: WASD, MouseX/Y and Space mappings. The existing
  EnhancedInput classes support these minimal legacy axis/action bindings.
- `Scripts/OpeningLobby/build_lobby.py`: original box-based construction,
  explicit BlockAll collision, eight material families and lighting. It
  refuses to overwrite an existing lobby map.
- `Content/OpeningLobby/Materials`: flat prototype floor, border, stone,
  wall, ceiling, metal, opaque dark-glass placeholder and emissive materials.
  The existing engine cube supplies geometry; the map defines the original
  layout. The film reference is not imported as content.

Lighting uses 15 movable point lights, ceiling emissive panels, Lumen and
manual exposure with bias -4 and physical camera exposure disabled. Material
families and circulation are assessable, but this is not the realistic art
milestone. The dark-glass material is intentionally opaque at this stage.

## Reproduce the checks

The tools extend the installed Epic ToolsetRegistry; they are not a separate
service or task dispatcher. In the editor Python console, add the project's
`Scripts/OpeningLobby` directory to `sys.path` and `import stage1_tools`.
The run bootstrapped this registration through Rider Python; all construction,
PIE session changes and verification commands then used Epic MCP. Rider was
also used for read-only API diagnostics and tool-module reloads.

1. Open the saved lobby and call Epic
   `Game.Scripts.OpeningLobby.stage1_tools.OpeningLobbyStage1Tools.inspect`.
2. Call `EditorToolset.EditorAppToolset.StartPIE` with `bSimulate=false`,
   `playMode=PlayMode_InViewPort`, `startTransform=null`, `warmupSeconds=2`.
3. Call the lobby tool `begin_verification`, then collect
   `verification_status` until `done=true`. Keep the editor in the foreground
   to avoid its background CPU throttle. The caller must remain active and
   collect the result; do not end an agent run while checks are active.
4. The test in `Scripts/OpeningLobby/verify_lobby.py` injects W/A/S/D, mouse
   deltas and Space through `PlayerController::InputKey`. It does not teleport,
   set actor transforms, move an editor camera, or call AddMovementInput
   directly. The normal bindings drive CharacterMovement on real PIE ticks.
5. Call `StopPIE`. For a plan image call `overview_plan(enable=true)`, capture
   `overview`, then call `overview_plan(enable=false)` to restore the ceiling
   and editor camera. Do not save while temporary plan visibility is active.

For the destination view looking back toward the entrance, start PIE and call
`begin_view_capture`, collect its status, then stop PIE. Its separate evidence
uses the `view-runtime-` prefix. The saved elevator image was captured this way
at approximately X=1466 cm with a 160-degree yaw, after the complete acceptance
route had already passed.

The injected events verify the controller/binding/movement pipeline. The
controller separately reopened the saved map and confirmed OS mouse capture
with yaw and pitch changes through the Windows window API. A brief OS W key
tap produced no measured movement sample; sustained physical WASD input and
subjective sensitivity remain for the owner's manual check. The Windows check
ended after external user input and a foreground-window change. No packaged
build or performance acceptance is claimed. The reproducible native build is:

```powershell
& D:/UE_5.8/Engine/Build/BatchFiles/Build.bat MeridianSquadEditor Win64 Development D:/devgames/MeridianSquad/MeridianSquad.uproject -WaitMutex -NoHotReloadFromIDE
```

## Evidence and preservation

Full generated evidence is under `Saved/OpeningLobby/Stage1`: `build.log`,
`construction.json`, `runtime-verification.json`, `runtime-samples.json`,
`entrance.png`, `center.png`, `elevator.png`, `overview.png`, and final state
and disk measurements. Images at the three route locations are from real PIE
camera positions; the overview is an editor top view with the ceiling hidden
temporarily. The final report records each reached waypoint, wall/column
contact, mouse response, jump rise, falling velocity and restored grounding.

The initial editor had four unrelated dirty benchmark materials and no dirty
map. Their unsaved versions were duplicated and saved under
`/Game/Development/PreservedBeforeLobby` before the clean C++ restart. Original
benchmark asset bytes were preserved; `preserved-dirty-materials.json` maps
each source to its saved copy. These copies are preservation artifacts, not
new accepted benchmark versions or registry rebaselines. The pre-existing
`.codex/config.toml` is checked byte-for-byte against the initial SHA-256.

The first verification attempt reached both side routes and stopped at the
wall plinth, but its assertion expected the wall plane 20 cm farther out.
The corrected check uses the actual plinth face. That diagnostic attempt is
retained separately as `attempt1-verification.json` and `attempt1-samples.json`.

The owner should review walking speed, mouse sensitivity, the broad center
aisle, column proportions, security placement and the intended darker final
atmosphere before authorizing modular art production.

## Technical acceptance and usage

Controller acceptance on 2026-09-13 covers the Stage 1 implementation and its
saved-file handoff. Source review and the saved runtime samples confirmed the
full route and return, side paths, grounding, collision and mouse bindings.
The final route check took 55.11 seconds and recorded 499 samples. The wall
stop was Y=1045.90 cm; the column stop was Y=415.90 cm after stepping onto the
base. Jump rise was 52.24 cm, followed by falling velocity and stable landing.

A fresh editor launch loaded `/Game/Maps/L_OpeningLobby` and spawned the same
possessed walking character. The controller's Windows mouse test changed yaw
by about 17.50 degrees and pitch by -8.75 degrees. Its separate evidence is
`Saved/OpeningLobby/Stage1/Controller/windows-input.json`. The editor is left
open on the lobby with PIE stopped and no dirty packages. The worker-launched
editor disappeared after the Multica run completed; the controller reopened
the saved project independently. This lifecycle behavior should be considered
when a future worker must restart an editor and leave it running.

All pre-existing tracked asset bytes, `AGENTS.md` and the pre-task
`.codex/config.toml` match the controller baseline. The project config's existing
owner change is preserved. A generated AndroidFileServer token line was removed
before staging. Preserved dirty benchmark copies remain explicitly separate
from accepted benchmark assets and the asset registry. Stage 1 drafts were not
registered as final lobby assets.

The measured net project increase was 28,084,159 bytes (about 26.8 MiB) at the
worker cutoff, including generated data and evidence then present. Subsequent
controller reports and local Git/LFS storage add a small amount. The measured
project size was approximately 9.01 GiB, below the 250 GB cap.

One Multica implementation run completed in 21m 15s using Astra, medium
reasoning and standard speed. Internal diagnostic attempts and capture
corrections are included in this run; they are not omitted from usage.

| Measurement | Tokens |
| --- | ---: |
| Native input, including cache | 5,342,348 |
| Cached input subset | 5,197,440 |
| Uncached input | 144,908 |
| Native output, including reasoning | 29,586 |

Native output already includes 6,118 reasoning tokens. Multica 0.4.43 reports
35,704 output because it adds that reasoning component again. The existing
accepted accounting parser reconciled the completed run with the API data;
details are in `Saved/OpeningLobby/Stage1/Controller/native-usage.json` and
`native-usage-details.json`. Controller/reviewer usage is recorded separately
in `controller-usage.json`. These counts are model activity, not a dollar or
remaining subscription-quota measurement.

The controller and independent reviewer snapshot at 14:24:50 UTC contains
9,990,341 input tokens, including 9,736,320 cached; 254,021 uncached input and
29,954 output tokens. It covers this task from its native turn start and excludes
the Multica worker. It is a lower bound while final reporting continues. Frequent
status and review turns contributed substantial controller activity; worker
usage alone would understate the task's subscription usage.

The new map and eight materials total 287,645 bytes; preserved dirty-material
copies total 47,868 bytes. All four original benchmark material hashes and the
Codex configuration hash match preflight (`preservation-check.json`). Binary
assets are stored through the existing Git LFS rules.
