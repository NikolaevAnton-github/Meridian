# MSQ-160: DestructionScaling01 implementation sequence

Updated 2026-09-29 under [DirectBatch01](../Approvals/DestructionScaling01-DirectBatch01.json). The owner explicitly started MSQ-162..167 together with direct execution and self-review, no Multica or other agents, and requested approximate before/after frame time. These six implementations are delivered; [batch evidence and measured limitations](../DestructionScaling01Batch01.md). Owner visual/play/performance verdict remains pending. MSQ-168 is not started. The prior [ImplementationOnly02](../Approvals/DestructionScaling01-ImplementationOnly02.json) separate-chat routing is superseded only for the six named tasks.

## Current state and start point

MSQ-161 / DS-01 is stopped by the owner and removed from the execution sequence. Its unfinished fixture and evidence are archived; [closure note](../DestructionScaling01DS01.md). Do not resume its benchmarks, require its acceptance, or use its preliminary captures as a performance gate.

The production baseline Perf02 `68f911c` was rebuilt before this batch's runtime work; the stopped diagnostic DLL was not used as the baseline. The batch's final source/DLL hashes and successful build are recorded in `Saved/DestructionScaling01/build-11.json`. Preserve unrelated owner edits. Only **MSQ-168** remains prepared for a future explicit start.

## Implementation sequence

| Order | Task | Concrete implementation |
| --- | --- | --- |
| 1 | [MSQ-162 / DS-02](DestructionScaling01-DS02.md) | Stable fragment identity, reusable state snapshots and serial calculation/apply seams. |
| 2 | [MSQ-163 / DS-03](DestructionScaling01-DS03.md) | Reversible sleep/wake, persistent interaction and selected grab/release. |
| 3 | [MSQ-164 / DS-04](DestructionScaling01-DS04.md) | Resource caches, fragment pools, batched render/physics submissions. |
| 4 | [MSQ-165 / DS-05](DestructionScaling01-DS05.md) | Shared spatial support and updates restricted to changed fragments. |
| 5 | [MSQ-166 / DS-06](DestructionScaling01-DS06.md) | Coarse parallel pure calculations with validated authoritative apply. |
| 6 | [MSQ-167 / DS-07](DestructionScaling01-DS07.md) | Compact intact and shared moving/sleeping debris rendering. |
| 7 | [MSQ-168 / DS-08](DestructionScaling01-DS08.md) | Remaining physics update cleanup, integration and owner handoff. |

The owner explicitly authorized the first six rows as one direct batch. No Multica service, task execution or task-state update was performed in that batch. Multica remains the live task-state source; this local delivery does not claim its board entries were changed. MSQ-168 still requires its own explicit start. The owner evaluates performance, feel and appearance; intermediate frame-time gains were not an implementation gate.

## Shared implementation boundaries

- Deliver the listed optimizations as working code. Do not replace an implementation task with research, profiling, another plan or optional experiment recommendations.
- Keep NGD/Chaos, exact geometry/materials/shadows, protected cores/nonfracturing upper sections, hit ownership, projectile history, collision fidelity and F6. Preserve owner edits and the central demo unless an explicitly shared lifecycle change requires a scoped update.
- Gameplay fragments remain physical and interactive. Do not hide cost through deletion, collision removal, permanent freezing, VFX substitution or an invented fragment cap. Prewarm capacity is an allocation choice, not a runtime interaction limit.
- Stable identity, reset generations and state/pose revisions govern reuse and delayed work. Workers own plain input/output data; safe phases retain exact engine queries, UObject changes and solver commands. Verify APIs against installed UE 5.8 source.
- Full abilities, structural collapse and collision-driven fracture are separate scope. Keep the existing impact-damage policy until separately decided; it must not block the authorized wake/manipulation optimizations.
- Build and run short, focused checks for changed behavior. Reuse applicable evidence; investigate concrete defects rather than replaying every historical case. No required 1/4/16 stress matrix, long soak, paired PIE/standalone A/B capture, FPS target gate or per-stage performance report. Do not run such campaigns unless the owner asks again.
- Execution/review routing follows project policy and explicit owner exceptions. DirectBatch01 supplies a fresh direct/self-review waiver for MSQ-162..167; the stopped MSQ-161 waiver is not reused. Preserve owner design/play acceptance; concise representative visual checks establish technical rendering correctness only.
- Restore editor/settings, preserve evidence and commit verified task-scoped changes before handoff. State functional gaps honestly. Do not claim an FPS gain without measurements or make measurements a prerequisite for implementing the already selected optimizations.

## Navigation

Start with `DemoColumnCladding`, `DemoColumnScatter`, `LobbyFacingPool`, `NGDPropComponent` and `CombatProjectileWorld` under `Source/MeridianSquad/`. Read only the named task and needed predecessor sections. Relevant code findings are preserved in `Saved/LobbyColumnsPerf02/mass-destruction-research.md`; they are reference material, not a request to restart profiling.

Task handoffs: `Docs/DestructionScaling01DSxx.md`; integrated delivery: `Docs/DestructionScaling01Batch01.md`. Direct-batch focused evidence is at `Saved/DestructionScaling01/`. MSQ-161 archive: `Saved/DestructionScaling01/DS01/Stopped20260929/`. Future Multica description/status edits use `--no-start`.
