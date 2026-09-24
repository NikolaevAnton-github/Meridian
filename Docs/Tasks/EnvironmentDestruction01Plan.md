# EnvironmentDestruction01: copied-lobby destruction laboratory

Date: 2026-09-24. Parent: **MSQ-74** under MSQ-67.
Authority: [owner lab request](../Approvals/EnvironmentDestruction01-LobbyLab01.json).
Multica owns live state. This document defines scope and sequence, not a scheduler.

## Direction and execution boundary

Destruction is the next implementation lane, ahead of Utility AI replacement.
Create `/Game/Maps/L_OpeningLobby_DestructionLab01` from the current retained
`/Game/Maps/L_OpeningLobby_PainterStone01`. Gradually populate the one laboratory
map with reusable nonstructural destruction specimens. Preserve the original
map, owner configuration, shared assets, editable sources and immutable evidence.
An edited referenced asset needs its own lab-derived copy; copying the map alone
does not isolate shared materials, Blueprints, meshes or map-owned dependencies.

ED-00 copy and baseline inventory are authorized now. The remaining children are
prepared sequential work; their creation does not auto-dispatch implementation.
No new architecture, structural walls/floors/columns, building collapse, resumed
glazing refinement or new art selection is implied. New specimen art follows the
existing bounded source/visual selection rules. Reuse existing editable sources.

MSQ-72 is no longer an initial destruction prerequisite. The existing rifle point
damage path can drive a specimen independently of enemy behavior. MSQ-131 later
integrates changed cover/routes into the new AI; it is not a reverse gate on MSQ-74.
Actual player/enemy traversal over rubble retains the MSQ-78/MSQ-95/96 boundary.

## Sequential children

| Package | Multica | Result | Prerequisite |
| --- | --- | --- | --- |
| ED-00 | MSQ-140 | [Isolated copied lobby and baseline inventory](EnvironmentDestruction01/ED-00.md) | Verified current source map and editor |
| ED-01 | MSQ-141 | [First rifle-driven destruction specimen](EnvironmentDestruction01/ED-01.md) | ED-00 |
| ED-02 | MSQ-142 | [Local accumulated damage and truthful openings](EnvironmentDestruction01/ED-02.md) | ED-01 |
| ED-03 | MSQ-143 | [Bounded debris, support and reset](EnvironmentDestruction01/ED-03.md) | ED-02 |
| ED-04 | MSQ-144 | [Second material and reusable specimen authoring](EnvironmentDestruction01/ED-04.md) | ED-03 |
| ED-05 | MSQ-145 | [Progressive population and measured optimization](EnvironmentDestruction01/ED-05.md) | ED-04 |
| ED-06 | MSQ-146 | [Impact presentation and existing slow-time consistency](EnvironmentDestruction01/ED-06.md) | ED-05 |
| ED-07 | MSQ-147 | [Representative laboratory and owner handoff](EnvironmentDestruction01/ED-07.md) | ED-06 |

Stages are local to MSQ-74. Keep one production worker/editor writer; no automatic
parent executor. Later AI/ability tasks consume the delivered destruction contract.

## Specimen behavior

Begin with one bounded cover object and a target behind it. Actual rifle hits
must produce localized visible breaks and corresponding collision changes.
Default first behavior: the impacting bullet damages the obstacle and stops;
later shots can pass through the resulting opening if their actual sweep fits.
Penetration through intact material is a separate proposed extension.

Damage accumulates near impact; it must not silently become global hit points
that delete the entire object. Chaos pre-fractured pieces and authored connections
are the initial technical candidate, validated against local installed capabilities.
Do not promise arbitrary runtime mesh cutting or physically exact structural failure.
Record fracture granularity, support/anchor rules, mass, thresholds and impulses.

Add a second materially distinct specimen after the first loop works. Select two
or three actual sources with identified derivations; do not assume a wooden box,
masonry barrier or any proposed visual has already been approved or exists.
Progressive population uses sparse, representative and bounded dense layouts in
the same map, with reproducible fixture/configuration identities rather than
duplicated projects or a growing set of full-map copies.

## Quality-preserving performance plan

The controller observed Ryzen 7 9800X3D and RTX 5090 on 2026-09-24. Record actual
hardware, resolution, scalability, upscaler, frame cap, engine build and execution
mode for each comparable measurement; this PC is not a minimum-spec promise.
No target FPS or universal fragment cap is approved by this planning record.
Set numeric cost budgets from the first measured specimen and intended scene
before density tuning; preserve margin for later AI, weapons and abilities.

Measure the same camera route and bounded hit sequence in four states:

1. Copied lobby before specimens: existing CPU/GPU/rendering baseline.
2. Populated intact scene: idle physics, geometry, materials and memory costs.
3. A representative break and bounded overlapping breaks: physics/event spikes,
   fragment activation, dust/audio and dynamic rendering costs.
4. Settled debris and repeated resets: residual cost, collision truth, bounded
   memory/body/component counts and remaining gameplay obstacles.

Report frame time in milliseconds, Game/Render/GPU and available physics timings,
sample size/duration, P95 and observed maximum with warm-up/streaming context.
FPS and averages alone cannot close break-event hitch acceptance. For 60 FPS the
whole-frame budget would be about 16.7 ms, not 16.7 ms available to destruction.
CPU/GPU costs may overlap; do not add their displayed times as serial work.

Physics work includes active rigid bodies, contacts, collision shape complexity,
solver/constraint work and activation/break bursts. GPU work includes visible
geometry, materials, shadows, lighting and particle overdraw; CPU events/render
submission and RAM/VRAM can also limit the result. Nanite is not a physics budget.

Optimize in this order, checking affected behavior and comparable views:

- Avoid idle per-object work; keep intact clusters cheap and activate locally.
- Tune stable sleeping and collision proxies while retaining gameplay collision.
- Bound simultaneous active simulation and batch event/effect work; retain a
  reproducible movable piece and do not freeze all debris to hide problems.
- Use cosmetic particles for genuinely nonblocking fine dust/chips, pool where
  useful, and tune particle coverage/lighting at equivalent perceived quality.
- Keep significant visible damage, openings and obstacles for the encounter.
  Sleeping is not removal. Any support/cover removal emits invalidation before
  deletion; never remove a supporting piece beneath an actor without a safe rule.
- Apply distance/visibility and effect scalability only with documented visual
  comparisons. General quality reduction is an explicit tradeoff, not a hidden fix.

ED-05 establishes density measurements; ED-06 repeats presentation-affected
measurements after dust/audio changes, plus normal and canonical slowdown checks
for affected physics, debris lifetime and reset transitions. Remeasure any such
behavior whose implementation changes; presentation-only timing is insufficient.
No unlimited stress population or new
benchmark framework. Reuse Unreal profiling and existing focused evidence tools.

## Shared contracts and acceptance

Expose bounded change information: object/fragment identity, affected bounds,
collision/cover revision, support invalidation and reset generation. Avoid wiring
new destruction behavior into the obsolete local navigation policy.
World physics/projectiles/rifle cadence use the current 0.25 slowdown and hero
movement 0.65. This does not implement the later full time-stop ability.

Each stage identifies its candidate and changed paths; executor checks and one
primary independent technical review cover substantive changes. The simple map
copy may use a bounded controller/self-check of preservation and load integrity.
Owner play/visual judgement stays separate; declare runtime test authority before
each dispatch and keep untested behavior pending. Keep all logs/captures under
`Saved/EnvironmentDestruction01/<package>/<candidate>/`; binary assets use LFS.
Controller makes task-scoped local commits, excluding unrelated owner changes.

Parent completion requires actual shot/collision truth, local damage, bounded
movable debris, clean resets, repeatable density measurements, reviewed findings
and an identified owner-ready map. It does not claim whole-level destruction,
future AI adaptation, integrated rubble traversal or owner visual/play acceptance.
