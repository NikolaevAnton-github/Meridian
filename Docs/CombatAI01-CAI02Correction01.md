# MSQ-104 / CAI-02: primary-review corrections

Candidate03/build01, 2026-09-24. **Executor corrections and focused self-checks
pass.** Return CAI02-R1 and CAI02-R2 to the same primary reviewer for finding
closure. Independent closure, controller acceptance, ordinary editor reload and
the local closure commit remain pending. Gameplay, actual motion/audio, position
usefulness, difficulty and performance remain **PENDING OWNER**.

Authority: the current MSQ-104 correction assignment and the
[original primary review](CombatAI01-CAI02Review.md), under the existing
[owner instruction](Approvals/CombatAI01-CAI02-OwnerStart01.json).
Read the unchanged [base handoff](CombatAI01-CAI02.md) and
[navigation handoff](CombatAI01-CAI02Navigation01.md) for the retained implementation.
This report supersedes their affected scan-retargeting and stance-assessment
behavior only. It does not change the original changes-requested verdict.

## CAI02-R1: complete a decision while fresh sounds continue

`EnemyCombatSenses.cpp::ApplyEvidenceIntent` now coalesces regional sound updates
into an existing protected investigation. It refreshes the permitted region,
assignment evidence ID, short attention window and sight scheduling without
calling `BeginSearch` again. Assignment/action tokens, scan start/progress,
travel deadline, transfer budget and spatial rejection history survive.
A different objective can still begin a search; physical authority and reset
retain their existing cancellation behavior.

The existing incremental scan still completes its candidate work or reaches its
four-world-second deadline, on the next eligible decision tick. Held-position
reassessment can discard an unsafe hold without repeatedly discarding that scan.
Cached candidates remain proposals: `ChooseTacticalPosition` reassesses the single
winner against current permitted evidence, actual feet, geometry and stance
before starting movement. An evidence update during movement rechecks the
destination before continuing the existing route. If it fails the existing
protection/exposure acceptance bounds, the route is canceled and remembered as
a failure. A safe update does not renew the ten-second tactical travel deadline
or grant another transfer. Movement retains a brief look toward new sound.

This does not promise that every sound stream yields a move. A validated hold or
bounded fallback can be the decision, and changed safety/authority can reject
movement. It removes ordinary regional updates as an unbounded scan restart.

## CAI02-R2: apply proposed and achieved stance to tactical probes

`CombatAITactics.h::TacticalProbes` defines explicit planning profiles, measured
in centimeters above supported feet:

| Profile | Body | Eye | Weapon-facing root | Self-exposure origin |
| --- | ---: | ---: | ---: | ---: |
| Standing | 95 | 150 | 125 | 130 |
| Crouched | 60 | 100 | 85 | 90 |

These are nominal tactical probes, not measured animation sockets. Candidate
assessment explicitly requests the crouched profile; current feet, arrival and
held positions use achieved Mover stance. A crouched proposal cannot authorize
travel until crouch is achieved. A change away from the selected stance cancels
the route before another movement command. A refused crouch request leaves
standing observation assessed at standing heights and retries the bounded scan.

Holding revalidates immediately on achieved stance changes, even before its
periodic timer. Held and fallback observation facing use the matching eye height.
The uncertain threat region retains its existing height; an enemy crouch does
not invent a crouched hidden player. Capsule support/clearance and route sweeps
continue to use actual capsule dimensions.

Visible contact still cancels the protected assignment and its cached positions.
It now requests standing before the contact-backoff branch as well, so weapon or
route backoff cannot leave the old crouch command asserted. An unachieved standing
request is not treated as achieved. Actual sight still originates at the head
socket, and `CanShoot`/`Fire` retain their exact current visibility, pose/readiness,
alignment, socket corridor and launch-time checks. Their bodies are unchanged.

## Focused verification

Evidence root: `Saved/CombatAI01/CAI-02/Worker/Candidate03/`.
Helpers: `Scripts/CombatAI01/CAI02Correction/`. Earlier helpers were not edited.

- `build01.log`: native `MeridianSquadEditor Win64 Development` **PASS**, 16
  actions, 25.98 seconds, UE 5.8/MSVC 14.44, two compiler actions at a time.
  Retained StructUtils deprecation notices remain; no new compiler warning.
- `checks-03.json` and `run-03.log`: **59 affected assertions PASS**, using 22
  verbatim extracted production methods, production value-only headers and
  extracted tuning defaults. The fixture executes connected sensing, policy,
  scan, selection, hold, arrival, action and physical-cancellation methods.
  Geometry, clocks, actor/movement and weapon boundaries are deterministic
  adapters; this is not Unreal gameplay, collision or performance evidence.
- **26 compile/source/preservation checks PASS**. They confirm the five-file
  native delta, unchanged tuning, navigation, sensory producers/audio wiring,
  launch checks, physical authority and earlier evidence/owner bytes.
- `execution-settings.json` verifies configured and actual native
  **Astra/max/default**, fast mode disabled, plus this run's turn context.
  No profile was changed.

| Finding / transition | Concrete check and result |
| --- | --- |
| R1 original repeated-step reproducer | Twenty accepted steps, 0.4 world seconds apart, move the permitted region 200 cm per event over eight seconds. At 120 decisions/second, five scans complete during the stream; the first takes 1.05 world seconds, with 35 candidates evaluated. The investigation token changes only on initial entry. Original candidate reached zero selections. |
| R1 finite deadline | At five decisions/second, the same stream reaches a decision at four world seconds with 13 candidates evaluated. The deadline is not renewed by fresh sounds. Counts are deterministic scheduling results, not performance measurements. |
| R1 latest evidence and movement | Cached unsafe winner is rejected before starting travel; safe moving retarget retains route/action/start time and one charged transfer; unsafe retarget cancels before the next follow call and preserves failure history. |
| R1 authority/reset/deadlines | Physical cancellation invalidates old route/assignment tokens, retains living knowledge, accepts new recovery evidence without movement, then replans from recovered feet. Disable/reset clears state. Sound does not cancel unpaid reload or override current sight. |
| R2 original height-sensitive reproducer | The analytical 120-140 cm ledge blocks the standing front weapon probe but clears the crouched probe; query segments now differ. A reverse low obstacle blocks crouch while leaving standing clear. |
| R2 body/eye/exposure | Low-screen fixtures change body/eye visibility and self-exposure with stance while retaining the threat-region height. |
| R2 arrival/hold/unachieved stance | Crouched arrival accepts actual feet; standing arrival and a mid-route stance change cancel old authorization. Refused crouch grants no movement. Held stance changes refresh assessment and facing before the periodic timer. |
| R2 standing contact | Contact with and without weapon backoff requests standing, invalidates the old crouched assignment, distinguishes requested from achieved stance, and retains unpaid weapon gates. |

All attempts remain preserved. `checks-01.json` records a missing `ZeroVector`
definition in the standalone adapter; it did not affect the successful native
build. `checks-02.json` records two incorrect fixture assumptions: its low screen
also occluded the standing chest, and its acquisition setup allowed normal
entry into a fresh aim action. The final fixtures separate the body/exposure
obstacle heights and supply an unpaid contact gate for the deadline assertion.
No production change was made to resolve those test-fixture failures.

## Changed scope, identity and evidence reuse

Exactly five native files differ from Candidate02, all in `Source/MeridianSquad/`:

- `CombatAITactics.h`: explicit stance probe profiles.
- `EnemyCombatComponent.h`: assessed stance/evidence identity and explicit
  stance parameter for tactical assessment.
- `EnemyCombatSenses.cpp`: coalesced investigation evidence and prompt attention.
- `EnemyCombatTactics.cpp`: stance-aware probes and affected selection/movement/
  arrival/hold validation; preserve scan progress during hold reassessment.
- `EnemyCombatPolicy.cpp`: request standing before the visible-contact backoff.

`source-delta-from-candidate02.patch` contains the complete native delta.
`candidate-manifest.json` and `CAI02-Candidate03-frozen.zip` freeze final native
sources, the DLL/module descriptor, helpers, this report and bounded evidence.
`freeze-result.json` records package identities and archive verification.

DLL SHA-256:
`c0c3b64f8ab48bd9c9eb6cbb4100a7a9a3a2c0ea42f240ba32fdf7c8ea66d488`.
Baseline Git revision: `c4da5eaaf5793556c3a0884a10ad975573d6a0e0`.
Candidate02 manifest SHA-256 remains
`2cf9d388930e7bc4142053a3eb38f7039980feff4b2736622c1a00d78f8d0566`.

Candidate01/02 handoffs, helpers, frozen manifests/archives and the original
review/reproducer evidence are unchanged (143 captured files). The 146 earlier
historical evidence files remain unchanged. Current owner configuration,
project/map, instructions, task/state/approval/acceptance documents are preserved.
No Content/Plugins assets were modified.

Reuse Candidate02's passing navigation checks and Candidate01's passing sensory
delivery, grounded-motion/audio, saved-class ancestry and source/weapon evidence
for unchanged criteria. The primary review's passing geometry channel, hearing,
world-clock, navigation, action and firing-clearance conclusions remain applicable
outside these corrected paths. Their old R1/R2 conclusions remain preserved as
the original review, not relabeled as a pass. No full matrix was repeated.

All tuning remains unchanged, including 70 m sight, 45 m navigation domain with
the matching 50 m ceilings, 24-world-second pursuit, sensory uncertainty, finite
projectiles and weapon deadlines. World/bullets/rifle slowdown remains 0.25 and
hero movement 0.65. Navigation remains one floor layer; local protected-position
queries and nominal stance profiles do not prove usefulness in the actual map.

## Controller and owner handoff

No editor was running before the build or at packaging; no editor lifecycle
change, PIE, simulation, firing, gameplay screenshot or performance run occurred.
The new DLL has not been loaded into an editor. The controller owns the ordinary
retained-lobby reload after the same primary reviewer closes the affected findings,
then scope/evidence acceptance, issue administration and the local commit.
The executor did not delegate, change status/profiles, dispatch successors or commit.

Owner gameplay remains pending. The bounded follow-up is to keep making footsteps
behind cover while observing whether the enemy completes a decision, change the
sound region during a protected move, and inspect actual crouched arrival/holding
and return to standing on renewed contact. Physical interruption and the existing
slowdown can be included in those affected transitions. Actual sound, motion,
geometry usefulness and combat feel have not been accepted by this handoff.
