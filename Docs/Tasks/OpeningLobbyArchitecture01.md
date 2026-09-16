# Opening lobby Architecture01: modular architecture and materials

Multica task: MSQ-6, Stage 2 of MSQ-4. The owner accepted the actual Layout03
scale on 2026-09-14 and explicitly authorized continuing, while stating that
detailing has not been assessed. See the exact scoped
[decision record](../Approvals/LobbyLayout03-Scale01.json).
This task produces a review candidate; it cannot claim owner detail acceptance.

## Authority and bounded result

Implement Stage 2 of [the lobby milestone](OpeningLobby.md) in the existing
`D:\devgames\MeridianSquad` project. Read the relevant sections of
`Docs/Design/GameBrief.md`, `Docs/VisualAcceptance.md`,
`Docs/OpeningLobbyLayout03.md` and the approved art/dimensional sources.
Inspect the actual two `OwnerReferences01` images and
`Review02/03-SecurityOblique.png`, plus the approved scale drawings.
`LobbyArt-Review02` remains the visual authority; `LobbyScale-Review01/schedule.json`
remains the dimensional authority. The reference pair takes precedence over
the generated supplement's fine details. Do not commission another concept round.

Create a separate saved map `/Game/Maps/L_OpeningLobby_Architecture01` and
dedicated assets under `/Game/OpeningLobby/Architecture01/`. Preserve the
accepted Layout03 map/materials, its recorded construction/captures/reviews,
all Stage1/Layout02 historical assets/evidence, and approved art/drawings.
Do not edit their bytes or reuse their material packages as writable targets.
No default-map or gameplay/source/configuration changes are required.

Deliver an intact architectural/material pass of the complete lobby with a
small reusable Blender kit. Replace the visible schematic architecture with
modeled pier cladding, wall panels, floor modules/strips, lintels, upper infill,
aisle ceilings/trim, both glazed fields and human-size door/checkpoint elements.
Repeated bays must reuse assets. Keep dark green-grey stone panels, subtle
seams and edge treatment, a polished veined floor with the two black strips,
restrained dark metal and distinct glass consistent with the approved art.
Do not add ornamental coffers or invent unseen rooms, door destinations or routes.

## Dimensions and construction

The accepted interior is 60 x 24 x 18 m, with six 2.4 m square pier pairs,
8.4 m shaft height/pitch, 6 m bay gaps, 11.2 m center and 4 m clear aisles.
Retain all scheduled glazing, lintel, door, detector, station and worktop
dimensions and placements. Reuse the approved human-size exceptions unchanged.
Keep speed 360 cm/s, capsule radius/half-height 34/88 cm, eye height about
1.72 m and gameplay HFOV 90 degrees. Do not resize the player or alter controls.

Production assets may subdivide a proxy into parts; compare the resulting
assembled envelope and clearances against the schedule and accepted saved
construction. Primary dimensions must remain within the existing 0.05 m
tolerance. Add edge treatment within those envelopes. Document technical
panel thickness, seams, UV scale and small nonblocking surface offsets as
implementation choices, not newly approved architecture or fabricated door depth.
Retain Correction01's positive end-band and door-layer separation.

Keep structural collision separate from visual cladding, metal, glass and
movable dressing. The accepted blocking shells may be reproduced in the new
map as dedicated invisible structural collision when useful; verify their actual
profiles and route behavior. Avoid duplicate visible/coplanar blockout surfaces,
glass backed by an opaque visible proxy, collision snags, inverted normals,
unexplained one-sided holes and one merged whole-room mesh.
Doors remain noninteractive boundaries with no invented destination.

## DCC, source and materials

One Multica environment worker owns the whole Blender/Painter/Unreal editing
operation, sequentially. Use GPT-6 Astra, high reasoning and standard speed for
this first production kit and cross-DCC integration. Runtime concurrency is one.
Use the existing subscription and installed tools; no paid APIs, purchases,
downloads of asset packs, new services, duplicate checkout or benchmark reruns.

Verify actual running versions/connections before using a bridge. Controller
preflight found UE 5.8.1 on clean Layout03 with PIE stopped; Blender and Painter
were not running and both bridge probes were disconnected. Recheck live state.
Start the existing local apps when needed using the documented bootstrap in
`Docs/AgentDevelopment.md` and `Docs/PainterWorkflow.md`; launch hidden unless
the owner needs an interactive window. Do not open duplicate instances or
discard unsaved user work. No installs or global preference/configuration changes.

Use the official Epic MCP for all Unreal scene/asset mutations, imports,
saving, PIE and captures; discover needed toolsets. Confirm project, map, PIE
and dirty packages before mutation. Reuse the existing bounded Python tool
registration pattern if necessary; Rider bootstrap may register those tools.
Blender and Painter operations use their working local bridges. Change diagnostic
approach after two equivalent failures; report real blockers precisely.

Store editable Blender/Painter source and canonical input textures under
`Assets/Source/OpeningLobby/Architecture01/`. Store bounded reproducible scripts
under `Scripts/OpeningLobby/`. Binary sources/assets use existing Git LFS rules.
Generated FBX/texture exports and verification logs stay under
`Saved/OpeningLobby/Stage2/Architecture01/` with explicit source/export/import
paths and SHA-256 inventory. A native source file is required for each authored
DCC contribution; do not deliver only procedural scripts or flattened exports.

Large repeated surfaces use shared tileable materials with physical-scale UVs,
restrained roughness/normal variation and no recognizable repetition at walking
distance. Use Painter where useful for a bounded door/checkpoint material set;
preserve its editable project and validate texture-set/material-slot mapping.
Use existing channel/export checks as components, not the asset-specific
benchmark harness. Check DirectX normal convention, color-space/channel settings,
packed channels, mipmaps, shader compilation and material assignments in Unreal.
Avoid unique 4K texture sets for every repeated module. Document texture sizes
and reuse; aim for at most 2 GB of new lobby source/assets/exports overall.

## Verification and handoff

Controller inspection extension, 2026-09-14: after Review02 and the restored
Correction02/03 diagnostic attempts, [LightStudy01](OpeningLobbyGlassLightStudy01.md)
authorizes a separate neutral glazing inspection map. Keep this task's original
same-light map and captures unchanged. The study explicitly records its added
inspection support; it does not alter the accepted scale, material bytes,
baseline light evidence or owner/MSQ-7 acceptance gates.

Define a concise kit/material inventory before authoring. Inspect one
representative assembled bay at eye level under the retained neutral lighting
before repeating it across the hall; correct visible tiling, seams, scale or
normals then. This is an internal quality check, not owner approval or permission
to defer the rest of the assigned architectural pass.

Keep the neutral Layout03 lighting/exposure for comparison. Do not add final
atmosphere, fog, color grading, damage, debris, signs, seating, squad bodies,
combat, abilities, destruction systems or new narrative facts. Security equipment
gets the needed modeled surfaces and materials, without invented functionality.
Do not hide weak material response with darkness or change the approved scale.

Reuse `Scripts/OpeningLobby/verify_lobby.py` and the existing revision/capture
patterns with a narrow new-map configuration. Preserve historical defaults and
identity guards. Verify saved/reopened assembled dimensions, pivots, transforms,
UVs/texel scale, normals, material slots, texture inputs, collision profiles and
references to the dedicated assets. Inspect actual full-size Unreal images.

Exercise the real PIE route once the map is stable: entrance/inner/return,
both full aisles, checkpoint both ways, crossovers, wall/pier contacts,
possession, look, grounding, jump and landing. Do not count teleports or editor
camera motion as movement evidence. Repeat only failed or affected checks after
bounded corrections. Record measured time and any limits separately from estimates.

Capture native 1920 x 1080 images for the same six Layout03 comparison views
(C1/C2 at 75 and 90 degrees, C3 and C3-context at 90), with actual poses/FOV,
eye height, resolution and hashes. Retain gameplay HFOV 90 after transient
comparison capture overrides. Add only a few walking-distance material/details
views for stone, floor, metal/glass and checkpoint readability. Preserve every
baseline view rather than replacing it with a detail crop. Review actual images
against the approved art and accepted neutral scale, not just numeric checks.

Save and reopen the candidate, verify OpeningLobbyGameMode, stop PIE, restore
temporary capture/throttle settings, and leave no dirty or hidden user assets.
Write `Docs/OpeningLobbyArchitecture01.md` with map/controls, kit and source paths,
technical verdict, comparison inventory, known visual limitations and measured
project/output size and growth. Save full reports under the dedicated Saved root.
Measure project size without following junctions; keep the whole project below
250 GB, including local tools/history. Never delete user assets to reclaim space.

The controller performs technical handoff review and dispatches a fresh
independent visual reviewer after the worker stops. Its report must distinguish
preserved scale from architecture/material quality and inspect actual art,
full matched views and walking-distance detail images. Critical or unverified
criteria require a bounded correction. Owner detail acceptance stays pending.
MSQ-7 remains backlog until the architecture/material review and owner decision.

Do not edit AGENTS.md, task specifications, other documentation, Multica
statuses/comments/assignments, approval files, accepted registry fingerprints,
source art, historical maps/assets or configuration. No delegation, commits,
pushes, registry registration/rebaseline, later task dispatch or new task database.
Return a concise English handoff. The controller records native input/cache/output
separately and counts reasoning in native output once; it handles administration.
