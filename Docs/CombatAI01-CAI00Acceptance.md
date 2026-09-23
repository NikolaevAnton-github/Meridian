# MSQ-102 / CAI-00 controller acceptance

Date: 2026-09-23. Delivery: **Candidate01/build02**.

Accepted for owner testing under the
[task start and reasoning decision](Approvals/CombatAI01-CAI00-OwnerStart01.json).
Native build, focused source checks, pure capture-contract checks and the
[sole independent technical review](CombatAI01-CAI00Review.md) pass.
Gameplay, in-engine reset/export, motion, audio/readability and performance remain
pending owner testing. This acceptance does not dispatch MSQ-103 or later packages.

## Scope and applicable evidence

The [handoff](CombatAI01-CAI00.md) records the existing MSQ-70 interfaces and limits,
adds a 64-entry diagnostic ring and explicit trace export, separates observed input
from the proposed privileged fairness channel, and introduces encounter generations
and stable per-agent seeds. The default encounter seed is 102, with stable placement
slots. Current walking, finite search/return, weapon, physical authority and time
policy remain the baseline. Persistent hunting, running and hearing remain later work.

`Saved/CombatAI01/CAI-00/Worker/Candidate01/build02.log` records successful
Development Editor compilation/linking on UE 5.8.3 in 8.41 seconds. The executor's
24 focused rows and production-header C++ tests pass. The latter cover stable seeds,
distinct test slots, 1000 supplied events, ordered bounded eviction, owned values,
reset, stale generation rejection and reason bounds. They establish the declared
value-capture contract, not complete policy or physics replay.

The primary reviewer inspected the implementation and reused applicable passing
evidence. No blocking source finding remains. The initial source-check regex matched
a comment; the corrected check passes and the initial result is preserved. Controller
acceptance covers scope, identity, preservation and evidence applicability without
repeating the full technical review or passing tests.

## Identity and preservation

Frozen candidate manifest SHA256:
`dbfc41a5e5cf976b76263239430db5c3d3d2614a3089ea95db5761945ecec2ec`.
Controller identity verification matches all **30 entries**, including 12 delivered
files, the project DLL/module descriptor and 16 evidence files. The current DLL is
`a70a3ffa6f0ba426c7958083ded4ea5a7ae434cc413ed38c2cb9b2c2449dbcb1`.
See `Saved/CombatAI01/CAI-00/Controller/identity-acceptance.json`.

The owner configuration, project descriptor and retained map match the pre-dispatch
hashes. The MSQ-70 immutable manifest remains unchanged. No content assets or editable
asset sources were modified. Generated evidence stays under Saved, outside Git.
The local closure commit includes only verified MSQ-102 source, tools and documents;
the owner's pre-existing config/project edits are excluded.

## Execution and owner handoff

One Multica Unreal executor ran in place; one independent source reviewer owned
technical review. Both native turn contexts record **Astra/high** under the owner's
task-scoped reasoning discretion. Executor profile/native arguments explicitly used
`service_tier=default` and disabled fast mode; reviewer had no fast override. Native
turn contexts do not independently expose a response service tier. The shared Unreal
profile is restored to its prior max/default configuration and instructions. The
Multica runtime is stopped; administrative services remain available.

Executor state records ordinary editor PID 41272, the retained lobby, stopped Play
and no dirty packages. At controller handoff, after worker/runtime completion,
that process was no longer running. The controller opened an ordinary retained
session as PID **43352** and verified the final DLL's loaded module hash, retained
lobby and stopped Play. See `Controller/editor-launch-final.json`,
`editor-loaded-final.json` and `editor-state-final.json`; no candidate bytes changed.
The earlier script-mode launch exited normally and is preserved as bootstrap history.
No agent gameplay, shots, screenshots, performance sample or runtime acceptance
matrix ran. The controller owns task closure and the local commit.

In Play, `msq.EnemyCombat status` prints diagnostic state and
`msq.EnemyCombat trace` exports a bounded tail under
`Saved/CombatAI01/CAI-00/Traces/`. The short owner route is break sight, allow/inflict
a hit, inspect the trace, and press F6. Runtime expectations are a new generation,
cleared old tail, retained seed and unchanged player ammunition. `seed 102` restores
the default seed and resets the current mode. These runtime expectations remain
pending observations, not passed criteria.
