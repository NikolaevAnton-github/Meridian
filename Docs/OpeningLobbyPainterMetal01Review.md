# LobbyPainter-Metal01 / WorkerCandidate01 review

On September 15, 2026, MSQ-26 completed one native Painter charcoal satin coating
for the checkpoint, four service-door frame/leaf pairs and elevator leaves.
Fresh independent MSQ-27 Review01 passed all eight visual and technical criteria.
No required correction or critical unverified requirement remains. The new metal
is ready for the owner's material-direction review. Stone and Floor01 are already
owner accepted; this review does not grant owner acceptance of the new metal.

## Exact reviewed identity

| Artifact | SHA-256 |
| --- | --- |
| `Saved/OpeningLobby/PainterMetal01/Worker/manifest.json` (194 entries) | `d056461ecf7bdaed92cb8ee463d6514c5b76218ef91fee3bdbf50c2c54b36035` |
| `Content/Maps/L_OpeningLobby_PainterStone01.umap` | `abc72118717b8333a109fdeeaf1583485a3e7b35badced84204e9fcc130ebc92` |
| `Assets/Source/OpeningLobby/PainterMetal01/Metal.spp` | `b22dbc14218056ca2bcd10edabcb430d40ec6925ade16e1f3bdc2815345ec12e` |

Candidate: `LobbyPainter-Metal01/WorkerCandidate01`, author `QARevision01`.
The exact pre-metal map is `Worker/Before/L_OpeningLobby_PainterStone01.umap`,
SHA-256 `5cc84cac736d24cfe0dedf4c4d1dd0413b3d07f081c9e82e5dd4ab2ca0ae9270`.
This archive resolves the accepted Floor01 map entry. Earlier stone and retired
maps retain their original Floor01 archive mapping. No historical manifest was
edited or rebaselined. See the separate [floor acceptance](Approvals/LobbyPainterFloor01-Acceptance01.json).

## Result and verification

One new editable three-layer Painter family represents an opaque satin coating
over metal. Its charcoal base, roughness 0.27-0.29, metallic 0 and microscopic
normal variation are coherent with that coating. The saved/reopened final .spp
reproduces BaseColor, DirectX Normal and packed ORM byte-for-byte. The compiled
13-node Unreal graph references only its three new textures and engine math.
Projection is 120 cm. One author QA revision reduced mottling in the elevator
highlight before independent review; initial source and image evidence remain.

Exactly ten component slot-zero overrides changed. Full comparison covers
127 actors, 148 components and 45,406 property values. Accepted stone's four
bindings and floor's three bindings, all prior asset/source/config bytes, owner
checkpoint X -2090 cm, geometry, lighting, glazing, collision and gameplay remain
preserved. All 194 candidate entries, 183 accepted Floor01 entries and 154 accepted
Stone01 entries verify, using exact archives for historical map entries.

The reviewer inspected both actual references and all five matched before/final
image pairs before reading author conclusions. Independent read-only checks
reused existing validators with output callbacks held in memory. Eight criteria
passed separately: reference fit, physical response, structure/repetition,
native provenance, integration, preservation, captures/restoration and identity/
storage. The full report and verdict are in
`Saved/OpeningLobby/PainterMetal01/Review01/`.

## Owner viewing and remaining scope

Current map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
Inspect these actual unedited 1920x1080 HFOV90 standing-height captures:

- [Checkpoint](../Saved/OpeningLobby/PainterMetal01/Worker/Final/checkpoint-metal-90.png)
- [Service door](../Saved/OpeningLobby/PainterMetal01/Worker/Final/service-door-90.png)
- [Elevator leaves](../Saved/OpeningLobby/PainterMetal01/Worker/Final/elevator-metal-90.png)
- [Entrance context](../Saved/OpeningLobby/PainterMetal01/Worker/Final/entrance-90.png)
- [Inner context](../Saved/OpeningLobby/PainterMetal01/Worker/Final/inner-90.png)

The elevator center split has low contrast in the dark lower region. Reflections
remain subdued under the existing geometry and fixed lighting. These are
nonblocking limitations for this material-direction review. Wide views retain
the accepted central columns' substantial occlusion. Standing possession and
capture restoration pass; no new full route or performance certification is claimed.

After review, the controller verified unchanged candidate bytes and queried live
Unreal through official Epic MCP: the current map is loaded, PIE is off, and no
map/content package is dirty. Artist/reviewer profiles, instructions and native
arguments are restored to their original Astra/high/standard settings. Task-only
advanced Painter overrides are removed and no Multica run remains active.
Controller receipts and separate native production/review usage are under
`Saved/OpeningLobby/PainterMetal01/Controller/`.

Independent storage measured about 1.845 GB cumulative lobby data, 133.2 MB
growth and 155 MB remaining lobby headroom, within the 2 GB lobby and 250 GB
project caps. Small final controller/review files add to that measurement.
MSQ-26 is in review for owner metal direction; MSQ-27 is done. Ceiling/soffit,
broad stone and entrance-metal rollout, final architectural detail, glazing B3,
atmosphere and MSQ-7 remain pending. No registry rebaseline, commit or push occurred.

See [the author handoff](OpeningLobbyPainterMetal01.md) and
[the bounded task](Tasks/OpeningLobbyPainterMetal01.md).
