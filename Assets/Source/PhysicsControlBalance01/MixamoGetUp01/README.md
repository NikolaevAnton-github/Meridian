# Mixamo GetUp01 source intake

Downloaded 2026-09-20 for MSQ-87 at the owner's request. These are the two
selected source candidates for later Manny retargeting and physical get-up
integration. This intake does not dispatch gameplay implementation or establish
in-game motion acceptance. Kimodo GetUp01 remains preserved separately.

| File | Mixamo catalog description | Frames at 30 FPS | Motion duration |
| --- | --- | ---: | ---: |
| `GetUp_FromBack_XBot.fbx` | Getting Up From Back | 251 | 8.333 s |
| `GetUp_FromStomach_XBot.fbx` | Getting Up From Stomach | 259 | 8.600 s |

Both catalog entries have the display title **Getting Up**. They were selected
by their distinct descriptions in the [Mixamo search](https://www.mixamo.com/#/?page=1&query=get%20up&type=Motion%2CMotionPack).
The browser downloaded them as `Getting Up.fbx` and `Getting Up (1).fbx`.
Only the stored filenames changed; the FBX bytes are original downloads.

## Export settings

- Character: X Bot, preserving its source mesh and skeleton for later retargeting.
- Format: FBX Binary; the downloaded files report FBX version 7700.
- Skin: With Skin for both self-contained sources.
- Frames per Second: 30.
- Keyframe Reduction: none.
- Trim: 0-100, full clip; Mirror off.
- Overdrive, Get Up and Character Arm-Space: 50 on both clips.
- Injury Level: original displayed values, 0 for back and 50 for stomach.
- No in-place conversion, custom retiming or other motion edits were applied.

The export settings and clip parameters were verified in the Chrome UI.
The source durations are not selected gameplay recovery times.

## File verification and import note

Blender 5.2.1 LTS's existing FBX parser successfully reads both files. Each
contains 65 skeleton bones, two mesh geometries and 315 animation curves.
Animation values are finite and curve times increase at the expected 30 FPS
sample interval. SHA-256 and sizes are recorded in `provenance.json`.

Each FBX contains both a `Take 001` stack and a `mixamo.com` stack. The latter's
local stop agrees with the full motion key range above; the generic global
timeline and `Take 001` stop at 3.333 s. During import, preserve the full
`mixamo.com` motion range rather than truncating to that generic timeline.
No Unreal import, Manny retargeting, ragdoll blend or visual validation is claimed.

Read-only inspection evidence and script:
`Saved/CombatSlice01/PhysicsControlBalance01/MixamoGetUp01/`.
Registry inventory: `MixamoGetUp01`, two source artifacts, no dependency edges.

Adobe's [Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)
states that the service is free and its characters and animations can be used
royalty-free in commercial projects, including games. Preserve the source
provenance; these files are third-party animation sources.
