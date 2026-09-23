# MSQ-103 / CAI-01 controller acceptance

Date: 2026-09-23. **Candidate01/build05 is accepted for owner testing** under the
[owner start and reasoning decision](Approvals/CombatAI01-CAI01-OwnerStart01.json).
Native build, 35 focused source/pure checks and the sole independent
[technical review](CombatAI01-CAI01Review.md) pass. No finding remains open.
S01/S06/S07/S10 gameplay, visible running/braking, motion, combat feel and performance
remain **PENDING OWNER**. No successor is dispatched by this acceptance.

## Scope and applicable evidence

The [executor handoff](CombatAI01-CAI01.md) delivers persistent encounter alert,
fresh sight during destination backoff, nine bounded local search proposals,
explicit walk/run selection and action identities/cancellation across movement,
aim, bursts, reload, physics and reset. Living recovery retains observed evidence
and replans from actual feet. Stationary launch gates, GASP/Mover authority, finite
bullets, weapon tuning and the existing slowdown policy remain preserved.

`Worker/Candidate01/build05.log` records the final successful Development Editor
build on UE 5.8.3: four actions, 4.65 seconds. The 35 focused checks include shared
production-header assertions for 10,000 bounded search/failure transitions, stale
tokens, same-generation reset, one-shot reload completion and gait selection.
The imported Blueprint audit maps commanded walking/running to 165/375 cm/s
defaults. Those are source/default facts, not measured motion.

The independent reviewer inspected affected code and callers, verified the final
build05 correction and reused applicable evidence. Controller acceptance checks
scope, candidate identity, preservation and the stated verification boundary;
it does not repeat technical review or passing tests. Earlier build/test failures
and their bounded corrections remain preserved in the worker evidence. The frozen
handoff records review as pending at executor delivery; this acceptance and the
separate review supply the later verdict without rewriting frozen files.

## Identity and preservation

All paths below are relative to `Saved/CombatAI01/CAI-01/`.
Frozen `Worker/Candidate01/candidate-manifest.json` SHA256:
`8895cac07915989168fa7e52573a31e3589d6ba3a4b25ef9c60b9e7ef63e3272`.
Controller verification matches all **79 entries**. Final project DLL SHA256:
`33557055caf7012005c525eef0482ed0cd22e82e99c16e67e8502bafe65455ae`.
See `Controller/identity-acceptance.json`.

Owner config/project edits and retained lobby match pre-dispatch hashes. Inspected
GASP assets match their prerequisite LFS identities. The graph inspection's temporary
in-memory dirty state was discarded after confirming its origin and stopped Play;
no asset was saved. MSQ-70 and MSQ-102 historical manifests remain unchanged.
No content/source asset edits, new paid services or duplicate project were introduced.

## Execution and closure

One Multica executor and one primary independent reviewer used native-verified
Astra/high under the task-scoped discretion. Executor native arguments explicitly
set default service tier and disable fast mode; the reviewer had no fast override.
Native turn contexts do not independently expose effective response service tier.
The shared executor profile is restored to max/default and its prior instructions.
Task runtime is stopped; administrative services remain available. AGENTS.md is
restored after Multica's temporary execution context.

The worker editor session ended with worker completion. The controller reopened an
ordinary retained-lobby session after stopping the task runtime; final launch,
loaded-module and project/map/PIE/dirty evidence are stored under `Controller/`.
No agent Play or firing probe ran. The local closure commit includes only verified
MSQ-103 code, scripts and documents; owner config/project edits are excluded.

## Owner route and limits

In Play, provoke pursuit across clear space, hide behind cover for **60 world
seconds**, relocate, inflict a nonlethal hit and observe search after recovery.
Use F6 during movement/reload. `msq.EnemyCombat status` reports alert, action,
request IDs and gait; `trace` exports the bounded tail to `CAI-01/Traces/`.

Navigation remains one floor layer within the existing 28 m home radius. Local
search does not establish room coverage or a flank. Hearing and incoming-fire
awareness belong to the next eligible package, **MSQ-104 / CAI-02**, which remains
undispatched. Owner judgement of pursuit usefulness and motion is still required.
