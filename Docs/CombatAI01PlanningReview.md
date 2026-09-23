# CombatAI01 planning review and controller acceptance

Date: 2026-09-23. Scope: documentation-only planning after the owner's MSQ-70 feedback.
Package: [design](Design/CombatAI01.md) and [implementation plan](Tasks/CombatAI01Plan.md).
Authority: [exact owner direction](Approvals/CombatAI01-Planning01.json).

## Independent review

One independent primary reviewer, `/root/combat_ai_plan_review`, inspected architecture
coherence, relevant source seams, dependency order, validation, time policy and scope.
The reviewer did not author the plan. Separate read-only architecture/gameplay advisors
supplied focused findings to the controller; their advice was not a technical verdict.

| Finding | Correction | Final status |
| --- | --- | --- |
| CAI-P1: hidden-position invariance conflicted with privileged fairness permissions | Compare knowledge, scores and targeting proposals before the start gate. Gate output is grant/generic wait; no hidden-location feedback into knowledge/routes/aim. Capture fairness inputs separately for timing replay. | Closed by the same reviewer |
| CAI-P2: suppression had no distinct authorization seam from current sight-only firing | Define DirectFire and SuppressRegion with common safety/launch gates, separate sight/evidence requirements, bounded region age/rounds and no automatic burst conversion. CAI-04 and S23 precede cooperative suppression. | Closed by the same reviewer |

Final reviewer verdict: **Pass — both findings closed.** The bounded recheck found no
remaining material issues. This is documentation acceptance, with no build or runtime
validation performed.

Native session metadata confirms `gpt-6-astra` and `max` for the two advisors and the
reviewer. Standard speed was requested with no fast override; native turn context does
not expose an explicit response tier. Evidence is recorded under
`Saved/CombatAI01/Planning/execution-settings.json`.

## Controller acceptance

- The owner's arcade/surprise priority and concrete awareness/search requests are
  preserved, with assumptions and proposed tuning distinguished from owner decisions.
- The plan contains 12 main packages, four prerequisite-specific CAI-09 integrations,
  23 focused scenario definitions, owner play criteria and explicit completion gates.
- It delivers an early single-enemy improvement before squad and future-power scope.
  New package references are not represented as created or dispatched Multica issues.
- Time rules consume the later cadence decision; the GASP physical and finite-projectile
  authorities remain explicit. Existing owner gameplay-test scope is not revoked.
- JSON, local document links introduced by this package, code fences and scoped
  whitespace checks pass. Generated validation details remain under `Saved/`.
- Current project/game/task navigation is updated. Owner config/project edits, map,
  runtime sources and historical candidate evidence are outside this documentation commit.

The controller accepts this as the requested detailed plan. Gameplay, performance,
motion, comparative AI quality and owner acceptance of future implementation remain
unmeasured. No editor operation, build, gameplay run or production dispatch was made.
The local planning commit is reported in the owner handoff.
