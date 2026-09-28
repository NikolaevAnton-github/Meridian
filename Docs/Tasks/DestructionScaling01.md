# MSQ-160: DestructionScaling01

Prepared only. Authority: [Preparation01](../Approvals/DestructionScaling01-Preparation01.json). All issues must remain unassigned with zero runs until the owner starts a named task in a new chat. The program is an index, not an instruction to execute every stage. Multica is the live status source.

## Baseline and objective

Start from verified Perf02 commit `68f911c`, [handoff](../LobbyColumnsPerf02.md) and [primary review](../LobbyColumnsPerf02Review.md). The paired PIE mean frame times are 7.668 ms intact, 8.572 ms firing and 8.166 ms settled. These rifle captures do not establish mass-destruction capacity; post-F6 timing excludes the reset hitch. The 120 FPS whole-frame budget is 8.333 ms.

Keep NGD/Chaos. Scale repeated destruction, pushing, grabbing/throwing and mixed-owner piles while preserving the appearance and physical interaction of gameplay fragments. Existing code uses individual loose-piece actors, NeverSleep concrete, kinematic retention, expiry and owner-local support. Those are measured starting limitations, not requirements for the new lifecycle. The 80-piece retention limit is not a cap on all active bodies. VSM and Geometry Collection Nanite are already enabled.

## Execution order

MSQ-160 indexes MSQ-161 through MSQ-168. Keep the parent unassigned. Start one named child at a time, using the accepted predecessor commit and its evidence. Each task contains its own new-chat entry point and relevant reads; do not recursively load every linked document.

| Stage | Task | Outcome |
| --- | --- | --- |
| DS-01 / MSQ-161 | [Load benchmark](DestructionScaling01-DS01.md) | Attribute 1/4/16-column bursts and repeated interaction; define a measurable budget. |
| DS-02 / MSQ-162 | [Fragment identity](DestructionScaling01-DS02.md) | Stable identities and a serial snapshot/apply reference. |
| DS-03 / MSQ-163 | [Reversible lifecycle](DestructionScaling01-DS03.md) | Sleep/hold/wake on a one-column pilot, then lobby validation. |
| DS-04 / MSQ-164 | [Reuse and batch updates](DestructionScaling01-DS04.md) | Reduce spawn/registration/GC spikes and repeated render/physics submissions. |
| DS-05 / MSQ-165 | [Local support updates](DestructionScaling01-DS05.md) | Shared support across owners; work follows changed nearby fragments. |
| DS-06 / MSQ-166 | [Parallel calculation](DestructionScaling01-DS06.md) | Snapshot, coarse worker jobs and validated apply, with measured task/wait costs. |
| DS-07 / MSQ-167 | [Render representation](DestructionScaling01-DS07.md) | Fewer intact render sections and a measured moving-debris rendering pilot. |
| DS-08 / MSQ-168 | [Physics scaling and acceptance](DestructionScaling01-DS08.md) | Tune remaining measured costs and establish the supported interaction/load envelope. |

## Shared acceptance and boundaries

- Preserve exact geometry/materials/shadows, first-hit routing, projectile history, support correctness and F6. Retain independent visual and owner play/design gates. Do not silently substitute VFX, delete interactive debris, disable its collisions or freeze piles to meet a timing target.
- Keep existing protected core and nonfracturing upper sections. Full structural collapse, new art and production grenade/telekinesis/push controls are separate scopes. Test adapters exercise their required interaction paths. Whether impact from a thrown fragment causes additional fracture remains an explicit gameplay decision; preparation does not silently enable collision damage.
- Use ordinary dynamic sleep with explicit waking where appropriate. A held object may be temporarily kinematic only with a validated return to simulation. Apply a finite measured scene workload; test counts are not hidden runtime caps.
- Reuse the existing CSV integrity rules and runtime validators. Compare identical settings, views and input schedules, separately from screenshots. Record mean/p95/p99 and transition hitches, active/sleeping bodies, shapes, contacts, queries, jobs/waits, spawn/GC and memory. State non-deterministic physics and editor overhead; add an appropriate standalone game comparison.
- One production worker/editor writer and one heavy operation at a time. Each substantive candidate gets one primary independent technical review; inspect visual evidence when representation changes. At dispatch, prepare a fresh bounded brief/checkpoint against the then-current commit and verify max reasoning/standard speed. Prepared documents are not executable native briefs.
- Accept measured improvements with functional equivalence; retain rejected experiments and do not manufacture a performance win. Controller commits the accepted task alone, updates its handoff, and stops before its successor.

## Navigation

Initial code: `DemoColumnCladding`, `DemoColumnScatter`, `LobbyFacingPool`, `NGDPropComponent` and `CombatProjectileWorld` under `Source/MeridianSquad/`. Exact read-only findings: `Saved/LobbyColumnsPerf02/mass-destruction-research.md` (candidate03 source equals Build05). Logs/evidence belong under `Saved/DestructionScaling01/DSxx/`; reusable tools under `Scripts/DestructionScaling01/`. Keep owner changes and the central demo intact unless a task explicitly expands the tested shared lifecycle.

Official references, read only when relevant: [Tasks System](https://dev.epicgames.com/documentation/en-us/unreal-engine/tasks-systems-in-unreal-engine), [Chaos Fields](https://dev.epicgames.com/documentation/unreal-engine/chaos-fields-user-guide-in-unreal-engine), [Chaos optimization](https://dev.epicgames.com/documentation/unreal-engine/chaos-destruction-optimization?application_version=5.6). Validate APIs against the installed UE 5.8 source; the optimization guide is version 5.6.

Preparation is administrative only: controller checks issue bindings, dependency order, links, context budgets and zero execution. Implementation review requirements apply when an individual task is started.
