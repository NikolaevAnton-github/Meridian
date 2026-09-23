# MSQ-118 / CAI-T01: bounded correction review

2026-09-23. **PASS at source/pure level for Candidate02/build01. CAIT-R1 and
CAIT-R2 are CLOSED for this candidate. No remaining technical blocker was found
within the assigned correction scope.** Controller acceptance and owner gameplay
judgement remain separate.

| Candidate | Independent verdict |
| --- | --- |
| Candidate01/build02 | **CHANGES REQUESTED**, unchanged historical verdict. The original report and both failing gap probes remain preserved. |
| Candidate02/build01 | **PASS** for the corrected boundaries, with applicable prior T02/T03/T05 evidence reused. All actual gameplay quality, performance and combat feel remain **PENDING OWNER**. |

The reviewed manifest is
`Saved/CombatAI01/CAI-T01/Worker/Candidate02/candidate-manifest.json`, SHA256
`84ec7657a45531c4fdf98ec85df528cfc5a43b7307daa3ea48955b1a0636afd3`.
Its **96 entries match both live files and the frozen archive**. The delivered DLL
SHA256 is `37bdfc7279f3d883bf849ba72827c0a74115dae7154cc15b56a055785bf50ae0`.
This verdict does not modify the frozen manifest's historical pending-review field.

## Finding closure

### CAIT-R1 — CLOSED

`Source/MeridianSquad/EnemyCombatNavigation.cpp:108` separates tactical grid
connectivity from actual arrival: the connection radius is 1.5 cells, bounded to
90–180 cm by the existing 60–120 cm cell clamp. At line 137, a tactical terminal
node succeeds only after `GroundPoint(PathGoal)` and `WalkSegment` validate the
exact supported endpoint and final strip. The endpoint is appended to the path.
A failed connector falls through to ordinary neighbor expansion at line 150;
it neither accepts the goal nor skips potentially useful approaches.

The unchanged segment validator checks support, step height and capsule sweeps
with at most six samples for that connector. Expansion count, per-call work,
world-time timeout and action-generation checks remain bounded. Non-tactical
pursuit retains its previous acceptance predicate.

The supplied extracted-method checks reproduce the original goal at (360,360)
and now find its exact endpoint in five expansions. The aligned control, all
48 cell-size/grid-phase cases and a displaced start pass. A blocked first
connector still reaches a useful neighbor; fully blocked or unsupported endpoints
fail without an accepted path and retain the configured expansion cap.

Actual arrival remains a separate 45 cm test in
`Source/MeridianSquad/EnemyCombatTactics.cpp:349`. It assesses actual feet and
requires `AcceptTacticalArrival` to preserve valid facing, protection and exposure.
The affected checks confirm that feet 50 cm away continue following with the
45 cm tolerance, exposed feet at the boundary reject the destination for
12 seconds, and valid protected feet enter outward observation. Source inspection
also confirms that the unchanged `FollowPath` revalidates the next segment from
actual feet before submitting movement. The wider connector cannot confer arrival.

### CAIT-R2 — CLOSED

`Source/MeridianSquad/EnemyCombatTactics.cpp:30` now uses one native channel trace
with a response container that ignores every object type except WorldStatic.
The requested channel and static object eligibility are both filtered before
selection of a blocking hit. This removes the old first-object/postfilter loss
of farther geometry while retaining the exclusion of pawn/dynamic object types.

The installed engine source confirms the adapter's semantics:

- `Engine/Private/Collision/WorldCollision.cpp:128` passes the response container
  to `RaycastSingle` with the default, invalid object-query parameter.
- `Engine/Private/PhysicsEngine/PhysicsInterfaceUtils.cpp:14` builds a channel
  query using that channel and response container.
- `Engine/Private/Collision/SceneQuery.cpp:519` supplies those filters and sets
  `bIgnoreTouches` for a single query; `CollisionQueryFilterCallback.cpp:158`
  discards touch results before ray-hit selection.
- `Experimental/Chaos/Private/Chaos/CollisionFilterData.cpp:467` combines the
  query-to-shape and shape-to-query responses by their minimum. The exact installed
  filter body is included unchanged in the executor's checked unit source.

The focused cases verify that ignore and overlap foreground objects at 200 cm
cannot hide the 210 cm wall: the wall is returned and the facing sector rejected.
Blocker-only, no relevant blocker, unordered nearest-hit, independent Pawn versus
Visibility response, and changing dynamic-object placement controls pass. Each
trace uses one world query. Newly invalid arrival facing is rejected; invalid
held facing cancels cached scan work and requests immediate reassessment.

The original mixed-response case remains an adversarial contract example, not
evidence of a defect observed in the retained lobby. No live-map behavior is
inferred from these adapters.

## Evidence applicability and limits

Only `ContinuePath` and `TacticalTrace` differ in production from the frozen
Candidate01 source. The original 87-entry archive verifies; all 51 captured
historical evidence/report files retain their hashes. The original review matches
its prior closure hash and `Controller/Candidate01-primary-review.md` exactly.

I inspected the correction fixtures, assertions, generated source, actual methods
and engine filter wiring. All seven extracted component methods and the installed
engine filter match their recorded hashes and generated bodies. The native
Development Editor build and existing **25 behavioral assertions / 48 grid cases /
17 source, preservation and wrapper checks** are applicable and reused. No missing
boundary required a new behavioral probe or repeated build. These are deterministic
collision/action/container/clock adapters, not execution of an Unreal collision
world or locomotion. The prior T02/T03/T05 review remains applicable within its
original source/pure limits.

| Criterion | Candidate02 conclusion |
| --- | --- |
| T01 | **PASS at source/pure level**: both identified route/facing gaps close; applicable original position-validation evidence is retained. |
| T02 / T03 / T05 | **Prior source/pure PASS reused**. Unaffected knowledge, timing and lifecycle implementation remains unchanged. The static-query exclusion is also covered by the correction controls. |
| T04 | **PASS at source/pure level**: route connection is corrected; blocked routes, destination rejection, transfer-budget backoff and invalid held geometry retain bounded behavior. Unaffected hold/selection evidence is reused. |
| T06 | **PASS**: matched native build, inspected focused correction evidence and closed regression gaps. |

New review evidence is under `Saved/CombatAI01/CAI-T01/Review/Candidate02/`:
`candidate-verification.json`, `preservation-and-delta.json`,
`reviewed-source-diff.patch`, `evidence-applicability.json`,
`review-run-settings.json` and `audit-final.json`. The initial audit's build-log
string check used the wrong decoding for the UTF-16 log; the BOM-aware audit
addendum resolves that checker-only false result without altering or rerunning
the successful build. Both audit records remain preserved.

The configured reviewer profile, current native process 46856 and this review's
turn context verify Astra/max. Explicit default-tier and disabled-fast-mode native
arguments verify standard speed; the turn context does not contain a tier field.
No setting was changed.

All actual movement, map-position usefulness, visible response, firing, physical
transitions, performance and combat feel remain **PENDING OWNER**. The authorized
local one-layer navigation, conservative direct tactical preview, sight-only
knowledge and one-member coordinator limits remain. Hearing, Recast, squad and
equipment completion are outside this correction review.

No production edits, editor operations, gameplay, delegation, profile or issue
administration, or commits were performed. Controller retains acceptance, final
ordinary editor handoff, task status and the MSQ-118 closure commit.
