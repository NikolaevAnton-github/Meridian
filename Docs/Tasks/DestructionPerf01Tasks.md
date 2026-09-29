# DestructionPerf01: optimization task breakdown

2026-09-29. Status: **DP-01 and DP-02 delivered; DP-03 through DP-10 prepared**.
Authority: [owner task-creation request](../Approvals/DestructionPerf01-TaskCreation01.json).
This index decomposes the existing [optimization plan](DestructionPerf01Plan.md).
The [F7 fixture and baseline](DestructionPerf01.md) are already delivered; these
tasks address the remaining optimization work, not a new fixture implementation.

## Tasks and dependencies

| ID | Task and concrete output | Depends on | Plan section |
| --- | --- | --- | --- |
| [DP-01](DestructionPerf01/DP-01.md) | Attribute CPU/worker/GPU cost; comparable phase measurements and workload counters | Delivered F7 baseline | 1, performance contract |
| [DP-02](DestructionPerf01/DP-02.md) | Controlled isolation experiments; ranked changes supported by paired results | DP-01 | 2 |
| [DP-03](DestructionPerf01/DP-03.md) | Remove redundant collision/profile work; batch correct gameplay notifications | DP-02 | 3, event path |
| [DP-04](DestructionPerf01/DP-04.md) | Bound dust, break effects and sound; presentation policy and counters | DP-02 | 3, presentation |
| [DP-05](DestructionPerf01/DP-05.md) | Separate meaningful chunks and visual debris; representative fracture/collision derivative | DP-02 | 4, asset recipe |
| [DP-06](DestructionPerf01/DP-06.md) | Bound debris lifetime and sleep/retirement; persistent rubble and follow-up interaction | DP-05 | 4, lifecycle |
| [DP-07](DestructionPerf01/DP-07.md) | Optimize fields and release bursts if justified; measured delivery/activation decision | DP-02 | 5 |
| [DP-08](DestructionPerf01/DP-08.md) | Bound intact/active/settled scene costs; representation transitions and optional reuse | DP-06 | 6 |
| [DP-09](DestructionPerf01/DP-09.md) | Publish measured asset presets and validation; second representative asset | DP-03 through DP-08 resolved | 7 |
| [DP-10](DestructionPerf01/DP-10.md) | Verify load scaling, combat, slowdown and reset; final regression and budget report | DP-09 | 8, performance contract |

DP-01 and DP-02 are technically delivered under the owner's direct start requests.
DP-03 through DP-10 remain prepared. IDs are local task IDs; board records and
Multica services are not required. Preparing a task grants no implementation
start. Authorized work runs directly in the owner's chat.

DP-02's paired diagnostics prioritize DP-03: warm burst p95 falls from 155.16 to
46.66 ms with exact-index profile batching and deferred break replay. Every break
callback is forwarded and the same ten core props break, but early motion and
individual openings differ. This is an actionable hypothesis, not an adopted
production path; scheduling, notifications and outcome checks remain in DP-03.
DP-02 ranks presentation, fracture/contact, lifecycle, field/release and representation
as conditional or unresolved. See its report for evidence and branch-specific limits.
DP-03/04/05/07 have no mutual hard
dependency. Execute shared editor/code changes serially and keep only one heavy
build, capture, bake or render active at a time.

For a conditional technique, an evidence-backed decision to retain the current
path resolves that branch. It must state the measured cost, rejected alternatives
and remaining limit. Merely skipping a task is not a resolved dependency.

## Shared scope and preservation

- Optimize current stock NGD destruction in the retained lobby and derive a
  reusable production standard. Retired custom-column/DS tasks remain retired.
- Preserve owner configuration, map and grenade edits, source assets, approved
  appearance and all previous evidence. Use project-owned adapters/configuration
  and explicitly versioned derivatives; do not overwrite vendor source assets.
- Keep intended damage, holes, useful cover, substantial chunks and meaningful
  player/bullet collision. Reduced damage or a weaker blast is not equivalent work.
  Tiered debris options are candidates; quality and gameplay acceptance remain
  with the owner. This breakdown does not approve new architecture or art.
- Confirm live project/editor/bridge state before future editor mutations. Follow
  [execution](../AgentPolicies/Execution.md), [gameplay](../AgentPolicies/Gameplay.md)
  and applicable [art](../AgentPolicies/Art.md) policy within each task's scope.
- No new paid services; keep the whole project within 250 GB. Bound captures,
  pools, caches and derived assets. Source/config/docs go in Git; binary assets
  use LFS; generated evidence and logs stay in `Saved/`.

## Shared measurement and completion contract

- DP-01 establishes the reusable comparison harness. Record candidate commit,
  asset/config identity, engine/build, hardware, graphics, camera and actual blast.
  Retain the existing 1920x1080, 100% screen-percentage Development `-game`
  comparison. Owner changes since the old capture require a new named reference,
  not restoration over their edits or relabeling historical measurements.
- Separate cold startup from at least three warmed repetitions with clean resets;
  keep an untraced control and account for diagnostic overhead. Compare stochastic
  outcomes and distributions with equivalent intended destruction.
- Measure intact, blast to 0.5 s, 0.5-3 s, 3-10 s and settled phases. Report frame
  median/p95/p99/max, blast hitch, Game/Render/GPU and available workload/resource
  counters. Record missing counters. Never add overlapping CPU/GPU/task totals or
  treat break notifications as simultaneously active bodies.
- Each adopted change needs a causal timing improvement above repeat variability,
  focused correctness checks and an explicit effect on damage/presentation. Do
  not require every intermediate task to achieve the whole-program frame target.
- 120 FPS / 8.33 ms remains a **proposed** target. Proposed warm acceptance is
  phase p95 <= 8.33 ms with no repeated frames > 16.67 ms; report every excursion,
  p99/max and assess the blast separately. DP-10 must record the agreed target
  hardware/scenes before claiming the production target is met. The current
  9800X3D/RTX 5090 is only the existing measurement machine.
- Numerical body/contact/release/effect/voice budgets follow attribution and load
  sweeps; do not invent universal limits. Update DP-09 presets if DP-10 disproves
  their provisional limits. Verify a packaged Development build before production
  performance claims; source/build passes do not establish owner acceptance.
- Test changed timing-sensitive behavior at normal speed and slowdown: world,
  rifle cadence and bullets 0.25; hero movement 0.65. Keep real time and simulation
  time distinct. DP-10 owns the full integrated matrix; earlier tasks use focused
  checks. F7 currently rejects slowdown arming; document a separate controlled
  slowdown workload without silently changing that delivered control contract.
- Record implementation/decision, dependencies, checks, limits and owner-acceptance
  status in the child task. Raw evidence belongs in fresh versioned paths under
  `Saved/DestructionPerf01/DP-xx/`; never overwrite baseline/rejected evidence.
  Commit checked task-scoped work locally with its ID. Final testing and visual/
  gameplay acceptance belong to the owner; no extra reviewer is mandated.

## Planning delivery

This package creates the ten child documents, records the exact owner request and
updates the plan/current-state navigation. Documentation checks and preservation
evidence are under `Saved/DestructionPerf01/TaskBreakdown01/`. It performs no
optimization, editor mutation, performance run or board operation.
