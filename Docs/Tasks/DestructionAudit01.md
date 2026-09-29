# MSQ-169: Destruction technical audit and optimization plan

Date: 2026-09-29. Scope: [owner request](../Approvals/DestructionAudit01-OwnerScope01.json).
Candidate: current dirty source and DLL matching all 80 entries in
`Saved/DestructionScaling01/build-31.json`; parent commit `f0e95a2`.
This audits the implemented system and existing measurements. It does not claim a
new runtime performance acceptance, complete ability support, or an optimized delivery.

## Decision

Do not continue stacking small sleep/render tweaks or adopt the rejected native
sleep-buffer filter. First remove provable repeated work in release, identity,
support and projectile paths; then restrict project bookkeeping to changed state.
If native GC synchronization still dominates, test a different granularity of
physics ownership. Keep persistent, individually interactive rubble as the main
design contract. Appearance, query geometry, shadows, collision and wake behavior
are acceptance constraints, not hidden sources of speedup.

The earlier regression is real. The system began retaining more interactive bodies
and support/query state while render batching only removed one part of the cost.
Native sleeping does not make all project and GC synchronization work disappear.
The latest small capture is faster, but its changed combat fixture and unmatched
baseline prevent a defensible net optimization claim for the current candidate.
There is no measured capacity for mass destruction yet.

## Evidence and limits

The audit covers the current cladding, scattering, fragment lifecycle, shared
renderer, projectile integration, NGD adapter, authored data/provenance, relevant
installed UE 5.8 source and 51 existing CSV files. Exact findings and offline
reanalysis are in `Saved/DestructionAudit01/{code-audit,asset-audit,measurement-audit}.md`.
`controller-identity.json` binds current source/DLL; `measurement-audit-data.json`
and `measurement-metrics.csv` retain the calculations. Historical evidence stays intact.
The latest capture follows build-31 by preserved file time; it has no embedded
source/DLL manifest. Current disk hashes do not retroactively prove which binary
was loaded for that historical capture. The original before-02/after-02 delivery
has a separate preserved identity verification.

Read-only checks found UE 5.8 running this project and a healthy Epic MCP with PIE
active. The MCP current-level string was empty, so it does not prove the identity
of the active gameplay world. No editor mutation, build, source switch or new
benchmark was performed. No claim is made about current on-screen FPS.

The current host is Ryzen 7 9800X3D / RTX 5090 / approximately 32 GiB RAM. This is
not a minimum specification or proof of every historical capture's hardware.
Latest recorded viewport is 1280 x 722, Epic quality, VSync/caps disabled in the
capture. Effective internal rendering resolution is not established by the zero
screen-percentage/default CVar readings. Packaged-game cost, mass fracture spikes,
dense multi-column piles, long-session memory and actual abilities remain uncovered.

### What the numbers establish

Frame-time medians, milliseconds; different rows are not one continuous A/B series:

| Capture | Intact | Post-fire moving/settling | Settled | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Original `before-02` | 7.61 | 8.20 | 7.72 | Earlier lifecycle, fewer retained ceramic pieces |
| Rejected `after-02` | 7.04 | 11.36 | 8.92 | Moving +38.6%, settled +15.5%; not a net win |
| Current `controlled-after-04` | 5.83 | 6.27 | 6.33 | No matching controlled-before capture exists |

Current p95 is 8.50 / 8.61 / 8.77 ms and p99 is 9.98 / 9.67 / 9.67 ms in those
windows. Thus even this short current sample does not establish consistent 120 FPS
(8.33 ms/frame), despite its faster medians. Latest settled sample has 88 managed
records, including 81 ceramic pieces, zero reported awake records and no sampled
record below Z=-100 cm. These are sample observations, not a long-term safety proof.

All 18 shots damage only one of 16 columns. `representative.py:31-41` records
the moving window at 34-40 seconds, after the last shot at about 30.95 seconds;
first-hit, firing and fracture bursts are absent from those CSV windows. Latest
controlled captures remove `GASPALSLocomotionFixture_0`, whereas `before-02` has no
matching control record. Random fracture/contact populations also differ. Identical
press counts do not imply identical physics work. Do not label these numbers a
mass-destruction or same-population comparison. Near-zero legacy RenderThreadTime
CSV values are not credible rendering-cost evidence. Overlapping scopes cannot be summed.
Later captures also add 10-11 geometry-history barriers and approximately
0.075-0.124 seconds of dropped projectile time between snapshots, despite all 18
shots being emitted. Attribute these transitions before declaring firing semantics
unaffected. The captures use normal time, not the required slowdown behavior.

`controlled-after-01` is additionally contaminated by an overlapping `buffer-03`
hold/move test on the same managed concrete handle. The held body's identity and
poses link the two logs; it is far below the floor in the later settled sample.
Do not use `compare-before-02-controlled-after-01.json` as performance acceptance.
This finding is specific to that run, not evidence of contamination in every later run.

### Current correction status

`Docs/DestructionScaling01PerformanceCorrection01.md` is stale about its sleep
buffer adapter. `rejected-buffer-adapter.json` records its removal after a sleeping
GC did not reliably wake from an incoming physical cube. Builds 19/20/23/25/26/27/28/29
using that adapter cannot establish acceptance of the current path. Current source
keeps complete native buffering. The revised native contact-wake harness can be
reused, but the existing evidence has no fully passing final buffer result and no
complete current-candidate correction verification. Build success and old passing
transitions do not close that gap. This audit supersedes the stale descriptive
status; it does not rewrite the rejected evidence or accept current code.

## Technical findings

Source references below are relative to `Source/MeridianSquad/`. Structural costs
are proven by source; their share of the latest frame is unmeasured unless stated.
Let R be persistent fragment records, P particles in a GC, A awake/changed records,
and K newly released leaves. Density matters independently of total fragment count.

| Priority | Finding and consequence | Concrete action |
| --- | --- | --- |
| P0 | New-leaf collision profile setup can reload profiles for the entire collection: `DestructionFragmentWorld.cpp:138`, `DemoColumnScatter.cpp:183-188`; UE `GeometryCollectionComponent.cpp:4823-4828,4950-4997`. Releasing K leaves incurs repeated O(K x P) work. Direct release also repeats filter/CCD setup. | Gather newly released bones by GC and submit one profile/filter/CCD batch at the safe phase, including indirectly released neighbours. Configure once per state transition. |
| P0 | Every persistent record is still visited twice per manager tick, including sleepers (`DestructionFragmentWorld.cpp:558-735`). Dirty support flags are written but not used to gate the current periodic query. | Active/changed/due queues, explicit wake and state transitions, component-level support sentinels. Retain native incoming-contact wake and an external-change fallback. |
| P0 | Dense support searches can approach all-pairs exact sweeps; GC hit selection scans all records (`DestructionFragmentWorld.cpp:385-392,469-509`). Periodic checks can align after a sleep wave. | GC/bone-to-handle and reverse-support indices, cheap candidate rejection, reusable scratch, revision-valid contact edges, distributed deadline queue. Exact hull checks remain the final test. |
| P1 | Global support invalidation and several damaged-column scans persist (`NGDPropComponent.cpp:178,189,211`; `DemoColumnCladding.cpp:637-739,964-1043`). Shard spawning cleans the growing debris array repeatedly. | Reverse dependents, one cleanup per spawn batch, carrier-to-tile lookup, pending first-ground-impact set, external-break deltas with a sentinel. |
| P1 | Tiny exact pose changes remove/reinsert spatial memberships even within the same cells (`DestructionFragmentWorld.cpp:453-466,608,673`). | Keep exact authoritative pose/bounds; update cell membership only when its occupied range changes. Separate pose, spatial and render revisions. |
| P1 | Actor registry still scans owned components at both projectile history boundaries (`CombatProjectileWorld.cpp:299-378,555,622`). BuildQuery still scans every world actor per active segment/launch (`:144-154,639`), including growth caused by rubble pools. | Lifecycle-maintained exclusion list and indexed managed blockers; preserve both history boundaries and detection of arbitrary component/response/ownership changes. Never replace these with an unchecked timer. |
| P1 | Loose bodies are actors/components; mesh/material-keyed pools retain peak allocations and repeated configuration (`DestructionFragmentWorld.cpp:148-233,329-355`). | Canonical acquire/configure path, measured prewarm outside impact, retire only surplus unused pooled bodies after quarantine. Never evict live debris. |
| P1 | Current tasks parallelize lowest-hull-point arithmetic and immediately wait; UObject/query/render work remains on the game thread (`DestructionFragmentWorld.cpp:651-680`). | Remove repeated work first, measure task/wait cost, use serial small-workload path. More threads are not a substitute for lowering work. |
| P2 | UE's dirty particle view includes sleeping GC leaves; selected proxies iterate their effective particle set and emit non-disabled leaf state. This is a native CPU floor distinct from project bookkeeping. | Keep native correctness. If measured dominant after P0/P1, prototype smaller GC ownership units or a different released-body backend. Do not resurrect view filtering. |

Correctness companion to P0: the runtime floor proxy copies a named source mesh's
collision/material once and makes that source query-only (`DestructionFragmentWorld.cpp:75-97`).
Its solid bounds box is specific to the known rectangular tiled slab. Later
source-only collision disable, mesh or material replacement is not propagated to
the proxy; support sentinels observe the proxy instead. Verify this uncovered
transition, bind geometry equivalence to the accepted source fingerprint, and
propagate changes or limit the optimization to an explicitly immutable source.
Actor-wide collision/movement is a different path. Do not generalize bounds-box
replacement to arbitrary floors or simplify required collision without approval.

Current incremental ISM updates are worth retaining. Compact facing reduces visible
sections to 36 per column while retaining the 11,576 authored facing triangles.
It does not remove the 768 original query tile instances per column (12,288 across
16). Original per-column authored concrete has 528 leaves, 81 anchored core leaves,
447 noncore leaves and 2,414,366 authored faces. These are asset topology counts,
not simultaneous awake bodies or per-frame GPU triangle counts. Nanite does not
remove per-body collision, query, synchronization or lifecycle cost.

The lobby authoring uses a flat root-to-leaf concrete hierarchy. NGD here is imported
content and a project adapter over Chaos, not an independent scalable physics solver.
Four static upper sections, protected cores and disabled collision-driven damage
are current scope. Full structural collapse and chain fracture are separate behavior
designs. Do not switch them on as an optimization experiment.

## Implementation order

These are proposed stages, not dispatched successors. The prior MSQ-161 stop and
MSQ-168 separate-start boundary remain intact. Future implementation follows one
Multica production worker and one fresh primary technical reviewer per substantive
candidate; owner visual/play acceptance remains separate.

### 0. Establish the candidate and measure the missing work

Keep build-31's exact dirty bytes as the audit baseline; do not restore HEAD or old
worker files over owner edits. Reconcile the final native wake/collision/floor
transitions with current source before calling the correction complete. Reuse the
existing probe and scopes, extending the recording to include first shot, all
firing/fracture bursts and F6's actual reset hitch. Do not rebuild the stopped DS-01
fixture or make a long benchmark campaign a prerequisite for contained fixes.

Use two distinct observations: a fixed-population workload for attribution and the
real rifle path for gameplay cost. Match view, source/DLL/config, combat fixture,
effective resolution, time dilation, seed where supported, counts and simulation
duration. Record actual shots and active/sleeping/held/pooled counts. Repeat only
enough to separate the candidate's effect from observed run variance.
Record deltas of projectile geometry barriers, overloads and dropped time rather
than treating cumulative pre-run counters as failures; cover slowdown for changed
time-dependent behavior.

Add narrow counters/scopes where missing: collision-profile reload count; released
bones; native GC buffer/pull; manager observation/apply; support candidates/exact
sweeps; graph invalidations; cell reinsertion; render dirties; allocation/free-pool
high-water memory; projectile collection/query preparation; task launch/wait.
Capture frame/GT/credible RT/GPU p50/p95/p99 and event peaks. Use Unreal Insights
for the critical path; overlapping scopes are attribution, not additive savings.

Output: one candidate-bound baseline and a ranked cost breakdown, with explicit
gaps. The historical 120 FPS aspiration implies 8.33 ms for the whole frame, not
8.33 ms for destruction. Set a destruction budget only against the intended target
hardware and full combat scene; this audit does not invent a guaranteed budget.

### 1. Batch and index without changing representation

Batch all leaf collision transitions per GC; consolidate duplicate body setup;
add GC/bone and owner/support reverse maps; use iterative wake propagation with
visited revisions; clean shard arrays once; consume existing carrier indices;
cache the projectile exclusion membership. Implement in small, separately attributable
candidates. Expected gain is less release spike and lookup work; no percentage
or FPS promise is justified yet.

Accept when K leaf releases cause one collection profile batch, existing identity
semantics survive, and changed paths show lower work without new frame-tail cost.
Cover direct and indirect release, collision incoming wake, selected impulse,
cross-owner pile, support deletion/movement/response, queued reset, swap removal
and pool reuse. A queued physics command must acknowledge success or reconcile
rejection; a failed hold/move must not leave the manager reporting a held object
that physics rejected. Explicitly cover unsupported scale and held-state semantics.
Restrict reruns to affected paths and uncovered final-candidate gaps.

### 2. Make idle cost proportional to change

Maintain active, dirty and due-validation sets. Make support dependencies event-led;
group sentinels by supporting component and spread fallback validation over its
full interval. Preserve urgent wake/support events; a frame budget may defer only
noncritical maintenance. Use unchanged spatial-cell fast paths and render-property
revisions. Remove redundant subscriptions/scans only after covering external
fractures, collisions and actor/component edits that bypass the local hit handler.

Target project-side complexity near O(A + changed + due), rather than O(R) every
frame. Native GC work is separate. Accept with visible counter reductions for a
large settled set plus incoming-body wake, slow-motion settling, held release,
moving supports and no lost hit or stale spatial result.

If intact query-body cost is material, prototype shared immutable per-asset query
acceleration: coarse owner/section bounds followed by exact original child shapes.
Resolve the globally earliest exact hit, preserving normals, material, masks and
stable tile/bone identity. A coarse first hit followed by rejection must not hide
a real obstacle behind it. Removing native query bodies is viable only when every
query consumer retains its contract; a weapon-only workaround is insufficient.

### 3. Address native GC granularity if it remains dominant

Prototype one representative column/cell, preserve original assets, and compare:

1. Spatially meaningful intermediate clusters and smaller GC partitions, retaining
   the same visible pieces and collision hulls. Sparse damage should dirty fewer
   leaves; too many partitions can increase component/proxy, contact and draw cost.
   Prove column support, crack pattern and cross-partition contact equivalence.
2. Separate intact query/render ownership from activated exact fracture cells.
   Prewarm likely cells; map every hit to the same authored piece and create all
   interacting neighbours before contact resolution. First-hit latency, memory
   duplication, damage across cell boundaries and support topology are rejection risks.
3. Transfer released leaves to a dense persistent rigid-body store with exact hulls,
   mass/inertia/material/pose/velocity and stable identities, while retaining shared
   rendering. Eliminate duplicate source colliders; preserve CCD, contacts and wake.
   Actor-per-piece transfer may cost more, and merely disabling leaves does not
   automatically remove the source GC's full-particle iteration. Measure actual
   visited/emitted rows, memory and contact cost before adoption.

Select the simplest winning prototype; reject it if synchronization savings are
consumed by body management or it alters required play. These are higher-risk
architecture tasks, not shortcuts to apply silently to the current map.

### 4. Establish the useful scale and polish remaining rendering costs

After a promising candidate, propose a new bounded capacity check by independent
axes: retained count, simultaneously awake count, local pile density and number of
columns damaged together. Include repeated interaction and memory high-water/reuse.
Stop increasing load once the intended frame budget is exceeded. This identifies
capacity; it does not impose a gameplay fragment cap or restart the stopped fixture.

Revisit material/shadow grouping, culling cells, hidden query updates and intact
root proxies only when the current trace attributes meaningful cost there. Preserve
shadow/appearance gates. Compare a representative packaged/standalone sample before
shipping claims; editor-only results do not establish a target-hardware guarantee.

## Unconventional alternatives and their boundaries

| Option | Why it may help | Boundary / rejection condition |
| --- | --- | --- |
| Reversible sleeping rubble islands | Retain per-piece poses/IDs and exact union hulls behind fewer dormant physics owners; expand the touched contact island before force resolution. | Research only. Compound mass/contact behavior, arbitrary incoming objects, deep stacks and pre-contact activation are difficult. Exact hulls alone do not prove equivalent dynamics. Never permanently freeze rubble or repeat the missed-wake failure. |
| Contact/impact-driven activation frontier | Keep untouched fracture cells cheaply represented; activate only the interaction neighbourhood and required supports, with conservative motion bounds. | Camera distance alone is unsafe. Bullets, off-screen forces, support loss and ability targets must activate in time. Delayed first contact rejects the prototype. |
| Per-frame release scheduling | Spreads a simultaneous allocation/fracture burst. | It changes destruction timing and sometimes contact outcomes. Only a separately approved design may defer noncritical pieces; immediate bullet obstruction and support failure cannot silently lag. |
| Gameplay chunks plus GPU micro-debris | Reserves expensive two-way bodies for meaningful chunks while preserving visual richness. | Explicit optional quality/mechanics tier only. Current requirements prohibit substituting interactive fragments with visual-only particles, reducing collision fidelity or deleting settled debris. Do not use this to claim an equivalent optimization. |

There is no defensible promise of unlimited independently interacting rigid bodies
at constant cost. The useful objective is minimal idle overhead, bounded mutation
spikes, local interaction work and an evidenced capacity at the required fidelity.
No new paid plugin, separately billed API or engine migration is needed for stages
0-2. Engine source changes are outside the proposed initial work.

## Source guidance and delivery

Epic documents root proxies, instancing, external strain and release throttling;
its removal/one-way/GPU substitution examples change this project's contract and
are optional design alternatives, not automatic prescriptions.
[Chaos optimization](https://dev.epicgames.com/documentation/unreal-engine/chaos-destruction-optimization?application_version=5.6).
Native cluster hierarchy can reduce simultaneous collision work;
[clustering guide](https://dev.epicgames.com/documentation/unreal-engine/cluster-geometry-collections-user-guide-in-unreal-engine).
Sleep and disabled states have different wake behavior;
[fields guide](https://dev.epicgames.com/documentation/unreal-engine/chaos-fields-user-guide-in-unreal-engine?lang=en-US).
These references support mechanisms, not projected speedups. Installed UE 5.8 and
candidate-specific evidence decide API applicability and acceptance.

Audit advisory sessions use verified native Astra/max; configured service tier is
default, actual tier is omitted in native records and remains unknown. Detailed
evidence is under `Saved/DestructionAudit01/`. No code/assets/config changes or
implementation dispatch are part of MSQ-169.

Primary independent technical review: **PASS**, with both nonblocking findings
closed (p95 rounding and explicit rejected-command acceptance).
`Saved/DestructionAudit01/primary-review.md` records its reviewed-document identity
and independent checks of the consequential metrics, source paths and evidence
limitations. This accepts the audit and plan only. Controller closure checks
preserve all 80 audited source/DLL inputs, validate report links/authority JSON and
context budgets, and commit only this audit/authority plus its ProjectState route.
Pre-existing owner source, configuration and documentation edits remain outside
the audit commit. `Saved/DestructionAudit01/closure-check.json` binds final artifacts.
