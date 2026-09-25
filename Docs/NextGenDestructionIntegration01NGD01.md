# MSQ-149 / NGD-01: Candidate01 handoff

2026-09-25. Executor verification passes on **Build03**, UE 5.8.3-58210709.
The current `/Game/Maps/L_OpeningLobby_PainterStone01` is saved and open with
three ready-made vendor breakables. Controller scope/evidence acceptance passed
for this exact candidate, with 29 passing checks and unchanged build/map hashes.
The task-scoped local closure commit excludes pre-existing owner edits.
Independent review is waived by
`Approvals/NextGenDestructionIntegration01-NGD01-OwnerStart01.json`;
owner visual/play acceptance remains separate.

## Play and placement

Use the existing MeridianSquad player: **WASD** move, **LMB** fire, **RMB** aim,
**R** reload, **F6** reset. The specimens occupy three free bays on the **+Y side**
of the lobby. Aim at solid chair parts, such as the seat; its empty spaces already
pass bullets. The central route and all original actors remain in place.

All three are unmodified `BP_BreakableObject` instances with an added native
`NGDIntegration` component, tag `NGD01`, and Outliner folder `NGD01_DemoProps`.
Delete these three actors to remove the placement. Instance scale is `(1,1,1)`;
coordinates below are centimetres, with zero pitch and roll.

| Stable identity / actor label | Editor actor | Source data asset | Location | Yaw |
| --- | --- | --- | --- | --- |
| `NGD01_ConcretePillar` | `BP_BreakableObject_C_0` | `DA_Pillar_Small_Concrete` | `(-840,700,0)` | 0 |
| `NGD01_WoodenChair` | `BP_BreakableObject_C_1` | `DA_Chair_Wood` | `(0,700,0)` | -90 |
| `NGD01_CeramicVase` | `BP_BreakableObject_C_2` | `DA_Vase` | `(840,700,0)` | 0 |

Blueprint: `/Game/NextGenDestruction/Blueprints/Actors/BP_BreakableObject`.
Data assets: `/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/`.
Geometry collections: `/Game/NextGenDestruction/GeometryCollections/`:

| Specimen | Collection | Existing material instances | Observed states |
| --- | --- | --- | --- |
| Concrete | `Concrete/GC_ConcretePillar_Small` | `MI_ConcreteInner`, `MI_ConcreteOuter` | Intact; local chipped opening; through opening with remaining solid upper section |
| Chair | `Wood/GC_Chair` | `MI_WoodenChair_01`; vendor second slot is `/Engine/EngineMaterials/WorldGridMaterial` | Intact with existing gaps; local break and detached pieces |
| Vase | `Ceramic/GC_Vase` | `MI_VaseOuter` in both slots | Intact; shattered body and detached pieces |

Material instances above live in `/Game/NextGenDestruction/Materials/Instances/`.
Exact component materials, source packages, collision profiles and transforms are
in the placement inventories and `lobby-final.json`. Vendor originals remain
byte-identical; asset derivatives were unnecessary.

## Integration and reset

`ACombatProjectileWorld::ResolveHit` routes an opted-in instance to
`UNGDPropComponent::ReceiveBullet`, which invokes the vendor `BulletImpact`
interface with the **original finite-sweep FHitResult**. A managed hit takes this
single route; the generic PointDamage route is skipped. Recent shot IDs suppress
duplicate delivery. Bullet consumption, 0.5 cm projectile radius, muzzle/near-cover
checks, launch timing and self-hit handling retain their existing implementation.

Rifle damage remains 25 for damage receivers. Fracture uses the vendor field's
strain **2,000,000**, rather than treating that damage value as strain. The vendor
100 cm sphere uses source spawn scales **0.4 / 0.3 / 0.5** for concrete/chair/vase
(nominal strain radii 40/30/50 cm). Existing radial velocity 200, directional
velocity 250, torque multiplier 10, falloff and noise are retained. Concrete and
chair retain `HasKinematicPieces=true`; the vase uses the vendor dynamic-state
activation. Fracture granularity is the authored collection/cluster structure,
not continuous cutting or new geometry generation.

F6 clears the projectile queue and replaces each task-owned vendor instance from
its source data and initial transform. It removes old break subscriptions, timers,
latent work, fields, physics proxies and per-particle overrides. Build03 fixes the
observed reset race: destroying a field actor alone left transient strain queued
in Chaos. Retirement now cancels **only commands named for fields created by this
adapter**, on the owning world's solver command queue, before replacement.

`UNGDWorldSubsystem::OnCollisionChanged` publishes stable `ObjectId`, monotonic
`CollisionRevision`, `ResetGeneration`, conservative `ChangedBounds`, and reason
`initial`, `break` or `reset`. The subsystem survives actor replacement; runtime
actor names change on reset. `LatestChanges` retains the latest notification per
identity. This is the initial contract; fragment motion/removal, support and
navigation invalidation need completion in NGD-02.

## Focused evidence

Evidence root: `Saved/NextGenDestructionIntegration01/NGD-01/Candidate01/`.
`verification.json` records **29 passing checks**. Reproduce its evidence and
preservation assertions with `Scripts/NextGenDestructionIntegration01/verify_evidence.py`.

- `pillar-shot04`, `pillar-shot05`, `pillar-shot07`: actual rifle shots 111–113
  each delivered once and were consumed by concrete; the witness remained at
  100 health. Three local hits opened this tested trajectory.
- `opening-after-shot07` confirms a 0.5 cm sweep along the recorded bullet path
  reaches the witness. `pillar-shot08` (shot 114) then reaches it through the
  opening, causing exactly one 25-damage hit. `pillar-solid09` (shot 115) hits the
  remaining upper solid and leaves witness health at 75.
- `chair-shot02` and `vase-shot01` each show one real rifle hit and fracture.
  Their early debris surveys record six and four 5 cm-radius fragment contacts
  outside the original footprint, respectively.
- `build03-reset-live-field01/02` each reset while one vendor field is still
  live. All three replacements stay intact with zero inherited hits, break
  events or fields. `build03-after-reset-shot` confirms normal breaking resumes.
  `build03-reset-settled` checks beyond the vendor's four-second delayed work;
  `build03-reset-clearance` records 216 surrounding sweeps hitting only the floor.
- `build03.log` passes. `build03-hashes.json` binds the compiled source, DLL and
  saved map. Build02 firing/fracture/material evidence is reused: Build03 changes
  field retirement only, with affected reset/next-shot transitions checked again.

The real PIE image is `pillar-opening-pie.png`. Editor placement evidence is
`lobby-three-props-overview.png`; `lobby-side-before/after.png` uses the same camera.
Earlier failed harness attempts and the reproduced Build02 reset defect remain
in the evidence directory and are not counted as passing acceptance evidence.

## Preservation and limits

The retained lobby was clean before mutation. `Before/L_OpeningLobby_PainterStone01.umap`
is its recoverable current snapshot, SHA-256
`b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
The 129 original actors' inventoried transforms/components/materials remain
unchanged; final count is 132. All 481 vendor packages and the controller's
protected owner-file hashes match. The temporary witness was removed before
saving. Final map SHA-256:
`902a8c2d1f2cfa5e91cc2ab19dde1bcb971334348be81d9d4f2aea8ea43b95ee`.

Verification temporarily disabled enemy combat in PIE and the editor's background
CPU throttle. PIE was stopped and the original throttle setting restored. The
existing GASPALS `CharactersSkeletalMeshes` warning occurred when the shared
prototype reset rebuilt its fixture; that unrelated behavior was left unchanged.

NGD-02 should define fragment lifetime/removal, significant-debris classification,
complete collision/support notifications and identity allocation for additional
instances. Current vendor removal/shrink behavior and `IgnoreCharChaos` fragment
profile (Pawn ignored) remain. No broad load/slowdown claim is made here. The
three placements are gameplay specimens awaiting owner play/design judgement.
