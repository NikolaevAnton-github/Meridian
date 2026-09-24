# MSQ-121 / GASPALSLocomotion01 Correction01

Candidate02 corrects **GL01-R1 and GL01-R2** from the sole primary
[Candidate01 review](GASPALSLocomotion01Review.md). The two production changes,
focused native checks and Development Editor build are complete. The matching
module is loaded in the retained lobby editor. Finding closure, controller
acceptance/registry/commit and owner Play judgment remain separate.

Authority remains the direct owner correction request and
[OwnerStart02](Approvals/GASPALSLocomotion01-OwnerStart02.json). This correction
uses one production executor, Astra/max/default with fast mode disabled. Native
process arguments and execution metadata are in Candidate02 evidence. No worker,
reviewer or Multica run was dispatched.

## GL01-R1: one projectile representation for the owned source pawn

[CombatProjectileWorld.cpp](../Source/MeridianSquad/CombatProjectileWorld.cpp)
now resolves a physical projectile owner consistently. An adopted source pawn
and its fixture represent the same skeletal body. The association requires
`Fixture->Foundation == Actor`; another actor merely owned by a fixture does not
acquire this identity.

The adopted `ACharacter` movement capsule is excluded from generic capsule
sampling, cached-sample aim queries and segment arbitration. The consumer gate
also rejects an old generic sample if that character has since been adopted.
The exclusion does not depend on health, readiness, crouch or ragdoll, so a corpse
cannot switch to a competing capsule receiver. A temporarily unready physical
body does not fall back to bone-less generic damage.

The retained physical tracer remains the authoritative contact source. Its hit
contains the fixture, skeletal component, actual bone and impact point. Nearest
contact arbitration and the existing single `ReceiveBullet` dispatch remain;
the correction does not forward a capsule hit or introduce another impulse.
Ordinary player/prototype characters retain their existing capsule/region path.

Both the wrapper and source-pawn shooter identities use the same skeletal launch
clearance and self-contact attribution. Existing immunity lasts until the shot
leaves its launch body; later re-entry can still produce a self-hit. Earlier world
or other-body contacts still win by contact time. Finite-flight sorting by contact
time then shot ID, collision filtering, frame scheduling, reset clearing and pose
epochs retain their previous production implementations.

## GL01-R2: proposed CMC stance geometry reaches clearance consumers

[EnemyCombatCover.cpp](../Source/MeridianSquad/EnemyCombatCover.cpp)
now handles the active `ACharacter`/CMC stack before the retained Mover branch.
Standing proposals use the character class default capsule, including while the
achieved capsule is crouched. Crouch proposals use the current unscaled radius
and actual CMC `GetCrouchedHalfHeight()`, clamped to at least that radius.

The component's current scale supplies the proposed dimensions. Installed UE
5.8 capsule getters scale radius by `min(X,Y)` and half-height by `Z`; the adapter
uses those rules. CMC crouch retains current radius, while uncrouch restores class
default radius and height. The engine excerpts are frozen in
`Evidence/source-contract-check.json`. Missing components/defaults, non-finite
values, non-positive scale/radius or a resulting height below radius fail closed.
The old Mover branch remains and also explicitly rejects non-finite radius.

| Geometry state | Reused source dimensions at unit scale | Correction behavior |
| --- | --- | --- |
| Standing proposal | Radius 50 cm, half-height 86 cm | Uses class standing defaults, including when currently crouched |
| Crouched proposal | Radius 50 cm, CMC half-height 60 cm | Uses the current radius and actual CMC crouch setting |
| Achieved crouched read | Radius 50 cm, half-height 60 cm | Existing `CapsuleSize` read remains unchanged |

These are source/default dimensions, not measurements from gameplay. The
production `TacticalGround`, `TacticalWalk`, `CoverCapsule` and `CoverWalk`
consumers can now obtain explicit CMC stance proposals and reach their existing
ground, overlap and sweep checks. Active mobile requests still supply standing
stance; standing lean-edge and crouched low-cover requests retain their policy.
No tactical selection policy or unrelated AI behavior was changed.

## Focused evidence

The [immutable Candidate02 manifest](../Saved/GASPALSLocomotion01/Worker/Candidate02/candidate-manifest.json)
records every final task production file, all native build inputs, the DLL,
build receipts, archive composition and frozen evidence hashes.

| Check | Result and exact boundary |
| --- | --- |
| `Evidence/routing-02.json` | **29 assertions pass.** Compiles exact production ownership helpers, capsule sampling/history, skeletal sampling, segment arbitration loops, physical launch-clearance branch, single damage dispatch and contact-time/shot-ID ordering. Covers owned versus ordinary/prototype character, stale generic sample, actual hit bone/point retention, one physical receiver call, earlier blocker, wrapper/source launch identity, self re-entry, corpse eligibility, reset sample replacement/epoch and no unready-body fallback. |
| `Evidence/geometry-01.json` | **26 assertions pass.** Compiles exact production geometry adapter, achieved read and clearance consumers. Covers standing, crouch, standing while crouched, source defaults, scale/radius rules, mobile ground/walk and standing/crouched cover reaching overlap/sweep queries, blocked or unsupported geometry and invalid input rejection; retains Mover compatibility. |
| `Evidence/source-contract-check.json` and `affected-source-excerpts.txt` | Identifies active call sites and engine size rules. Confirms unchanged `BuildQuery`, `CapsulesAt`, `ClearProjectiles`, `ResetTargets` and `AdvanceFrame` against preserved pre-correction bytes. Preserves physical trace, pose-epoch and mobile request wiring excerpts. |
| `Evidence/build-correction01-01.json` / `.log` | Development Editor build **passes**, exit 0, 13.485 seconds. Compiles the two changed production files and links the module. Existing StructUtils plugin deprecation is retained; no new correction compile warning. |
| Editor state and loaded-module evidence | Official Epic MCP confirms the project, retained map, no PIE and no dirty packages. Windows module inspection confirms editor PID **14348** loaded the matching project DLL. |

These checks execute extracted native production code with explicit plain-data
actor, contact and collision-query boundaries. They do not instantiate an Unreal
world or validate physical motion. The unchanged skeletal trace supplies the
production bone hit; the pure arbitration check receives a recorded contact at
that boundary. Query counters show the actual compiled clearance consumers reach
their collision calls. No gameplay, firing, PIE, game-world simulation or broad
AI retest was performed. One initial routing harness compilation failed because
an extracted nested type needed a local alias; the corrected harness passes and
the failed evidence is retained.

The loaded DLL is `Binaries/Win64/UnrealEditor-MeridianSquad.dll`, SHA-256:

`600731ab8e22aba32834ec33bd2b26798377b69879f1de0f70d3a0f28667f3b8`

## Reused evidence and preservation

Candidate01's source intake, assets, Blueprint compilation, dependency closure,
animation/source defaults and 21 production FireMotion assertions are reused.
No asset import, graph edit, full asset matrix or repeated animation test was
needed. The sole primary review supplies the corrected graph count: **1,172
full-path unique non-comment original nodes retained, four added**. Its
[technical evidence](../Saved/GASPALSLocomotion01/Review/technical-evidence.json)
is referenced by hash. The original worker report's 1,084 count remains untouched
as historical evidence; it collapsed repeated graph names.

`Evidence/preservation-check.json` verifies the 68 protected historical files,
all 2,133 Candidate01 production entries, its three original preservation
records and all 2,096 asset-revision entries remain byte-for-byte unchanged.
The correction's pre-edit source/config/map bytes are in `Evidence/before.zip`.
Current owner `Config/DefaultEngine.ini`, `MeridianSquad.uproject`, the retained
map and `.gitattributes` remain exactly as found before this correction. Original
source intake provenance is unchanged; nothing was written to the source project.
Controller-owned approval, state, task, review and acceptance documents were not
edited.

The complete final candidate uses the immutable Candidate01 `production.zip`
plus Candidate02 `production-delta.zip`. The delta holds corrected/new files,
otherwise unchanged native build dependencies and the matching DLL/receipts;
it does not duplicate or replace unchanged source assets. Candidate02's complete
`production` inventory and separate `native_build_inputs` identify the final
bytes, rather than treating a delta alone as the final identity. Archives and
generated build/evidence files stay under ignored `Saved`; inherited binary
content retains existing Git LFS rules. The project capacity measurement is in
the manifest and remains below the 250 GB ceiling.

## Changed files and controller handoff

The complete correction file list is
[Candidate02/changed-files.txt](../Saved/GASPALSLocomotion01/Worker/Candidate02/changed-files.txt).
It contains these 14 files:

- `Source/MeridianSquad/CombatProjectileWorld.cpp`
- `Source/MeridianSquad/EnemyCombatCover.cpp`
- `Scripts/GASPALSLocomotion01/Correction01/check.py`
- `Scripts/GASPALSLocomotion01/Correction01/evidence.py`
- `Scripts/GASPALSLocomotion01/Correction01/geometry_boundaries.cpp`
- `Scripts/GASPALSLocomotion01/Correction01/geometry_consumer.cpp`
- `Scripts/GASPALSLocomotion01/Correction01/geometry_tests.cpp`
- `Scripts/GASPALSLocomotion01/Correction01/package.py`
- `Scripts/GASPALSLocomotion01/Correction01/prepare.py`
- `Scripts/GASPALSLocomotion01/Correction01/routing_boundaries.cpp`
- `Scripts/GASPALSLocomotion01/Correction01/routing_tests.cpp`
- `Assets/Source/GASPALSLocomotion01/revision-Candidate02.json`
- `Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate02.json`
- `Docs/GASPALSLocomotion01Correction01.md`

The new [revision](../Assets/Source/GASPALSLocomotion01/revision-Candidate02.json)
references unchanged intake and Candidate01 asset provenance, both native
corrections, the new DLL and Candidate02 evidence. The new
[registry input](../Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate02.json)
retains inherited artifact descriptors and adds this revision with Candidate02
evidence. It is prepared only: no registry mutation, staging or commit occurred.
Controller review closure should remain limited to GL01-R1/GL01-R2 and their
directly affected seams, reusing the passing original review criteria.

## Next owner Play route and limitations

The editor remains on `/Game/Maps/L_OpeningLobby_PainterStone01`. The owner can
start Play using the existing enemy route, check ordinary skeletal hits and
continued fighting, enemy shots leaving their own body, strong impacts/death
and corpse hits, then use the existing F6 reset and Y slowdown controls through
those transitions. Observe lateral/mobile movement, crouched low-cover and
standing/lean proposals after crouch. No new debug input or gameplay system was
added for this correction.

Source movement/aim equivalence, physical hit feel, knockdown/get-up reliability,
actual mobile fire/cover use and reset/slowdown behavior still require owner Play.
The pure checks and editor build do not establish those runtime or visual
outcomes. Packaging and multiplayer remain outside this editor-prototype scope.
