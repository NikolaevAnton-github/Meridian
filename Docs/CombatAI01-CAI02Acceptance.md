# MSQ-104 / CAI-02 controller acceptance

Date: 2026-09-24. **Candidate03/build01 is accepted within build/source scope
and delivered for owner testing.**
The [original primary review](CombatAI01-CAI02Review.md) found repeated-sound scan
starvation and standing-height probes during crouched observation. The
[bounded correction](CombatAI01-CAI02Correction01.md) passes the executor's native
build and affected checks. The same primary reviewer's
[finding closure](CombatAI01-CAI02Correction01Review.md) passes both findings,
and controller identity checks pass. Owner gameplay,
motion, sound, position usefulness, difficulty and performance remain pending.

Authority: [owner follow-up](Approvals/CombatAI01-CAI02-OwnerStart01.json) and
[task](Tasks/CombatAI01/CAI-02.md). Read the preserved
[base handoff](CombatAI01-CAI02.md) and
[navigation correction](CombatAI01-CAI02Navigation01.md).

## Scope and evidence applicability

The change addresses exposed column-back positions through exposure-first
selection, nearby comparably safe choices and bounded routes around static
columns. Protected search requests actual GASP crouch and quiet step presentation.
Sight covers the retained location with a 70 m default and multiple body samples.
Footsteps, accepted shots and resolved hits supply uncertain evidence that updates
the existing policy. Brief sight loss and physical recovery retain appropriate
knowledge; current visibility and muzzle clearance still gate actual firing.

The navigation follow-up expands the home domain to 45 m, with a 50 m hard ceiling,
and the pursuit deadline to 24 world seconds. The retained floor's farthest corner
is 42.84 m from the actual spawn. This removes the former radius veto; actual
collision and bounded planning still govern movement. Full topology, groups,
equipment, player health and successors are separate scope.

Candidate01 supplies the native build, 66 pure assertions, 22 extracted-method
assertions, source checks and read-only audio/class-wiring evidence. Candidate02
changes three native files and passes its native build, 202 affected navigation
assertions and 16 supporting checks. Candidate03 corrects five native files and
passes its native build, 59 affected assertions and 26 supporting checks. It retains
finite scan progress under fresh sounds, revalidates current evidence before
movement, and applies proposed/achieved stance to tactical probes and transitions.
Unchanged sensory, audio, weapon, navigation and physical evidence is reused.
These are source/fixture results, not observed gameplay.

The controller checks scope, identity, preservation and evidence applicability;
the sole primary reviewer owns the technical verdict. No second full technical
review or passing test suite was repeated by the controller.

## Identity and preservation

Evidence: `Saved/CombatAI01/CAI-02/Controller/identity-Candidate03.json`.
All 100 live and archived manifest entries match. Earlier archive checks retain
131 entries in Candidate01 and 97 in Candidate02; their manifest/archive hashes
remain unchanged. Original reports and evidence remain
preserved. Owner config/project/map and durable instruction bytes match the
pre-dispatch baseline, including exact AGENTS bytes after task-runtime shutdown.
No binary assets or geometry changed, so no asset registration is required.

Candidate03 manifest SHA256:
`1f4e673a78284708739f047f718bf3886401b678bb714f2434664b845ab281ad`.
DLL SHA256:
`c0c3b64f8ab48bd9c9eb6cbb4100a7a9a3a2c0ea42f240ba32fdf7c8ea66d488`.

## Delivery and closure

The sole primary reviewer closes CAI02-R1 and CAI02-R2 with no remaining technical
blocker in the affected scope. The ordinary editor is open on the retained lobby;
the mapped project DLL matches Candidate03 exactly. Official Epic MCP confirms
no PIE world and no dirty packages. No agent gameplay, simulation or firing ran.
The task runtime is stopped. Administrative closure records and the local
task-scoped commit identity are stored in
`Saved/CombatAI01/CAI-02/Controller/closure-summary.json`; MSQ-105 onward remain
undispatched and MSQ-101 remains coordination only.
The executor and reviewer use verified native Astra/max/default, fast disabled.
Their shared profiles retain those settings after closure.
The extra queued continuation was cancelled before execution because the active
executor received the controller note and performed Candidate02 in the same run.

The owner route is in the two handoffs. Actual protected-position quality,
crouch/audio presentation, hearing response, pursuit, slowdown/deception balance
and performance remain owner play judgements. The local grid, conservative static
column routes, distance/occlusion sound model and fixed-stride audio remain limits.
