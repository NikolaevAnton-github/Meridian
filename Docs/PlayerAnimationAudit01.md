# PlayerAnimation-Audit01 — MSQ-52 handoff

2026-09-17. **Technical audit accepted by the controller.** Datum16 remains
the owner-selected appearance. This audit does not approve a final character,
retarget result, camera fit, or gameplay implementation.

UE **5.8.1 / CL 56057345** played the four requested reload cases in both views,
with synchronized character and rifle sequences. The retained art subset contains
**186 byte-identical packages / 548,917,253 bytes**, including **82 sequences**.
All 186 packages loaded in a fresh editor process; no hard `/Game` dependency is
missing. Nine unresolved soft-reference edges are explicitly retained in the
report, mainly optional preview meshes and editor Control Rigs. They are not
runtime dependency closure failures and are not silently repaired in source bytes.

## Deliverables and evidence

Canonical contract directory: `Assets/Source/PlayerCharacter01/AnimationAudit01/`.

| File | Meaning |
| --- | --- |
| `rig-contract.json` | Concrete 161-bone hierarchy, parents, local/component bind transforms, fingers, twist/IK bones, measured skin influences, dimensions, import/export and representation interfaces. |
| `selected-sources.json` | Exact source/destination paths, SHA-256, byte counts, provenance and final selection. |
| `clip-matrix.json` / `.csv` | All 82 selected sequences: skeleton, duration, root/additive/base-pose settings, tracks, notifies, sampled poses and actual playback status. |
| `reload-timing.json` | Eight source montage timelines and their `DefaultSlot` / `Aiming` sequence pairs. Demo notify objects were deliberately not imported. |
| `contact-measurements.json` | Eight paired reload recordings and eleven representative local locomotion recordings, measured timestamps and bone-space findings. |
| `socket-contract.json`, `import-settings.json`, `blendspace-contract.json` | Native socket offsets/parents, recorded imports, and the five inspected blend-space sample/axis definitions. |

Full evidence: `Saved/PlayerCharacter01/AnimationAudit01/Worker/`.
Open `index.html` locally for the sampled playback viewer and camera comparison.
`Playback/Contact04-*` is the final reload evidence: fixed manual exposure,
default handguard/rear sight, main/reserve magazines and diagnostic visibility
events. Each adjacent JSON contains native PIE bone transforms and timestamps;
`frames.json` associates screenshots with samples. These are sampled captures,
not full-rate video. `Playback/Local-*` records native template locomotion.

Other important evidence: `assets.json`, `rigs.json`, `skin-weights.json`,
`socket-contract.json`, `details.json`, `rig-details.json`,
`source-montage-references.json`, `final-dependencies.json`, `cold-load.json`,
`preservation-final.json`, `lfs-policy-final.json`, `storage-final.json`, and `Logs/`.
Earlier failed/partial previews, exposure trials and the failed Contact02 callback
remain preserved. Use **Contact04**, not those earlier frames, for reload review.

## Actual checks

| Check | Result and boundary |
| --- | --- |
| Live editor identity / safety | Official Epic MCP confirmed MeridianSquad, correct lobby, PIE stopped; initial dirty maps/content were empty. Rider Python was used only to bootstrap the bounded Epic toolset and inspect initial state. |
| Reload playback | All 16 sequences, paired as four variants × FP/TP, reached **3.666666746 s**. Final recordings contain 76–82 telemetry samples per pair; observed character/rifle timestamp difference was **0 s**. Native `AnimPreviewInstance` evaluated authored additive bases. |
| Contact observations | Right-wrist displacement relative to the rifle root stayed within **0.003–0.080 cm** across final recordings. Main/reserve bone paths, left-hand reach, trigger-side finger motion and visibility intervals are recorded. This supports source grip coherence, not original-glove surface acceptance. |
| Native locomotion | Cardinal walk/jog and jump start/fall/land reached their source ends in eleven PIE recordings. All sixteen directional walk/jog clips and six jump assets were loaded and evaluated at four phases. |
| Mesh influence audit | Native GeometryScript inspected every LOD0 vertex: body 46,098 vertices / 74 weighted bones; FP mesh 20,326 / 52; rifle 13,365 / 7; opaque magazine 5,074 / 10. No invalid-weight vertices; character maximum eight influences, rifle/magazine one. |
| Final dependency/load check | 186/186 cold loads; zero missing hard `/Game` references. Nine unused soft-reference edges remain documented. No vendor Blueprint gameplay or montage survives in the final subset. |
| Preservation | **927 pre-existing files** verified unchanged: 671 Weapon source files, 242 original Content files, five Config files and nine native Source files. All 186 selected copies match their original SHA-256. |
| LFS | Every selected binary resolves to `filter=lfs` under the existing attributes. No commit or push was made. |

Initial editor-only preview components did not advance reliably; those frames were
rejected as playback evidence. The completed tests used disposable PIE worlds.
The source's saved header is `++UE5+Release-5.4`; it loaded and played in 5.8.1.

## Rig and fitting contract

Use **`MSQ52-RigContract01`**, not a generic “Manny-compatible” claim. The pack
`SKEL_TFA_Mannequin` and installed template `SK_Mannequin` have 161 bones and exactly
matching component bind positions. They remain different skeleton assets, with
empty compatible-skeleton lists. Direct reassignment/retargeting of reviewed
copies still requires a later validation; no source skeleton was edited here.

The simple full-body and FP meshes carry an 89-bone subset. Preserve the full
contract hierarchy in the original master; its corrective/helper branches are
identified separately from actual simple-mesh skin influences. The contract
enumerates all five fingers on both hands: three thumb joints; metacarpal plus
three joints for index, middle, ring and pinky. Preserve the two upper/lower-arm
twist bones per side and leg twist chains, plus `ik_hand_root -> ik_hand_gun ->
ik_hand_l/ik_hand_r` and `ik_foot_root -> ik_foot_l/ik_foot_r`. Additional corrective
twist branches are included in the exact manifest; do not infer their skin role
from a name. The supplied simple meshes do not contain `weapon_r`, although an
inherited `weapon_r_muzzle` socket references it; use the actual rifle muzzle
socket instead of assuming that mannequin socket is valid on the simple mesh.

Distances are centimeters. The source mannequin faces **+Y**, with **+Z up**,
while the gameplay actor faces +X: the component interface starts at **-90° yaw**.
Root reference transform is identity at ground level; the supplied bind is an
**A-pose**, distinct from the approved art's T-pose. Exact local bone rotations
and translations are authoritative; do not automatically reorient bones in a DCC.

Measured source constraints:

- Shoulder-joint separation **38.0198 cm**; upper arm **27.7711 cm**, forearm
  **27.2511 cm**, total shoulder-to-wrist chain **55.0222 cm**.
- Wrist to middle distal joint **15.9452 cm**. This is a joint measurement, not
  fingertip surface length or an approved glove size.
- Diagnostic mesh bounds height **180.5439 cm**; head reference/socket height
  **162.5751 cm**. Neither is owner-approved protagonist height.
- Preserve **34/88 cm capsule**, **170 cm camera**, **90° FOV**, **360 cm/s walk**
  and **35 cm step**. The **7.4249 cm** source-eye/camera difference is visible in
  `Camera/Final-*`; source ADS is below the fixed camera axis without fitting.
  Resolve original arm/body placement in MSQ-54/55, not by silently moving the camera.

The rifle uses a separate **16-bone** rig; the magazine uses **43 bones**, including
30 bullet transforms. Attach the rifle to character `ik_hand_gun` at identity and
evaluate its matching sequence on the same timebase. Attach main/reserve magazine
representations to `SOCKET_Magazine` / `SOCKET_Magazine_Reserve`; the weapon animation
drives their transfer paths. Exact sockets and import settings are recorded.

The original local body, FP arms and complete world body derive from one master.
Keep a stable gameplay camera; local torso/legs retain world scale; avoid duplicate
arm sections and shadows. TP upper-body actions layer over separately evaluated
leg motion. Owner-hidden world components must keep evaluating for shadows and
reflections. The audit did not build these gameplay components.

Source FBX import settings are scale 1, zero import translation/rotation, Convert
Scene on, Convert Scene Unit off, Force Front X off, T0-as-reference off and
reference-skeleton update off. `rig-contract.json` supplies a **proposed** Blender
export profile and exact matrix tolerances. No Blender export/round trip was
performed; MSQ-54 must prove the round trip rather than treating those settings
as a tested preset.

## Reload timing and extraction

All ordinary/empty and aimed/unaimed sequence counterparts exist and play.
Character reloads use local-space additive data over their recorded idle or aim bases;
weapon sequences are absolute. Do not play character additive deltas as complete
poses. Source montages pair ordinary and aimed sequences in `DefaultSlot` and
`Aiming` at rate 1. Native sequences themselves do not implement gameplay ammo,
visibility or dropped-magazine events.

Montage section extraction was unavailable for all eight inspected montages
(`reload-timing.json[*].composite_sections.unavailable`). Slot assignments,
sequence pairings and notify times were measured; complete section structure
was not verified and must be inspected if MSQ-57 relies on section transitions.

| Source view/case | Show reserve from | Hide main from | Drop event | Unlock actions |
| --- | ---: | ---: | ---: | ---: |
| FP ordinary | 0.455137 s | 2.520381 s | none | 2.631934 s |
| TP ordinary | 0.256150 s | 1.944525 s | none | 2.566667 s |
| FP empty | 0.860815 s | 0.433333 s | 0.433333 s | 2.949777 s |
| TP empty | 0.572721 s | 0.350720 s | 0.350710 s | 2.800000 s |

Visibility states run to the 3.6667 s montage end. The source left-hand grip
notify-state windows also differ; exact records are in `reload-timing.json`.
Contact04 emulates those visibility intervals using two attached magazines;
it does not execute vendor notify Blueprints, apply a gameplay IK layer, or spawn
the dropped magazine's physics. The latter remains an MSQ-57 integration test.
At montage completion, return to the base pose and normalize magazine identities
and visibility; freezing the raw end pose is not a complete reload state machine.

The one-second `A_TFA_AR_Magazine_FireDepletion` changes follower height from
**-4.7003 to 8.9268 cm** and drives bullet-scale depletion (sampled through its
native evaluated poses). The selected opaque mesh has only ten weighted bones;
the skeleton's 30 bullet bones do not imply 30 visible animated bullets in that
mesh. Treat this as a normalized ammo pose, not a one-second gameplay fire cycle.

All source montage references were inventoried from untouched packages. The eight
reload montages were temporarily loaded for timeline inspection with demo classes
absent; notify names/times remain readable, while demo notify objects are null.
The full unresolved dependency classes include `ANS_TFA_LeftHandGrip`,
`ANS_TFA_ShowReserveMag`, `ANS_TFA_HideMainMag`, `AN_TFA_DropMagazine` and
`AN_TFA_UnlockActions`; other excluded montages additionally reference the vendor's
ADS, casing, spawn/throw-object logic. See `source-montage-references.json` for the
complete source-to-reference mapping, including unrelated excluded actions.

Clean integration route: retain selected sequences and their hard art dependencies
at the original embedded root; create project-owned montages/events from reviewed
timing. Choose one authoritative ammo/drop/commit timeline and reconcile FP/TP
visual differences explicitly. Handling audio referenced only by excluded montages
must be selected and migrated with its cue dependencies in MSQ-57; source metadata
is available, but audio/gameplay event execution was not tested here. No author
showcase map/controller, whole sample framework or unrelated mechanic was migrated.
This follows the vendor's
[art-only extraction guidance](https://docs.infimagames.com/product/tactical-fps-animation-packs/guides-and-tutorials/editor/how-to-safely-remove-the-demo-code-logic),
while preserving the original paths and all source bytes.

## Motion coverage and bounded follow-up actions

| Requirement | Verified source coverage | Remaining bounded action |
| --- | --- | --- |
| Idle / aim / fire / dry fire / equip / holster | Selected pack FP/TP poses/actions; exact paths/settings in the matrix. Reload counterparts alone received paired end-to-end playback. | MSQ-55/57: original-rig presentation, ADS fit and firing/recoil probes. Front/rear iron-sight sources are selected; final sight zeroing is not accepted. |
| Directional walk / run | Installed template: eight walk + eight jog directions; cardinal directions played, diagonals evaluated. Pack FP has directional arm walk, forward run/sprint. | MSQ-56: retarget copies; review loop seams and speed/direction blends. All 22 selected local clips have root motion enabled; explicitly choose CharacterMovement-compatible in-place copies or a reviewed root-motion policy. Do not double-apply motion. |
| Jump start / fall / land | Pack FP phases and installed six-asset body jump set; representative body start/fall/land played. | MSQ-56: airborne state transitions, foot contact and landing recovery on the original rig. |
| Crouch start / end / idle | Pack FP transitions and crouched idle exist and evaluate. | MSQ-54/56: author original pelvis/leg crouch poses and joint-clearance tests. |
| Crouch movement | **Missing dedicated crouched leg motion.** `BS_TFA_FP_AR_Locomotion_Crouched` uses standing F/B/L/R arm loops at **0.8 rate**, plus crouched idle. Axes are Horizontal/Vertical, each -100..100. Sampled FP walk feet remain stationary. | MSQ-56: author four low-speed crouch directions plus idle/start/end around the original rig; add diagonals by blending only after a planted-foot check. |
| Planted stationary turns | **No selected turn-in-place clips.** | MSQ-56: author/review left/right 90° and 180° stepping turns, with explicit planted-foot intervals; separate body yaw from view yaw. |
| Pivots / starts / stops | **No selected directional pivot set.** Generic jog loops are not evidence of pivot coverage. | MSQ-56: author forward stop and left/right 90° / 180° direction changes at the selected walk/jog speeds. If authored results fail, inspect a bounded Lyra/Game Animation Sample clip inventory before any download; do not import its framework. |

No additional downloads, purchases, provider generation, paid APIs or local models
were used. Template source is the installed UE 5.8.1 High Characters resource;
its [UE EULA](https://www.unrealengine.com/eula/unreal) identifies Templates as
Examples. The weapon pack is owner-supplied; its purchase receipt/tier is not
present in the source directory. Exact installed hashes identify this audit's
source; no broader redistribution entitlement is asserted.

## Preservation and controller handoff

Preview worlds were `/Temp/Untitled_*` and their PIE duplicates. No preview map
was saved under shipped Content. Unselected worker-created copies and temporary
montages were moved to `Worker/ExcludedAuditCopies`, not deleted from the original
Weapon directory. The lobby was restored with no dirty map, then the editor was
closed, matching its pre-run closed state. A fresh final load also ended with
zero dirty packages. The first editor startup auto-added a configuration field;
only that automatic addition and trailing newline were removed, with the exact
pre-run SHA-256 verified in `engine-auto-config-restoration.json`.

Preservation above is the successful **12:44 UTC** check. During final handoff,
a later editor process (PID 25364, started approximately 12:48 UTC) was observed.
`DefaultEngine.ini` again contains the automatic startup field/trailing-newline
change; removing those in memory reproduces the exact pre-run hash. This later
session and its configuration were left untouched. See
`post-verification-state.json`; the worker's completed evidence was not rebaselined.

Measured project storage grew from **51.291 GB to 52.202 GB** (decimal), about
**0.912 GB**, including retained failed evidence/copies. Subsequent handoff/log
copies add under 10 MB; the result remains below **52.22 GB**, within the 250 GB
cap. No owner asset was removed to reclaim space.

Bounded scripts are under `Scripts/PlayerCharacter01/animation_audit01_*`.
They reuse the existing official Epic MCP transport. `verify_hashes` checks
preservation and selected identities; `animation_audit01_evidence.py` validates
completed recordings and rebuilds the local viewer. The final staging script
restores only manifest-identical selected files when a final manifest exists.

The controller inspected the contract, actual Contact04/camera images and source
identities, supported by a separate read-only technical review. Two prose
corrections distinguish idle/aim additive bases and disclose unavailable montage
section extraction. The original worker report remains preserved in
`Saved/PlayerCharacter01/AnimationAudit01/Controller/worker-handoff-original.md`.
Source-rig playback is not original-character retarget/contact acceptance.

Controller evidence: `Saved/PlayerCharacter01/AnimationAudit01/Controller/technical-review.json`.
The `meridian_assets` registry now inventories `PlayerAnimationAudit01` with
195 artifacts (186 selected Unreal packages and nine contract/metadata files)
and 271 observed hard-reference relationships. Register, inspect and validate
passed using the existing registry tools. Its manifest is
`Scripts/AssetRegistry/manifests/PlayerAnimationAudit01.json`; unused soft
references retain their documented limitations. Exact contract bytes are protected
from Git newline conversion, and selected binaries use the existing LFS policy.

The controller restored the saved Multica profile/native arguments and completed
MSQ-52 administratively without starting another run. No successor was started;
the worker did not change task states/profiles or make a commit/push. Controller
staging adds up to the selected 549 MB to local Git LFS storage, keeping the
project below 53 GB against the 250 GB cap.
