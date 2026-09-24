# MSQ-119 / CAI-T02: primary-review correction

Executor handoff, 2026-09-24. **Candidate02/build01** corrects **CFT02-R1** and
**CFT02-R2** from the [sole primary review](CombatAI01-CoverFire01Review.md).
The native Development Editor build and **44 focused assertions PASS**.
Finding closure remains pending the same primary reviewer and controller acceptance.
Actual motion, cover usefulness, reaction feel, difficulty and performance remain
**PENDING OWNER PLAY**. No gameplay, PIE, simulation, firing probe, screenshot or
performance probe ran.

This is a bounded correction under the existing [CAI-T02 task](Tasks/CombatAI01/CAI-T02.md).
The [Candidate01 handoff](CombatAI01-CoverFire01.md), build04, manifest, archives,
original review and its reproductions are preserved unchanged. Candidate02 does
not rebaseline Candidate01 or declare any successor task complete.

## CFT02-R1: search stance ownership

`ChooseTacticalPosition` now reapplies the freshly validated winner's crouch
request immediately after clearing the previous intent. `AdvanceSearch` likewise
reapplies the validated arrival stance when transferring ownership to a hold.
The actual Mover consumer therefore receives crouch throughout the selected route,
arrival and subsequent protected observation.

`ClearIntent` retains its cancellation cleanup. Reset/enable, disable, death,
living physics interruption, weapon loss and rejected routes still cancel pose,
movement and pending rounds. A real mismatch between requested and achieved stance
still rejects the route; the correction does not turn a request into an achieved
stance or allow travel through an unverified capsule volume.

The affected handoff audit covered search selection/arrival, rejection, navigation
goal replacement and the existing cover transitions. Cover transfer/return paths
already reapply crouch or continue into their stance-owning phase in the same
decision. Navigation's obsolete-goal and invalid-token cancellation remains
appropriate; the selected checked search route installs its matching `PathGoal`.
No unrelated `ClearIntent` caller was changed.

The new fixture uses the real scan/selector from `(-400,0,0)` to the protected
column at `(40,0,0)`. Each search decision passes through the exact stance-facing
branch of `AGASPEnemyFixture::UpdateRifleInput`, the installed Mover
`CanCrouch`/`Crouch`/`UnCrouch` methods, and the actual
`AGASPEnemyFixture::IsMovementCrouched` getter. Explicit engine boundaries then
acknowledge or refuse the request; `ActualCrouch` is not held artificially constant.
The route survives the next decision, accepts actual arrival and retains crouched
protection through timed hold validation. Separate affected checks retain genuine
stance-loss rejection, failed-route cleanup and cancellation consumers.

This compiles the real stance-consumer branch, not the unrelated reflected
aim/controller portion of `UpdateRifleInput`. Native modifier application,
clearance resolution, travel and animation are explicit fixture boundaries.
The build verifies the complete native implementation; these checks do not claim
observed game motion. Source wiring is retained at `GASPEnemyFixture.cpp`
(`Tick` advances combat; `ProduceInput_Implementation` calls `UpdateRifleInput`).

## CFT02-R2: current obstruction evidence before range choice

Obstruction evidence now has a **0.5-world-second validity**. Before non-cover
range selection and its out-of-range early return, `RefreshObstruction` expires
old evidence and rechecks the actual corridor for an existing obstruction or a
currently visible out-of-range target. A current blockage renews validity; a
clear corridor removes it immediately. Without permitted visible evidence, the
refresh neither reads a hidden target transform nor casts a new corridor toward it.

`MuzzleCorridorBlocked` contains the existing torso-to-muzzle and
muzzle-to-observed-aim sweeps, including the same query filtering. Both `CanShoot`
and the bounded range reassessment use it. Range reassessment can check geometry
while aim, stance or braking is settling; it does not grant firing readiness.
`CanShoot` retains its authority, weapon, visibility, achieved stance, animation,
movement and barrel alignment gates before the shared sweep. `Fire` retains its
fresh observation, action, range, cadence and ammunition checks.

The review transition first records an actual muzzle rejection at world time
1.11, then clears geometry and supplies fresh visible evidence at 6500 cm.
Candidate02 requests the existing **450 cm walking step at world time 1.25**,
with ordinary cover scans enabled and zero launches. The requested destination
remains beyond 5500 cm from the target. Actual step arrival retains the existing
0.8-second pause; no target-foot pursuit or speed change was introduced.

Related checks cover a continuously blocked lane across scan/validity expiry,
clearance while physical aim is pending, expiry without visibility, blocked-lane
reacquisition, torso-to-muzzle clipping despite a clear forward barrel corridor,
and retained firing gates. Current obstruction continues to choose `SeekLane`
and cannot license a cautious advance merely because a timer expired.

Reassessment adds at most the existing two corridor sweeps per applicable
non-cover decision. This is an operation bound, not a performance measurement.
All validity, scan, movement, rest and shot times remain world time.

## Candidate identity and verification

- Baseline HEAD: `29dfdfad682311df9cf5649e0d4f655bc554c69a`.
- Candidate01 manifest SHA256:
  `cdb9bc52670d8133930184d0cecb45ac49db35f5faab89a33b2566b5eeeb6d2d`.
  All 131 entries matched before correction. Its frozen bytes remain the baseline;
  changed current files are identified separately by Candidate02.
- Candidate02 DLL SHA256:
  `26ba450661cc116c24c2d0c438bd94556b42ac87396548748bc7ee383a6104b6`.
- Evidence root: `Saved/CombatAI01/CAI-T02/Worker/Candidate02/`.
  `candidate-manifest.json` and `CAIT02-Candidate02-frozen.zip` freeze source,
  DLL/modules, this report, scripts and affected evidence without overwriting
  either historical candidate or review evidence.
- `checks-02.json`, `compile-02.log`, `run-02.log`: 44 assertions, zero failures;
  MSVC C++20 with warnings as errors. The reused extractor compiles 51 component
  methods, the real stance getter, three installed Mover request methods and
  the exact stance-consumer fragment. Only the new affected checks execute.
- `checks-01.json` is retained: one initial assertion expected the old movement
  adapter to apply the real follower's crouch-to-walk term. That adapter only
  models `WantsWalk`. The assertion was corrected to check the crouch command
  and search purpose actually submitted to the unchanged follower. Production
  source did not change between these two attempts.
- `build-result01.json`, `build01.log`, `build-stdout01.log`: native Win64
  Development Editor PASS, 41 actions, 90.18 seconds. One build ran, capped at
  two compiler actions with approximately 12 GiB available physical memory.
  Only existing StructUtils deprecation notices were reported.
- `correction-source.diff` isolates the four changed native files against
  Candidate01: `EnemyCombatComponent.h/.cpp`, `EnemyCombatPolicy.cpp`, and
  `EnemyCombatTactics.cpp`. All other 52 source files match the captured input.
- `preservation-final.json`: owner configuration/project/map and both historical
  reports match, as do all 360 captured historical evidence/script files.
  Assets, player/projectile clocks, physics, navigation and sensory producers
  are unchanged. Whitespace checks pass.
- `execution-settings.json`: configured profile, actual native PID 37948 and
  this run's native turn context verify Astra/max. Native arguments explicitly
  select default service tier and disable fast mode; the turn tier field is
  null. No profile was changed.

Applicable Candidate01 evidence is reused without rerunning its full matrix:
`checks-09.json` / `compile-09.log` / `run-09.log` (71 assertions), build04 as
historical baseline, and its preservation records. Unchanged cover geometry,
left/right independence, cover lifecycle, context inputs and timing behavior
retain that evidence and the original review's passing findings. The new build
supersedes build04 only for the changed current native bytes. CF03, CF07 and CF08
receive the focused correction evidence above; no second independent review was
performed by the executor.

## Controller handoff

Scripts are under `Scripts/CombatAI01/CAIT02Correction01/`; generated evidence
stays under `Saved/`. To reproduce the affected checks with a new numbered result:

```powershell
& 'D:/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' Scripts/CombatAI01/CAIT02Correction01/check.py
```

The editor/process guard found no running editor before the build. No editor
lifecycle operation was performed; `editor-final.json` records the final process
state. The correction dispatch leaves reopening the ordinary editor with the
matching DLL and retained lobby to the controller after finding closure.

Return this candidate to the same primary reviewer for CFT02-R1/R2 closure and
directly affected transitions, reusing the unchanged passing evidence. The owner
retains gameplay testing. No commit, status/profile/registry administration,
review dispatch or successor execution was performed; controller ownership of
acceptance and the eventual local task closure commit is preserved.
