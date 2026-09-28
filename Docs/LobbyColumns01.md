# LobbyColumns01

The subsequent [LobbyColumnsPerf01](LobbyColumnsPerf01.md) removes repeated
blocker lookups and full updates of pristine stationary cladding. Its focused
PIE checks preserve the destruction/reset behavior documented here.

[Owner scope](Approvals/LobbyColumns01-OwnerScope01.json): direct implementation,
without a Multica task or independent review. The central accepted demo is the
reference and remains unchanged. Only read-only source research was delegated.
The older [MSQ-156](ReinforcedColumn02.md) and [rev13](ColumnRelief06.md) remain
separate preserved candidates.

## Delivered scene

- Twelve 240 x 240 x 840 cm low columns and four 240 x 240 x 1800 cm tall columns
  retain their positions. All sixteen share the accepted demo's destruction
  behavior, protected core, facing fractures and 80-piece per-instance retention.
- A derived collection covers Z=0..840 cm at unit scale. It preserves 486 lower
  fragments and cuts only the 42 fragments intersecting the height boundary,
  yielding 528 concrete leaves and 768 facing pieces. Only 44 facing pieces need
  boundary crops; unchanged source meshes and ceramic shards are reused.
- The four tall upper sections, Z=840..1800 cm, use a static concrete core and
  the reference facing geometry/UVs. Their upper sections do not fracture.
- Reinforcement spans Z=-30..840 cm, calculated from the vendor mesh's actual
  bounds. The new data-asset route applies this placement after F6 as well.
- The existing 40 cm floor slab stays continuous. Its sixteen column footprints
  expose the same inner-concrete material used by the reference, without the
  decorative finish. Both dark floor strips are cut out under the tall columns.
  Floor finish outside these footprints is preserved.
- The old RC01 insert overlapping one tall column is removed from the scene;
  its source assets and prior candidates remain preserved.

Source layout: `Assets/Source/LobbyColumns01/layout.json`. Derived resources:
`/Game/OpeningLobby/LobbyColumns01/`. Authoring and checks:
`Scripts/LobbyColumns01/`. The generator reads the preserved Correction04 tile
source; native authoring crops Correction08 and remaps tile support to new bones.
The original reference assets are never edited. Runtime routing recognizes only
the new data path; the central specimen keeps its original path and behavior.

## Verification

Evidence and the pre-edit map are in `Saved/LobbyColumns01/`, outside Git.

- Development Editor build `compile02` passed and was loaded in a fresh editor.
- `scene-verified.json`: all sixteen concrete sections end at 840 cm; all rebar
  bounds are -30..840 cm. The central actor and every unrelated actor retain their
  labels, paths, transforms, tags, meshes and material overrides. No dirty packages
  remain. Material-aware collision rays confirm concrete under all sixteen
  footprints, no strip coverage there, and unchanged finish on an outside sample.
- `low03`: ten real rifle shots at Z=22 and 810 cm damaged facing and released
  concrete at both heights. F6 restored all 768 facing pieces.
- `tall01`: ten shots damaged the same two lower heights; five further shots at
  890 cm hit the static upper section without changing lower destruction state.
  Collision sweeps distinguish the lower managed prop from the static upper mesh.
- All sixteen replacements remain ready after three F6 resets, with 768 facing
  pieces each and correct rebar bounds. Sampled protected-core movement,
  unsupported facing, debris inside the core and retained bodies resuming
  simulation are zero. `analysis.json` records these checks.
- Captures: `low03-damage.png`, `tall01-damage.png`, `editor-final.png`.
  PIE is stopped, the original editor camera is restored, and background throttling
  is restored. The project footprint scan measured 121.1 GiB before the closure
  commit, with ample room for its approximately 212 MiB of new LFS assets.

`low01` is excluded: background editor throttling produced 0.333-second frames,
exceeding the existing projectile overload guard, so its input presses generated
no shots. Native debugging reached FirePressed and PrepareTimingFrame with
CanAct=true, bAllowedAtFrameStart=true and bTimingBarrier=false. The live projectile
state then recorded 565 overload frames. Disabling background throttling for the
probe restored normal frame durations and all 25 planned shots. `low02` is also
excluded: ammunition setup ran before the previous release input was sampled;
the helper now allows a frame before that setup. No weapon code was changed.
Temporary breakpoints were removed and the debugger detached; all eight original
exception breakpoints, including five enabled, were preserved.

A Rider viewport capture terminated the editor after a successful saved-scene
check. Capture was moved to the verified Epic MCP path, followed by a fresh
editor load and the passing scene/runtime checks above. That failed capture is
not acceptance evidence. This is a functional check, not a whole-lobby performance
benchmark; per-column debris budgets multiply across simultaneous destruction.
