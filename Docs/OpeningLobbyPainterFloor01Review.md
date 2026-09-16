# LobbyPainter-Floor01 / WorkerCandidate01 review

On September 15, 2026, MSQ-24 completed the current-map cleanup and two native
Painter floor materials. Fresh independent MSQ-25 Review01 passed all eight
visual and technical criteria, with no required correction or critical unverified
requirement. The floor pair is ready for owner review. The existing stone direction
is owner-approved; the new floor bytes and final lobby atmosphere remain pending.

## Exact reviewed identity

| Artifact | SHA-256 |
| --- | --- |
| `Saved/OpeningLobby/PainterFloor01/Worker/manifest.json` (183 entries) | `0b7a2c9733eabc304c60c47ffa64beed93da1d6d0a0c96d8324969de709f9fc1` |
| `Content/Maps/L_OpeningLobby_PainterStone01.umap` | `5cc84cac736d24cfe0dedf4c4d1dd0413b3d07f081c9e82e5dd4ab2ca0ae9270` |
| `Assets/Source/OpeningLobby/PainterFloor01/Floor.spp` | `c316fb0efc36467d3147980326fbeefc24053305f6ec8ea7def7799f5910f9b0` |
| `Assets/Source/OpeningLobby/PainterFloor01/Strip.spp` | `5cfde914cf26bd145fe6f53bf7c5fab62c72e1fb5e6a0d6fe2f9a57546939159` |

The unchanged stone approval is [LobbyPainterStone01-Acceptance01](Approvals/LobbyPainterStone01-Acceptance01.json).
The current map intentionally changed for the three floor bindings. Its pre-floor
bytes and the nine retired map identities resolve through
`Saved/OpeningLobby/PainterFloor01/Worker/archive.json`. Historical manifests
remain unchanged; do not compare their map entries against the new live map.

## Completed scope

Nine obsolete lobby maps were removed from Content after an all-category
dependency audit and exact archive verification. The current map is the only
lobby level in Content and the asset registry. Both GameDefaultMap and
EditorStartupMap now target `/Game/Maps/L_OpeningLobby_PainterStone01`.
Shared meshes, textures, materials, gameplay assets and source/reference/review
history remain preserved. Exact retired maps are outside Content in Worker/RetiredMaps.

The floor and near-black strips have separate new editable three-layer Painter
projects, with actual native resources and final saved/reopened readbacks. All
six final channel exports reproduce exactly. New opaque graphs reference only
the new floor-family textures. Floor coverage is 360 cm and strip coverage 240 cm.

The scene comparison covers 127 actors, 148 components and 45,396 property values:
only three component material slots changed. The four approved stone bindings,
stone source/native bytes, owner checkpoint at X -2090 cm, geometry, lighting,
glazing, collision and gameplay remain intact. All 183 current manifest entries
and all 154 approved-stone entries verify, using exact archives for retired maps.

## Review and owner viewing

The independent reviewer inspected both actual owner references and all five
matched before/final image pairs before author conclusions. Its exact report and
verdict are under `Saved/OpeningLobby/PainterFloor01/Review01/`. All eight criteria
pass, including natural mineral hierarchy, polish, strip distinction, repetition,
preservation, native provenance, integration and cleanup/capture evidence.

Inspect the actual unedited `Worker/Final/floor-near-90.png`,
`strip-boundary-90.png`, `long-floor-90.png`, `entrance-90.png` and `inner-90.png`.
They match the original views at 1920x1080, HFOV90 and 172.15 cm eye height.
One author QA revision corrected visible texture boundaries and an overly pale,
busy floor before independent review. No subsequent reviewer correction was needed.

Broad pale mineral clusters, locally softened veins from phase blending and a
quieter strip than the reference's foreground speckling remain nonblocking visual
limitations. Fixed neutral lighting produces broad highlights; this is not final
cinematic lighting or performance acceptance. A stale inherited descriptive 240 cm
floor field is explicitly superseded by the actual 360 cm graph audit and recipe.

After review, the controller verified unchanged candidate bytes and queried live
Unreal through official Epic MCP: the current map is loaded, PIE is off, and no
map/content package is dirty. Temporary artist/reviewer instructions and native
arguments were restored to their prior Astra/high/standard settings; task-only
advanced Painter overrides were removed. There are no active Multica runs.
Controller receipts are in `Saved/OpeningLobby/PainterFloor01/Controller/`.

Recorded cumulative lobby storage is about 1.711 GB, including about 201 MB growth,
within the 2 GB lobby and 250 GB project limits. MSQ-24 remains in review for the
owner floor-direction decision; MSQ-25 is done. Metal/door/elevator finishes,
ceiling/soffit, broader stone rollout, final architectural detail, glazing B3,
atmosphere and MSQ-7 remain pending. No registry rebaseline, commit or push occurred.

See [the author handoff](OpeningLobbyPainterFloor01.md) and
[the bounded task](Tasks/OpeningLobbyPainterFloor01.md).
