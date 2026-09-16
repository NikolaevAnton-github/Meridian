# LobbyPainter-Floor01 / WorkerCandidate01

The current lobby now has two new native Painter floor materials, with exactly
three component overrides. Nine authorized obsolete map packages were archived
and removed; `/Game/Maps/L_OpeningLobby_PainterStone01` is the sole surviving lobby
map. This is an author handoff for fresh independent review. The floor pair has
not received owner acceptance; the corrected column stone remains owner-approved.

## Candidate and recovery identity

Exact file identities are in `Saved/OpeningLobby/PainterFloor01/Worker/identity.json`
and its nonempty unique path/bytes/SHA-256 `manifest.json`. The map intentionally
has new bytes following the three slot changes.

`Worker/archive.json` maps all ten original map identities to exact snapshots:
the original clean current map is in `Worker/Before/`, and the nine retired maps
are in `Worker/RetiredMaps/`. The same record preserves the original startup
configuration. Historical manifests were not changed. For their map entries,
resolve the original path through this archive mapping, never against the newly
edited current map. `approved-history-final-verification.json` verifies all 154
entries of the original approved correction manifest through that mapping.

The all-category asset-registry audit found no referencers for any retired map,
no obsolete-map dependency from the retained map, no streaming sublevels and no
external actor files. All nine editor deletion calls returned true and unloaded
their packages, but left disk files. Exact hashes were rechecked before removing
the nine explicit files with PowerShell LiteralPath, without recursive deletion.
The refreshed registry and filesystem contain only the retained lobby map.
All shared assets, owner edits, sources and history remain preserved.

Exactly `GameDefaultMap` and `EditorStartupMap` changed in `Config/DefaultEngine.ini`.
Original line endings and every other byte were preserved. Their live defaults
were synchronized; no SaveConfig or global/project bridge edit was made.
Saved editor MRU/view/command-line history still records old map strings; these
are historical caches, not cook/server/transition map configuration. See
`config-audit.json`, `startup-defaults-live.json` and `map-dependency-audit.json`.

## New materials

`Assets/Source/OpeningLobby/PainterFloor01/Floor.spp` and `Strip.spp` are newly
created Painter 12.1.4 / API 0.3.5 projects. Each contains three genuine native
Fill layers using installed SBSAR building blocks. No smart material, old opaque
asset dependency, rejected pixels or external noise was used. The shared
authoring mesh retains its old texture-set slot name only.

The floor combines a dark green-grey mineral body, broad irregular pale veins,
finer independent fractures and a polished dielectric response. Its projected
tile covers 360 cm. The near-black strips have much finer, restrained mineral
color and roughness variation over a 240 cm tile. Both use 2048 PNG BaseColor,
DirectX Normal and packed ORM. AO is neutral; metallic is zero; polished normals
remain essentially planar. The exact recipes and native readbacks are beside
the .spp sources. `exact-regeneration.json` proves all six final exports reproduce
byte-for-byte after save/reopen and match their canonical import sources.

Both opaque Unreal graphs live exclusively under `/Game/OpeningLobby/PainterFloor01/`.
The scoped adapter reuses existing import, graph, world-projection, channel and
dependency audits. Color phase blending reduces obvious repeated motifs; ORM and
normal use the unchanged physical projection logic. Each graph has 13 connected
expressions and three new texture dependencies. Texture import settings and
shader statistics are recorded under `Worker/Floor/` and `Worker/Strip/`.
The authoritative floor CoverageCm value is 360 in the actual graph audit;
the initial reused authorship report's 240 field was inherited helper metadata.

## Preservation and evidence

Only StaticMeshActor_0 / Floor, StaticMeshActor_11 / FloorStrip_-1 and
StaticMeshActor_22 / FloorStrip_1 changed StaticMeshComponent0 slot 0.
The complete before/final/restored comparison covers 127 actors, 148 components
and 45,396 leaf values with no unexpected difference. Four approved stone
bindings and all approved stone source/native bytes remain exact. The owner
checkpoint remains at X -2090 cm. Mesh defaults, geometry, lighting, exposure,
glazing, collision, gameplay, doors and the blank logo field are unchanged.

Inspect genuine PNGs in `Worker/Before/` and `Worker/Final/`: `entrance-90`,
`inner-90`, `floor-near-90`, `strip-boundary-90` and `long-floor-90`. All ten
images match at 1920x1080, HFOV90, 172.15 cm standing camera height, position,
rotation and renderer settings. Camera metadata confirms live ticking and
possession. The focused standing PIE check passed with walking contact and
normal gravity; no full route rerun was performed. PIE is off and the saved,
reopened current map is clean. Temporary capture settings were restored.

## Author QA and limits

One purposeful author revision followed the three-view Trial01. It corrected
nonperiodic rotated texture boundaries, darkened the overly pale floor body,
reduced secondary vein density/contrast and increased subtle strip detail.
Initial exports, trial views and native recipes remain as evidence. Final
standing views show continuous mineral structure and distinct black strips.
Phase blending can soften veins locally, and the floor still contains broad
pale mineral clusters; the independent reviewer should assess their recurrence.

The fixed neutral hall lighting produces broad pale specular highlights and
does not reproduce the reference's final cinematic reflections. No atmosphere,
light or exposure change was made. Painter GUI viewport appearance is not used
as evidence; reopened native sources/readbacks and exact regeneration establish
authorship, and genuine Unreal images show the integrated result.

`Worker/storage.json` records actual project/lobby totals and growth using the
existing walker. Metal/ceiling, broad stone rollout, final architecture/detail,
glazing B3, atmosphere and MSQ-7 remain pending. Independent review and the owner's
floor-direction decision are still required.
