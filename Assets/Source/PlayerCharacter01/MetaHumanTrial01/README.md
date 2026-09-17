# Datum16MetaHumanTrial01

MSQ-54 experiment, 2026-09-17. Live body-only conformation succeeded. These are
experimental sources, not accepted character assets. The visible garment loses
construction detail and the MetaHuman rig differs from MSQ52-RigContract01.

Use `../../../../Docs/PlayerCharacter01MetaHumanTrial01.md` for the handoff and
`Saved/PlayerCharacter01/MetaHumanTrial01/Worker/index.html` from the project root
for comparisons, all ten digits and native reload captures.

| Artifact | Status / purpose |
| --- | --- |
| `Datum16Trial01.blend` | Editable untouched-source layer, temporary scaled full body and body-only derivative. |
| `Datum16_BodyOnly01.fbx`, `input-settings.json` | Controlled Creator input; hood island excluded, other topology retained. |
| `Solve02/SourcePose/Datum16_Solve02_Posed.dna` | Actual fitted source T-pose DNA, saved before A-pose commitment. |
| `Solve02/APose/MH_Datum16_Trial01_Body.dna` | Separate committed A-pose body DNA. |
| `Solve02/APose/MH_Datum16_Trial01_Body.fbx` | Usable fitted body export; primary geometry / UV / skin inspection input. |
| `Solve02/Datum16_APose02_Inspection.blend` | Imported A-pose export with original derivative retained for inspection. |
| `Solve02/Datum16_APose03_Deformation.blend` | Actual static deformation probes, keyed frames 1–16. No Unreal corrective rig evaluation. |
| `Solve02/SourcePose/MH_Datum16_Trial01_Body.fbx`, `Solve02/Datum16_Solve02_Inspection.blend` | Rejected initial geometry export: still the template A-pose, not the fitted result. |
| `Solve02/SourcePose/SK_Datum16_PosedDNA02.fbx`, `Solve02/Datum16_PosedDNA02_Inspection.blend` | Retained failed posed-DNA import: mesh and skeleton axes disagree. |
| `Solve02/Datum16_PosedDNA02_Aligned.blend` | Mesh-only +90° X diagnostic correction for matched source-pose surface comparisons; not a verified production rig. |
| `Solve02/Datum16_APose02_Deformation.blend` | Rejected first pose-render attempt: render reevaluation reset the pose. Use Deformation03. |
| `manifest.json` | Immutable Worker01 hashes for source, experimental Unreal assets, report and scripts; generated after those outputs settle. |

Units and axes are recorded in `input-settings.json`. The full-source diagnostic
height is 180.5439 cm, not approved protagonist stature. Gameplay camera and
capsule were not altered. The generated default head is only a scaffold.

The output body has MetaHuman UV tile 1002, a 342-bone Unreal hierarchy and up
to 12 skin influences. Do not normalize its UVs or substitute its hierarchy for
the accepted 161-bone contract. Source and failed variants must remain preserved.

The scripts are bounded execution records with existing output identities.
Do not rerun mutation/export commands over this frozen package. Any further
candidate needs a distinct identity and must retain the Worker01 manifest.
