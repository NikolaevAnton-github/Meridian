# LobbyPainter-Stone01: native Painter stone sample after owner rejection

On 2026-09-15 the owner rejected MSQ-22's NumPy-generated pilot textures as very
poor and not resembling stone, and explicitly challenged the lack of Painter.
The controller stopped that run. Its map, textures, recipes and captures are
rejected history, not a source for this revision. Continue the same MSQ-22 issue
through Multica at Astra/max/standard, existing subscription, concurrency one.

The immediate deliverable is one convincing, editable Painter-authored stone
sample shown on existing lobby architecture. Resolve this material before another
whole material-family rollout. The controller stays through fresh independent
review and one bounded correction/recheck, then presents the identified sample
for the owner's material-direction decision. Other opaque families and atmosphere
remain paused; do not claim the full MSQ-6 milestone is complete.

## Visual and source authority

Read AGENTS.md, Docs/Design/GameBrief.md, Docs/PainterWorkflow.md,
Docs/OpeningLobbyFunctionalBuild01Review.md and the owner-edit record. Inspect
both actual Assets/Concepts/OpeningLobby/OwnerReferences01 PNGs. Judge the stone
on visible columns and portal faces, including a real-scale detail from the image.
Record observed grain/mineral structure, variation scale, polish and color before
building the layer stack. Do not use the rejected pilot as the visual target.

Target polished dark green-grey architectural stone with legible, irregular
mineral structure and subtle natural variegation. The failed result reads as
blurred cloudy noise with grass-like streaking, uniform groundmass and weak
geological detail. A different noise seed, sharper noise or a darker tint alone
does not correct that. Preserve calm highlights without chalky, wet/plastic,
coarsely pitted or pebbled normals. No fake panel grid, cracks/damage, decals or
geometry changes. Stone type is a visual interpretation of the supplied art,
not a claim that a specific quarry/rock identity is known.

Author a new native Painter .spp from a fresh mesh/project and a deliberate named
layer stack: base material, mineral/color structure, restrained fine detail and
separately controlled roughness/height as useful. Installed procedural resources
are allowed as building blocks, with meaningful parameter, projection, channel,
blend and opacity decisions. Do not insert one unchanged stock smart material and
call it new authorship. Do not import, recolor, resample or derive from any old
lobby texture, including the rejected NumPy maps. A ceremonial .spp wrapping
externally generated noise does not satisfy the owner's instruction.

Keep Assets/Source/OpeningLobby/PainterStone01/ for the new .spp, source README,
layer recipe and canonical channel images. Authoring mesh and its native source
also belong here if created in Blender; generated FBX/exports go under
Saved/OpeningLobby/PainterStone01/Worker/Exports/. A simple correctly scaled,
UV-mapped reusable square sample is enough; no new lobby mesh is commissioned.
Use 2048 initially and a stated physical coverage; increase only for a demonstrated
walking-distance requirement within the budget. Preserve native editable sources,
not only exports. Record stock resource URLs/versions, parameters, source mesh
scale/UVs, texture channels and complete source/export/native dependency paths.

## Available Painter authoring route and limits

Controller verified Painter 12.1.4/API 0.3.5 connected at localhost:60041, with no
open project. Recheck. The current run has task-local advanced tools and path
roots; project/global configuration remains unchanged. Use the exposed native
Painter tools, discover actual resources and parameter metadata before edits.
The old Scripts/painter_mcp_client.py checks the on-disk basic allowlist and will
reject advanced tools; do not modify it or treat that as a Painter limitation.

Installed bridge facts, checked from its source:
- create_layer_recipe creates groups/fills with uniform channel values. Assign
  procedural resources afterward with set_fill_resource.
- Resource/parameter/projection setters support FillLayerNode. They do not support
  FillEffectNode or generator/filter effect parameter authoring. In particular,
  insert_mask_effect(type=fill, resource_url=...) ignores the resource URL. Do not
  repeat attempts through that unsupported path. Work with genuine outer Fill
  layers and channel blending, or report a concrete missing capability.
- get_fill_parameters needs a channel in Split mode and no channel in Material
  mode. Use returned parameter IDs/ranges/enums rather than guessed fields.
- set_layer_properties needs exact runtime channel names; inspect capabilities
  and project channels (e.g. SpecularRoughness/BaseMetalness where applicable).
- search_resources can find installed marble_fine/marble_wide/marble_veins and
  grunge_stone_details/grunge_marble_* building blocks. Use returned resource URLs;
  names do not establish visual suitability. No downloads, installs, paid service,
  arbitrary Python bridge enablement or bridge-code patch is authorized.

Native Painter exports and the layer tree must demonstrate actual
authoring. Verify project save/reopen with snapshot_layer_tree/list_layers and
resource/parameter evidence, not merely that a file named .spp exists.

## Unreal sample and verification

Preserve current owner source /Game/Maps/L_OpeningLobby_FunctionalBuild01, SHA-256
46972ef30ef07f5a5aaa8cad0f8c026302c1269f1b5e08828e6f87795d168d31 at controller
preflight. Its checkpoint is at X -2090 cm. Never restore old worker geometry.
Keep /Game/Maps/L_OpeningLobby_MaterialIntegration01 and its entire asset/source
set unchanged as rejected history. Create the new
/Game/Maps/L_OpeningLobby_PainterStone01 from the saved owner source, with new
native material/texture assets only under /Game/OpeningLobby/PainterStone01/.

Apply the new stone through explicit component/slot overrides on a bounded
entrance-column/portal/front-and-return assembly. Choose a clear existing wall
face and an adjacent column so the same finish is seen at walking distance,
obliquely and in repetition. Record exact labels/slots and physical projection.
Leave all other source materials, geometry, transforms, lighting/exposure, glass,
collision, gameplay, blank logo field and source mesh defaults unchanged.

Use official Epic MCP for Unreal operations. Reuse technical capture/property/
texture-channel/PIE validators through new guarded task helpers; no broad new
harness. Last pilot's capture issue was transient: StartPIE warmup alone did not
prove world ticks; actual camera/readiness must pass before a capture is accepted.
Do not fake ticking, rewrite time as movement evidence or accept the initial
camera at (0,0,0). Preserve all failed evidence separately and change diagnostics
after two equivalent failures. No gameplay/project configuration changes.

Capture matched native 1920x1080 before/after: full entrance context at gameplay
HFOV90, a column near view, oblique front/return view, and a restrained grazing
highlight detail. Actual source reference comparisons must remain separate images,
with camera/framing differences stated. No cosmetic image editing or flattering
crop substituted for the full assembly. Inspect every actual capture; allow at
most two purposeful Painter sample revisions in worker QA before handoff.

Verify Painter channel exports, BaseColor sRGB, linear masks/roughness, DirectX
normals, mipmaps, native graph connections/compilation and source provenance.
Save/reopen Painter and Unreal, compare complete source/candidate nonmaterial
properties and exact approved binding deltas, verify original asset bytes and a
fresh standing PIE possession check. A full route rerun is unnecessary for an
unchanged collision/material-only sample. Restore temporary capture/FOV/throttle
settings and leave the clean identified sample loaded, PIE stopped.

Allowed writes: named new source/native assets/map, Scripts/OpeningLobby/painterstone01_*.py,
Saved/OpeningLobby/PainterStone01/Worker/, and Docs/OpeningLobbyPainterStone01.md.
Old helper/source/map/evidence files are read-only. Aim <=300 MB fresh growth;
measure cumulative lobby and project usage against 2 GB/250 GB. One DCC writer
and one heavy workload. No deleting user assets, downloads, paid services,
config/skill changes, comments/task administration, delegation, registry writes,
commits/pushes or other-material dispatch by the worker.

Hand off LobbyPainter-Stone01/WorkerCandidate01 with exact map/manifest hashes,
standard relative-path/SHA-256/bytes inventory, actual .spp/layer/resource evidence,
images and concise English material assessment. Include limitations honestly.

## Fresh independent review

Astra/max/standard Visual Reviewer in a fresh issue/session, read-only candidate,
assigned environment-architecture-review for the architectural sample. Inspect the
actual reference stone and actual full/near/oblique candidate images before author
conclusions. Record first look, then audit .spp/layers/resources/export/native
provenance, real scale, scene preservation and exact fingerprints.

Judge separately: actual likeness to stone rather than generic noise; dense natural
mineral structure and suitable scale; calm credible polish/roughness; front/return
and repeated-assembly coherence; genuine native Painter authorship from new inputs;
correct native/channel integration; exact preservation; valid comparable evidence
and restored clean state. Report PASS/FAIL/UNVERIFIED with specific image/data
citations, required_corrections, critical_unverified_requirements and owner_review_ready.
Do not pass because Painter was used. One bounded correction and focused recheck
are allowed. The owner decides the material direction before broad rollout.
