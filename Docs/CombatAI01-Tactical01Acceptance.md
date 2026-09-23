# MSQ-118 / CAI-T01 controller acceptance

Date: 2026-09-23. **Candidate02/build01 is accepted at build/source level for
owner testing.** The sole primary reviewer closes CAIT-R1/R2 with no remaining
technical blocker in this scope. Actual position usefulness, motion, firing,
physical transitions, performance and combat feel remain **PENDING OWNER**.

Authority: [owner start](Approvals/CombatAI01-Tactical01-OwnerStart01.json).
Read the [base behavior handoff](CombatAI01-Tactical01.md),
[correction handoff](CombatAI01-Tactical01Correction01.md) and
[final independent review](CombatAI01-Tactical01Correction01Review.md).
The [original changes-requested review](CombatAI01-Tactical01Review.md) and its
failed reproducers remain unchanged historical evidence.

## Scope and applicable evidence

The one-member tactical assignment selects engagement or protected observation.
Lost contact now evaluates static geometry, supported routes, useful facing,
rear/side protection and bounded alternative observation opportunities.
Arrival is accepted from actual feet, with held-geometry reassessment and finite
rejection/retry history. Physical authority, action/reset identities, finite
bullets and slowdown clocks remain authoritative.

Known-contact reacquisition adds no new initial acquisition wait. A substantially
changed direction adds a 0.2-world-second reaction gate; initial acquisition and
normal aim settling retain 0.65 seconds. Separate weapon deadlines preserve burst
pauses, reload completion and cadence. These are source/default facts, not measured
reaction times in the owner's session.

Candidate01 supplied a native build, 45 pure contract groups and 43 supporting
checks. The primary reviewer found two integration defects: off-grid endpoints
and channel filtering behind an irrelevant foreground object. Candidate02 changes
only ContinuePath and TacticalTrace. Its native build passes (5 actions, 4.52
seconds); 25 affected assertions, including 48 grid-phase/cell-size cases, and
17 supporting checks pass. The same reviewer closes both findings, reusing
applicable prior T02/T03/T05 and unchanged behavior evidence.

The controller accepts scope, identity, preservation and evidence applicability,
without duplicating technical review or rerunning passing tests. No agent PIE,
simulation, firing or gameplay/performance probe occurred. Editor loading and
static geometry inspection are not gameplay acceptance.

## Identity and preservation

Final evidence: Saved/CombatAI01/CAI-T01/Worker/Candidate02/.
Manifest SHA256:
84ec7657a45531c4fdf98ec85df528cfc5a43b7307daa3ea48955b1a0636afd3.
DLL SHA256:
37bdfc7279f3d883bf849ba72827c0a74115dae7154cc15b56a055785bf50ae0.
All **96 entries match** in Controller/identity-Candidate02.json; the reviewer
also matches live and archived bytes. Owner config/project/map, character sources,
original archives and MSQ-103 evidence remain preserved. The correction retains
all 51 historical evidence/report files it consumes. No assets or geometry changed.

A controller monitor initially appended later reviewer context to a controller
log frozen with Candidate01. The later readout was preserved separately and the
exact original log restored from the verified archive. The explicit record is
Controller/frozen-evidence-restoration.json; no manifest, source or binary was
rebaselined. Later monitoring uses separate files excluded from Candidate02.

## Execution and closure

One Multica Unreal executor and one primary Code reviewer performed implementation,
bounded correction and finding closure sequentially. Every native run is verified
as Astra/max, with explicit default tier and fast mode disabled. Turn contexts omit
tier; actual arguments and matching profiles establish standard speed. No task-local
profile changes were needed.

All four runs completed; MSQ-118 is closed in Multica at build/source level.
MSQ-101 remains the coordination parent, and MSQ-104 remains backlog, unassigned
and without runs. Its prerequisite/description now includes this delivered policy.
The task runtime is stopped and both agent profiles remain unchanged at max/default.
AGENTS.md matches its original bytes. The retained lobby is reopened in the ordinary
owner editor (PID 40372): Epic MCP confirms the correct project/map, no PIE and no
dirty packages. The loaded project DLL matches the accepted hash above. Evidence:
Controller/closure-summary.json, closure-issues.json, closure-profiles.json,
editor-state-final.json and editor-loaded-final.json. Controller records the local
task-scoped commit in the closure summary before owner handoff.

## Owner route and limits

In the retained lobby's one-enemy Play mode, establish contact, briefly hide and
reappear. Then break contact longer, observe the chosen position and watched
approaches, and reappear visibly from another angle. F6 restarts the encounter.
The existing msq.EnemyCombat status and trace expose objective, position/facing,
reason and timing gates; exports use Saved/CombatAI01/CAI-T01/Traces/.

This is one enemy on one floor layer, with the retained 28 m home navigation
radius, conservative direct tactical previews and sight/last-sight evidence.
Hearing remains MSQ-104, which must consume this policy; it and successors remain
undispatched. Full groups, Recast topology, suppression, smoke and traps remain
later scope. Owner judgement of believable combat remains the next acceptance step.
