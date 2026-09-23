# TripoCharacter01: stopped model trial and chat handoff

Date: 2026-09-23. **Stopped at the owner's request. Result rejected for excessive deformation.**
Authority: [exact owner stop and preservation request](Approvals/TripoCharacter01-OwnerStop01.json).

## Resume context

The owner wants to continue the discussion in a new chat. Read this handoff and
[the separate GASPALS trial](GASPALSUE58Trial01.md). Wait for the owner's next
instruction; the old attempt is not a work queue or an accepted character.
Do not automatically regenerate, reimport or fix this model.

The owner requested a standalone GASPALS experiment on UE 5.8 outside Multica,
then wanted to try a Tripo character in place of the mannequin. The project is
`D:/devgames/GASPALS_UE58/GASPALS.uproject`, using installed UE **5.8.3** at
`D:/UE_5.8`. Its upstream baseline is `a6d3812545063f0954b4b80d632848f2eb8032e2`;
the local setup commit is `7a62ee63977298d5d5fb0193959b26e058aa3130`.
Main MeridianSquad gameplay/assets were not changed by this model trial.

The owner is exploring Tripo's automatic rigging and its **UE5 Mannequin** preset.
The label alone does not prove exact Manny/UEFN skeleton compatibility: inspect
the actual export before deciding how it should be attached or retargeted.

## Preserved owner input

Original folder, unchanged:
`C:/Users/Origa/Downloads/tactical+jumpsuit+3d+model/`.

FBX: `tripo_convert_af913427-06d0-4fb0-8d94-afa79913f5f0.fbx`.
SHA-256: `8B342034E043263C83B3DC4C985941F0A1023429E506506F3E9F65A0F7B0667C`.
Its sibling `.fbm` folder contains base color, normal, roughness and metallic maps.
All five original file hashes were checked before discarding our working copy.

Earlier soldier reference images remain in
`C:/Users/Origa/.codex/generated_images/01a0cddd-4a26-7951-8158-cb2cf01fa6c1/`:

- `exec-a54261d4-d55b-4e1a-916c-e26bd05e785b.png`: original basic enemy soldier concept.
- `soldier-a-pose-v2.png`: unarmed front A-pose reference for Tripo.
- `exec-51664127-c23b-4dc0-9a23-0df0579e4364.png`: generated A-pose image.

The tested downloaded tactical jumpsuit is a different model from those images.
It is not an approved character design or a production asset.

## What the attempt established

- Export has **61 bones**, a UE4-like hierarchy (three spine bones, one neck,
  no UE5 extra spine/neck or IK helper bones), **28,332 control vertices** and
  **56,640 triangles** after triangulating its mixed polygons. It is authored
  in a T pose, not an A pose. All vertices had normalized skin weights.
- Raw export uses metre units and is about 94 cm tall. Import scale 1.9 made
  the mesh about 178.59 cm but left root scale **190**, producing a severe
  retarget translation error (pelvis around 185 m high).
- A separate Blender **5.2.1 LTS** normalization baked scale into mesh/rig data.
  The resulting UE root scale was **1**, height **178.59 cm**, with bone names,
  hierarchy and skin weights preserved. This fixed the huge translation error;
  it did **not** establish acceptable deformation or motion quality.
- Trial used a hidden UEFN animation driver and a visible custom mesh, a copied
  UE4 IK rig/retargeter, automatic target pose alignment and its own Blueprint/map.
  It was not a direct Manny skeleton substitution.
- UE 5.8 splits the old `Retarget IK Goals` operation into modern operations.
  Upstream `ABP_GenericRetarget.UpdateRetargetProfile` still accessed the obsolete
  IKChains controller. A **trial-only** graph port used `Blend to Source` and
  `Offset Goals`, with safe failed-cast paths. Original upstream assets were kept.
- The port preserves hand offsets interpolating from +/-2 cm to zero and leg
  offsets +/-4 cm. Its generated graph snapshots baseline chain settings; rerun
  the generator after changing those settings. Full hand-contact/traversal
  behavior was not validated.
- Idle, running, crouching and ragdoll/get-up executed in PIE. A bounded independent
  technical review found no blocker for a limited experiment. **The owner then
  rejected the visible result as too deformed. Technical checks do not override
  that judgement. The remaining deformation cause was not isolated.**

## State after stopping

PIE stopped; editor returned to `/GASPALS/Levels/DefaultLevel`.
All imported `/Game/TripoCharacter01` assets, the custom trial map, and our
`Assets/Source/TripoCharacter01` copied/normalized model and texture files were removed.
No trial model or texture binaries are retained in the closure commit.
The original Downloads folder and upstream GASPALS assets are preserved.

Investigation scripts remain at
`D:/devgames/GASPALS_UE58/Scripts/TripoCharacter01/` as historical reference only.
They depend on deleted working assets and are not an instruction to resume.
Local evidence remains under
`D:/devgames/GASPALS_UE58/Saved/Experiments/TripoCharacter01/`: source audit,
normalization and retarget reports, generated graph text, runtime samples,
screenshots and `discard_trial.json`. Evidence records an **unsuccessful owner
trial**, not accepted appearance. No new Multica task was created or dispatched.

The retained investigation scripts and stop notice are committed locally in the
separate trial as `835e0bc`. That repository is clean and contains no model asset
changes from this attempt.

Existing unrelated owner edits in MeridianSquad `Config/DefaultEngine.ini` and
`MeridianSquad.uproject` remain excluded from these documentation commits.
