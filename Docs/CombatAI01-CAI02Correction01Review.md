# MSQ-104 / CAI-02 correction finding review

Date: 2026-09-24. Reviewer: MeridianSquad Code, the original primary reviewer.
**PASS: CAI02-R1 and CAI02-R2 are closed for Candidate03/build01 within the
authorized build/source scope.** No technical blocker remains in these findings
or their directly affected transitions. This does not grant owner gameplay,
motion, audibility, difficulty, map-position usefulness or performance acceptance.

Authority: the current MSQ-104 review-only assignment,
[task](Tasks/CombatAI01/CAI-02.md) and
[owner instruction](Approvals/CombatAI01-CAI02-OwnerStart01.json).
Read with the [correction handoff](CombatAI01-CAI02Correction01.md).
The [original changes-requested review](CombatAI01-CAI02Review.md) and its failed
reproducers remain unchanged. This review closes those findings on the new
candidate; it does not replace the earlier verdict or repeat the full review.

## Candidate and evidence applicability

Final manifest: `Saved/CombatAI01/CAI-02/Worker/Candidate03/candidate-manifest.json`.

- Manifest SHA-256:
  `1f4e673a78284708739f047f718bf3886401b678bb714f2434664b845ab281ad`.
- DLL SHA-256:
  `c0c3b64f8ab48bd9c9eb6cbb4100a7a9a3a2c0ea42f240ba32fdf7c8ea66d488`.
- Frozen archive SHA-256:
  `9a217117114b4e6e06fde23b7ab29024f8c7df1b3dad706e4955d6ff5b958b1d`.
- Baseline Git revision: `c4da5eaaf5793556c3a0884a10ad975573d6a0e0`.

All **100 manifest entries** match both the working files and frozen archive.
The independently captured delta confirms exactly five changed native files
relative to Candidate02: `CombatAITactics.h`, `EnemyCombatComponent.h`,
`EnemyCombatSenses.cpp`, `EnemyCombatTactics.cpp` and `EnemyCombatPolicy.cpp`.
The generated correction fixture contains all **22 production methods verbatim**;
their hashes, the generated source and the recorded run output match the final
worker evidence. The adapters and assertions were inspected, not just the PASS
summary.

Reuse Candidate03's successful native Development Editor build (16 actions,
25.98 seconds), **59 affected assertions** and 26 supporting checks. The fixture
executes the relevant policy/scan/action paths against deterministic geometry,
clock and pawn boundaries. Its movement and weapon adapters do not exercise
Unreal movement, collision, animation or firing. There was no missing concrete
check requiring a rerun or another fixture after source and evidence inspection.

New review records are under
`Saved/CombatAI01/CAI-02/Review/Correction01/`: `candidate-identity.json`,
`verified-native-delta.patch`, `evidence-applicability.json`,
`capture-disposition.json`, `reviewer-settings.json` and `preservation-final.json`.
Configured profile, this run's actual native process and current turn context
verify **Astra/max/default**, with fast mode disabled. No settings were changed.

## CAI02-R1: closed

`EnemyCombatSenses.cpp:41` still applies freshness/response, current-sight and
reload precedence. Compatible sound regions now update the existing protected
investigation at line 49 instead of calling `BeginSearch` on each regional shift.
The evidence region/ID, attention target and next sight query are refreshed;
the assignment token, scan progress/start, active route and travel start survive.
The held-position path at `EnemyCombatTactics.cpp:383` also no longer discards an
in-progress scan whenever updated evidence invalidates a hold.

`AdvanceTacticalScan` retains its finite candidate work and four-world-second
deadline. The correction fixture uses the original 20 accepted steps, 0.4 world
seconds apart and 200 cm regional changes over eight seconds. At 120 updates per
second it reaches five decisions during the stream, first after 1.05 world
seconds with 35 candidates evaluated. At five updates per second it reaches a
decision at the four-second deadline with 13 candidates evaluated. The assignment
changes only on initial entry. The original candidate reached zero selections
until silence. These are fixture scheduling results, not measured performance.
A decision can legitimately retain a validated hold or choose a bounded fallback;
movement is not promised for every sound region.

Cached scores remain proposals. `ChooseTacticalPosition` freshly assesses current
feet at `EnemyCombatTactics.cpp:258` and the winner at line 291, using the current
permitted anchor and uncertainty before starting movement. During movement,
lines 414-419 detect a new evidence ID and reassess the destination before the
next `FollowPath`. The inspected tests reject an unsafe cached winner, retain a
safe moving update's route/action/start time and single charged transfer, and
cancel an unsafe update before another follow call. Failure history remains.
The short sound-attention window is also retained during travel.

Cancellation ownership remains explicit: `EnemyCombatPolicy.cpp:37` checks death,
physical authority and readiness before sensory intent can move the pawn. The
extracted cancellation/recovery checks reject old action and assignment tokens,
retain living evidence, accept sound during recovery without movement, then plan
from recovered feet. Disable/reset clears the correction state. Sound does not
cancel an unpaid reload or override current sight. Transfer limits, rejection
history, knowledge uncertainty and world-time deadlines are unchanged. The new
path does not read a hidden player's transform or turn sound into a firing target.

## CAI02-R2: closed

`CombatAITactics.h:104` supplies explicit nominal planning profiles above supported
feet: standing body/eye/weapon/exposure heights are 95/150/125/130 cm; crouched
heights are 60/100/85/90 cm. `AssessTacticalPosition` applies them to both body
samples, protection/open-space tests, weapon-facing sweeps and self-exposure.
The threat-region height stays independent of the enemy's stance. These profiles
are tactical estimates, not measured animation sockets or launch authorization.

Candidate scans request the crouched profile explicitly. Current feet use
achieved Mover stance, and selection at `EnemyCombatTactics.cpp:292` refuses to
authorize a crouched route while the pawn remains standing. Movement checks the
selected stance before another follow command (line 408). Arrival assesses actual
feet in achieved stance (line 426), and holding revalidates immediately on stance
change (line 374), including its observation-facing height. The actual stance
getter remains `UCharacterMoverComponent::IsCrouching` in `GASPEnemyRifle.cpp:34`;
the request boolean is not treated as achievement. Support/capsule/route checks
continue to use actual capsule dimensions.

The original analytical 120-140 cm ledge now blocks the standing front weapon
probe while clearing the crouched probe. The reverse low obstacle blocks crouch
while leaving standing clear. Low-screen checks exercise lower body/eye and
exposure origins without lowering the presumed hidden threat. Related fixtures
cover refused crouch, crouched actual-feet arrival, standing arrival refusal,
mid-route stance change, and immediate held-position/facing reassessment.

On renewed visible contact, the policy cancels the old protected assignment and
cached positions before engagement. `EnemyCombatPolicy.cpp:114` now requests
standing before the contact-backoff return as well. Contact fixtures with and
without backoff distinguish requested from achieved standing and retain unpaid
aim/pause/cadence deadlines. An obstructed stand request cannot be assumed to have
changed the pose. `TryObservePlayer`, `CanShoot` and `Fire` are unchanged: actual
head/muzzle sockets, current visibility, pose/readiness, alignment, corridors and
birth-time checks still own shot safety. Their prior source-review evidence is
reused; the correction fixtures' fake weapon boundary is not credited as firing
proof.

## Preservation, reuse and remaining owner criteria

Candidate01/02 and the original review remain preserved: all 143 files in the
worker's previous-evidence snapshot and all 146 earlier historical files match.
The raw capture deliberately retains its failed all-documents preservation
assertion: `AGENTS.md` and the controller's acceptance draft changed after the
worker snapshot. `capture-disposition.json` records both differences without
changing historical hashes. Durable AGENTS text matches the saved controller
baseline; the managed suffix identifies this reviewer. The current acceptance
draft names Candidate03 and explicitly awaits primary closure. Neither document
is a frozen candidate entry or a basis for this technical verdict. Owner
configuration, project/map and the other seven captured paths still match.
The final preservation record checks the current files against this review's
initial capture.

Reuse the original review's unaffected passing criteria: sensory producers and
delivery, grounded-motion/audio wiring and saved animation ancestry, uncertain
memory, sight/launch safety, physical authority, clocks, bounded navigation and
slowdown. Candidate02's 202 navigation assertions remain applicable; Candidate01's
66 pure and 22 extracted-method assertions remain applicable to unchanged paths.
The coupled R1/R2 behavior is supported by Candidate03's inspected correction
evidence above. No full test matrix or native rebuild was repeated.

Owner testing must still establish useful protected positions in the retained
map, visible crouched travel/arrival/holding and return to standing, actual step
audibility, hearing response, pursuit, slowdown/deception balance and performance.
The focused follow-up is continued footsteps behind cover, a changed sound region
during movement, crouched arrival/holding, renewed visible contact and physical
interruption/recovery. Source and fixtures cannot establish those runtime results.

No production/editor edits, PIE, gameplay simulation, firing probe, profile/status
change, delegation or commit was made. The controller retains scoped acceptance,
ordinary editor reload, issue administration, runtime shutdown and the local
MSQ-104 closure commit. Only this separate review report and its new evidence
were authored by the reviewer.
