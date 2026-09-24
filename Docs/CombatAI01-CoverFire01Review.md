# MSQ-119 / CAI-T02 primary technical review

2026-09-24. **REQUEST CHANGES: two bounded findings in Candidate01/build04.**
The native build and the executor's 71 assertions remain applicable passing
evidence. Two additional production-method checks expose a crouched-search
handoff regression and an obstruction flag that can permanently suppress the
out-of-range approach. Technical acceptance requires their correction.

This is the sole primary independent technical review against CF01-CF08 in
`Docs/Tasks/CombatAI01/CAI-T02.md` and the exact owner decision
`Docs/Approvals/CombatAI01-CoverFire01-OwnerStart01.json`. Actual motion, useful
cover, reaction feel, difficulty and performance remain **PENDING OWNER PLAY**.
No editor operation, PIE, gameplay, simulation, firing, gameplay screenshot or
performance probe was performed. Test launch counters are inert C++ boundaries.

## Reviewed identity and evidence

- Baseline HEAD: `29dfdfad682311df9cf5649e0d4f655bc554c69a`.
- Handoff: `Docs/CombatAI01-CoverFire01.md`.
- Immutable manifest: `Saved/CombatAI01/CAI-T02/Worker/Candidate01/candidate-manifest.json`.
  SHA256: `cdb9bc52670d8133930184d0cecb45ac49db35f5faab89a33b2566b5eeeb6d2d`.
- **All 131 manifest entries match** the reviewed working files, including the
  production source, headers, test source/results and final DLL.
- Final DLL SHA256:
  `ee173c3b9416592a1ae4d66e1d08f1f014a583fa4e1b9f94ea28a840e2869b34`.
- Reviewer configuration and live native PID 40600 specify
  `gpt-6-astra`, `max`, explicit `default` tier and `--disable fast_mode`.
  Native turn context independently records Astra/max; its tier field is null,
  so standard speed is evidenced by the explicit native arguments and profile.
  See `Saved/CombatAI01/CAI-T02/Review/execution-settings.json`.

Reused without rerunning: `build-result04.json` / `build04.log` (Development
Editor, success, 17 actions), `checks-09.json` / `compile-09.log` / `run-09.log`
(71 assertions, 49 extracted production methods, zero failures),
`preservation-final.json` (owner inputs and 249 historical evidence files), and
`editor-after02.json` / `editor-load-check02.json` (the executor's guarded editor
handoff). These are in the worker candidate directory. The editor records are
handoff evidence, not a new claim about the owner's current editor session.

I inspected the changed production files, the complete new cover adapter and
contract, actual navigation and rifle/stance consumers, the retained sight
producer, the fixture extraction script and adapters, and the affected native
Mover stance implementation. Candidate files, historical reports and manifests
were not modified. Production code, profiles, status and commits remain under
controller ownership.

## Findings

### CFT02-R1 — P1: committing a protected search route requests standing and then rejects its own route

`Source/MeridianSquad/EnemyCombatComponent.cpp:63` adds an unconditional
`SetCrouchCommand(false)` to `ClearIntent`. The existing protected-position
selector calls `ClearIntent` at `EnemyCombatTactics.cpp:313` after verifying
achieved crouch at line 301, installs the crouched route at lines 319-321, and
returns without restoring that crouch request. The arrival handoff at line 443
also clears the request while accepting a crouched hold.

This flag has an actual consumer: `GASPEnemyRifle.cpp:93` forwards it to the
foundation input, and lines 96-99 call Mover `Crouch` or `UnCrouch` accordingly.
The installed Mover's `CharacterMoverComponent.cpp:184` cancels achieved crouch
when standing is requested and expansion is clear. On the next decision,
`EnemyCombatTactics.cpp:417` sees a stance mismatch and rejects the freshly
selected destination. With ordinary standing clearance, protected searching
can repeatedly reject valid transfers; accepted crouched holds can also receive
an unintended stand request. This regresses the MSQ-104 fallback used by this slice.

**New evidence:** `Review/review_checks.cpp` runs the real bounded scan and
selector against the existing deterministic collision adapter. It selects a
supported route from `(-400,0,0)` to `(40,0,0)` beside a column. The committed
result is `selected=1, stance=1, actual_crouch=1, requested_crouch=0`. After the
explicit, source-audited engine boundary acknowledges that standing request,
the actual `AdvanceSearch` rejects it: `selected=0, rejected=1, path_points=0`.
The fixture does not move a game actor or claim observed Mover animation.
See `Review/checks.json` and `Review/run.log`.

**Bounded correction:** retain the new pose clearing for cancellation,
reset/death/disable/weapon/authority loss, but preserve or reapply the selected
stance when committing a search transfer and accepting its arrival. Audit the
affected `ClearIntent` handoffs only. Verify a real selected transfer, subsequent
stance consumption, and arrival/hold; the existing `ActualCrouch` fixture value
must not remain artificially frozen across the command handoff.

Affected criteria: CF07 no-cover/protected-search fallback and CF08 actual
producer/consumer wiring.

### CFT02-R2 — P2: an obsolete muzzle obstruction permanently vetoes cautious approach

`Source/MeridianSquad/EnemyCombatPolicy.cpp:51` records `ObstructedSince` when
`CanShoot` rejects the muzzle corridor. Line 131 subsequently uses only
`ObstructedSince >= 0` as the lane-blocked input. `CombatAICover.h:81` gives that
input priority over range selection, returning `SeekLane`.

If the muzzle corridor clears and the visible target is now beyond effective
range, `EnemyCombatPolicy.cpp:182` enters the out-of-range branch, and line 184
returns because `SeekLane` is not `CautiousAdvance`. It never reaches
`AdvanceWeapon` to reassess the muzzle. A successful shot clears the flag at
`EnemyCombatComponent.cpp:256`, but a shot cannot occur outside effective range.
Reset/weapon loss/physical interruption can clear it; elapsed time, a completed
no-option scan and a new clear lane cannot. Repeated finite scans therefore
leave a healthy, armed opponent stationary indefinitely.

**New evidence:** `Review/range_check.cpp` first exercises an actual production
muzzle rejection at world time 1.11. It then supplies a clear collision boundary
and fresh visible evidence at 6500 cm. The real `CanShoot` reports a clear,
aligned corridor. With ordinary cover scans left enabled, `AdvanceCombat`
through world time 17.28 retains `range=2` (`SeekLane`),
`obstruction_since=1.11`, `follow_calls=0`, and no cover action. No approach or
expiry occurs. The actor/visibility inputs remain explicit fixture boundaries;
the range, obstruction and scan decisions are the frozen production methods.
See `Review/range_check-checks.json` and `Review/range_check-run.log`.

**Bounded correction:** give the obstruction evidence a bounded validity and
revalidation path that operates before the out-of-range early return. Use
current permitted evidence and actual corridor checks; clearing obsolete
obstruction must restore only the existing bounded cautious step. Preserve the
blocked-muzzle hold/cover behavior and never reintroduce target-foot pursuit.
Add this cleared-lane/out-of-range transition to the focused production checks.

Affected criteria: CF03 cautious out-of-range engagement, CF07 finite useful
fallback/reassessment, and CF08 adversarial producer/consumer transitions.

## Acceptance mapping

| Criterion | Technical disposition | Evidence and limits |
| --- | --- | --- |
| CF01 | PASS within source/fixture scope | `EnemyCombatCover.cpp:146` evaluates each side independently with bounded offsets; `AssessCoverOption` at line 125 requires support, capsule, outgoing/return strips and lane. `ChooseCover` at line 201 refreshes the winner and route. `EnemyCombatNavigation.cpp:176` uses actual feet and submits Mover movement, and `EnemyCombatComponent.cpp:230` rechecks the achieved firing pose and actual muzzle at launch. Both blocked-side fixtures pass. Actual movement/usefulness remains owner testing. |
| CF02 | PASS within source/fixture scope | Discovery at `EnemyCombatTactics.cpp:201` samples 60 and 100 cm. `EnemyCombatCover.cpp:63` gets separate proposed standing/crouching volumes from native Mover settings. `AdvanceCover` at line 271 requests achieved crouch, exposure/stand, finite fire and protected return, with stand/contact/return deadlines. Native consumers are `GASPEnemyRifle.cpp:33` and line 96. The worker's usable low-cover fixture is 112 cm; this does not certify arbitrary sub-100 cm geometry as protective or prove actual animation. |
| CF03 | **FAIL — R2** | The 85 cm obstruction chase is removed. In-range contact holds and out-of-range requests use weapon range, a maximum 450 cm step and walking intent (`EnemyCombatPolicy.cpp:175`, `CombatAICover.h:86`, `CombatAIAction.h:84`). Stale obstruction can nevertheless prevent the bounded approach indefinitely. |
| CF04 | PASS within source/fixture scope | Default reaction/aim are .08/.10 world seconds (`EnemyCombatComponent.h:30`). `AdvanceCombat` overlaps them; `ResponseGates::ReadyAt` at `CombatAITactics.h:65` preserves contact, aim, pause, reload and cadence deadlines. The passing eligible-contact fixture fires at +.11 s with preseeded visibility. The documented .22 s plus decision ticks includes .12 s sight polling; it is a policy target, conditional on physical readiness, geometry and no existing pause/reload. No measured feel or performance claim. |
| CF05 | PASS within source/fixture scope | Active cover precedes ordinary search/acquire handling (`EnemyCombatPolicy.cpp:128`). `RefreshCoverThreat` at `EnemyCombatCover.cpp:84` uses successful sight only, invalidates large observed displacement, and enforces six-second evidence/twelve-second commitment limits. Launch calls actual fresh observation at `EnemyCombatComponent.cpp:239`; failed sight cannot update remembered transforms (`TryObservePlayer`, line 186). Own ducking preserves ownership. Actual damage still transfers physical authority through `GASPEnemyFixture.cpp:518` and line 71. |
| CF06 | PASS within current extension scope | `RefreshTacticalContext` at `EnemyCombatCover.cpp:30` reads actual own health and explicitly unknown target health; `ReceiveTargetHealth` validates identity, generation, lifetime and provenance. Ally summaries count fixtures once, exclude unavailable members, and summarize capabilities without target positions. `CombatAICover.h:67`, `CoverTransferEligible` and `CoverScore` connect those values to deterministic eligibility/scoring. Known/unknown health and support cases pass. This is a future producer contract, not implemented player health or group coordination. |
| CF07 | **FAIL — R1/R2** | Reset, death, weapon loss and physical interruption invalidate cover/action tokens; refusal/return/scan/history/transfer limits are finite (`EnemyCombatComponent.cpp:74`, line 124; `EnemyCombatPolicy.cpp:101`; `EnemyCombatCover.cpp:172`, line 251, line 271). The protected-search stance handoff regresses fallback, and the obstruction flag lacks bounded invalidation. |
| CF08 | **FAIL pending focused corrections** | Matching native build and executor 71/49 evidence pass and are reused. The new two-case review check compiles the frozen production methods and reports seven assertions: three setup passes and four failures exposing R1/R2. No full matrix, native rebuild or gameplay test was repeated. |

Every launch still requires the current target observation, live authority,
weapon/hand/animation readiness, achieved stance, actual velocity threshold,
barrel alignment, torso-to-muzzle and muzzle-to-target sweeps, ammunition and
valid action token. The existing finite projectile adapter and slowdown clocks
remain unchanged. This review found no hidden-transform consumer, fabricated
target health, restored old action token or new live ally command in the slice.

## Supporting evidence and correction boundary

New evidence is under `Saved/CombatAI01/CAI-T02/Review/`:

- `identity.json`: all 131 immutable candidate entries match.
- `execution-settings.json` and `capture_execution.ps1`: configured/native/turn settings.
- `review_checks.cpp`, `checks.json`, `compile.log`, `run.log`: R1 reproduction.
- `range_check.cpp`, `range_check-checks.json`, `range_check-compile.log`,
  `range_check-run.log`: R2 reproduction.
- `run_review_checks.py`: compiler invocation and evidence capture. It includes
  the worker's hash-verified `generated-09.cpp`, renames but does not execute its
  original test entry point, and runs only the named missing review case. Both
  new checks compile with the worker's MSVC C++20 warnings-as-errors settings.

Reproduce with the installed Unreal Python:

```powershell
& 'D:/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' Saved/CombatAI01/CAI-T02/Review/run_review_checks.py
& 'D:/UE_5.8/Engine/Binaries/ThirdParty/Python3/Win64/python.exe' Saved/CombatAI01/CAI-T02/Review/run_review_checks.py range_check
```

Those commands reproduce the frozen candidate defects; a correction must extract
and identify its new production bytes rather than silently replacing the frozen
include. Preserve this evidence. Return the corrected candidate to this same
primary reviewer for R1/R2 closure and directly affected transitions only; reuse
all unaffected passing evidence. The controller owns correction dispatch,
scope acceptance, issue status and the eventual local closure commit.
