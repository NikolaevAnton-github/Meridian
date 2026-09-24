# MSQ-119 / CAI-T02 controller acceptance

2026-09-24. **Candidate02/build01 is accepted within the authorized build/source
scope and delivered for owner testing.** The native build, focused production
checks and the sole primary technical review pass. CFT02-R1 and CFT02-R2 are
closed. Actual motion, cover usefulness, reaction feel, difficulty and performance
remain pending owner play.

Authority: [owner follow-up](Approvals/CombatAI01-CoverFire01-OwnerStart01.json)
and [task](Tasks/CombatAI01/CAI-T02.md). Read the
[base handoff](CombatAI01-CoverFire01.md),
[correction](CombatAI01-CoverFire01Correction01.md),
[original review](CombatAI01-CoverFire01Review.md) and
[same-primary finding closure](CombatAI01-CoverFire01Correction01Review.md).

## Scope and evidence applicability

The enemy has independently validated left/right step-out positions and a
low-cover crouch/stand/burst/return lifecycle through existing GASP/Mover commands.
Rifle effective/preferred range is 55/28 m. Initial reaction and aim deadlines
are .08/.10 world seconds concurrently, with retained .12 s sight sampling.
Actual visibility, achieved position/stance, braking, aim, weapon readiness and
muzzle safety still authorize every finite-flight shot. Policy latency is not
a measured animation or gameplay result.

The former obstruction chase to the player's feet is removed. Useful distant
shots hold range; necessary advance uses bounded 4.5 m walking requests. Typed
weapon, actual self-health, optional target-health evidence and available ally
capabilities enter the current policy. Player health is absent and explicitly
unknown; its comparison needs a future real producer. No new weapon, live group
cooperation, player health/death, suppression, full topology or art/map work is
declared implemented by this slice.

Candidate01 provides 71 passing assertions over extracted production methods,
the native build and reviewed cover/context/timing evidence. Its two review
findings exposed lost crouch requests during protected search handoff and stale
muzzle obstruction blocking an otherwise valid cautious approach. Candidate02
changes four native files, preserves the validated stance at route/arrival
handoffs, and revalidates bounded obstruction evidence before range selection.
Its native Development Editor build and 44 affected assertions pass. The same
primary reviewer closes both findings and passes CF01-CF08, reusing applicable
unchanged evidence. No full matrix or passing behavior suite was repeated by
the controller. No agent gameplay, simulation or firing ran.

The controller checks requested scope, candidate identity, preservation, evidence
applicability and finding closure. The primary reviewer owns the technical
verdict; this acceptance is not a second full technical review.

## Identity and preservation

Final manifest SHA256:
`4a38e81d8e422a249d66cf7ce9558c9b4e0889548453f36f78a8f47e8b1c2537`.
Final DLL SHA256:
`26ba450661cc116c24c2d0c438bd94556b42ac87396548748bc7ee383a6104b6`.

All **98 final manifest entries** match current and archived bytes in controller
`Saved/CombatAI01/CAI-T02/Controller/identity-Candidate02.json`. Candidate01's 131
archived entries were verified before correction; its manifest/archive, reports
and original review remain preserved. The reviewer also verifies 56 extracted
method/consumer identities and 360 preserved historical evidence/script files.
Owner config/project/map and durable instructions retain their captured bytes.
No binary assets changed, so asset registration is unnecessary.

All four intended executor/reviewer runs use configured and native
**Astra/max/default with fast disabled**. Shared profiles retain those settings.
One advisory comment generated a redundant queued run; it was cancelled before
execution, preserving one intended production writer. Its reason and history
remain in the controller evidence directory.

## Delivery and closure

The controller reopened the ordinary editor after the worker process lifetime
ended its earlier editor. The mapped project DLL matches Candidate02/build01;
official Epic MCP confirms the retained lobby, no PIE world and no dirty packages.
The task runtime is stopped. Administrative closure, unchanged profiles,
preservation and local task commit are recorded in
`Saved/CombatAI01/CAI-T02/Controller/closure-summary.json`.
MSQ-105 through MSQ-117 remain undispatched; MSQ-101 remains coordination only.

Owner route: Play the retained lobby, engage at rifle range, use columns and low
cover, change the available peek side and reappear from another direction. Check
stand/burst/crouch, interruption by hits, F6 reset and Y slowdown. Existing
`msq.EnemyCombat status`/`trace` explains phase, side, range and pending gates.
Actual movement, cover utility and reaction feel remain the owner's judgement.
The local single-floor navigator and conservative static geometry remain limits;
lateral motion uses real step-outs without a newly authored lean animation.
