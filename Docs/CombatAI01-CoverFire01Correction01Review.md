# MSQ-119 / CAI-T02 correction review

2026-09-24. **PASS within the authorized technical scope. CFT02-R1 and CFT02-R2
are CLOSED for Candidate02/build01.** No remaining finding was identified in the
two corrections or their directly related transitions. This is finding closure
by the same sole primary reviewer; the original review remains unchanged.

The executor's matching native build and 44 affected assertions are reused.
Unchanged CF01/02/04/05/06 conclusions and applicable Candidate01 evidence remain
valid. No additional behavior check was necessary after inspecting the corrected
production paths, the original failure boundaries and the test adapters.
Actual motion, cover usefulness, reaction feel, difficulty and performance remain
**PENDING OWNER PLAY**.

Scope follows `Docs/Tasks/CombatAI01/CAI-T02.md`, the current issue's correction
review instructions, `Docs/CombatAI01-CoverFire01Review.md` and
`Docs/CombatAI01-CoverFire01Correction01.md`. No editor operation, gameplay, PIE,
simulation, firing, gameplay screenshot or performance probe was performed.

## Candidate and evidence identity

- Baseline and current HEAD: `29dfdfad682311df9cf5649e0d4f655bc554c69a`.
- Candidate: `Saved/CombatAI01/CAI-T02/Worker/Candidate02/`, **Candidate02/build01**.
- Manifest SHA256:
  `4a38e81d8e422a249d66cf7ce9558c9b4e0889548453f36f78a8f47e8b1c2537`.
- Final DLL SHA256:
  `26ba450661cc116c24c2d0c438bd94556b42ac87396548748bc7ee383a6104b6`.
- Frozen archive SHA256:
  `b7b959a1b2d603a2a405121c1890e0ea3aa62ce99548926ead217eca01e96121`.
- **98/98 manifest entries match** both current and archived bytes, including
  sizes. The archived manifest itself matches. Exactly four of 56 native source
  files differ from Candidate01: `EnemyCombatComponent.h/.cpp`,
  `EnemyCombatPolicy.cpp` and `EnemyCombatTactics.cpp`; the other 52 match.
- **56/56 extracted identities match** the current production/installed engine
  source and occur verbatim in the frozen `generated-02.cpp`: 51 component
  methods, the fixture's achieved-stance getter, the exact stance-consumer
  fragment and three installed Mover request methods. The generated file's
  hash matches `checks-02.json`.
- All five captured owner/report inputs and all 360 captured historical
  evidence/script files still match. Candidate01 and the original review's
  reproductions retain their original identities and results.
- Reviewer profile and native ancestor PID **46448** specify **Astra/max/default
  with fast disabled**. This run's native turn context independently records
  `gpt-6-astra` / `max`. Its tier is null; explicit native arguments and the
  configured profile establish standard speed. No settings were changed.

The new read-only identity and settings evidence is under
`Saved/CombatAI01/CAI-T02/Review/Correction01/`.

## CFT02-R1: CLOSED

`Source/MeridianSquad/EnemyCombatTactics.cpp:315` reapplies the checked winner's
crouch request immediately after `ClearIntent` cancels the previous owner.
Achieved-stance and refreshed geometry/score validation still precede that
handoff. The checked route installs its own `PathGoal` and action token at line
321, so ordinary following does not treat it as an obsolete destination.

The arrival handoff at `EnemyCombatTactics.cpp:446` similarly reapplies the
validated hold's stance after clearing the completed route. Arrival still uses
actual feet and fresh protection/facing assessment; the next hold validation at
line 382 uses achieved stance. A real stance mismatch at line 419 and a failed
route at line 455 still reject and cancel the transfer.

This resolves the original producer/consumer failure rather than preserving a
test-only crouch value. The corrected fixture repeatedly executes the actual
scan and selector from `(-400,0,0)` to `(40,0,0)`, then the exact
`GASPEnemyRifle.cpp:96` consumer branch, installed Mover `Crouch`/`UnCrouch` request
methods and the real `IsMovementCrouched` getter at line 34. The explicit engine
boundary acknowledges or refuses the request between decisions. The request
survives selection, the next route decision, accepted arrival and timed holding.
The preserved result is `held=1 crouch=1 requested=1 goal=40,0`.

Related cancellation remains intact: `EnemyCombatComponent.cpp:63` still clears
the request; `RejectTacticalPosition` at `EnemyCombatTactics.cpp:340` invokes that
cleanup. The focused checks cover route failure, achieved-stance loss, disable,
reset/enable, death, physical interruption and weapon loss, including movement,
pending rounds and obsolete action ownership. A refused stand remains actually
crouched until expansion is allowed. `ResetCombat` delegates to `SetEnabled` at
`EnemyCombatComponent.cpp:109`.

The unchanged follower's obsolete-goal and invalid-token cleanup at
`EnemyCombatNavigation.cpp:198` and line 217 remains appropriate. Related cover
movement, return and protected reload explicitly restore their owned crouch
request (`EnemyCombatCover.cpp:247`, line 261 and line 346); protected arrival
continues into the stance-owning `Protected` branch in the same decision
(line 301 / line 333). Cancellation into a new search remains cancellation.

Affected criteria **CF07 and CF08 now PASS** for this finding.

## CFT02-R2: CLOSED

`Source/MeridianSquad/EnemyCombatPolicy.cpp:132` now calls `RefreshObstruction`
before `SelectRangeIntent` and the out-of-range early return at line 184.
`EnemyCombatComponent.cpp:235` expires obstruction evidence after its bounded
validity and rechecks an existing obstruction or a visible out-of-range target
using the current actual muzzle corridors. Clear geometry removes the old veto
immediately; current blockage renews validity for **0.5 world seconds**.

Revalidation checks visibility, target validity and required components before
querying. It uses the permitted remembered aim and never obtains a hidden target
transform. If sight is unavailable, expiry cannot cast a new corridor toward a
hidden relocation. Reacquisition beyond effective range performs the current
corridor check even when the prior obstruction already expired.

The original failure transition is covered by the corrected production-method
fixture with ordinary cover scanning enabled: a muzzle rejection at world time
1.11 is followed by clear geometry and fresh visible evidence at 6500 cm.
At **world time 1.25**, the result is
`obstruction=-1 follow=1 step=450`. The request uses `MovePurpose::Cautious`,
requests walking, leaves more than 5500 cm to the target and launches no shot.
Actual-feet arrival retains the existing **0.8-world-second pause**.

The restored movement remains the existing bounded path at
`EnemyCombatPolicy.cpp:191`, with a five-second attempt bound at line 196.
`CombatAICover.h:86` caps the step by the weapon profile; default is 450 cm.
`CombatAIAction.h:84` and `EnemyCombatNavigation.cpp:231` retain walking for
cautious movement. No target-foot pursuit is restored.

The focused evidence also covers continuous blockage across scan/expiry
boundaries, clearance while aim/braking is unsettled, expiry without sight,
blocked reacquisition and torso-to-muzzle clipping. A currently blocked corridor
continues selecting `SeekLane` with no approach or launch. Timer expiry alone
therefore cannot authorize movement through a presently blocked lane.

`MuzzleCorridorBlocked` at `EnemyCombatComponent.cpp:222` preserves the original
torso-to-muzzle and muzzle-to-observed-aim sweeps and projectile query filtering.
Sharing these sweeps does not change firing permission: `CanShoot` retains its
authority, weapon, visibility, achieved stance, animation, velocity and alignment
gates before the query; `Fire` at line 254 retains fresh observation, range,
action/generation, cadence and ammunition checks. The affected fixture verifies
the physical/visibility gates and an eligible launch through an inert counter.
Reset, physical interruption, weapon loss and successful launch clear the new
validity state with the old obstruction state. All deadlines remain world time.

Affected criteria **CF03, CF07 and CF08 now PASS** for this finding.

## Adapter fidelity and reused checks

`Scripts/CombatAI01/CAIT02Correction01/check.py` reuses the existing extractor and
adapters without executing Candidate01's 71-assertion entry point. It compiles the
corrected methods and exact stance-facing consumer fragment with MSVC C++20,
warnings as errors. `tests.cpp` exercises the original defects and related
cleanup, arrival/hold and corridor transitions; it does not replace those
production decisions with copied predicates.

The stance acknowledgement remains an explicit engine boundary, consistent with
the installed Mover request and expansion branches in
`D:/UE_5.8/Engine/Plugins/Experimental/Mover/Source/Mover/Private/DefaultMovementSet/CharacterMoverComponent.cpp:139`
and line 184. Native modifier application, collision resolution, travel and
animation are not executed. Actual wiring remains
`GASPEnemyFixture.cpp:665` -> combat decision and
`GASPEnemyFixture.cpp:107` -> rifle input before foundation input production.
Collision and sight are deterministic test boundaries; projectile launches are
inert counters.

The initial `checks-01.json` failure is retained and explained: its reused
`FollowPath` adapter models `WantsWalk` but omits the real follower's
`bCrouchCommand ||` term. The corrected assertion checks the crouch command and
search purpose submitted to that boundary. Source inspection at
`EnemyCombatNavigation.cpp:231` confirms actual quiet walking. This assertion
change does not mask the original stance-handoff defect. No production source
changed between the two check attempts.

| Evidence reused | Applicability |
| --- | --- |
| Candidate02 `checks-02.json`, `compile-02.log`, `run-02.log` | 44 affected assertions, zero failures; compile/run exit 0; reviewed adapters and matched production extraction. |
| Candidate02 `build-result01.json`, `build01.log` | Native Win64 Development Editor succeeds, 41 actions, 90.18 seconds; recorded DLL matches the reviewed candidate. |
| Candidate01 `checks-09.json`, `compile-09.log`, `run-09.log` | Original 71 passing assertions remain applicable to unchanged geometry, cover lifecycle, context and timing behavior. |
| Original `CombatAI01-CoverFire01Review.md` | CF01/02/04/05/06 technical conclusions retained; this report supersedes only the unresolved R1/R2 and affected CF03/07/08 dispositions. |
| Candidate02 preservation records | Confirmed against current bytes; original manifests, reports and reproduction evidence remain unchanged. |

No native rebuild, original matrix, original failing reproduction or additional
behavior check was rerun. The correction evidence covers the remaining risks at
the original failure boundaries; the added work is source review, settings
verification and candidate/evidence identity checking.

## Final disposition and handoff

**CF01-CF08 PASS within the authorized source/fixture/native-build scope**, combining
the retained primary review with this correction closure. **R1/R2 CLOSED.** This
does not confer owner gameplay acceptance or complete later AI task families.

New files under `Saved/CombatAI01/CAI-T02/Review/Correction01/` contain
`identity.json`, `verify_identity.py`, `execution-settings.json`,
`capture_execution.ps1` and the packaged review evidence. The executor's frozen
reports and prior review report/evidence were not rewritten.

The controller owns scope acceptance, issue status, the eventual local closure
commit and ordinary editor reopening with the matching DLL. This reviewer made
no production, profile/status, registry or editor changes and delegated no work.
