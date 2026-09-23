# MSQ-118 / CAI-T01 independent technical review

2026-09-23. **CHANGES REQUESTED for Candidate01/build02.** CAIT-R1 and CAIT-R2
require executor correction before a technical PASS. This is the sole independent
source review of T01-T06; controller scope/identity acceptance and owner gameplay
judgement remain separate.

Reviewed against `Docs/Tasks/CombatAI01/CAI-T01.md`, the owner start, tactical
design refinement, MSQ-103 prerequisite and executor handoff
`Docs/CombatAI01-Tactical01.md`. No production changes, editor operations, PIE,
firing, gameplay probes, delegation, profile/status changes or commits were made.
Only this report and review evidence were written.

## Findings

### CAIT-R1 — High: reachable tactical goals can have no acceptable grid node

Location: `Source/MeridianSquad/EnemyCombatNavigation.cpp:128`, with the final
connector at lines 132-139 and grid construction at line 150;
`Source/MeridianSquad/EnemyCombatTactics.cpp:367` supplies the new 45 cm acceptance.
Affects T01 and the useful-transfer portion of T04.

The final strip to the exact goal is considered only after a grid node is already
within the actor's 45 cm arrival radius. At the default 80 cm cell size, a goal
halfway between four grid nodes is 56.57 cm from every nearest node. The tactical
adapter generates arbitrary surface/probe coordinates, so its valid direct route
does not establish that this terminal predicate can ever succeed. The previous
85 cm search acceptance did not have this default-grid hole.

A narrow unit check executes the unchanged production `PlanPath` and
`ContinuePath` bodies with a flat supported unobstructed collision fixture,
Home/feet at (0, 0), default tuning and Search purpose:

```text
goal=320,320 found=1 failed=0 expansions=5
goal=360,360 found=0 failed=1 expansions=1200
```

The second goal is only 509.12 cm away, within the tactical adapter's 900 cm route
limit and the home region, but every possible grid node fails the distance test.
Appending `FinalGround` inside that test cannot fix it. The live caller will
consume failed path attempts and reject a reachable observation destination for
12 seconds. This is a source/control-flow defect, not an observed lobby failure.

Required correction: connect a reachable grid node to the exact tactical goal
using a validated final segment without requiring that node to satisfy the
actor's final arrival tolerance. Keep the actual-feet 45 cm and protection/facing
acceptance. Add a focused non-grid goal regression and a blocked-final-segment
case; a failed connector must not accidentally accept the goal or prevent useful
neighbor expansion. Recheck only this path/arrival boundary and related failure
history after correction.

### CAIT-R2 — Medium: channel filtering after a single object hit misses later blockers

Location: `Source/MeridianSquad/EnemyCombatTactics.cpp:35`, consumed by approach
distance/facing at lines 107-127 and by support, surface and region queries.
Affects T01's rejection of invalid facing geometry.

`TacticalTrace` retrieves the first WorldStatic object hit and then checks that
component's response to the requested channel. If the nearest queryable static
object ignores that channel, returning false discards any blocking static object
behind it. A single object query does not prefilter by `Response`; the installed
UE 5.8 implementation confirms this in `Engine/Private/Collision/WorldCollision.cpp:222`
and `Engine/Private/PhysicsEngine/CollisionQueryFilterCallback.cpp:30`.

The focused test executes the unchanged `TacticalTrace` body with a deterministic
single-object-query adapter and passes its result into production `RatePosition`:

```text
ignored_static_at=200 blocking_wall_at=210 trace_blocked=0 rated_open=600 valid_facing=1
blocking_wall_only trace_blocked=1 facing_rejected=1
```

The first 120 cm remains clear for the weapon sweep, so it does not compensate
for the false 600 cm opening. The useful-facing contract requires at least 220 cm;
the real 210 cm wall should reject that sector. The same first-hit filtering can
also hide usable floor/protection or inflate remembered-region exposure.

Required correction: find the nearest static hit that actually blocks the
requested channel, preserving the exclusion of concealed pawns and a bounded work
policy. Do not turn this into an unrestricted dynamic-player query. Add an ignored
or overlap-response foreground object plus a farther blocking object to the
adapter checks, with a blocker-only control and a no-relevant-blocker control.

Applicability limit: the supplied static-mesh inventory contains 69 query-enabled
WorldStatic meshes blocking both channels; the other 39 have collision disabled.
It does not show an active mixed-response example in the retained lobby. CAIT-R2
is a confirmed adversarial adapter contract failure, not a claim that this scene
already exhibits it. It requires no hearing, topology, group or equipment work.

## Criterion verdicts

| Criterion | Independent source/pure verdict |
| --- | --- |
| T01 | **FAIL**: CAIT-R1 prevents valid local goals from connecting to the navigator; CAIT-R2 can accept invalid approach-facing space. Protection scoring, footprint/capsule checks, winner refresh and actual-feet arrival guards otherwise have substantive source/pure evidence. |
| T02 | **PASS at source/pure level**: proposals, scoring and held facing use retained sight values and static geometry; no hidden-player getter enters the tactical adapter. Physical navigation/launch vetoes remain separate. The privileged-position loop proves the selector's typed input boundary, not live-map independence. |
| T03 | **PASS at source/pure level**: contact is classified before sight refresh; known contact interrupts Search/hold work before ordinary waits; an unpaid initial gate survives a brief hide. Contact, aim, burst pause, reload and cadence remain separate. Reload retains its original action token and one-time completion. |
| T04 | **PARTIAL**: commitment, score margin, informative-sector comparison, visit/failure history and bounded scan/transfer work are present and exercised. CAIT-R1 prevents accepting the proposed useful-transfer behavior. No unbounded queue or retry loop was found; the defect wastes bounded retries. |
| T05 | **PASS at source/pure level**: authority/death/readiness checks precede decisions; cancellation invalidates action/path/scan requests; reset/death clear the stated memory boundary, while living recovery retains awareness and starts from actual feet. Existing finite bullets keep their lifecycle. |
| T06 | **Native build PASS; existing focused checks PASS, regression gaps open.** The 45 production-contract groups and 43 source/preservation/wrapper checks are credible for what they exercise, but did not cover the two integration boundaries above. The added narrow checks reproduce both gaps. |

Status/trace records the selected objective, position/facing, evidence age,
candidate/rejection counts and the separate contact/aim/pause/reload/cadence gates.
The action and tactical timestamps support source-level diagnosis of decision
versus execution waits. No in-engine trace/export or performance result is inferred.

All actual movement, map-position usefulness, visible turning/responsiveness,
firing, physical transitions, performance and combat feel remain **PENDING OWNER**.
The conservative direct-strip scope, one floor layer and one-member coordinator
are authorized limitations, not demands for Recast, hearing or group completion.

## Evidence and correction handoff

Evidence is under `Saved/CombatAI01/CAI-T01/Review/`:

- `candidate-verification.json`: all 87 manifest entries match both live files and
  the frozen archive. Manifest SHA256:
  `ed74b3e4d0012572da702631b41899b569912c925ca73a4344272bda366a574d`.
  Candidate DLL SHA256 remains
  `54e8a54e2b5ec25145720a5e07ef168ff9e1ccbb57dc87a9e2118797cda9c0c3`.
- `review-run-settings.json`: reviewer profile and native process 44224 use
  Astra/max/default with fast mode disabled; the reviewer turn context records
  Astra/max. The turn context omits tier, so standard speed is supported by the
  explicit native arguments. No setting was changed.
- Reused worker evidence: `build02.log` (native Development Editor success),
  `self-check-check03.json`, `pure-test-check03.log`, execution settings and
  read-only editor geometry inventory. These passing checks were not rerun.
- `gap-probe-result.json`, `gap-probe.log`, `gap-probe-build.log` and
  `run_gap_probes.py`: only the missing navigation/trace boundary checks.
  Production method bodies are extracted unchanged and fingerprinted. Collision,
  containers and clocks are small deterministic unit adapters; this is not an
  Unreal navigation or gameplay run. Final compilation passes MSVC `/W4 /WX`.
  Exit 0 means both reported defects and their controls reproduced, not product
  acceptance. The initial adapter-only name-shadowing compile failure is retained
  in the `attempt01` logs; the adapter member was renamed without source edits.

Return CAIT-R1/CAIT-R2 to the executor. Substantive corrections require a newly
named candidate; preserve Candidate01 and its exact evidence. The next review
should cover those findings and affected boundaries, reusing the applicable T02,
T03 and T05 evidence. Controller retains issue administration, acceptance and
the MSQ-118 closure commit.
