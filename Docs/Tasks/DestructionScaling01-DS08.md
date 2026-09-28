# MSQ-168 / DS-08: remaining physics costs and final load acceptance

Multica: MSQ-168 (`01a0e9bc-bdf9-784c-8920-01f1a8032378`), parent MSQ-160, stage 8. Prepared, unassigned, no execution authorized. Dependency: accepted DS-01 through DS-07 handoffs. Read [shared acceptance](DestructionScaling01.md); owner start authorizes this final task only.

## Outcome

Attribute the remaining physics/contact costs, apply only justified fidelity-preserving tuning and establish a reproducible supported load envelope for repeated interactive destruction.

## Work

- Re-run only relevant changed workload transitions with the final representation. Inspect awake/sleeping bodies, collision shapes, contact/constraint pairs, solver step, queries, callbacks, GT/RT/GPU, task waits, memory and transition hitches.
- Tune measured redundant callbacks, body/shape setup or contact scheduling where correctness is preserved. Investigate CCD selection only with high-speed thin-piece/stack evidence. Ordinary pooling does not remove solver/contact cost.
- Collision simplification, interaction filtering, lower physics rates, one-way debris, removal or visual-only replacements change the contract and require a separate explicit design decision. Do not silently adopt them to hit a target.
- Validate 1/4/16-column bursts, repeated explosions after rest, selected-piece grab/throw, mixed-owner support loss, sustained fire and F6 in matched PIE and an appropriate standalone run. If collision-driven damage was separately accepted, include the resulting chain reactions; otherwise state that coverage boundary.
- Compare against DS-01 and each applicable accepted predecessor. Preserve original captures and clearly state any hardware/configuration difference. Use representative sustained runs long enough to expose pool growth/cleanup and memory accumulation.

## Acceptance and handoff

Publish the supported workload table, frame mean/p95/p99 and largest transition hitches, finite resource use, functional/visual results and remaining bottlenecks. 120 FPS is an 8.333 ms whole-frame target, not a guarantee for unlimited bodies. If a target case misses budget, report the measured gap and concrete remaining decision; do not relabel a weaker workload as passing.

Deliver `Docs/DestructionScaling01DS08.md`, final reproducible fixtures/evidence, primary independent technical review and relevant independent visual evidence. Keep owner play/design acceptance distinct. Commit verified scoped changes and update the program with final results; start no other work.

New chat opener: "Start MSQ-168. Read Docs/Tasks/DestructionScaling01-DS08.md and the indicated program/predecessor sections. Execute only this task; do not start successors."
