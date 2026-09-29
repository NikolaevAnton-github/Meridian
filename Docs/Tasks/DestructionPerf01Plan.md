# DestructionPerf01 — Scalable NGD Destruction Plan

Status: proposed future work; no optimization described here has been implemented or accepted. The current task provides the fixed central blast fixture and baseline measurements. Final testing and acceptance belong to the owner.

## Scope and design contract

Optimize the current NGD stock assets in the opening lobby, then establish a repeatable production standard for future destructible environments. This plan does not restore the retired custom-column implementation. Preserve owner assets, source content, approved appearance, and exact baseline evidence; implement candidates through project-owned configurations/adapters and explicitly versioned asset derivatives.

The desired result is rich destruction with bounded runtime cost. Holes, changed cover, substantial falling chunks, and collision that matters to movement and bullets must remain real gameplay state. Dust and tiny debris may supply visual detail without every visible chip becoming a long-lived rigid body. Do not accept a faster result that merely destroys fewer intended objects or removes useful cover immediately.

The [baseline report](DestructionPerf01.md) establishes a CPU-side sustained limit, substantial task waits, and hundreds of thousands of repeated collision callbacks/profile updates. Disabling Niagara activation leaves the warmed slowdown almost unchanged. The current trace does not fully separate physics solver/contact work from generic task scopes; that narrower attribution remains open. Approximately 3,953 break notifications, mainly from ten central pillars with occasional secondary damage, are event counts, not simultaneously active bodies.

## Proposed performance contract

- Target: 120 FPS, corresponding to 8.33 ms per frame. This is a proposed target, not an achieved result or an agreed minimum-hardware specification.
- Proposed warm-run acceptance: frame-time p95 at or below 8.33 ms in each measured destruction phase, with no repeated frames above 16.67 ms. Report every excursion, maximum, and p99 so a percentile cannot hide an explosion hitch. Assess the blast frame separately.
- The current Ryzen 7 9800X3D / GeForce RTX 5090 system is the measurement machine; passing there does not establish a shipping hardware target. Choose a representative minimum/target PC before locking production limits.
- Retain the current comparison configuration: standalone Development Editor `-game`, 1920x1080, 100% screen percentage, recorded quality settings and fixed camera. Also verify an appropriate packaged Development build before making shipping claims.
- Derive the destruction allowance from the measured intact-scene budget. Allocate CPU, GPU, memory, and burst allowances independently; overlapping CPU/GPU timings must not be added as though they were serial.
- Set numerical body, contact, VFX, voice, and release quotas only after attribution and load sweeps. No unmeasured universal fragment limit is promised.

## 1. Attribute the cost before changing behavior

Capture the fixed blast with Unreal Insights CPU/frame/task tracing and GPU timing as supported by the installed engine. Use explicit start, blast, phase, and completion bookmarks. Capture narrowly scoped supplementary Chaos/Niagara/audio diagnostics when needed; measure instrumentation overhead separately. Keep an untraced reference run alongside the trace.

Resolve the game-thread and worker contributions: field evaluation, cluster breaking/particle creation, collision generation and solver work, physics synchronization/waits, break/collision dispatch, Blueprint execution, Niagara activation/ticking, audio work, render updates, and garbage collection. A long game-thread interval can include waiting for another task; identify the actual dependency before assigning blame.

Record by phase: intact baseline, blast to 0.5 s, 0.5–3 s, 3–10 s, and settled state. Export frame median/p95/p99/max, Game/Render/GPU times, relevant task totals, new and active/sleeping rigid bodies, contacts, break/collision events, Niagara instances, audio voices, and allocation peaks where available. Record unavailable counters explicitly. Identify actors by unique actor path plus adapter ID because copied props can share `ObjectId`.

Use clean resets and a fixed camera/position, blast radius/strength, and scene. Separate cold-start cost from at least three warmed repetitions. Log real elapsed time and simulation time independently. The destruction path is stochastic; compare distributions and the resulting damage rather than claiming bit-identical fragments.

Deliverable: a short cost-attribution report with trace paths, the dominant call stacks/tasks, phase totals, observed workload counts, and a ranked explanation of the slowdown. Validation: the traced workload reproduces the untraced symptom, and the reported cause accounts for a material portion of the measured frame cost.

## 2. Run controlled isolation experiments

Use reversible runtime switches or versioned test candidates. Change one factor per comparison and restore the original baseline between experiments.

| Experiment | Keep equivalent | What the result can establish |
| --- | --- | --- |
| Disable break VFX only | Damage, forces, fracture, audio | Effect-instance, particle, and rendering contribution |
| Disable break/collision sound only | Damage, fracture, VFX | Audio and associated callback contribution |
| Bypass optional material switching | Geometry, collision, other presentation | Material-update contribution |
| Hide fragment rendering diagnostically | Physics and damage | Rendering contribution while simulation continues |
| Candidate small-debris collision policy | Major fractures and large chunks | Contact/solver contribution |
| Reduce tiny rigid fragments in a derivative | Major openings, collapse shape, apparent debris density | Body-release and sustained-simulation scaling |
| Simplify field commands diagnostically | Intended affected area and fracture outcome | Field evaluation versus motion/contact amplification |

Hiding rendering and removing velocity/torque are diagnostic variants, not acceptable final visuals. Check damaged actors, major openings, large-chunk trajectories, and effect visibility alongside timing. Do not count a smaller or weaker explosion as an optimization of the same workload.

Deliverable: paired timing/effect tables and a prioritized change list. Validation: repeated improvements exceed run-to-run variability and have an explained causal link. Stop low-value experiments once the evidence identifies the limiting work.

## 3. Bound event, VFX, and audio work

The current vendor break graph invokes material switching, breaking effects, breaking sound, and per-particle collision-profile changes for each break. Collision callbacks also perform sound/profile/sleep-related work. The warm trace records 638,381 collision callbacks and 509,731 per-particle profile updates in 15 seconds. Start with redundant updates and collision-notification fanout, verifying their first-five-second cost; reserve additional VFX tuning for measured benefit because disabling activation did not resolve the warm CPU limit.

Aggregate presentation events by affected area/material and a short time window. Select representative energetic or large breaks for sound and dust; give nearby important damage priority. Use explicit per-frame and concurrent effect/voice limits with measurable dropped/merged-event counters. Apply audio concurrency, distance and energy thresholds. Avoid repeated identical material/profile updates when the state is already correct.

Pool frequently reused effect components where beneficial, prewarm bounded pools outside the measured event, and test a shared Niagara system/data-channel route when instance creation dominates. Assign Effect Types and distance/significance budgets. Aggregate the adapter's collision-change publication once per affected actor/frame where consumers permit it, while retaining the complete changed bounds and correct revision/reset semantics.

Deliverable: project-owned presentation policy and counters, with before/after evidence for each adopted change. Validation: the same holes and major fracture events remain, dust/sound still communicate impact, gameplay collision updates remain correct, and presentation bursts no longer grow unchecked with fragment count. Check reset during active effects for stale callbacks and leaked instances.

## 4. Separate gameplay chunks from visual debris

Define asset tiers by gameplay role and observed cost, not only polygon count:

- Structural/large chunks: preserve meaningful shape, blocking, bullet interaction, and required damage behavior.
- Medium debris: simplified collision and bounded active lifetime; evaluate one-way interaction when mutual force transfer is unnecessary.
- Tiny chips/dust: visual fragments with limited lifetime and rendering cost; avoid independent gameplay collision unless a specific mechanic needs it.

Create candidate fracture recipes with enough hierarchy to expose local damage without releasing every leaf at once. Merge unhelpful microscopic pieces and simplify collision hulls while retaining visible silhouette and important contact shapes. Measure physical bodies, contacts, and released bodies per frame for each recipe; triangle count alone is insufficient.

Define sleep and retirement per tier. Detect settled/slow pieces, then remove their active cost or transition them into a cheap persistent rubble representation where the scene needs visible remains. Preserve relevant blocking through a suitable simple proxy. Measure wakeup behavior under a second blast and avoid synchronized mass cleanup or abrupt visible disappearance.

Deliverable: one representative pillar family with documented fracture/collision/lifetime settings and a bounded debris lifecycle. Validation: identical blast placement still opens the intended space; bullets, player traversal and cover agree with the visible result; secondary impacts behave acceptably; no rising active-body/contact count persists across repeated blasts.

## 5. Change fields and activation only where the profile justifies it

Inspect the current field's strain, radial velocity, directional velocity, torque, falloff, affected-object filter, and command lifetime. Saved exports show several transient field commands per blast; verify the live asset before basing a change on those exports.

If field cost is material, compare a simpler bounded field or targeted strain/velocity application against the original damage envelope. Prevent duplicate delivery to the same target, and avoid repeatedly waking already retired cosmetic fragments. Cache immutable configuration and expensive lookup results when a trace demonstrates recurring setup work.

If particle-release bursts dominate, evaluate per-frame release/cluster throttling in the installed engine and preserve a convincing immediate impact. Measure added break latency explicitly. Never hide a hitch by stretching destruction into an unacceptable delayed reaction or by globally reducing physics quality without evidence.

Deliverable: the smallest measured improvement to blast delivery/activation, or an explicit decision to retain the current field path. Validation: affected props, radius, local destruction, significant impulses, reset cancellation, and follow-up shots remain correct; trace evidence shows the intended work was reduced.

## 6. Bound the cost of intact and settled environments

Use instanced/root mesh proxies for repeated intact assets when they reduce measured scene cost. Keep asset activation local to relevant damage. Consider pooled runtime representations only when construction/allocation cost warrants them; a returned object must fully reset physics, collision, materials, IDs, delegates, latent work, and effect ownership. Pool size and memory use must be capped.

Choose persistent settled-rubble representations with measured rendering and collision costs. Evaluate Nanite, material slots, shadow behavior and dust overdraw where Render/GPU traces identify a limit. Each representation transition must preserve the visible damage and any required gameplay state.

Deliverable: bounded intact/active/settled representations and their transition contract. Validation: no visible pop that harms the scene, no collision disagreement, no stale damage after reuse, and stable memory/actor/component counts across repeated cycles. Include project footprint when evaluating new derived assets and caches.

## 7. Turn the result into an authoring standard

Publish a destructible asset template with measured limits for hierarchy, meaningful rigid pieces, collision complexity, simultaneous release, presentation events, material slots, and retirement behavior. Provide large/medium/small debris presets and a clear rule for retaining gameplay-important rubble. Limits should name the hardware, engine/build, quality settings and stress scenario from which they were derived.

Add focused asset validation for missing lifecycle settings, excessive measured/configured complexity, unbounded effects, duplicate adapter IDs, unsupported reset behavior, and missing source/derivative provenance. Keep inexpensive checks in normal content validation; use representative runtime tests for costs that static metadata cannot predict.

Deliverable: asset presets, authoring checklist, reusable fixed-blast scenario, and a readable regression summary. Validation: a second representative destructible material/shape can follow the template and pass its own visual/gameplay checks without bespoke performance fixes.

## 8. Prove scale under actual gameplay

Run controlled 1/2/4/8 affected-prop cases and retain the existing ten-pillar fixture as an additional reference. Include close and distant views, successive blasts into fresh and already scattered debris, multiple active destruction areas, sustained combat with AI/shooting, and late-session memory/cleanup behavior. Warm-run comparisons use identical graphics and workload definitions.

Test normal time and the project's slowdown configuration: world scale 0.25 with player scale 0.65. Record real-time frame cost separately from simulation-time progress; ensure lifetimes, event aggregation, throttling, and reset work correctly under both. Slowdown must not artificially pass a real-time frame budget by changing the amount of work observed in the comparison window.

Deliverable: regression matrix with performance, visual damage, gameplay collision, and reset results; raw evidence remains in `Saved/`. Validation: the proposed frame criteria hold on the chosen target machine in the agreed representative scenes, resource counts stabilize, and the owner accepts the destruction quality. A current high-end-machine pass alone does not close the production performance target.

## Sources and implementation anchors

- `Source/MeridianSquad/PrototypeGrenadeComponent.cpp`: vendor grenade/field integration and blast scaling; `PrototypeGrenadeComponent.h`: current blast-radius configuration.
- `Source/MeridianSquad/NGDPropComponent.cpp`: per-break publication, material preservation, reset and owned-field cancellation. Preserve these behavioral guarantees while optimizing.
- `Saved/NextGenDestructionIntegration01/NGD-01/Candidate01/vendor-breakable.dsl`, `BP_DestructionField-EventGraph.dsl`, and `BP_BreakableObject-SetAllDestructibleVars.dsl`: historical vendor exports; confirm live graph/settings before edits.
- Epic's [Chaos Destruction Optimization](https://dev.epicgames.com/documentation/unreal-engine/chaos-destruction-optimization?application_version=5.6) documents root proxies, removal on sleep/break, one-way interaction, release throttling, tiny-fragment substitution, and simpler strain application. Check exact feature/API availability in the installed engine.
- Epic's [Niagara Scalability and Best Practices](https://dev.epicgames.com/documentation/unreal-engine/scalability-and-best-practices-for-niagara) explains system-instance overhead, aggregation, pooling and Effect Types. Pooling reduces allocation cost but does not eliminate per-instance execution cost.
- Epic's [Performance Budgeting Using Effect Types](https://dev.epicgames.com/documentation/unreal-engine/performance-budgeting-using-effect-types-in-niagara-for-unreal-engine) describes distance and instance-count budget controls. These are implementation options, not evidence that the present slowdown is caused by Niagara.
