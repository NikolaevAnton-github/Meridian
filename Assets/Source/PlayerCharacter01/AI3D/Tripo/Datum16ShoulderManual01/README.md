# Datum16ShoulderManual01: first owner-operated Tripo generation

Task: MSQ-54, bounded input preparation. Component: wearer's right shoulder armor
cap. This package provides input illustrations, not a production mesh or fitted
body. The owner operates Tripo; no Tripo generation was performed by Codex.

Open `index.html` for the image gallery and per-file links.

## First generation: use one image

1. Open https://studio.tripo3d.ai/workspace/generate and choose **Smart Mesh**.
2. Confirm **P2.0 - Preview**. Keep the **single-image** input mode.
3. Upload **Inputs/01-StartHere-Outer45.png** only. Do not upload the original
   full-character concept, the gallery, or a multi-image contact sheet.
4. Open **General Settings > Topology**. Select **Quad** and enter **3000** in
   the **Polycount** number field. The observed default was 5000. The target is
   a pilot recommendation; the actual output count may differ.
5. Select **Privacy > Private**. The controller's fresh inspection tab displayed
   Sharing Only, so do not assume the saved default is Private.
6. Generate the geometry once using the existing web subscription allowance.
   Read the current credit quote before clicking Generate. No purchase, top-up
   or API integration is required by this workflow.
7. Keep the original result. Do not run Texture, Retopo, Segment, Fill Parts,
   Auto Rig or Animate before returning it. The observed Smart Mesh panel had
   Topology rather than the HD panel's Geometry & Texture controls; there was
   no separate Texture switch in that panel. Do not seek an absent toggle.
8. Use **Export > FBX**, choosing native quad preservation if that option is
   offered. Keep the downloaded source untouched, including any sidecar files
   or original archive. Do not use GLB/STL as the only editable quad source.
9. Put the export in `OwnerExports/`. Suggested name:
   `Datum16-ShoulderR-P2-Quad3000-Try01.fbx`. Record the task URL or ID, actual
   model/settings, displayed output face count, and credits used if available.
   Copy `generation-notes.template.json` to a new filename if convenient.
10. Tell Codex that the export is ready and give the local path. Screenshots in
    chat are optional. A visibly imperfect output is still useful for inspection;
    keep it instead of spending more credits on repeated guesses.

The first requested action is **one generation**, not one generation per image.
The optional text prompt in `tripo-prompt.txt` is only for a text-guidance field
if the chosen image mode offers one. Do not switch to Text-to-3D to use it.

## Additional views

The other images describe the same intended component in component-local axes:

| Reference-only file | Intended meaning | Local view label |
| --- | --- | --- |
| ReferenceOnly/02-Front.png | Broad outer armor face | Front |
| ReferenceOnly/03-Left.png | Object-left profile | Left |
| ReferenceOnly/04-Right.png | Object-right profile | Right |
| ReferenceOnly/05-Back.png | Reverse / concave interior | Back |

These local axes do not mean the character's anatomical front/back/left/right.
StartHere is a three-quarter single-image input and is not an extra fifth slot.
Do not mix these component images with views of the whole character.

**Do not upload these four images together as Multi-view.** Controller inspection
found oblique profiles and varying fastener/edge landmarks; the Back also infers
interior hardware that is not established by the concept. They are preserved
construction illustrations, not calibrated renders of a shared 3D mesh. Use
StartHere alone for this pilot. The original deeper-shell attempt is retained
under Attempts/ and is not the selected input.

## What happens after the export

Codex will check actual polygons, object separation, normals, thickness and the
inside surface. The part will then need fitting over a common original body and
sleeve, using the MSQ52-RigContract01. Arm elevation, aim and cross-body reload
reach determine usable clearance. This package does not claim those tests passed
or that a fitted body master already exists.

The original selected concept establishes external design identity. The isolated
part's occluded interior is an inferred working construction. Physical dimensions,
attachment details and production acceptance remain to be established. All prior
concepts and owner experiments are preserved.

## Sources and settings evidence

- Primary art: Assets/Concepts/PlayerCharacter01/Concept02/16.png.
- Pose/placement references: Datum16MultiViewTpose01 Front, Back and Right45.
- Controller inspected the current web interface on 2026-09-17 without uploading
  files, changing stored topology/privacy values, or generating a model.
- [Smart Mesh](https://www.tripo3d.ai/features/smart-mesh): single image and up to
  four fixed views; triangle or quad topology.
- [P2.0](https://www.tripo3d.ai/blog/tripo-p2-0-preview): 500-25000 quad range.
- [Export formats](https://www.tripo3d.ai/help/getting-started/what-3d-file-formats-do-you-support):
  Studio supports FBX and OBJ; actual quad preservation is verified on the file.

Image creation uses built-in imagegen with a Multica-authored prompt package.
The prompts and exact render requests are retained alongside the input images.
The owner alone evaluates the derived art; technical packaging checks do not
grant owner design acceptance or complete MSQ-54.
