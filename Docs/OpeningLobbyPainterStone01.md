# LobbyPainter-Stone01 / Correction01

**A bounded native Painter color correction is complete and ready for focused
independent recheck.** This is one stone finish on the four existing sample slots.
It does not grant owner material-direction, whole-lobby or atmosphere acceptance.

## Current identified candidate

| Item | Identity |
| --- | --- |
| Candidate | LobbyPainter-Stone01/Correction01 |
| Native map | /Game/Maps/L_OpeningLobby_PainterStone01 |
| Manifest and identity | Saved/OpeningLobby/PainterStone01/Worker/Correction01/manifest.json and identity.json |
| Map SHA-256 | 1694ce8033c6d3a109b720a37f4d608325d2adbe285b5610dd12937e311d169f |
| Painter source | Assets/Source/OpeningLobby/PainterStone01/PainterStone01.spp |
| Painter SHA-256 | 6cc3e43b29eb8fb96c753a1790835a806ecc9f716d2308fa6cf61a7e9cb18324 |
| Owner source SHA-256 | 46972ef30ef07f5a5aaa8cad0f8c026302c1269f1b5e08828e6f87795d168d31 |

The map bytes remain identical because the four bindings are fixed; its scoped
material and BaseColor texture have changed. The new manifest identifies those
bytes. The old WorkerCandidate01 manifest and Review01 apply to historical inputs,
which the controller archived before correction. Never rebaseline the old manifest.

## R1/R2 response

R1: isolated layer 177 and confirmed it produced the dominant dark rings. The
final stack replaces its color resource with parameterized native marble_fine,
UV scale 4 and Overlay 0.40. A quieter green-grey ground and reduced larger-vein
contrast reveal finer branching mineral relationships and sparse pale threads.
Native layers 120 and 177 are the only changed layers. Layer 186 and the three
calibrated finish layers retain their exact sources, parameters and settings.

R2: the one allowed adjustment followed a three-view Trial01, whose replacement
resource still produced rings. The final BaseColor node now blends differently
offset samples over a smooth triangular pattern in world space. This breaks the
simple 240 cm color repeat without changing texel scale, geometry or bindings.
ORM and Normal exports and their native sampling paths remain unchanged.

This is native Painter layer/resource authoring, not external pixel generation.
The final source retains six editable Fill layers and three installed procedural
resources. All authored color/finish pixels come from the saved/reopened .spp.
No old/rejected opaque texture or material is a dependency of this finish.

## Inspect these actual images

All new evidence is under Saved/OpeningLobby/PainterStone01/Worker/Correction01/.
Open the six unedited Final PNGs: column-near-90, front-return-90, grazing-90,
entrance-90, sample-context-90 and portal-complete-90. The original matched source
images remain in Worker/Before; the complete portal source remains in
Worker/BeforeContext. No source image was recaptured or renamed.

Compare the actual OwnerReferences01/01-InnerEnd.png and 02-EntranceSecurity.png
separately, concentrating on the foreground column faces and returns. Reference
lighting, camera and architecture differ from the neutral sample. Final portal
framing is complete above the unchanged checkpoint, which obscures its lowest area.

Author inspection: the final body is quieter, with irregular branching structure;
its original dark-ring color field is gone. The simple repeated color motif is no
longer readily traced up the tall jamb. Strong reflections remain broad and smooth.
Faint ring-shaped modulation persists inside highlights from the unchanged
roughness input. Fine mineral density is more subdued than the denser reference
regions; the independent reviewer must assess that difference and natural likeness.
Full observations and the rejected Trial01 assessment are in visual-inspection.md.

## Verification

| Check | Result and evidence under Correction01 |
| --- | --- |
| Archived baseline | All 27 live/archive mappings matched before mutation; archive-verification.json. Initial Worker, Review01 and controller archive were preserved. |
| Editable Painter source | Actual save/open and layer/resource/parameter readback; Painter/save-reopen-export-calls.json and final-source-evidence.json. |
| Exact export regeneration | All three 2048 final native exports are byte-identical between FinalSaved and FinalReopened. Canonical Channels files match; exact-regeneration.json and texture-channel-verification.json. |
| Calibrated finish preservation | ORM/Normal exports match the first candidate byte for byte; native ORM/Normal assets, authoring mesh and map are unchanged. Four unchanged layer sources/settings checked in affected-assets-verification.json. |
| Material integration | 13 connected expressions, three task textures, correct color/mask/DirectX-normal settings and no old dependencies. Native audit differs only in BaseColor code/description and pixel instruction count: 351 versus 244; four samplers unchanged. |
| Owner scene preservation | 127 actors, 148 components and 45,396 compared leaf values; exactly the same four source-to-sample overrides, no other difference. Final equals original candidate and restored state. property-preservation.json and difference records. |
| Protected files | 869 correction-start protected files remain byte-identical, including source/history, original Worker/Review01 and controller archive; protected-after.json. |
| Comparable captures | Nine inspected new stills: three trial and six final, exact source/original-candidate poses, HFOV90, 1920x1080, renderer and source lighting; capture-verification.json. |
| Standing and restoration | Fresh grounded possession, advancing real world time, gravity -980 and 170 cm eye offset. Capture settings restored; candidate loaded, no dirty content/maps, PIE off. Final/standing-possession.json and final-state.json. |
| Storage | storage.json records correction/archival growth and current cumulative lobby/project totals against mandatory 2 GB/250 GB limits. |

Same explicit material slot 0 overrides on StaticMeshComponent0:
Pier_1_1 (StaticMeshActor_17), RA01_PortalJamb_1 (80), RA01_Shoulder_1 (81) and
RA01_FirstPier_1 (85), all to M_PainterStone01. The owner's source, checkpoint at
X=-2090 cm, geometry, glazing, lights, exposure, collision and gameplay remain fixed.

## Limits and handoff

The permitted single correction and its one adjustment are exhausted. Hand these
exact bytes to the controller for the focused independent R1/R2 and polish recheck.
A technical pass and native Painter use do not establish visual acceptance.
Remaining observations are the subdued mineral density, faint highlight rings and
possible detail softening at color-sampling transitions. No performance benchmark,
full route rerun or arbitrary-curved-surface validation is claimed.

The initial Painter GUI preview limitation remains historical and unverified.
No new GUI capture investigation was performed. Native source persistence and
regenerated exports provide provenance; the actual Unreal stills provide visual
evidence. No broad material rollout, atmosphere work or further dispatch occurred.

Current editable recipe/usage details are in
Assets/Source/OpeningLobby/PainterStone01/README.md and layer-recipe.json. Native
exports are under Worker/Exports/Correction01/. The exact manifest includes all
current task source/native assets, helpers/docs, relevant correction evidence and
unchanged source evidence used here. The controller archive is preservation
history, not current material input.
