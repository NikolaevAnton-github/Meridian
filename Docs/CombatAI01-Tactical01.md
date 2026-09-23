# MSQ-118 / CAI-T01: single-enemy protected observation

Executor handoff, 2026-09-23. **Candidate01/build02** implements the bounded
sight-based tactical slice on MSQ-103. Native Development Editor build, **45 pure
production-contract test groups and 43 source/preservation/build-wrapper checks
PASS**. Independent source review is **PENDING CONTROLLER DISPATCH**. Every actual
movement, map-position utility, visible reaction, firing, physical transition,
performance and combat-feel criterion remains **PENDING OWNER TESTING**.

No agent PIE, simulation, gameplay/firing probe, gameplay screenshot or performance
run was performed. Editor work was lifecycle control and read-only static geometry
inventory. Source/test success is not observed gameplay acceptance.

## Candidate identity and preservation

Baseline HEAD: `5ae0fbc48a2c2f2b3cd3da64d15ec1a70446712a` (delivered MSQ-103).
Engine: UE 5.8.3-58210709, Win64 Development Editor. Evidence root:
`Saved/CombatAI01/CAI-T01/Worker/Candidate01/`.
DLL SHA256: `54e8a54e2b5ec25145720a5e07ef168ff9e1ccbb57dc87a9e2118797cda9c0c3`.
`candidate-manifest.json` freezes source, scripts, this report, DLL/modules and
evidence; `CAIT01-Candidate01-frozen.zip` retains those exact bytes, including the
DLL. A separate small evidence archive is the issue attachment. Substantive
post-freeze corrections require a new candidate name.

Configured/native execution is Astra/max, standard/default service tier, fast
mode disabled. `execution-settings.json` checks the saved controller profile,
native process arguments and native turn context. The turn context omits the tier;
the actual native arguments explicitly set `default` and disable fast mode.
The executor did not delegate, change profiles/status, commit, dispatch successors
or edit controller-owned approvals/task/state/AGENTS content.

`preservation-check03.json` matches the controller's exact owner config, project
and retained map hashes. The full `AGENTS.md` hash differs because Multica appended
its auto-managed runtime block at task startup; `instructions-preservation-check03.json`
verifies the original durable instruction bytes unchanged. The original controller
manifest was not edited or silently rebaselined. No assets were edited or saved.
Player/rifle/projectile/physics/GASP source preservation checks pass against the
baseline, including unchanged `CanShoot`, sight adapter and finite `Fire` bodies.

## Behavior and selection contract

Personal encounter memory remains in `EncounterMemory`. A small value-only
`TacticalAssignment` selects `Engage` or `ProtectedObservation` from permitted
member reports. It carries generation, monotonically increasing revision, evidence
ID and decision time. The local component alone executes movement, aim and weapon
actions. This is a one-member assignment seam; no group behavior is implemented
or validated, and it introduces no second path planner.

Successful sight is classified using memory/visibility/direction **captured before**
the sight adapter refreshes them. First contact retains the configured .65-second
response delay. Reacquisition within 1.5 world seconds is `brief`; a longer absence
is `known`. Both add no new acquisition wait. A direction change exceeding 60 degrees
adds a bounded .2-second response gate. Continuous sight does not restart a gate.
Brief hiding cannot erase an unpaid first-contact delay.

Fresh visible contact cancels an obsolete scan/hold/move during the next sight
decision, ahead of ordinary observation waits. A current weapon/route backoff still
prevents that failed action, while the enemy faces the newly observed threat.
Normal aim settling remains .65 seconds on entry to aim; real movement, animation,
alignment, muzzle corridor, direct sight at bullet birth and physical readiness
gates are unchanged. Acquisition, aim, completed-burst pause, reload and shot cadence
now have separate not-before deadlines. Reacquisition does not shorten a burst
pause, cadence or active reload, and cannot restart the reload's ammo commit.

After losing sight, the component scans collision near actual feet. Up to eight
radial chest-height surface hits generate a standing point offset from the real
surface normal plus two tangent neighbors. Current feet and four local observation
probes are also considered. Coordinate offsets alone never earn protection.
The maximum is **29 candidates**; duplicates within 65 cm are coalesced.

All proposal generation/scoring/facing queries use **WorldStatic collision**, not
the concealed player's transform. Each candidate requires a center plus four
footprint support rays, slope/height limits, a standing capsule with clearance and
a supported swept route from the scan origin. The route preview deliberately
requires a direct local strip, up to 900 cm, sampled at no more than 35 cm spacing
(26 steps maximum). Candidates needing a bend around an intervening obstacle are
conservatively rejected by this slice. The existing bounded navigator still
executes accepted movement and applies physical safety vetoes.

Eight sectors measure open approach distance at 95/150 cm above feet. Close vertical
blockers within 160 cm must block both pawn and visibility queries to count as
rear/side protection. A useful facing requires at least 220 cm clear space plus
a 120 cm weapon-space sphere sweep. Four 105 cm supported escape strips contribute
to the score. Three rays toward the last observed region estimate exposure;
uncertainty expands from 180 to 500 cm with evidence age. None supplies knowledge
of unobserved movement, sound or incoming fire.

The score favors rear/side protection, reduced remembered-region exposure,
approach visibility, useful weapon space and multiple validated escapes, with a
travel penalty. The current position has zero travel cost. The single winner is
revalidated before movement. Navigation appends a validated final strip to the
tactical goal, addressing overlap between grid acceptance and waypoint tolerance.
Arrival within 45 cm must pass a new assessment at **actual feet**, retaining useful
facing and approximately the selected protection/exposure. Failure rejects the
destination for 12 world seconds and returns to alert observation.

While holding, aim/strafe inputs turn the existing adopted foundation toward open
sectors; the look point is horizontally ahead at 140 cm height. The policy does
not follow the hidden pawn or aim at its own feet. It visits useful sectors on the
existing observation dwell, revalidates held geometry each second and periodically
rescans. Lost geometry invalidates cached work and releases ordinary commitment.
These are source contracts; visible turning quality remains an owner gate.

Ordinary switches require commitment and a score margin. After a stale hold, a
nearby informative probe can replace it if it reveals additional open sectors
while retaining comparable protection/exposure. Recently visited neighborhoods
are suppressed for 20 seconds. No timer alone forces an exposed walk. If there is
no useful alternative, observation continues with an explicit fallback reason.

## Work, lifecycle and tuning limits

One surface-generation step **or** one candidate assessment runs per scan tick,
at most 40 steps per world second, with a four-world-second scan deadline. Held
validation and the two final current/winner assessments are additional bounded
work; this is not a hard microsecond CPU budget. One full assessment has at most
299 static collision queries by loop bounds (6 standing, 182 route, 16 sectors,
8 weapon, 84 escape and 3 region queries). Counts are exposed for owner diagnosis;
no measured frame-time or performance claim is made.

Travel is limited to two requests per 12-world-second assignment window. Each
tactical move has a ten-world-second deadline; the existing navigator retains its
two-failure behavior, 1200 default expansion cap, 16 nodes/frame, 1.5 ms boundary
between nodes, five-world-second planning timeout and 1.8-second stuck check.
Eight-entry spatial histories bound failed/visited storage. A failed goal is not
retried until its neighborhood expires; exhausted travel attempts wait for their
window. New evidence/lifecycle changes can rebuild the assignment without erasing
the applicable destination history. There is no callback or action queue.

Reset, death, disable and living physical interruption cancel assignments/scans,
selected positions, paths and action requests. Living recovery preserves personal
encounter awareness and last observation, then rebuilds from actual displaced
feet. Death/reset clear the declared memory boundary. Existing generation/ID
guards and guarded one-time reload completion remain in place. Already launched
finite bullets keep their original lifecycle.

| Setting | Default / effective bounds |
| --- | --- |
| Sight sampling | .12 world seconds, retained |
| Initial response / aim | .65 / .65 seconds, retained |
| Known reacquisition / new direction response | 0 / .2 seconds |
| Tactical surface radius | 650 cm / 250–750 |
| Nearby probe radius (`SearchRadius`) | 360 cm / 200–400 |
| Reassessment interval | 2.5 seconds / 1.5–8, after completed scan |
| Ordinary commitment | 4 seconds / 1–10 |
| Informative probe eligibility | 6 seconds / 3–20 |
| Switching score margin | 10 / 3–30 |
| Sector observation dwell (`search`) | 2 seconds / .5–3 |
| Failed destination / visited neighborhood | 12 / 20 seconds, 120 cm radius |

All tactical deadlines use world time. Retained combat values include 1000 cm
attack range, 12-round magazine, three-round bursts, .18-second cadence,
1.1-second pause, 2.6-second reload and unlimited reserve. World/bullets/rifle
cadence .25 and hero movement .65 during slowdown are unchanged.

## Verification and owner gates

| Criterion | Source/pure result | Actual behavior |
| --- | --- | --- |
| T01: geometry protection, support/capsule/route/facing, actual arrival | PASS ranking/adversarial inputs, static adapter wiring, fresh winner/arrival checks | PENDING OWNER: useful retained-map positions and actual arrival |
| T02: permitted evidence and outward facing | PASS typed input separation, static-only proposal queries, 10,000 identical-input comparisons, usable-sector cycling | PENDING OWNER: visible orientation and response to unobserved relocation |
| T03: fresh contact and preserved weapon gates | PASS pre-refresh classification, independent deadlines, continuous-sight and unpaid-delay cases, source ordering | PENDING OWNER: perceived reaction delay and real firing |
| T04: active holds, switching and bounded failure | PASS commitment/novel-sector boundaries, 10,000 stable choices/failure history transitions, 12,000 transfer attempts | PENDING OWNER: non-passive useful holds, unreachable routes and performance |
| T05: interruption/reset/recovery | PASS assignment/action token cases, live cancellation wiring, preserved memory/actual-feet origin | PENDING OWNER: living physics, death and F6 transitions |
| T06: native build and focused checks | PASS `build02.log`; 43 checks in `self-check-check03.json`; 45 pure groups in `pure-test-check03.log`, compiled `/W4 /WX` | No runtime acceptance inferred |

The isolated privileged-position test proves the pure selector's input boundary,
not live hidden-player independence by observation. Source inspection establishes
that the native tactical adapter uses the same permitted evidence and static
geometry boundary. The read-only `editor-geometry.json` inventories 108 mesh actors,
including 70 WorldStatic meshes blocking pawn and visibility. It confirms available
collision classes, not tested tactical positions or navigation success.

Focused self-check corrections before freezing separated the transfer retry window,
added fresh winner/held-geometry invalidation and refined diagnostic facing. Both
native builds passed; final build02 used 14 actions, 11.55 seconds total. The initial
pure build failed on a test include path and was corrected. Its failure log remains.
The initial geometry audit used an unavailable Python enum spelling; the corrected
audit completed without dirty packages. No rejected historical evidence was edited.

`editor-launch.json` records the ordinary retained-lobby editor PID and durable log.
`editor-load-check.json` matches its loaded DLL to build02; `editor-after.json`
confirms the expected project/map with no PIE or dirty packages. This is the owner
handoff session, not background task work. Close the editor normally when finished;
continued availability is best effort without a supervisor.

## Changed files and owner route

- `CombatAITactics.h`: pure coordinator, contact deadlines, ranking, switching,
  arrival, sector, bounded history and transfer contracts.
- `EnemyCombatTactics.cpp`: static geometry adapter, incremental scans, validation,
  movement selection and active holds.
- `EnemyCombatComponent.h/.cpp`, `EnemyCombatPolicy.cpp`: tuning, separate gates,
  pre-refresh sight classification, assignment/action lifecycle and controls.
- `EnemyCombatNavigation.cpp`: validated final tactical goal strip.
- `CombatAIObservation.h`, `EnemyCombatObservation.cpp`: schema 3 tactical fields
  in the existing bounded 64-event trace; no privileged observation channel added.
- `Scripts/CombatAI01/CAIT01/`: focused tests, read-only editor audit and freezing.
  This report is the only executor-owned documentation change.

Play the retained lobby in its current one-opponent mode. Establish contact,
briefly hide and reappear. Then stay hidden longer behind existing geometry and
approach visibly from another direction. Inspect protection choice, useful facing,
active sector checks and whether new contact cancels a stale move. Try a blocked
route, a living physical displacement, and F6 during movement/reload. Silent hidden
movement is not a heard clue in this slice.

F6 / `msq.EnemyCombat reset` resets the encounter without refilling player ammo.
`one`, `fixtures`, `pause`, `resume`, `status` and `trace` retain their roles;
pause/resume clear encounter memory. `trace` explicitly exports under
`Saved/CombatAI01/CAI-T01/Traces/`. Existing combat tuning commands remain, with
`tune tacticalradius`, `reassess`, `commit`, `probe` and `margin` added. `tune search`
sets sector dwell. Tune changes are session-local and become effective on the next
relevant scan/gate, with clamping above.

Status/trace exposes objective/revision, selected position/facing, phase/reason,
candidate/evaluation/rejection counts, protection/exposure score, evidence age,
scan/decision/action/movement/hold timestamps and pending gates. Separate contact,
aim, burst-pause, cadence and reload deadlines explain a wait before the first shot.

Limits: one enemy, one floor layer, home-centered 2800 cm local navigator,
conservative direct-strip tactical previews, simple static collision and bounded
regional uncertainty. No hearing, incoming-fire awareness, ally-loss knowledge,
Recast/topology, validated groups, suppression, equipment, new art or geometry.
CAI-03/04/05 are not declared complete. Controller owns independent review,
acceptance, administration and the local closure commit with MSQ-118.
