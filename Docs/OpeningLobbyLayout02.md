# Opening lobby Layout02

Current disposition on 2026-09-14: MSQ-9 is cancelled as a rejected prototype,
superseded by the scale drawings in MSQ-10 and accepted Layout03 scale in MSQ-11.
It is not queued for another run. See [the scoped scale decision](Approvals/LobbyLayout03-Scale01.json).
The preserved handoff below describes the historical submission and its gates.

MSQ-9 implements a walkable prototype from the owner-approved LobbyArt-Review02
package. Controller technical review passed after the bounded script corrections.
The owner subsequently reviewed MSQ-9 and rejected its architectural scale:
the space must feel monumental and be at least twice as large. Layout02 is not
accepted. Prepare the [scale drawing package](Tasks/OpeningLobbyScaleReview.md)
and follow [independent visual acceptance](VisualAcceptance.md) before more 3D work.
The following handoff and editor state describe the historical submission.
MSQ-6 and MSQ-7 remain unassigned backlog items. Open
`/Game/Maps/L_OpeningLobby_Layout02` and press Play. The map is saved
and left open in the existing UE 5.8.1 editor, PID 25372, with PIE stopped and no
dirty packages. Its game mode is `/Script/MeridianSquad.OpeningLobbyGameMode`.

WASD walks, mouse looks, Space jumps, Escape stops PIE, and Shift+F1 releases the
mouse. The existing native character, bindings, 360 cm/s speed, 34 cm capsule
radius, 88 cm half-height, gravity and 90-degree FOV remain unchanged. Runtime
eye height is approximately 172 cm above the floor, including floor separation.
The project default-map configuration was not changed.

## Spatial interpretation and review limits

All three approved PNGs were inspected visually before construction. The owner
reference pair defines opposite ends of one hall; the Review02 oblique image
defines the checkpoint relationship. Their approved SHA-256 hashes still match.
The following are implementation estimates, not exact dimensions recovered
from the images.

| Element | Prototype estimate |
| --- | --- |
| Interior envelope | 30 m long, 12 m wide, 9 m central height |
| Central clear span between piers | 5.6 m |
| Square piers | 1.2 x 1.2 m, 4.2 m shaft height; six symmetric pairs |
| Longitudinal bay pitch / clear gap | 4.2 m / 3 m |
| Each continuous side aisle | 2 m clear width, 4.6 m ceiling height |
| Heavy longitudinal lintels | 1.2 m wide, 1.4 m high, underside at 4.2 m |
| Inner opaque door leaf | 1.04 m wide, 2.18 m high |
| Entrance glazing | 2.6 m wide; lower entry field 2.64 m high, upper field 6.2 m |
| Detector passage | 1.14 m clear width, 2.28 m clear height |
| Screening station body | 0.85 x 2.2 m, 0.96 m high |
| Parallel black floor strips | Two 0.32 m strips, centered at Y +/-1.1 m |

X increases from the entrance at -15 m to the inner end at +15 m. Pier centers
are at X = -10.5, -6.3, -2.1, 2.1, 6.3 and 10.5 m, Y = +/-3.4 m. Side-aisle
route centers are Y = +/-5 m. The detector is at X=-12.3 m, Y=-1.05 m; the station
is at Y=+0.95 m, therefore left of the detector when looking toward the entrance.
There is room behind the checkpoint to cross between either side aisle and the
detector. Only the single inner door is represented; its destination is undefined.
The entrance and inner boundaries remain closed beyond the lobby.

The two end-view captures retain the same ordered pier rhythm, higher central
volume, narrow side aisles and aligned black strips. The reverse view confirms
the tall entrance glazing and left-hand station; the oblique view shows the
human-scale detector and its passage. These are prototype proportions awaiting
owner review, not acceptance of final architecture.

The scene contains 140 actors and eight dedicated material families. Materials
use simple constants, without a texture pipeline. Dark stone has no marble
veining, the green-grey floor has simple flush joints, and glazing uses an opaque
emissive placeholder with mullions. Lighting uses cool side strips and movable
fill lights; visible light pools and simple specular highlights remain. The
checkpoint is schematic rather than a functional screening system. The captured
viewport is 1520 x 1181, unlike the wider reference images, so framing is not
pixel-matched. The security oblique is tighter than its reference and crops the
adjacent column/aisle relationship; the overhead view and verified route provide
that circulation context. No final modules, decorative kit, damage, story events or additional
gameplay were produced.

## Verification and evidence

All evidence is under `Saved/OpeningLobby/Layout02/`.

Review correction checks are isolated in `ReviewChecks/results.json`: 18 identity
cases and 10 cleanup cases passed in the existing UE 5.8.1 PIE session. Project
identity now compares normalized absolute paths with the workspace derived from
`layout02_verification.py`, including direct builder/refinement entry points.
Another workspace with the same project filename is rejected before mutation.
The original identity-validator cases were reused; decorated action bodies were
tested without their Unreal exception wrapper to observe rejection directly.

Verifier completion is idempotent. Key releases, callback removal, throttle
restoration and report writes are independent; cleanup failures are retained in
the report and logged. The checks used real callback registration/removal and
controller key events, with simulated key-release and registration failures,
plus injected unregister/restoration errors, for both prior throttle values.
Normal cleanup also passed. These are focused lifecycle checks, not another
geometry traversal; individual fault-case reports intentionally show failure.
`ReviewChecks/final-state.json` confirms PIE stopped, the saved Layout02 map open,
the expected game mode, no dirty packages or hidden actors, and throttle restored
to true. `ReviewChecks/preservation-after.json` compares the map, materials,
Stage1 evidence and successful Layout02 route/captures with pre-check hashes.
The controller independently confirmed the saved editor state after the worker
exited, and verified that AGENTS.md returned to its exact pre-dispatch hash.
See `Controller/final-editor-state.json` and `Controller/final-preservation-audit.json`.

| Evidence | Meaning |
| --- | --- |
| `construction.json` | Estimated dimensions and measured bounds of every blocking box |
| `runtime-verification.json` | Passed: 35 real-input steps, 109.406 seconds |
| `runtime-samples.json` | Timestamped possession, movement, grounding and input samples |
| `view-runtime-verification.json` | Passed: final appearance capture route, 29.625 seconds |
| `view-runtime-samples.json` | Final capture route and eye-level camera states |
| `view-entrance-to-inner.png` | Final entrance-side view toward the small inner door |
| `view-inner-to-entrance.png` | Final reverse view toward entrance and checkpoint |
| `view-security-oblique.png` | Final checkpoint view from its side |
| `view-center.png` | Final center view |
| `overview.png`, `overview-camera.json` | Overhead perspective plan and capture metadata |
| `reopened-state.json` | Reopened map, correct game mode, clean packages, no hidden actors |
| `preservation-audit.json` | Controller-baseline comparisons and disk accounting |

The complete runtime route verifies initial possession and grounding, mouse yaw
and pitch, entrance-to-inner-door travel, both full side aisles, return routes,
checkpoint traversal in both directions, wall and column blocking, and a jump
with falling and landing. All movement uses the existing `probe_key` controller
input-event path on real PIE ticks. No pawn teleports or direct movement calls
are used. Map identity strips `UEDPIE_<number>_` before comparison and rejects
the wrong map or unpossessed/wrong-class pawn before sending input. World-space
movement steps require control yaw zero; all rotations use mouse events.
Eight offline checks against the actual identity-guard function passed, including
wrong-map, similar-name, missing-possession and multi-digit PIE-prefix cases;
results are in `identity-checks.json`. Python compilation and the verifier's
Git whitespace check also passed.

Collision expectations are derived from `get_actor_bounds` of the blocking
geometry and the live capsule radius. With a bounded +/-3 cm tolerance, the
wall face at Y=600 cm predicts capsule-center Y=566 cm; observed Y=565.900 cm.
The column face at Y=280 cm predicts Y=246 cm; observed Y=245.900 cm. Both held
inputs stop with negligible lateral velocity. Jump rise was 52.244 cm, followed
by negative vertical velocity and a grounded landing at the original height.

The first run timed out because the existing editor was minimized and throttled
to approximately 3 Hz, causing route feedback to overshoot. It is preserved in
`Attempts/01-BackgroundThrottle`. The same editor window was restored; the
verifier temporarily disables background CPU throttling in memory, then restores
its original value on completion, without saving preferences. A
read-only final diagnostic confirmed background CPU throttling restored to true
and the absolute project path `D:/devgames/MeridianSquad/MeridianSquad.uproject`.
A preliminary
lighting capture route is preserved in `Attempts/02-LightingReview`. The full
passing runtime report and unprefixed captures precede the material/light-only
refinement; the final `view-*` captures and route use the final saved appearance.
Blocking geometry was unchanged by appearance refinement.

For the overhead plan only, ceiling slabs, high side walls above the piers and
lintels were temporarily hidden. Visibility, editor camera and game-view state
were restored before saving and reopening. Collision and dressing remain
separate: `Layout02/Dressing` uses `NoCollision`; structure, piers and security
passage use their explicit blocking boxes.

## Reproduction

Use the same project and editor. The official Epic MCP is available at
`http://127.0.0.1:8000/mcp`. Do not start a duplicate editor. If the custom
toolset is not registered, execute this once in the editor Python console
(Rider was used only for registration and read diagnostics during this task):

```python
import sys
sys.path.append('D:/devgames/MeridianSquad/Scripts/OpeningLobby')
import layout02_tools
```

Discover `Game.Scripts.OpeningLobby.layout02_tools.OpeningLobbyLayout02Tools`
with Epic `describe_toolset`. Its `action` tool accepts `{"operation":"inspect"}`.
Verify the target map, project, PIE and dirty-package state first. Start PIE via
`EditorToolset.EditorAppToolset.StartPIE` with:

```json
{"options":{"bSimulate":false,"playMode":"PlayMode_InViewPort","warmupSeconds":1}}
```

Call `action` with `{"operation":"verify"}` for the complete runtime route, or
`{"operation":"views"}` for the shorter final-view route, each from a fresh PIE
session at PlayerStart. Collect `{"operation":"status"}` until `done` is true
inside the same foreground agent turn. Then call the native `StopPIE` tool.
Keep the editor window restored, not minimized. Archive earlier evidence before
an intentional rerun; normal and alternate runs have separate filename prefixes.

With PIE stopped, `overview`, `capture_overview`, `restore`, and `save_reopen`
are sequential `action` operations. Always restore inspection state before saving.
`build` invokes `Scripts/OpeningLobby/build_layout02.py` and refuses to overwrite
an existing map. `refine` reapplies its final dedicated material/light constants.
`layout02_verification.py` contains the revision coordinates and collision data;
`verify_lobby.py` remains the shared verifier, with Stage1 as its default.
`stage1_tools.py`, including its historical preservation manifest paths, is intact.

## Preservation and resources

Final controller-baseline verification found all 35 Stage1 evidence files
unchanged, all three approved images unchanged, and 142 of 143 project-baseline
files unchanged. The intended existing-file change is
`Scripts/OpeningLobby/verify_lobby.py`. The original worker audit recorded the
temporary Multica-injected AGENTS.md block as a mismatch; after both runs exited,
AGENTS.md matched its original hash. The raw worker audit remains preserved.
The correction run preserved the map, materials and successful route/captures;
only the transient `latest-state.json` snapshot refreshed during inspection.
These comparisons precede the controller's final task-status documentation edits.
The pre-existing `.codex/config.toml`, original map/materials, input/movement,
default-map configuration, concept metadata, benchmark sources and registry
remain byte-identical to the controller baseline.

Measured project size after both runs is approximately 9.89 GB, with about 86 MB
growth during the task, including generated logs/runtime data. Dedicated map, materials and
evidence occupy approximately 26 MB; measured byte counts are in the final
controller audit. Usage accounting for both Multica runs is recorded separately
from controller/reviewer work under `Controller/worker-usage.json` and
`Controller/controller-usage.json`; native output includes reasoning once.
Directory reparse points are not followed, avoiding duplicate counts of shared
Multica/plugin caches and dependency junctions. This is below the 2 GB lobby and
250 GB project caps. No user assets were removed, no build or paid service ran,
and no asset fingerprints were registered or rebaselined.

New map: `Content/Maps/L_OpeningLobby_Layout02.umap`. New materials:
`Content/OpeningLobby/Layout02/Materials/`. Existing Git LFS rules cover both.
No commits, pushes, status changes, delegation or later-stage work were performed.
