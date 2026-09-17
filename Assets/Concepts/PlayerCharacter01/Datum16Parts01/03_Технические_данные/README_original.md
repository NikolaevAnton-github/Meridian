# Datum 16 — Component References 01

Thirteen component groups, supplied as sixteen individual PNGs with light backgrounds or preserved transparency, prepared from the existing Datum 16 character artwork for a Meshy-to-Blender workflow. Paired equipment is represented by one anatomical left-side component; `L` refers to the character's left, not the left side of the image.

Open [the local gallery](index.html) to inspect each image, then click its preview to open the full PNG.

## What these images represent

These are AI-isolated and reconstructed **2D references**, not exact pixel crops, finished game assets, or verified coherent 3D views. Previously concealed surfaces and attachment details may be inferred. Individual images can differ in scale, thickness, openings, panel placement, or wear. Use the original character artwork to resolve design relationships in Blender.

The built-in ImageGen tool was used for every image. All PNGs are 1254 x 1254 pixels. The shoulder, shin and palm images preserve the tool's actual alpha channel; the gallery displays those on white. Main-object framing was inspected. This package has not been submitted to Meshy, so generated 3D fidelity and multi-view consistency remain untested.

The undersuit's concealed paneling, armor padding and attachment backs are reconstructed. Torso auxiliary proportions, glove cuff orientation and boot tread continuity need manual reconciliation before multi-view submission. The forearm and glove were corrected once to remove duplicated elbow/wrist armor; the two first drafts are retained under `provenance/` and are not Meshy inputs.

The owner evaluates the artwork. This package does not establish final concept acceptance or production modeling approval. No 3D output is included.

## Image inventory

| Group | Primary PNG | Additional view | Blender assembly notes |
| --- | --- | --- | --- |
| 01 · Helmet | [Helmet](parts/01_helmet.png) | — | Keep visor, shell and jaw components distinct where their materials or movement require it. |
| 02 · Undersuit | [Undersuit](parts/02_undersuit.png) | — | Continuous deformable neck, torso, sleeves and trousers; derive FPS sleeves from this same garment. |
| 03 · Torso armor | [Front](parts/03_torso_front.png) | [Back](parts/03b_torso_back.png) | Preserve the three lower-torso lames and their separation. Split rigid plates from deformable straps and backing. |
| 04 · Left shoulder | [Shoulder cap](parts/04_shoulder_L.png) | — | Separate rigid cap; fit it to the shoulder and test arm elevation. |
| 05 · Left upper arm | [Upper-arm guard](parts/05_upper_arm_L.png) | — | Fit the plate to the sleeve without bridging the elbow. |
| 06 · Left elbow | [Elbow guard](parts/06_elbow_L.png) | — | Keep independent of the forearm guard and test full elbow flexion. |
| 07 · Left forearm | [Forearm bracer](parts/07_forearm_L.png) | — | Prioritize FPS silhouette, wrist clearance and forearm rotation. |
| 08 · Left glove | [Glove](parts/08_glove_L.png) | [Palm](parts/08b_glove_L_palm.png) | Retopologize as a continuous hand and fingers; test grip and finger articulation. |
| 09 · Utility belt | [Belt](parts/09_belt.png) | — | Separate pouches and rigid hardware from the flexible belt where needed. |
| 10 · Left thigh | [Thigh armor](parts/10_thigh_L.png) | — | Separate rigid panels from straps; test hip and knee movement. |
| 11 · Left knee | [Knee guard](parts/11_knee_L.png) | — | Preserve clearance from the thigh and shin armor. |
| 12 · Left shin | [Shin guard](parts/12_shin_L.png) | — | Fit around the leg while leaving the ankle free to move. |
| 13 · Left boot | [Boot](parts/13_boot_L.png) | [Sole](parts/13b_boot_L_sole.png) | Preserve sole contact and allow the required ankle and toe deformation. |

The back, palm and sole images are auxiliary views of groups 03, 08 and 13. They are not three extra production parts.

## Using the references in Meshy

1. Open the intended **individual PNG** from `parts/`. Use that image as the input for its component. Do not upload a gallery screenshot, contact sheet, or a picture containing several unrelated components.
2. Treat the primary image as the starting reference. Use a corresponding auxiliary back, palm or sole view alongside it **only after verifying their consistency**: silhouette, proportions, panel boundaries, fasteners and visible surfaces must agree.
3. If the views disagree or cannot be confidently reconciled, use the primary PNG alone for image-to-3D. Keep the auxiliary image and original full-character artwork as separate visual guides for the Blender work. Do not force contradictory views into one multi-view input.
4. Fit the resulting components to a shared character blockout in Blender. Generated pieces are not guaranteed to arrive at matching scale, with usable interior cavities, mounting surfaces, joint clearances or clean topology.

## Blender priorities for a first-person character

- **Hands, forearms and sleeves come first.** Verify them under the intended in-game camera before finishing lower-priority detail. Check relaxed hands, weapon grip, reloads, wrist bends, forearm rotation and elbow flexion.
- Keep each glove continuous through the palm, wrist and fingers. Do not assemble a deforming hand from disconnected generated finger pieces. Keep sleeve deformation continuous; hide any practical FPS mesh boundary beneath a cuff or armor overlap.
- Use one coherent body scale and skeleton plan. Components that must deform together need compatible placement, skinning and animation. Rigid armor can remain separate while following the appropriate bones.
- A reference group is not a requirement to create one rigid object. Torso plates, the **three lower-torso lames**, straps and fabric backing need appropriate separation so the torso can bend. Keep the intended spacing and overlap rather than merging the lames into one slab.
- Mirror suitable left-side geometry in Blender to create the right side, then check handedness, normals, fasteners and fit. Apply asymmetric scratches, fabric variation and wear afterward rather than mirroring the complete appearance unchanged.
- Resolve openings, wall thickness, hidden backs, attachment points and collision clearances manually. Final retopology, UVs, baking, weights and engine deformation tests remain production work.

## Source artwork and provenance

The original reference package is preserved separately:

- [Original front](../Datum16MultiView01/16-Datum-Front.png)
- [Original back](../Datum16MultiView01/16-Datum-Back.png)
- [Original left profile](../Datum16MultiView01/16-Datum-Left.png)
- [Original multi-view gallery](../Datum16MultiView01/index.html)

This package's [prompts.json](prompts.json) records generation instructions, and [manifest.json](manifest.json) records the delivered inventory and provenance. Consult those records for image-specific details. Shared design intent does not establish exact cross-view or 3D consistency.
