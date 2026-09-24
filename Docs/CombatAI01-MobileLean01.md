# MSQ-120 / CAI-T03 mobile fire and torso lean

2026-09-24. Candidate01/build03 implements the authorized follow-up on MSQ-119
Candidate02/build01. Native build, 67 extracted production assertions and 18
native pose-math cases pass. Primary independent technical review and owner
gameplay/motion acceptance remain pending. No agent gameplay, PIE, firing,
animation playback, gameplay simulation, screenshots or performance probes ran.

Authority: [task](Tasks/CombatAI01/CAI-T03.md) and
[owner instruction](Approvals/CombatAI01-MobileLean01-OwnerStart01.json).

## Behavior

Movement has its own generation-checked action runtime. Aim, burst start,
individual shots, burst completion and burst rest preserve a valid movement
request. Existing navigation follows the actual supported route and stops on
arrival, obstruction, stale ownership, lack of progress or deadline. Search and
low-cover movement use this same movement runtime. ClearIntent cancels both
movement and weapon ownership.

After establishing useful direct fire, the opponent can request a deliberate
1.8 m lateral walking step. Two deterministic sides are considered independently;
the proposed route and intermediate/final sight are checked before commitment.
The endpoint retains weapon range instead of closing toward the player's feet.
Completed or failed attempts rest for 3.2 world seconds. Movement is capped at
four world seconds and does not restart at each burst. Cover scans run between
these short steps. A hurt agent retains the existing protection preference.

Beyond effective rifle range, a valid cautious approach is at most 4.5 m per
request. It may start firing as it enters range while finishing that same step.
Blocked corridors produce a bounded stationary fallback; an obstructed muzzle
does not authorize charging the remembered player position.

The supported fire envelope is **achieved grounded walking at 0–220 cm/s**, with
absolute vertical speed at most 45 cm/s. A running command above 15 cm/s is
unsupported. Recovery/death/readiness, achieved stance, rifle blend, current
sight, actual barrel alignment, near-cover corridor, finite ammunition, reload,
cadence and finite projectile gates remain. Unsupported motion cancels pending
burst ownership, lowers the rifle and requires aim settling again. The projectile
manager and its collision/time consumers are unchanged; no stationary-only
enemy launch consumer remains.

Moving spread adds `1.6 * clamp(actual_speed / 220, 0, 1)` degrees to the retained
0.6-degree cone. At 175 cm/s the total is approximately 1.87 degrees. This uses
Mover velocity, not a movement-request flag. Cadence (.18 s), three-round bursts,
rest (.45 s), 12-round magazine and reload (2.6 s) retain world-time behavior,
including Y slowdown. Player movement and rifle presentation are unchanged.

## Cover posture and geometry

Left/right cover exposure now uses a signed upper-body rotation at `spine_01`.
The existing AnimBP native correction call feeds an additive component-space
ModifyBone control before left-hand IK in right-hand space. The head, chest,
arms and attached rifle inherit the rotation. Pelvis and legs lie outside this
subtree. The pawn/capsule is not rotated or translated to fake exposure.

The native correction composes lean around the already corrected barrel vector,
preserving pitch and yaw. Default lean is ±32 degrees, at 120 degrees per world
second (about .27 seconds out and back). The retained rear-aim turn blend also
limits lean; if the final physical posture cannot achieve it, exposure times out.

The static-cover scan finds each side's shadow edge using one 6 m bracket and
eight binary refinements, then checks standing support, protection, clearance,
weapon range and reachable route. The proposed anchor retreats 40 cm from the
original cover sample to leave room for the upright rifle. The edge is inset
inside the shadow. Once arrived, **anchor and firing feet are the same**.
There is no lateral step-out exposure. Low cover separately retains actual
crouch/stand/burst/crouch behavior.

At the achieved edge, the opponent raises the rifle behind cover and captures
actual head/chest/hand/muzzle sockets plus the spine pivot and barrel axis. Four
arc samples check head, torso, hand and rifle volumes, with connecting body and
rifle segments. The upright head must still be concealed. The projected head and
muzzle must have a lane toward permitted last-sight evidence. This proposal
cannot authorize firing: the actual animation angle, signed head/chest socket
displacement, grounded feet, achieved stance and current clearance must agree.
Sight originates at the actual head and each projectile at the actual rifle
muzzle. Every birth re-observes the target and rechecks the actual muzzle corridor.

The cycle has bounded anchor travel (8 s), neutral pose/arc preparation (1.8 s),
exposure/aim/burst phases (2 s each), missing-contact wait (.45 s) and return
(1.2 s). Existing six-second evidence freshness, twelve-second commitment and
180 cm observed-threat-shift limits remain. It performs at most three finite
bursts before reassessment. Blocked sides receive independent five-second
backoff. Failed return stops at actual feet, clears offsets and replans.

Returning keeps feet owned until both animation angle and actual head/chest
displacement return. Death, recovery, disable, weapon loss and reset cancel both
action lanes, pending fire, cover assignment and stale lean data. Physical
authority takes the pose immediately. Recovery plans from current feet.

## Tuning and observability

`msq.EnemyCombat tune <key> <value>` adds these bounded controls:

| Key | Default | Allowed values | Meaning |
| --- | ---: | ---: | --- |
| `strafe` | 180 | 100–240 cm | One lateral combat step |
| `moverest` | 3.2 | 2–8 world s | Pause between attempts |
| `movespread` | 1.6 | 0–4 degrees | Added cone at 220 cm/s |
| `lean` | 32 | 20–35 degrees | Maximum signed torso lean |

Existing `range`, `preferred`, `advance`, `reaction`, `aim`, `interval`, `pause`
and `reload` tuning remains. Lower lean values can make a previously usable edge
unusable; actual geometry then refuses it and reports a bounded fallback.

Status/trace includes movement action ID/outcome, mobile phase/goal/deadlines,
actual horizontal/vertical speed, grounded state, motion gate, last launch gate,
moving spread, requested/animated lean and neutral-pose capture. Existing cover,
evidence, timing and tactical reasons remain. `trace` writes explicitly requested
exports under `Saved/CombatAI01/CAI-T03/Traces/`.

## Verification and preserved inputs

Evidence is frozen under `Saved/CombatAI01/CAI-T03/Worker/Candidate01/`:

- `build-result03.json` / `build03.log`: Development Editor succeeds; task code
  warnings from the earlier build were corrected. Existing StructUtils plugin
  deprecation notices remain outside scope.
- `checks-07.json`: 67 passing assertions over exact production policy,
  navigation-following, action ownership, motion producer, CanShoot/Fire,
  cover/lean geometry and lifecycle. Includes the real native lean-update fragment
  and installed UE constant-interpolation template. Collision, clock, pose
  acknowledgement and projectile storage are explicit deterministic boundaries.
- `editor-after.json`: 18 native correction cases on an unregistered transient
  component/AnimInstance, covering ±32-degree lean, yaw −45/0/+45 and pitch
  −35/0/+35. Signed child offsets change both ways while barrel-vector dot with
  its unleaned direction stays above .99999. No actor, world or playback is used.
- `graph-before.json`, `graph-after.json`, `ik-after.json`, `bone-parents.json`
  and `pose-wiring.json`: actual retained asset wiring and skeletal ancestry.
- `preservation-final.json`: owner config/project/map/instructions, 157 captured
  binary assets and 362 historical evidence files preserved. Original native
  source and asset inputs are archived in `preserved-inputs.zip`.
- `candidate-manifest.json` and `CAIT03-Candidate01-frozen.zip`: source, assets,
  matching DLL, scripts, focused evidence and input identities. No prior
  candidate or accepted asset fingerprint was rebaselined.

No binary asset changed, so no AssetRegistry revision is needed. The unchanged
MSQ-119 evidence for senses, health/weapon context and finite projectile timing
is reused; no full animation/feature matrix was run. Configured and actual
executor settings are Astra/max/default, fast disabled. No shared profile,
issue status, registry or commit administration was performed by the worker.

The ordinary retained-lobby editor is reopened with the matching DLL, no PIE
and no dirty packages. `editor-process.json` records PID 39256 and a Windows
breakaway launch independent of the task process job. Close it normally when
finished, preserving subsequent owner edits. Its live log is `editor.log`;
an immutable readiness excerpt is recorded separately.

## Changed files and owner route

New native files: `CombatAIMobile.h`, `EnemyCombatMobile.cpp`,
`EnemyCombatLean.cpp`. Modified native files: `EnemyCombatComponent.h/.cpp`,
`EnemyCombatPolicy.cpp`, `EnemyCombatNavigation.cpp`, `EnemyCombatCover.cpp`,
`EnemyCombatTactics.cpp`, `CombatAIObservation.h`, `EnemyCombatObservation.cpp`,
`GASPEnemyFixture.h`, `GASPEnemyRifle.cpp`, `GASPALSRifleAnimInstance.h/.cpp`.
Task scripts are under `Scripts/CombatAI01/CAIT03/`; this report is the handoff.

Owner route: Play the retained lobby, keep useful rifle distance in open space
and watch short lateral movement through a burst and its rest. Start beyond
effective range to check cautious approach and firing after entering range.
Use a column to offer each edge independently; observe planted feet and actual
torso exposure. Block a side, break sight, use low cover, interrupt with hits,
then test Y slowdown and F6 reset. Status/trace explains pending gates.

Motion quality, actual hit/recovery integration, edge usefulness, difficulty and
feel remain owner tests. Conservative static geometry, standing-only lateral
lean, a 220 cm/s walking-fire ceiling, single-floor local navigation and no
lean-fire during travel are intentional limits. No player Q/E controls, weapons,
group tactics, map changes, player health or successor tasks are included.
