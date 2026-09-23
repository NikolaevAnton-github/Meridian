# MSQ-118 / CAI-T01: Candidate02 correction handoff

2026-09-23. **Candidate02/build01 is ready for the same primary reviewer.**
CAIT-R1/R2 corrections pass the native Development Editor build, 25 focused
behavioral assertions (including 48 grid-phase/cell-size cases), and 17
source/preservation/test-wrapper checks. Independent finding closure remains
pending. Runtime position usefulness, movement, responsiveness, performance and
combat feel remain **PENDING OWNER**.

This corrects the two findings in `Docs/CombatAI01-Tactical01Review.md`. Candidate01,
its original handoff, the review and its failed reproducers remain unchanged.
No gameplay, PIE, simulation, firing, new art or geometry was performed.

## Findings and evidence

| Finding | Correction | Focused evidence |
| --- | --- | --- |
| CAIT-R1: arbitrary goals cannot connect within the 45 cm grid-node test | `EnemyCombatNavigation.cpp`, `ContinuePath`: tactical nodes may attempt a supported final connector within 1.5 cells (90-180 cm). A failed connector falls through to neighbor expansion. The exact supported endpoint is appended only after `GroundPoint` and `WalkSegment` succeed. Actual-feet arrival remains 45 cm with the existing protection/facing guard. | The reported (360,360) goal succeeds in 5 expansions; the aligned control succeeds in 4. All 48 grid-phase cases at 60/80/120 cm cells pass, as does a displaced start. A blocked first connector succeeds through a neighbor; blocked or unsupported final destinations fail without accepting a path, at the configured expansion cap. |
| CAIT-R2: a foreground channel-ignore object conceals a farther blocker | `EnemyCombatTactics.cpp`, `TacticalTrace`: a native channel ray uses a response container that ignores every object type except WorldStatic. Unreal filters both responses before selecting the nearest blocking hit. Ignore/overlap responses and dynamic pawns cannot terminate the query. | Ignore and overlap foreground objects at 200 cm both reveal the blocking wall at 210 cm and reject its facing sector. Blocker-only, no-relevant-blocker, unordered nearest-hit, independent pawn/visibility response and changing dynamic-object placement controls pass. Each trace remains one world query. |

The navigation connection radius is **not** a new arrival tolerance. Extracted
`AdvanceSearch` checks prove that feet 50 cm from the goal continue moving;
exposed feet at the 45 cm boundary fail protected arrival and enter the existing
12-second rejection history. Valid protected feet enter outward observation.
Newly invalid facing rejects arrival; invalid held facing cancels cached scan
work and immediately schedules reassessment. Exhausted transfer attempts retain
the existing retry-window backoff.

Support, capsule, segment, actual-feet arrival, hold, failure-history and follow
methods are unchanged from Candidate01. Only `ContinuePath` and `TacticalTrace`
changed in production. Unaffected timing, weapon, lifecycle, reset and other
source/pure evidence from Candidate01 and the primary review is reused.

## Verification scope and identity

Evidence root: `Saved/CombatAI01/CAI-T01/Worker/Candidate02/`.

- `build01.log`: UE 5.8.3 Win64 Development Editor succeeds, 5 build actions,
  4.52 seconds. Existing StructUtils deprecation notices remain.
- `correction-check-check01.json`, `correction-run-check01.log` and
  `correction-build-check01.log`: 25 assertions and all 17 checks pass; MSVC
  `/W4 /WX` compilation succeeds. `check_correction.py` extracts seven component
  methods unchanged and the installed UE `ChannelTypeNarrowFilter` body. Small
  deterministic collision, action, container and clock adapters supply inputs;
  the fixture assessment uses production `RatePosition`. This does not execute
  the Unreal collision world, locomotion or actual map-position selection.
- Native filter wiring was checked in installed `WorldCollision.cpp:139`,
  `SceneQuery.cpp:519`, `PhysicsInterfaceUtils.cpp:14` and
  `Chaos/CollisionFilterData.cpp:467`. The extracted filter body and its digest
  are retained in the generated unit source/result.
- `execution-settings.json`: configured profile, live native arguments and
  native turn context verify Astra/max/default, fast mode disabled. This is a
  one-time snapshot; mutable controller monitor files are excluded.
- `editor-initial-availability.json`: Epic MCP was unavailable and no editor
  process existed before rebuilding. A temporary diagnostic editor then loaded
  the exact new DLL. Epic MCP verified the retained project/map, no PIE and no
  dirty packages; the guarded close rechecked those conditions. `editor-state.json`,
  `editor-load-check.json`, `editor-close.json` and `editor-exit-check.json` record
  the completed check. The diagnostic editor exited; controller owns the final
  ordinary owner editor launch and restoration.

Built and loaded DLL SHA256:
`37bdfc7279f3d883bf849ba72827c0a74115dae7154cc15b56a055785bf50ae0`.
`candidate-manifest.json` and `CAIT01-Candidate02-frozen.zip` retain the exact
source, correction scripts, report, DLL/modules, checks and immutable evidence.
`CAIT01-Candidate02-evidence.zip` is the compact review attachment.

All 51 historical evidence/report files captured before correction retain their
hashes. Owner config, project and retained map match the controller baseline;
durable AGENTS bytes are unchanged. `preservation-final.json` and
`correction-source-diff.patch` record preservation and the two-method delta.
The executor made no commits, status/profile changes, successor dispatch or
review delegation. Controller retains primary-review return, acceptance, final
editor handoff and the MSQ-118 closure commit.

The local one-layer navigation, conservative direct tactical route preview,
sight-only knowledge and one-member coordinator limits remain. T01 and the
affected T04 boundaries now have passing correction self-checks; T02/T03/T05
evidence is reused within its original source/pure limits. No owner gameplay
acceptance or measured frame-time result is inferred.
