# LobbyMaterials-Complete01 / SlabLayout01

The opaque lobby material batch is complete as an author candidate for fresh
independent Review02. All 44 stone components now use glossy large-format slab
materials. The complete census contains 107 lobby components: 101 opaque surfaces
and six existing glazing components. Glazing visual criterion 6 and R1 are
**DEFERRED_BY_OWNER**, not passed. Owner acceptance of these bytes and final
atmosphere remain pending.

## Exact package

- [Identity](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/identity.json)
- [Manifest](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/manifest.json)
- [Manifest verification](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/manifest-verification.json)
- Sole current map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
- Map SHA-256: `c94331250d378e950ac7780c20bfee0e10145990fb28ac300b38c42477b0b62a`.
- [Owner stone direction](Approvals/LobbyMaterialsComplete01-StoneSlabs01.json)
  and [glass deferral](Approvals/LobbyMaterialsComplete01-GlazingDeferred01.json).

The resume performed verification and packaging only. The scene snapshot, native
master and all 44 instance properties match the interrupted run's final evidence.
No map, material, texture, source or geometry was rewritten during this resume.
The current UE 5.8.1 session has the clean current map loaded and PIE off.

## Material and layout

The new `M_Slabs01` master and 44 component-specific instances live under
`/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/`. Editable native source is
the [recipe and HLSL](../Assets/Source/OpeningLobby/MaterialsComplete01/SlabLayout01/recipe.json).
The [44-row plan](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/plan.json)
records original/new bindings, physical bounds, origins, axes and role modes.

| Setting | Final value |
| --- | --- |
| Regular vertical module | 120 cm wide by 240 cm high |
| Joint width | 5 mm |
| Normal recess depth | 0.75 mm; 1.25 mm edge ramp |
| Shared horizontal course datum | World Z = 0 cm |
| Mineral source coverage | Accepted 240 cm world sampling |
| Slab face roughness | Accepted Painter ORM.G directly, outside joint coverage |
| Dielectric specular | 0.4, equivalent F0 0.032 |
| Grout response | Roughness 0.65, face-color multiplier 0.32 |
| Metallic / coat | Accepted zero metallic / no coat |

The 120 by 240 cm module is the controller's working choice, not exact owner
approval of dimensions. Scalar parameters and per-instance origins remain
editable; plane/orientation and role logic are editable in the native graph/HLSL.
Rotation-only building axes and centimetre positions avoid stretched cube UVs.
Dominant geometric planes prevent doubled triplanar joint grids. Derivative
filtering preserves physical joint coverage at distance.

There are 39 regular cladding roles: 18 columns/piers, 17 wall/shell/shoulder
components, two portal jambs and two inner continuation bands. Five roles use
trim-aware cut pieces: two long beams, two thin head/datum strips and the single
composite elevator surround. Horizontal shell surfaces use long-axis cuts. The
elevator's jamb courses switch to head-length cuts above world Z = 420 cm. Narrow
returns retain cut-strip treatment; there is no small rectangular trim grid.

The new native graph samples the accepted stone's three textures read-only.
Its 13 accepted face nodes retain the source response, including mineral normal
strength. No new pixels or Painter project were generated for the joints.
The graph has 28 connected nodes, 441 pixel and 148 vertex shader instructions,
and four samplers. There are no rejected opaque dependencies or newly generated
textures.

The complete opaque batch retains its genuine native Painter ceiling source:
`Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp`, SHA-256
`392a4c5bc63756c6c5ad4771c675715fe354475a2555d23e366e7f8cf963849e`.
Accepted stone, floor and metal sources and their prior regeneration evidence
are linked through the manifest and verified history. Ceiling.spp was checked
against its exact original regeneration identity without another export.

## Visual inspection and limitations

All 16 final native frames were inspected, along with matched before and
representative trial views and both original owner references. The slab grid is
visible on columns, broad walls, terminal walls and returns; horizontal courses
continue across the inspected column corner. Broad walls now carry the column
gloss requested by the owner. The older quieter-wall R2 target is superseded.

Useful matched evidence is under
[Before](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/Before/) and
[Final](../Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/Final/):
`column-corner-90`, `column-face-90`, `broad-wall-90`, `portal-return-90`,
`room-wall-90`, `side-aisle-90`, `trim-head-90` and `whole-hall-90`. Bay, ceiling,
soffit, checkpoint, elevator and both end views provide context.

Existing circular highlights remain strong on walls and columns. At those
highlights fine mineral detail is less legible; shadowed near/return views are
dark, while fine joints remain visible. The ceiling is quieter and the unchanged
charcoal metal stays distinct from green mineral surfaces. Current lighting and
the denser approved architecture differ from the original concept composition;
this pass does not claim final atmosphere or overall architectural likeness.

Mineral sampling intentionally remains the accepted continuous world projection;
there is no randomized per-slab brightness or new mineral variation. The recess
is a shader-normal effect and does not change silhouettes. Still frames and
derivative/filter numerics support joint readability, but do not establish a new
temporal anti-shimmer or performance benchmark. No new author refinement was
needed after the representative trial; no material tuning occurred on resume.

## Verification

| Check | Evidence and result |
| --- | --- |
| Coverage | `coverage.json`: 107 lobby components, 44 stone + 3 floor/strip + 45 metal + 9 ceiling + 6 retained glass; zero proxy/error bindings; one separate unchanged support mesh |
| Authorized scope | `property-preservation.json`: exactly 44 slot-0 differences; 63 nonstone assignments and 13 accepted floor/metal bindings exact |
| Scene preservation | All reflected properties of 128 actors / 149 components exact apart from the scheduled overrides; no geometry, lighting, exposure, gameplay, glass, support or postprocess change |
| Resume | `Resume01/scene-verification.json`: current full scene equals `RestoredFinal`; clean map and PIE off |
| Native assets | `native-source-verification.json` and `Resume01/reused-verification.json`: current master and 44 instances equal final saved/reopened audits; source/capture hashes revalidated |
| Layout | `layout-numerics.json`: physical 5 mm width, equal world-Z phases, column widths, dominant planes and trim modes pass |
| Captures | `capture-verification.json`: 36 matched genuine images, including 16 final and four trial frames; 1920x1080, HFOV90, standing Z172 cm, possessed runtime, metadata and restored settings |
| History | `history-verification.json`: 2,401 entries across seven prior manifests verified, resolving only historical map paths through exact archives |
| Preservation | `Resume01/protected-after.json`: 4,736 checked protected files, no unexplained differences; explicit administrative/runtime/polling exceptions below |

Original `protected-after.json` remains the interrupted failed result. The resumed
authoritative check is **`Resume01/protected-after.json`**. Original failed bytes
and checker source also remain in `Resume01/PreResume/` and the controller's
`SlabsInterrupted01/` archive. `protected-before.json` was never changed.

The two exact controller helper before/after versions are accepted solely through
`Controller/slabs-controller-admin-exceptions.json`: `prepare_slabs_review.py`
and `usage_snapshot.py`. Three `*-current.json` controller polling logs changed
externally. Multica also added the exact 237-byte authorized resume instruction
suffix to its auto-managed Agent Identity in `AGENTS.md`. Removing only that
suffix reconstructs the original 35,059-byte file and SHA-256; the proof and exact
profile links are in `Resume01/runtime-dispatch-verification.json`. This is not
universal byte equality or an unrestricted exception for controller/project files.

The editor had restarted externally before live verification. Epic discovery
showed the helper missing, so the authorized single Rider Python call registered
the existing guarded slab helper only. All subsequent scene state, snapshot and
native graph reads used official Epic MCP. No configuration files were edited.

## Storage and rollback

The pre-freeze no-junction scan measured 13.867 GB project usage and 2.286 GB lobby
usage; complete-batch growth was 440.003 MB. These fit the 250 GB project cap,
2.4 GB lobby ceiling and 450 MB batch plan. Slab-stage growth was 92.249 MB,
exceeding the advisory 80 MB aim; retained captures, snapshots and interruption
evidence are included. No history or user assets were deleted. `storage.json`
contains exact counts, and final verification checks package headroom.

Exact rollback is
`Saved/OpeningLobby/MaterialsComplete01/Controller/BeforeSlabs01/files/Content/Maps/L_OpeningLobby_PainterStone01.umap`,
243,537 bytes, SHA-256
`b4cc37e0dd8281fddd250183c5e878f20fec35babcdefc520d3b09929857cb73`.
Its archive receipt also binds the unchanged Correction03 manifest/identity.
Rollback is recorded only; it was not applied. Historical manifests and old
material/source bytes remain intact.

Fresh independent combined opaque-material Review02 is the next controller
handoff. Glass remains deferred, and no owner acceptance is asserted.
