# PurchasedArms01 — minimal lobby walkthrough

MSQ-61, 2026-09-18. Worker implementation and actual PIE verification are complete.
Controller review, the task-scoped local commit and owner acceptance remain with
the controller. The retained lobby opens with the existing native
`OpeningLobbyGameMode` / `OpeningLobbyCharacter` and the purchased FP arms, rifle,
handguard, iron sights and socket-driven magazines.

## Play and controls

Open `MeridianSquad.uproject`, press Play and focus the game viewport.

| Input | Result |
| --- | --- |
| W / A / S / D | Walk forward / left / backward / right, with directional arm animation |
| Mouse | Look |
| Hold right mouse button | Aim; release to return to the hip pose |
| R | Supplied ordinary magazine reload, including its aimed counterpart |
| Escape in PIE | Return to the editor |

Reload takes 3.666667 seconds. Repeated R presses during the action are ignored.
Its starting aim blend is held while the action plays; aim input received during
the reload takes effect when it finishes. Movement remains available throughout.
There is no ammunition simulation, empty reload, shooting, damage, inventory,
pickup, weapon switching, sprint, crouch, jump or showcase HUD. The former Space
jump binding was removed for this bounded walkthrough. No vendor gameplay
Blueprints or notify classes are used.

The capsule remains 34/88 cm, eye height 170 cm above its bottom, world FOV 90°,
walk speed 360 cm/s and step height 35 cm. The map is still
`/Game/Maps/L_OpeningLobby_PainterStone01`.

## Runtime presentation

`PurchasedArmsAnimInstance` is a native runtime animation instance. It samples
the supplied standing/aimed idle and four directional loops, blends from actual
movement velocity, applies the source idle-to-aim pose offset, and evaluates
reload additive data over explicit source base-pose assets. It does not rely on
editor `AnimPreviewInstance` behavior. Character and rifle proxies read one pawn
clock, with ordered component ticks and identical action times.

The rifle attaches to `ik_hand_gun`. Main and reserve magazines follow
`SOCKET_Magazine` / `SOCKET_Magazine_Reserve`. The reserve becomes visible at
0.455137 s; the main magazine hides at 2.520381 s. Completion restores one seated
main magazine and hides the reserve. These are the audited ordinary FP timings;
no dropped physical magazine or unrelated vendor event is spawned.

The final 0.15-second rifle blend preserves the sampled `Magazine_Reserve` bone
until completion. Its reference pose stores the magazine below the rifle; blending
that visible bone back to the reference pose caused the R1 displacement found in
controller review. Preserving the seated transform allows the final visibility
switch to the main magazine without that displacement. Other rifle channels and
the arms still blend normally. No source animation was changed.

The source +Y orientation is rotated -90° for the native +X pawn. Arms use a
camera-relative offset of (-0.663123, 0, -162.5751) cm, with an additional 0.85 cm
vertical fit at full aim. The camera itself keeps its existing height and FOV.
UE first-person rendering scales presentation depth by 0.3 to limit wall clipping;
this pawn's view uses a 0.1 cm near plane to retain wrists and the rear sight.
The front sight uses the handguard's authored `SOCKET_Sight_Front`.

All seven presentation components—arms, rifle, two magazines, handguard, rear
sight and front sight—disable cast, dynamic, static, hidden and contact shadows.
They have no collision. The arms are the inherited character mesh; there is no
additional body or hidden body mesh. Lobby lighting and shadow settings are
unchanged.

## Preservation and active content

The baseline covers 1,307 files, including all then-active Content, native Source,
Config, original protagonist editable sources and the untouched Weapon project.
`Worker/preservation-before.json`, `git-status-before.txt` and `Rollback/` preserve
the starting state. The final comparison reports no missing files and only the
four intended existing text files changed: the character header/implementation,
input mappings and project plugin list. New files are listed below.

No binary asset was edited or resaved. The retained map's SHA-256 before and after
is `b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
Owner geometry, material assignments, lighting, atmosphere and collision bytes
are therefore preserved. The owner's pre-existing Config edits and source FBX
change remain intact.

The live Asset Registry was inspected before pruning. No outside asset refers to
an archived package. The final unchanged hard-dependency closure contains **87
packages / 448,901,899 bytes**, including the source assets' hard art dependencies.
Five optional editor preview edges to four absent meshes remain documented in
`dependency-plan.json`; they do not enter the runtime hard closure.

**125 packages / 310,763,147 bytes** were moved to
`Assets/Archive/PurchasedArms01/Content/`, preserving their old relative paths:
26 original-character development packages, 44 audit-only template packages and
55 unused purchased-pack packages. `Assets/Archive/PurchasedArms01/manifest.json`
records both paths, sizes and SHA-256 for every move. The original source roots,
concepts, experiments, old decisions and review evidence remain inactive history.

With the editor closed, restore an archived package by verifying its manifest
hash and moving it back to its recorded original path only when that destination
has no conflicting file. The archive is outside Unreal's active Content root.
All 212 retained/archived binary packages resolve to the existing Git LFS policy.
Historical MSQ-52 selection manifests remain unchanged; the archive manifest
records the new locations without redefining their accepted fingerprints.

The explicit editor-only `MetaHumanCharacter` plugin entry was removed after its
development assets were archived and outside references were checked. No original
character startup script or other original-only config hook was present. Other
plugin and configuration entries were preserved.

## Verification and inspected evidence

Evidence root: `Saved/PurchasedArms01/Worker/`. `index.html` is the local screenshot
gallery; `verification-summary.json` contains the measured results.

| Check | Result |
| --- | --- |
| Execution settings | Actual session is Astra/max; native arguments use max and default service tier. `execution-settings.json` records the profile/native evidence. |
| Compilation | UE 5.8.1 / CL 56057345 Editor Development build succeeded after the R1 native correction (`build05-magazine-continuity.log`). |
| Fresh editor and spawn | Retained startup lobby and native game-mode override confirmed; possessed native pawn spawns at the existing PlayerStart. |
| Walking, looking, collision | Actual controller key/mouse pipeline; checkpoint lane, full hall approach and return. Wall stopped the capsule at Y=525.900 cm versus expected 526 cm. Subsequent diagonal movement, turn while walking, and moving aim press/release passed. No teleport or direct movement calls. |
| Aim and reloads | Aim press/release; five consecutive completed cases: hip, aimed with release during reload, aim requested during hip reload, aimed reload while walking, and hip reload while walking. Two extra R presses per action did not restart or enqueue it. |
| Synchronization | 965 route/action telemetry samples; maximum paired action-time difference 0 s. Rifle/magazine socket attachment error below 0.000001 cm. Right wrist drift relative to the rifle during sampled reloads was at most 0.112 cm across the recorded runs. |
| Magazine continuity, R1 | Actual evaluated samples before, inside and after the final fade in all five cases. Exactly one magazine is visible throughout this interval. Maximum seated-position gap 0.020341 cm; normalized-quaternion rotation difference below 0.000399 degrees. |
| Shadow flags | All five requested flags false on all seven presentation components, including the hidden reserve magazine. |
| Excluded controls | LMB, Space, Shift, Ctrl, C/F/E/Q/G, 1/2/3 and wheel input caused no movement, action-count or actor-count change. |
| Pruned project | Fresh process loaded 87/87 retained packages; no missing hard `/Game` reference and no archived package left active. |
| Handoff state | Retained lobby open, PIE stopped, no dirty map/content packages; temporary background-throttling change restored. |

`Acceptance02` contains the successful route. `Correction01` records the added
diagonal/turn/moving-aim checks. `Correction03` is the final action and R1 evidence:
598 samples and five completed reloads. `Visual01` supplies a comparable movement
capture near the same central position as the idle, aim and reload views. The
worker inspected actual idle/movement/aim frames, reserve/transfer frames and
late-fade/recovery views. Wrists and sight alignment remain coherent; the magazine
is largely below the gameplay camera during the final fade, so its continuity is
established by evaluated component transforms, with screenshots corroborating
the visible arms/rifle recovery. Independent controller review and owner visual
acceptance are separate.

`magazine-continuity.json` records the seated reference from the original rig
audit, normalized rotation comparisons, evaluation counters and screenshot
sidecars. Each row below has before/mid/late screenshots and a recovery capture
in `Correction03/`; the times are native evaluated action times, not wall time.

| Reload case | Before fade (s) | Mid-fade (s) | Late fade (s) | First recorded recovery (s) |
| --- | ---: | ---: | ---: | ---: |
| Hip | 3.478231 | 3.556565 | 3.632747 | 3.666667 |
| Aimed, release requested | 3.475914 | 3.556590 | 3.634870 | 3.666667 |
| Hip, aim requested | 3.471205 | 3.557101 | 3.633740 | 3.666667 |
| Aimed while walking | 3.475930 | 3.552907 | 3.636474 | 3.666667 |
| Hip while walking | 3.474644 | 3.574489 | 3.650525 | 3.666667 |

The final fade spans 3.516667–3.666667 s. For these narrow captures the verifier
temporarily pauses an already evaluated PIE frame while HighResShot renders and
consumes its large frame delta, then resumes normal simulation. The pause belongs
only to the diagnostic; production gameplay time and animations are unchanged.
All captures resumed successfully; PIE is stopped at handoff.

Earlier attempts remain preserved. `Acceptance01` used an old route that crossed
the owner's relocated checkpoint desk; the route was corrected from measured
live bounds. `Acceptance02/03` and `Correction01` exposed verifier wall-clock
timeouts while HighResShot suspended simulation. The verifier now uses the native
animation clock for reload and aim checks. `Acceptance04` passed the earlier
action checks but did not detect R1. `Correction01/02` lacked sufficient late-fade
capture coverage; `Correction03` supplies it and the offline analysis asserts the
actual evaluated capture times. These harness corrections required no further
native change after the R1 fix. Initial framing captures preserve the superseded
near-plane/aim-fit trials.

This is PIE/local editor validation, not a packaged-build or multiplayer test.
Handling audio and empty-magazine behavior are outside this walkthrough.

## Scoped files and controller handoff

- Modified: `Source/MeridianSquad/OpeningLobbyCharacter.h`, `.cpp`,
  `Config/DefaultInput.ini`, `MeridianSquad.uproject`.
- Added runtime code: `Source/MeridianSquad/PurchasedArmsAnimInstance.h`, `.cpp`.
- Added report and bounded tooling: this document and `Scripts/PurchasedArms01/`.
  The tools reuse the existing official Epic MCP transport and lobby input verifier.
- Reversible moves and manifest: `Assets/Archive/PurchasedArms01/` and the original
  Content paths enumerated by its manifest.
- Generated evidence, rollback text copies, build logs, active-file hashes and
  exact scoped file list: `Saved/PurchasedArms01/Worker/` (outside Git).

The controller owns the independent review, registry bookkeeping as needed for
historical relocated paths, local task-scoped commit and Multica closure. The
worker made no commit, status/profile changes, purchases, new models or lobby edits.
