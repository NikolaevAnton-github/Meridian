2026-09-24. **PASS within the authorized technical scope for MSQ-120 / CAI-T03,
Candidate01/build03.** No acceptance-blocking technical finding was identified.
This is the sole primary independent review of ML01-ML06. Controller scope/evidence
acceptance and closure remain separate. Actual motion, cover usefulness, combat
feel, difficulty and performance remain **PENDING OWNER PLAY**.

The review follows `Docs/Tasks/CombatAI01/CAI-T03.md`, its linked owner decision
and the current Multica review assignment. It directly inspected the changed
production paths, relevant unchanged consumers, actual retained asset exports
and matching evidence. No editor operation, gameplay, PIE, animation playback,
gameplay simulation, firing probe, gameplay screenshot or performance probe ran.
Production, profiles, status, historical evidence and Git history were not changed
by the reviewer.

| Criterion | Verdict | Technical basis |
| --- | --- | --- |
| ML01: useful movement and independent weapon ownership | PASS | Real bounded lateral/approach requests reach the route follower; Aim/Burst/shot/rest retain the movement token. Range, support, progress, deadline and retry bounds remain. |
| ML02: achieved-motion fire and preserved safety/timing | PASS | One motion contract feeds policy, CanShoot and launch spread. Fresh sight, achieved stance, actual barrel alignment/corridor, authority, ammo/reload and world-time gates remain. |
| ML03: signed skeletal lean and return | PASS for source/math/asset wiring | Native correction reaches component-space additive spine_01 before hand IK; both signs preserve barrel direction under the checked yaw/pitch combinations. Pelvis/legs are outside the lean subtree. Actual physical motion remains owner testing. |
| ML04: protected reachable edges and achieved exposure | PASS | Each side is assessed from static geometry and permitted sight evidence. Same feet anchor both neutral and firing poses. Actual socket displacement and clearance precede fire. The additional full-selector checks close the executor fixture gap. |
| ML05: handoffs, cancellation and observability | PASS | Cover/mobile/low-cover owners are exclusive; return retains feet until neutral posture is acknowledged. Physical interruption, death, weapon loss, disable and reset clear both action lanes and offsets. Dedicated status fields expose motion, ownership, lean and launch gates. |
| ML06: build, production checks and preservation | PASS within stated boundaries | Matching Development Editor build, 67 reused production assertions, 18 reused native math cases, actual graph/bone evidence and 33 new selector/route assertions. Identity and administrative drift are recorded below. |

**Movement and firing.** `Source/MeridianSquad/EnemyCombatComponent.cpp:48`
creates a separate generation-checked movement runtime. `ClearMovement` at line
60 ends that lane; `ClearIntent` at line 71 cancels both lanes. The producer in
`EnemyCombatMobile.cpp:43` assesses two bounded lateral options or one cautious
step, validates support/route, retains useful range and checks intermediate/end
sight for a strafe. Defaults are 180 cm lateral travel, 450 cm cautious approach,
four world seconds per active attempt and 3.2 world seconds between completed or
failed attempts. The selected goal is fixed during that attempt.

`EnemyCombatPolicy.cpp:195` advances movement before the independent weapon
action. `AdvanceWeapon` at line 29 only stops travel when cover owns the feet;
ordinary aim, shots, burst completion and burst rest do not replace movement.
The real follower at `EnemyCombatNavigation.cpp:217` consumes `MoveAction` and
the actual route, rejects obsolete tokens and applies support/progress checks.
Its final waypoint threshold respects the lean anchor's tighter 12 cm acceptance.
Reload may stop movement; firing while reloading is not claimed.

`GASPEnemyRifle.cpp:43` derives speed and vertical motion from Mover and ground
state from CharacterMover. `CombatAIMobile.h:13` permits grounded walking through
220 cm/s with at most 45 cm/s absolute vertical speed; a running request above
15 cm/s is rejected. This contract is consumed by `EnemyCombatPolicy.cpp:34`,
`EnemyCombatComponent.cpp:233` and the launch spread at line 302. The retained
stationary check in `EnemyCombatCover.cpp:312` belongs to low-cover posture
transitions; it does not veto direct mobile fire. No contradictory stationary-only
enemy launch consumer was found.

Every birth in `EnemyCombatComponent.cpp:281` validates burst generation and
deadlines, re-observes the player, then checks range and CanShoot. Successful
sight alone updates remembered positions (`EnemyCombatComponent.cpp:207`), using
the actual head as sensor origin at line 184. The actual rifle muzzle, achieved
aim/stance and torso-to-muzzle plus muzzle-to-target corridors gate launch at
lines 224 and 249. Moving spread adds a bounded speed-dependent cone to the
existing spread; it uses achieved velocity rather than the movement command.
Successful launches alone decrement magazine/burst counts and schedule the next
world-time shot (`EnemyCombatComponent.cpp:305`). The unchanged projectile manager
retains finite-flight births and world-delta advancement
(`CombatProjectileWorld.cpp:149`, line 321). Unaffected MSQ-119 projectile,
senses, health/weapon context and slowdown evidence is reused; no new gameplay
timing claim is made.

**Pose and geometry.** `GASPALSRifleAnimInstance.cpp:113` composes lean about the
heading-corrected swept barrel axis, rather than rotating the pawn or capsule.
The frozen actual graph connects `GetRifleAimCorrection` to an additive
component-space `spine_01` ModifyBone, then left-hand TwoBoneIK, then the retained
PreRagdoll pose. The layer, correction and hand IK all use `RifleAlpha`. The IK
effector is in `hand_r` bone space; the rifle itself attaches to `hand_r`
(`GASPEnemyRifle.cpp:128`). The recorded skeleton ancestry places the head and
both hands below `spine_01`, with pelvis, thighs and feet outside it.

The native function's 18 transient-object cases cover both 32-degree signs at
yaw -45/0/+45 and pitch -35/0/+35. The rotated child offset changes sign while the
barrel dot product stays above .99999. These are native transform tests, not
measurements of a running character. The actual animation consumer at
`GASPALSRifleAnimInstance.cpp:75` removes voluntary pose authority during physical
recovery/death/weapon loss and uses the installed constant interpolator for
120 degrees per world second out/return. The retained turn blend limits rearward
lean; inability to achieve it is bounded by exposure deadlines.

`EnemyCombatCover.cpp:159` independently brackets/refines both static shadow
edges; `AssessCoverOption` at line 125 checks a protected standing anchor and a
lean arc with identical anchor/firing feet. Selection at line 224 freshly
reassesses the winner and obtains a route to the **edge anchor**, rather than to
the original scan sample. Proposed geometry cannot authorize a shot.
`EnemyCombatLean.cpp:73` captures actual neutral head/chest/hand/muzzle sockets,
requires concealed upright head position and checks four arc samples plus body
and rifle segments. `AchievedLeanClear` at line 99 requires both the signed
animation angle and actual signed head/chest displacement, settled grounded feet
and current clearance. A requested float alone fails. Fire rechecks the achieved
posture and current muzzle after fresh sight; it never reads a hidden player's
live location to choose an edge.

The cover owner handles no contact, rejected pose, blocked space and stale
evidence through finite exposure/return/retry paths
(`EnemyCombatLean.cpp:127`, `EnemyCombatCover.cpp:278`). Return waits for both
angle and actual socket displacement; a refused return ends after 1.2 world
seconds and replans from actual feet. Side failure histories are independent.
The existing low-cover branch remains separate at `EnemyCombatCover.cpp:310`.
Cleanup paths at `EnemyCombatComponent.cpp:94`, line 113, line 135 and line 145,
plus weapon loss in `EnemyCombatPolicy.cpp:117`, cancel ownership, pending fire
and lean state. Recovery begins a new search from actual feet. New observation
fields at `EnemyCombatObservation.cpp:109` and line 253 expose the separate
movement lane, mobile phase/goal, achieved speed/grounding, motion/launch gates,
spread and requested/animated lean.

**Reused and new evidence.** The frozen executor results are applicable:
`checks-07.json` reports 67/67 production assertions; `build-result03.json` and
`build03.log` record a successful native Development Editor build;
`editor-after.json`, `graph-after.json`, `ik-after.json` and `bone-parents.json`
supply the native cases and actual asset evidence. Inspection confirmed all
**75 extracted method/fragment identities** against current production or the
installed engine, and their verbatim presence in `generated-07.cpp`.

The executor's lean fixture directly installed a selected plan. It therefore
did not establish the newly changed full scan-to-edge-route handoff. The review
added only that missing check, reusing the frozen extraction and existing
collision/clock/achieved-feet boundaries. `selector-result01.json` records
**33 assertions, zero failures**. Actual production scanning selected the left
edge at `(0,-77.6875,0)` with both sides available, the right edge at
`(0,77.6875,0)` with the left blocked, and the left edge with the right blocked.
Both blocked yielded a finite no-option retry. The scans took 32/34/34/36 bounded
decisions. Selection installed the correct edge route/token, weapon ownership
preserved that route, acknowledged arrival entered upright protection, and
expired evidence ended the unexposed plan without authorizing fire. No original
behavior test or native build was rerun.

The fixtures replace collision queries, world clocks, sight acknowledgements,
pose sockets, locomotion acknowledgement and projectile storage at explicit
boundaries. They do not validate actual animation playback, Physics Control
tracking, dynamic scene collision or owner-perceived motion. The native math and
actual graph inspections provide separate pose-wiring evidence. Those limits are
compatible with the owner's prohibition on agent gameplay testing.

**Identity and preservation.** Evidence generated by this review is under
`Saved/CombatAI01/CAI-T03/Review/`.

- Baseline/current HEAD: `5ec150a5fe232c72ddc7163d52495f93b41d99e3`.
- Candidate manifest SHA256:
  `5036d92fc6998c9af3dc7c67fc3d9975b14adb6b8ee63cb4f720badd1a1bc0af`.
- Matching DLL SHA256:
  `a0a8a67d1c15450aa14c2244477f88966d06ae8408f255473b03868a8e304fc7`.
- `identity01.json`: **298/298** current manifest entries match, including
  source, assets, DLL, scripts and evidence. The executor's frozen archive
  verification is reused; the manifest was not rewritten.
- `preservation01.json`: **157/157 assets** and **362/362 historical files**
  match. Six of eight captured administrative/owner files remain byte-identical,
  including owner config, project and retained map. The other two differences
  are explicitly resolved by `administrative-drift01.json` and its exact diffs:
  AGENTS.md's auto-managed identity changed from executor to reviewer, and
  ProjectState gained the paragraph saying Candidate01 is in primary review.
  Durable rules are unchanged. These are live administrative changes outside
  the candidate, not production drift; neither was made or restored by this
  reviewer. The initial strict preservation assertion failure remains preserved.
- `reviewer-settings01.json`: configured profile and actual native PID 51472
  specify Astra/max/default with fast disabled. This run's native turn context
  separately records `gpt-6-astra` / `max`; its null tier is interpreted together
  with the explicit default native argument. No setting was changed.

No correction is required by this technical review. Owner testing still needs
to judge planted-foot appearance, actual torso/rifle motion, practical edge
usefulness and combat feel. Standing lateral lean, conservative static geometry,
the documented walking-fire envelope and no lean-fire during travel remain the
declared limits. The controller owns final live-editor readiness, scope/evidence
acceptance, task status and the local closure commit.
