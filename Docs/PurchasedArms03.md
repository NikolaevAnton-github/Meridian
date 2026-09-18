# PurchasedArms03: heading-independent rifle aiming

MSQ-63 worker handoff, 2026-09-18. The rifle now maintains its camera-relative
aiming pose while turning, including canted aim and nonzero pitch. The retained
`/Game/Maps/L_OpeningLobby_PainterStone01` is open with PIE stopped and no dirty
content or maps. Controller review, registration and the closure commit remain
controller-owned; this report does not grant owner visual acceptance.

## Confirmed cause and correction

The supplied `ABP_TFA_FP_BaseCharacter:AnimGraph` applied the translation of
`AímDownSightsTransform` to `ik_hand_gun` through
`AnimGraphNode_ModifyBone_2` in **world space**. Its rotation and scale already
used component space. The adjacent recoil and crouch nodes also used component
space, and the hand FABRIK targets used bone space.

The ADS spring supplies the constant authored translation `(-2,-6,2.05)` cm.
The native integration attaches the mesh to `FirstPersonCamera` at relative yaw
`-90` degrees. A fixed world translation therefore rotates in the player's
camera frame as the player turns. Before the change, measured gun displacement
was 8.9443 cm at a quarter turn and 12.6491 cm at the opposite heading. This
matches `2*sqrt(40)*abs(sin(yaw/2))`, independently predicted from that vector.
The recorded screenshots reproduce the owner's centered initial sight and
large lateral displacement on turning around, while RMB remains held.

Only the adapted FP AnimBP package changed. The ADS node now uses component
space for translation. One `RotateVector` node converts its incoming translation
by yaw `+90`, the inverse of the native camera-to-mesh anchor. Thus the normal
ADS vector becomes `(6,-2,2.05)` in mesh coordinates while retaining the original
camera-relative pose. This conversion also handles the composed canted vector
and follows camera pitch. It contains no spawn-heading capture or yaw-specific
aim compensation. If the native mesh anchor changes later, this documented
basis conversion must change with it.

The source ADS rotation/scale links, spring, recoil, hand IK, offsets, animation
clips and native camera code are unchanged. The vendor bundle and lobby map are
unchanged. No native C++ rebuild was needed for this asset-only gameplay change.

## Focused verification

The existing MSQ-62 input probe and evaluated-pose sampler were reused through
official Epic MCP. Mouse input turned a stationary pawn through
`0 -> +90 -> 180 -> -90 -> 0` while aim remained held. No locomotion, traversal,
jump, crouch or reload matrix was run. A second stationary take checked aim
release/re-entry at 180, canted aim at 0/180, pitch `+25` at 0/180 in both aim
modes, return to normal aim, and one aimed semi-auto shot/recovery.

The following maxima compare evaluated camera-space poses at matching phases of
the selected aimed locomotion blendspace, within 0.001 cycle and weight 1.
All comparisons hold grip, stance, camera mode and zero input velocity constant.
Cached unselected branches retain stale clocks/weights and are not mistaken for
currently contributing motion. Duplicate evaluation IDs are excluded.

| Check | Maximum position residual | Maximum rotation residual |
| --- | ---: | ---: |
| Normal aim, +90 / 180 / -90 / full-turn return | 0.000555 cm | 0.001013 degrees |
| Held-aim turn, nearest-phase subset | 0.000597 cm | 0.001095 degrees |
| Complete held-aim turn, interpolated initial-heading reference | 0.011481 cm | 0.029260 degrees |
| Original-heading pose before versus after | 0.000384 cm | 0.000846 degrees |
| Aim re-entry at 180 | 0.000559 cm | 0.000445 degrees |
| Canted aim, heading and +25 pitch comparisons | 0.000721 cm | 0.001023 degrees |
| Normal aim with +25 pitch | 0.000483 cm | 0.000981 degrees |
| Normal aim after the shot recovered | 0.000310 cm | 0.000520 degrees |

Position/rotation maxima include the gun bone, both hands and front/rear sight
components. These are unscaled presentation centimeters, before the existing
0.3 first-person rendering scale; they are not pixel measurements. The scoped
engineering gates were 0.05 cm / 0.05 degrees. There are 791 matched evaluations
in the nearest-phase post-fix held-turn comparison. The pre-fix opposite-heading settled
window has only two matches under the strict phase tolerance; the 229-match
continuous baseline and screenshots independently show the same defect.

The controller's coverage request was addressed by additional analysis of these
same traces, without a runtime rerun. The 791 nearest-phase matches alone have
uneven angular coverage. Linear position / shortest-path normalized-quaternion
interpolation of the initial-heading samples to each candidate's exact phase
covers all 1,860 unique held-turn evaluations, including all 24 fifteen-degree
yaw bins. The largest interpolation bracket is 0.166667 cycle, so the larger
0.011481 cm / 0.029260-degree residual above includes reference-interpolation
error and must not be described as a sub-0.001 cm full-turn measurement.

| Held-turn segment | All-phase comparisons | Samples while actively turning | Covered yaw |
| --- | ---: | ---: | --- |
| 0 to +90 | 534 | 63 | 0.0000 to 89.9997 |
| +90 to 180 | 517 | 67 | 89.9997 to 179.9999 |
| 180 to -90 | 508 | 65 | 179.9999 to 269.9986 |
| -90 to original | 301 | 70 | 269.9986 to 359.9987 |

Acceptance requires at least 1,800 all-phase comparisons and 40 turning samples
per segment, in addition to the geometric gates. Nearest-phase settled heading
counts are 78 / 99 / 113 / 56 (minimum 30 each); original before/after preservation
has 65. Re-entry has 38; canted heading/pitch comparisons have 87 / 96 / 87;
normal pitch has 19 / 81; normal return and recoil recovery have 71 / 45
(minimum 15 per variant). All matched sample timestamps, evaluation IDs,
heading bins and counts are recorded in `analysis03.json`.

Each comparison asserts equality of aim, canted state, crouched state, source
stance, grip, camera mode and source head lock. Aim is held, the stance/grip are
standing/default, no montage is active, and simulated velocity is zero. FOV is
78 degrees within 0.001 degree; paired FOV difference and target ADS position/
rotation differences are zero. Current ADS offsets and their distance from the
target must agree within 0.001 cm / 0.001 degree. In the held-turn comparison,
maximum current-offset difference is 0.000004668 cm / 0.000356 degrees, with
maximum settling error 0.000004668 cm / 0.000357 degrees. The same assertions
apply to each normal or canted variant against its corresponding reference.

All 20 screenshots are actual first-person captures at 2806 x 1948, with 78-degree
aim FOV and the same stationary capture location. The five normal after views
were visually inspected: the front/rear sight alignment stays centered across
headings. Canted/pitched views preserve the supplied canted presentation. Natural
idle motion and changing environmental lighting remain visible. Captures are
not a pixel-subtracted comparison or a performance benchmark.

Both after takes returned to 90-degree hip FOV with aim disabled and the ADS
spring translation below 0.000000001 cm. The single shot played
`AM_TFA_FP_AR_Fire_Semi`, reduced ammunition from 30 to 29, and produced nonzero
source recoil (1.8247 cm maximum translation) before recovering. Player
presentation and spawned physics checks found no shadow violations. The native
comfortable camera remained selected. No gameplay pause was requested; screenshot
capture can stall rendering. Twenty and 34 repeated evaluation samples in the
two after takes were excluded from pose analysis.

## Evidence and load checks

Evidence is under `Saved/PurchasedArms03/Worker/`:

| Artifact | Purpose |
| --- | --- |
| `graph-audit-before.json`, `ADS-nodes-before.txt`, `fix.json` | Actual node spaces/links, config offsets, exact before/after package hashes and successful compile with warnings treated as errors. |
| `Before01.json`, `After01.json`, `Variants01.json` | Evaluated camera/gun/hands/sights, native input activity, ADS targets, recoil, aim and camera states. |
| `analysis03.json`, `focused-checks.json` | Final matched-state and complete angular-coverage results, zero movement/shadows, FOV exit and shot recovery. Earlier `analysis.json`/`analysis02.json` are retained as partial analyses. |
| `Views/Before01-*.png`, `Views/After01-*.png`, `Views/Variants01-*.png` | Comparable original first-person images; dimensions in `view-dimensions.json`. |
| `cold-load.json`, `editor-cold.log`, `editor-state-handoff.json` | Fresh UE 5.8.1 process loaded the saved AnimBP as `BS_UP_TO_DATE`; the saved conversion/link/space were verified; retained map open, PIE stopped, no dirty packages. |
| `preservation-before.json`, `preservation-after.json`, `Rollback/` | Immutable starting hashes, exact binary rollback and final preservation check. |
| `execution-receipt.json` | Actual Astra/max context, max profile/default tier and native fast mode disabled; no worker profile changes. |
| `changed-files.json`, `lfs-policy.txt` | Exact worker-owned inventory/hashes and existing binary LFS policy. |

The fresh editor is PID 16676, recorded in `editor-cold.pid`; close it normally
through the editor when finished. The already-running editor was closed only
after confirming clean packages. Background throttling was restored to its
original enabled setting. The cold log contains normal host/plugin diagnostics
(optional profiler DLLs, audio sample-rate conversion, MCP licensing notice,
motion-vector CVar warning) and one expired pre-restart MCP session, recovered by
client reinitialization. No asset-load or Blueprint compile failure was observed.

Rider 2026.2 was connected to the actual project and debugger status returned no
active sessions. A `debugging-code` skill was absent from the installed skill
catalog and searched skill locations. No debugger attach or breakpoint claim is
made: live node properties, installed engine `AnimNode_ModifyBone.cpp`, and
evaluated runtime transforms establish the cause. Rider was used for read-only
inspection and tool bootstrap; Epic MCP performed the production mutation.

Preserved diagnostic attempts are not acceptance evidence: a node-type query
marked the target package dirty without retaining a node; it was reloaded from
the starting disk bytes. An unsupported Python graph-comment property aborted
the first edit before save; that unsaved attempt was discarded, then the bounded
change succeeded. A protected compiled-player property could not be inspected
through Python. The early attempt to match all cached player clocks was replaced
with the selected aimed blendspace analysis described above. Editor startup's
automatic config insertion was removed only after confirming that its removal
exactly restored the starting file; `config-restoration.json` records that check.

## Changed files and preservation

Existing binary changed:

- `Content/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/ABP_TFA_FP_BaseCharacter.uasset`

New project files:

- `Docs/PurchasedArms03.md`
- `Assets/Source/PurchasedArms03/source-manifest.json`
- `Scripts/PurchasedArms03/bootstrap.py`
- `Scripts/PurchasedArms03/tools03.py`
- `Scripts/PurchasedArms03/unreal03.py`
- `Scripts/PurchasedArms03/fix03.py`
- `Scripts/PurchasedArms03/analyze03.py`
- `Scripts/PurchasedArms03/handoff03.py`

The new source manifest is a single-package revision over the 400-package
PurchasedArms02 baseline. The other 399 active hashes and the prior manifest
remain unchanged. Exact active SHA-256:
`1688fbf28b0b1545df4cb9a0f8aab14df076f9649c0e9e808292280d026973e8`.
Starting adapted package SHA-256:
`5b7a53f454cd8670eb9f93c5ad808d1921be50d987c7b0c25debb307af95da9d`.
The vendor source fingerprint is also retained in the revision manifest.

The full preservation check covers 1,419 starting files, with none missing and
only the one authorized AnimBP changed. Native source, configuration, map,
vendor bundle and original-character sources match their starting bytes.
Pre-existing owner/controller changes in AGENTS, ProjectState and task/approval
files were not edited or staged. Historical acceptance/registry manifests were
not rewritten. Measured final project storage is 26,460,320,735 bytes (26.46 GB),
below the 250 GB cap. Generated evidence stays under Saved; no registry writes, status
administration, staging, commit, paid service or paused production work was
performed by the worker.
