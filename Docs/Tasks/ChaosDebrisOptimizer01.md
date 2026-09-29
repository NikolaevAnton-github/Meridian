# ChaosDebrisOptimizer01: installed plugin check

2026-09-29. Owner requested checking the already installed
[Chaos Debris Optimizer](https://www.fab.com/listings/9777d5d8-4a9c-4d9f-bd62-d0b04466a154)
after preparation of the DestructionPerf01 tasks.
Status: **installation/module/content checks passed; gameplay integration and
performance benefit not tested or accepted**.

## Installed and project state

- Installed plugin: **1.1.0**, Runtime module, Win64, descriptor EngineVersion
  **5.8.0**. Local engine is **5.8.3-58210709**; plugin and engine module BuildId
  both equal **55116800**. The actual module-load check passed.
- Location: `D:/UE_5.8/Engine/Plugins/Marketplace/ChaosDeb4b5daa82fee2V2/`.
  Includes source, documentation, six presets and a demo map.
- The plugin is **not enabled in MeridianSquad by default**. Its descriptor has
  no EnabledByDefault override, the project has no explicit plugin entry, and a
  project-default commandlet exposes neither optimizer nor preset class.
- A separate commandlet with `-EnablePlugins=ChaosDebrisOptimizer` mounts the
  plugin and exposes both classes and the expected Blueprint control API.
  This switch applied only to that process; no persistent enablement was made.
- The editor was closed when checked. No live editor bridge was available, so
  isolated UnrealEditor-Cmd processes supplied the engine-side evidence.

## Checks performed

Three serial Python commandlets used this project with `-unattended -nop4
-NullRHI -nosound`, all exiting **0**. They did not load a gameplay world,
simulate destruction, save packages, or rebuild the plugin.

1. Project-default probe: optimizer/preset classes absent, confirming inactive state.
2. Session-enabled probe: module mounted; component/preset classes and
   ResetTracking, DestroyAllProxies, PauseProcessing, ResumeProcessing,
   ApplyPreset and KillEverything exposed. API presence is not a behavioral pass.
3. Content probe: explicit asset-registry scan finds **98 plugin assets**, registers
   `/ChaosDebrisOptimizer/Demo/Maps/DemoMap`, and loads all six preset DataAssets
   as ChaosDebrisOptimizerPreset. The first probe's zero asset count came from
   its unscanned commandlet registry, not missing content; both records are kept.

Actual loaded component defaults: first velocity check after **3 s**,
SleepAndKill, proxy collision disabled, proxy shape Box, profile Destructible,
and Query Only true when proxies are enabled.

| Loaded preset | Initial check delay | Action | Proxies | Query Only |
| --- | ---: | --- | --- | --- |
| Balanced | 2.5 s | SleepAndKill | Off | True |
| Quality | 4.0 s | SleepAndKill | Off | True |
| Performance | 1.5 s | Kill | Off | True |
| Mass Destruction | 1.0 s | Kill | Off | True |
| Walkable Box | 4.0 s | SleepAndKill | On | True |
| Walkable Convex | 3.0 s | SleepAndKill | On | True |

These are initial-check delays, not guarantees of exact removal time or measured
performance. No preset is selected for production by this check.

## Source findings relevant to NGD

Paths below are relative to the installed plugin's
`Source/ChaosDebrisOptimizer/` unless identified as project source.

- **Component integration is required.** `Private/ChaosDebrisOptimizerComponent.cpp`
  lines 194-224 discover GeometryCollection components on the same owner in
  BeginPlay and subscribe to break events. Merely enabling the plugin does not
  optimize all lobby objects. The module startup itself is empty.
- **Kill disables physics.** Component.cpp lines 2383-2388 call
  `DisableParticles_External`. The plugin does not itself replace the rendered
  rubble with a shared render representation. Its optional proxies are invisible
  collision primitives/convex shapes, not replacement artwork. Actual NGD visible
  debris and engine removal-event behavior still need a gameplay check.
- **Default collision semantics change after cleanup.**
  `Public/ChaosDebrisOptimizerComponent.h` lines 349-378 define proxies off by
  default, and query-only when enabled. Query-only proxies can support character
  sweeps but do not physically block simulated objects. Walkability alone proves
  neither bullet/cover equivalence nor interaction with another falling chunk.
- **Repeated impacts need a dedicated contract.** Component.cpp lines 1385-1397
  deduplicate terminal sleep; lines 531-534 reject a permanently tracked sleep key
  on later registration. SleepAndKill final processing at 1540-1556 does not
  recheck velocity after a subsequent impact. The source has no general
  re-enable-particles/reactivation path. Do not use kill for rubble that must
  remain fully physical on subsequent blasts without a verified alternative.
- **ResetTracking is not restoration.** Component.cpp lines 298-364 clear
  bookkeeping/queues/counters; they do not restore killed particles or clear all
  proxy collision. In-place reuse would also need appropriate GC restoration and
  DestroyAllProxies. EndPlay at 232-276 removes subscriptions, timers and proxies.
- **Proxy generation has its own cost and correctness limits.**
  `Private/ChaosConvexProxyComponent.cpp` lines 37-45 cook collision synchronously;
  merged convex hulls can bridge empty space. Component.cpp lines 2629-2647 defer
  proxy creation when capped, while physics disable can already have occurred.
  Check transition collision gaps and creation hitches rather than assuming cheap
  settled collision guarantees cheap transitions.
- **F6 destroys and respawns NGD actors.** Project
  `Source/MeridianSquad/NGDPropComponent.cpp` lines 246-251 retire the whole vendor
  instance, while 299-307 currently add the NGDIntegration component on spawn.
  A future optimizer attachment must participate in every spawn/reset generation;
  a one-time attachment would not survive F6. Verify cleanup after pending physics
  work as well as ordinary EndPlay. This is source analysis, not an F6 plugin test.
- **Projectile proxy hits need mapping checks.** Project
  `CombatProjectileWorld.cpp` lines 616-622 and `NGDPropComponent.cpp` lines 180-204
  route the original hit to the vendor Blueprint. Proxy primitives share the owner
  but do not establish an equivalent GC fragment-hit mapping. This is an untested
  integration boundary, not a demonstrated shooting failure.
- **Measure optimizer overhead as well as savings.** The enabled physics audit
  walks solver particles per active optimizer instance (Component.cpp 628-727).
  Many attached components can multiply that work. Timers use world/game time,
  so canonical slowdown also changes real-time cleanup latency.
- Some shipped limitation prose differs from the installed implementation, such
  as cluster proxy handling. Use the installed source and runtime evidence for
  candidate decisions rather than treating every documentation claim as verified.

## Fit to the optimization tasks

- [DP-06](DestructionPerf01/DP-06.md): candidate implementation of sleep/cleanup,
  settle detection and optional retained collision. Compare a bounded configured
  candidate against the existing lifecycle before building equivalent facilities.
- [DP-08](DestructionPerf01/DP-08.md): candidate collision-proxy representation;
  measure component/hull creation, steady-state cost and collision agreement.
  Render instancing, intact proxies and pooling remain separate questions.
- [DP-01](DestructionPerf01/DP-01.md), [DP-02](DestructionPerf01/DP-02.md), fracture
  authoring, event deduplication and field/release work remain necessary. The
  publisher explicitly scopes the plugin to post-destruction cleanup. A claim
  that it fixes the existing initial blast hitch or reaches 120 FPS is unsupported.

The next applicable experiment is an authorized, versioned DP-06 candidate on
representative NGD objects after attribution: measure the same F7 workload and
check retained cover, player/bullet collision, repeated blast, F6 and slowdown.
Select eligible debris by gameplay role; do not blindly apply an aggressive
whole-object preset. This check does not execute the prepared optimization tasks.

## Evidence and preservation

Raw scripts, stdout, native logs and JSON results:
`Saved/ChaosDebrisOptimizer01/Check01/`.
`identity.json` records plugin DLL/descriptor hashes and build IDs;
`project-default.json`, `session-enabled.json` and `content-probe.json` retain the
engine results. `preservation-before.json` / `preservation-after.json` confirm
unchanged project descriptor, DefaultEngine.ini, owner lobby map and grenade asset.
The same three pre-existing owner modifications remain outside this documentation
commit. No source code, plugin source, settings or asset changes were made.

Limits: no playable demo/F7 run, physics cleanup test, rendered quality judgement,
packaged-build check, timing comparison or owner acceptance. This establishes
installation, binary loading, reflected API and preset availability only.
