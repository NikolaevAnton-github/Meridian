# LobbyMaterials-Complete01 / SlabLayout01

Finish the owner's full lobby material batch with the latest stone feedback.
Read Docs/Approvals/LobbyMaterialsComplete01-StoneSlabs01.json and
LobbyMaterialsComplete01-GlazingDeferred01.json first. The owner likes the current
column gloss, wants walls to share it, and requests readable large-format slabs
on walls and columns. Glass is explicitly deferred; do no further glass work.

Multica Environment Artist, Astra/high/standard, existing subscription/project,
concurrency one, English. The controller obtains a fresh combined Review02 after
this handoff. Do not stop for another family, concept or geometry approval gate:
this is a material-layout change on unchanged geometry, already requested.

## Current identity and protected history

Current sole map: /Game/Maps/L_OpeningLobby_PainterStone01.
Predecessor LobbyMaterials-Complete01/Correction03 has678 manifest entries:
Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03/manifest.json
SHA-256 ed6b3c105b8f2b22536707e668e7db7ba3cff720b7938ed7899a091b985f520a.
Current map SHA-256 b4cc37e0dd8281fddd250183c5e878f20fec35babcdefc520d3b09929857cb73.
Validate the controller's BeforeSlabs01 exact rollback archive and live project,
map, dirty/PIE state before mutation. Preserve later owner edits/unsaved work.

Read the original complete-batch task for reused coverage/source/capture rules,
but this task and the latest owner records supersede its gloss, accepted-binding
and glass-closure restrictions. Review01 R1 is DEFERRED_BY_OWNER, not passed.
Review01 R2's quiet-wall direction is superseded by the explicit preference for
column gloss. Do not keep the quieter wall response merely to satisfy old R2.

Preserve every historical source/material/helper/report/evidence byte. Only the
current map changes in place, with exact previous map bytes archived outside
Content. Never rebaseline earlier manifests. No other lobby map, deletes, registry
mutation, commits/pushes, paid usage, installs/downloads or global config changes.

## Bounded stone change

Replace the44 effective stone slot0 overrides with newly authored slab variants.
25 currently use accepted M_PainterStone01 and19 use M_C01_BroadStone. The latest
owner instruction permits changing four previously protected stone bindings:
StaticMeshActor_17 Pier_1_1,80 RA01_PortalJamb_1,81 RA01_Shoulder_1 and85
RA01_FirstPier_1, all StaticMeshComponent0 slot0. Their old material/source bytes
remain immutable. The other13 accepted bindings (3floor/strip,10metal) remain exact.

Preserve all63 nonstone lobby assignments, the separate far-field support mesh,
all geometry/mesh data/UVs/slots/transforms, collision, routes/gameplay, owner
checkpoint, lights/exposure, existing postprocess flags, glazing/support bytes and
properties. No actor additions/removals. Both shoulders must have coherent slab
finish. The future logo field stays opaque and blank. Nine ceiling parts remain.

Build a new master from the accepted column stone graph, using its exact native
Painter texture resources read-only. Preserve the accepted face response:
ORM.G directly to Roughness; DielectricSpecular=.4 (F0 .032); metallic0, no coat.
Remove the19 wall variants' .57+.35*ORM.G roughness and specular .35 by new
assignments, never edits to historical assets. Preserve mineral palette, normal
strength and240cm physical source coverage. New joints may have a restrained
rougher dark-mineral grout response; the slab face gloss remains the column's.

Use editable native Unreal material math for physical joint layout. There are no
new texture pixels, so no Painter regeneration or ceremonial new .spp is needed.
Verify unchanged accepted native Painter source and texture identities. Reuse
existing guarded graph/projection/manifest validators; do not rebuild tooling.

## Slab layout and roles

Working default: vertical120cm width x240cm height,5mm joints and approximately
0.5-1mm edge/recess normal response. This is a controller working choice after an
optional owner preference question, not exact owner approval of dimensions.
Keep module, orientation, joint width/depth and alignment editable. Apply any
newer explicit owner preference in the controller dispatch if one exists.

Use centimetre coordinates with rotation-only face axes and explicit origins;
do not use stretched normalized cube UVs. Share a world-Z course datum across
adjacent faces and align offsets per assembly. Column240cm faces support two
120cm slabs. Use dominant geometric face masks for joints instead of blending
multiple triplanar grids into doubled/crossed lines. Wrap horizontal courses
around corners. Narrow returns use coherent cut strips. Filter thin lines with
pixel derivatives, avoiding shimmer, artificially thick distant grid or black
drawn outlines. Mineral sampling may use restrained per-slab source offsets to
read as cut stone while preserving accepted colour/roughness, with no random
brightness checker or conspicuous repeat. Inspect actual appearance first.

Confirm these44 roles against live census and record per-component module/phase:

| Role | Count | StaticMeshActor indices |
| --- | --- | --- |
| Columns/piers, full courses |18|6-10,17-21,35-38,71,74,82,85|
| Walls/shells/shoulders, full courses |17|1,2,5,12,15,25,26,27,30,32,42,70,73,79,81,84,90|
| Portal jambs with aligned returns |2|69,80|
| Inner wall continuation bands |2|31,33|
| Long beams, elongated cut pieces |2|72,83|
| Thin head/datum/elevator surround, trim-aware cuts |3|91,92,40|

39 regular cladding slots and5 trim-aware slots. Do not force a full rectangular
grid onto12cm datum,20cm portal head or narrow elevator-frame faces. Composite
single-slot room shells require vertical/horizontal face treatment within the
shader, keeping their original mesh intact. Existing floor tiles stay untouched.

## Execution and verification

New candidate LobbyMaterials-Complete01/SlabLayout01. New UE assets only under
/Game/OpeningLobby/MaterialsComplete01/SlabLayout01/. Editable source/recipe under
Assets/Source/OpeningLobby/MaterialsComplete01/SlabLayout01/. New helpers only
Scripts/OpeningLobby/materialscomplete01_slabs*.py. Evidence under
Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/. New report
Docs/OpeningLobbyStoneSlabs01.md. Do not overwrite previous helper/evidence paths.

Prefer official Epic MCP. One Rider Python bridge call solely to register the
new guarded Epic helper is authorized if needed, then use Epic for the editing
operation. Do not ask the owner about this routine registration. Inspect actual
capabilities and exact schemas. Full installed helper Python:
D:/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe.

Save a44-row binding/layout plan, full actor/component/property baseline and
protected-file hashes before mutation. First implement representative column,
broad wall and narrow return using new assets, inspect matched near/oblique
native frames, then extend the same coherent family to all44 slots in this run.
At most two purposeful author QA refinements; save each comparison with rationale.
No new owner gate between representative check and full authorized application.

Check joint physical module/width/normal response, corner/return continuity and
trim logic numerically and visually. Slab faces must match accepted column gloss
through exact graph/dependency evidence and identical-light camera comparison;
do not fail desired gloss solely for strong existing-light highlights. Judge
readable mineral and slab layout in the same frame, avoid painting over them.

Save/reopen native graphs and current map; audit compiled connectivity and
dependencies, full107 lobby slot census plus separate support, no proxies/errors,
44 authorized binding differences only,13 accepted nonstone bindings exact,
all63 nonstone assignments exact and every nonmaterial property/history exact.
Reuse existing unchanged Painter and route verification through hashes. No DCC
source export, full movement suite, glass diagnostics or lighting work needed.

Capture genuine1920x1080 HFOV90 standing-height before/final matches: near
column face and corner, broad wall, side aisle, terminal/room wall, portal return,
trim/head, whole hall/bays, ceiling context, checkpoint and elevator. Reuse exact
existing camera poses where suitable; add clearly identified near views for slab
joints without replacing comparable context frames. Keep true runtime pose/FOV,
exposure/tick/settings metadata, no processed/composited presentation images.
Restore capture settings, save/reopen, leave the sole clean current map PIE off.

Deliver unique nonempty path/bytes/SHA-256 manifest.json and identity.json for
current map, all new native assets/recipe, accepted source links, full coverage,
preservation, final images, checks and exact rollback. Report module, joint width,
gloss source, role exceptions and honest remaining issues. Original400MB batch
planning headroom is extended to450MB for this new owner-requested slab scope;
aim <=80MB additional and <=2.4GB cumulative lobby, hard250GB project cap unchanged.
No history/user deletion or unnecessary duplicated texture/SPP assets.

No delegation, task comments/admin, later dispatch or owner-acceptance claim.
Controller runs fresh independent combined opaque-material Review02 next, with
glass criterion6 explicitly deferred and desired column gloss as current target.
