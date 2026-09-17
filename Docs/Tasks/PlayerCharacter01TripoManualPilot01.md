# MSQ-54: Datum16ShoulderManual01 owner-operated Tripo input preparation

## Current authorization

On 2026-09-17 the owner chose to operate Tripo personally for now and asked
Codex to prepare what is required. This authorizes this bounded preparation
stage inside MSQ-54. It does not dispatch the complete body prototype or
authorize Codex to upload to Tripo, spend its credits, or generate a 3D model.
The controller prepares input art and a precise manual handoff. MSQ-54 remains
incomplete until its original-model deliverables are verified.

Read Docs/ProjectState.md first, then this task and
Docs/Approvals/PlayerCharacter01-Datum16Selection01.json. The selected design is
Concept02 / Candidate01, 16 / Datum. MSQ-52 and MSQ-53 prerequisites are satisfied.
Owner-only concept evaluation remains; no independent concept reviewer.

## First component and design authority

Prepare the wearer's RIGHT shoulder armor cap: the large rigid plate over the
deltoid, visible on the image-left shoulder in the original front figure.
This is one complete armor shell, excluding torso harness, sleeve, anatomy,
separate upper-arm/elbow armor and arbitrary new accessories.

Primary design authority:
Assets/Concepts/PlayerCharacter01/Concept02/16.png.
Supporting placement references, not authority for changed details:
Assets/Concepts/PlayerCharacter01/Datum16MultiViewTpose01/16-Datum-Front.png,
16-Datum-Back.png and 16-Datum-Right45.png in that directory.

Preserve the original restrained, angular, beveled dark-metal cap, its main
silhouette and visible fastener arrangement. Do not borrow Chevron armor,
enlarge into a fantasy pauldron, add layered wings or turn the part into a solid
shoulder-shaped lump. Its hidden interior is an inferred shallow concave shell,
not recovered or dimensionally approved construction. No physical dimensions
or completed body-master fit are claimed by the input art.

## Bounded Multica artist output

Use the existing Concept Art profile, task-local Astra/high/standard, one run.
Inspect the actual source images. Write only:

- Assets/Source/PlayerCharacter01/AI3D/Tripo/Datum16ShoulderManual01/prompts.json
- Saved/PlayerCharacter01/Datum16ShoulderManual01/Artist/handoff.md

Prompts JSON is an array of five objects with id, filename, purpose, camera,
and prompt. Prepare:

1. StartHere: 01-StartHere-Outer45.png, a clear outer three-quarter product view
   showing the complete rigid cap and its shallow curved thickness. This is the
   recommended SINGLE-image input for the first owner generation.
2. Front: 02-Front.png, near-orthographic view square to the broad outer face.
3. Left: 03-Left.png, corresponding object-left profile of that same shell.
4. Right: 04-Right.png, corresponding object-right profile.
5. Back: 05-Back.png, reverse view of the inferred concave inside surface.

Use a fixed local object orientation, top of cap up; Front means outside surface,
Back means inside surface. These are component-local axes, not full-character
camera labels. Describe profile orientation explicitly and consistently. The
controller generates StartHere using the source art, then derives each other
view using the generated anchor. Do not send the whole-character images as
alternate views of the isolated component.

All images: one isolated complete object, square framing, ample white margin,
pure opaque white background, neutral soft illumination, no ground/cast shadow,
no labels, collage, body part, sleeve, straps or additional component. Keep the
same material/design across views. Each prompt should be concise and clearly
state invariants. Preserve modest chamfers and believable shell construction;
do not specify final dimensions or add unnecessary intricate surface decoration.

The artist handoff records source SHA-256, design observations and assumptions,
camera conventions and areas that remain inferred. This is authorship, not
independent review or owner acceptance. No other file changes, APIs, browser
actions, image rendering, DCC, installation, delegation, comments, task changes,
commits or pushes. The controller renders with built-in imagegen and packages.

## Controller acceptance and owner handoff

Deliver actual local PNGs, exact prompts/render requests, an English HTML gallery
with per-file links and input-mode map, English README/settings, a manifest with
hashes/dimensions and explicit inferred-surface/cross-view limits, and an empty
owner-export destination documented by a tracked README. Inspect actual images;
do not represent independent 2D generations as calibrated 3D views.

Recommend one first generation from StartHere only: Smart Mesh P2.0 Preview,
Quad target 3000, Texture off, no auto rig/animation, Private. Generate in Parts
is unnecessary for this single shell. The additional four views are construction
references and an optional multiview set, not an instruction to run a second job.
If view consistency is insufficient, keep the images as references and mark them
unsuitable for combined upload instead of silently claiming validation.

Ask the owner to export the untouched generated source as FBX (native quad
option if available), preserve task/settings information and place it in the
named OwnerExports folder. Do not require a screenshot upload to chat; a saved
export plus generation details is sufficient. Root chat explains the same steps
in Russian. No Tripo job, upload, change to owner experiments, or paid API is part
of this preparation. Existing source/owner edits remain unchanged.

The first 3D source still needs geometry inspection, proportional-body fitting,
the MSQ52-RigContract01 and shoulder/aim/reload tests. Input delivery is not
MSQ-54 completion or a claim that a fitted body master already exists.
