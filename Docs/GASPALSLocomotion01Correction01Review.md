**MSQ-121 / GASPALSLocomotion01 Correction01 independent technical review**

Date: 2026-09-24. Final candidate: **Candidate02**. Verdict: **PASS** for closure
of **GL01-R1 and GL01-R2** and their directly affected integration seams. No
remaining technical finding was identified within this correction scope.

This is the resumed sole primary review, following [ProjectState](ProjectState.md),
the preserved [Candidate01 review](GASPALSLocomotion01Review.md), and the
[executor correction handoff](GASPALSLocomotion01Correction01.md). The original
review remains unchanged and records Candidate01's two defects. Production
finished at `2026-09-24T12:09:47.817118Z`; this review started at
`2026-09-24T12:10:20.913456Z`. Controller launch metadata and the actual reviewer
process arguments agree on native Astra/max/default with fast mode disabled.

The [Candidate02 manifest](../Saved/GASPALSLocomotion01/Worker/Candidate02/candidate-manifest.json)
was frozen at `2026-09-24T12:08:14.514238+00:00`. Its SHA-256 is
`6f793201dcb434658006c477fec6857dd0861525844b9ef3caf403455f4e6291`.
The reviewed DLL is `Binaries/Win64/UnrealEditor-MeridianSquad.dll`, SHA-256
`600731ab8e22aba32834ec33bd2b26798377b69879f1de0f70d3a0f28667f3b8`.

| Finding | Closure result | Production locations |
| --- | --- | --- |
| GL01-R1: movement capsule intercepts skeletal damage | **CLOSED** | [CombatProjectileWorld.cpp:25](../Source/MeridianSquad/CombatProjectileWorld.cpp#L25), sampling at 237, cached aim gate at 145, segment arbitration at 478, dispatch at 603 |
| GL01-R2: proposed stance geometry requires Mover | **CLOSED** | [EnemyCombatCover.cpp:65](../Source/MeridianSquad/EnemyCombatCover.cpp#L65), [EnemyCombatTactics.cpp:42](../Source/MeridianSquad/EnemyCombatTactics.cpp#L42), [EnemyCombatMobile.cpp:48](../Source/MeridianSquad/EnemyCombatMobile.cpp#L48) |

GL01-R1 now has one authoritative skeletal projectile representation for the
adopted source character. `PhysicalProjectileOwner` accepts the fixture itself
or its actual `Foundation`; mere ownership of another actor is insufficient.
The active spawn path possesses the source character and then restores its
fixture owner at [GASPALSLocomotionFixture.cpp:170](../Source/MeridianSquad/GASPALSLocomotionFixture.cpp#L170).
`UsesProjectileCapsule` excludes that character in sampling, cached aim queries
and segment arbitration, including a stale generic sample after adoption. This
classification does not change with health, crouch, readiness or ragdoll. An
unready fixture has no generic capsule fallback.

The actual retained tracer at
[PhysicsControlDummy.cpp:339](../Source/MeridianSquad/PhysicsControlDummy.cpp#L339)
constructs the hit from the fixture, its current skeletal `Body`, shape bone and
surface impact point. `AdvanceSegment` preserves that hit when it wins the
nearest-contact comparison against world, ordinary-character and other-body
contacts. One pending hit retires the bullet; `ResolveHit` makes one virtual
`ReceiveBullet` call. The active override at
[GASPALSLocomotionPhysics.cpp:233](../Source/MeridianSquad/GASPALSLocomotionPhysics.cpp#L233)
therefore receives the bone contact needed for health, localized reaction,
strong-hit ragdoll, death and corpse impulse. It retains the Candidate01 physical
implementation and does not reintroduce the custom-balance handoff.

Wrapper and source-pawn shooters now share launch-body clearance, temporary
self immunity and self-hit attribution. Clearance still ends immunity so later
re-entry may hit the same body. Ordinary characters retain capsule contact and
generic point damage; the prototype retains its per-region branch. Readiness,
rather than health or movement-capsule collision, controls physical sampling at
[PhysicsControlDummyWorld.cpp:55](../Source/MeridianSquad/PhysicsControlDummyWorld.cpp#L55),
so dead bodies remain eligible. The unchanged reset clears bullets and physical
history, destroys the old source pawn, increments its pose epoch and records the
replacement. Epoch-aware interpolation/tracing, finite-flight time calculation,
contact-time/shot-ID sorting and reset-generation cancellation remain intact.

GL01-R2 now computes proposed CMC dimensions before the retained Mover branch.
Standing uses the actual character class default capsule, including while its
achieved capsule is crouched. Crouching uses the current radius and CMC
`GetCrouchedHalfHeight()`, clamped to at least the unscaled radius. The current
component scale is applied using installed UE 5.8 getters: radius by `min(X,Y)`
and half-height by `Z`. The installed CMC implementation confirms that crouch
retains current radius and uncrouch restores class default radius and height.
Missing components/defaults, non-finite dimensions, non-positive scale/radius
and an invalid scaled capsule fail closed.

The retained source exports supply radius **50 cm**, standing half-height
**86 cm** and CMC crouched half-height **60 cm** at unit scale. These are source
defaults, not gameplay measurements. The unchanged achieved `CapsuleSize` read
continues to use the current component. The source command adapter still calls
actual CMC `Crouch`/`UnCrouch`, and achieved stance still reads `bIsCrouched`.

The corrected helper is on the production route: explicit-stance
`TacticalGround` and `TacticalWalk` now reach their support, overlap and sweep
queries. Mobile proposals request standing stance; standing lean-edge cover
and crouched low-cover proposals use `CoverCapsule`, with crouched travel through
`CoverWalk`. [AssessCoverOption](../Source/MeridianSquad/EnemyCombatCover.cpp#L146)
and the mobile producer were inspected directly. Their tactical policy and
achieved aim/muzzle/fire gates are unchanged. The native checks verify query
reachability and rejection at these real consumers, not successful movement
or tactical selection in the retained map.

| Applicable evidence | Independent review and result |
| --- | --- |
| Candidate02 `Evidence/routing-02.json` | Reused **29 passing native assertions**. Read the harness and boundaries; verified current exact ownership, sampling and routing functions plus arbitration, launch-clearance, dispatch and sorting fragments against both their hashes and the compiled generated translation unit. |
| Candidate02 `Evidence/geometry-01.json` | Reused **26 passing native assertions**. Verified the exact current adapter, achieved read and clearance consumers in the generated translation unit. Cases include standing while crouched, default/current radius distinction, scaled proposals, invalid input and blocked/unsupported geometry. |
| Candidate02 `Evidence/build-correction01-01.json` / `.log` | Reused successful Development Editor build, exit 0. The log compiles both corrected production files and links the module. Existing StructUtils deprecation is recorded. All **65** frozen native build inputs, the current DLL and build receipts match Candidate02. |
| Candidate02 loaded-module and editor-delivery records | Frozen observations identify PID 14348, the matching DLL, retained lobby, no PIE and no dirty packages. No new editor inspection was required or performed by this reviewer. |
| Candidate01 technical evidence | Original L01/L02/L05 conclusions, source/asset/animation exports, Blueprint checks and **21 FireMotion assertions** remain applicable. All **24** previously reviewed key source/package identities still match. The original review and its referenced evidence retain their hashes. |

The native tests use plain-data actor, contact and collision-query boundaries.
Their physical contact producer and damage receiver are substitutes; the real
tracer, ownership setup, virtual receiver and reset wiring were therefore read
separately as described above. This supports production routing and proposed
geometry correctness without claiming an Unreal physical-response or gameplay
test. The initial routing harness compile failure remains preserved; the final
applicable result is `routing-02`. No passing native test or build was repeated.

Candidate02 changes exactly two production code files:
`CombatProjectileWorld.cpp` and `EnemyCombatCover.cpp`. Their archived preimages
match the original review's recorded hashes, and the correction diff exactly
matches current source. The other twelve declared additions are correction
scripts/documentation and revision/registration inputs. Candidate01's 2,133
production inventory entries retain the same recorded fingerprints in Candidate02;
the bounded key-file identities above were independently checked on disk. The
frozen delta archive contains the reviewed corrected sources and new DLL. This
establishes technical evidence applicability without repeating a complete asset,
historical-preservation or registry acceptance audit.

No source asset or animation graph was revised by this correction. The actual
local CMC pawn, canonical AnimBP, Masculine/Rifle selection, directional speed
functions and source rifle transitions retain the original review's technical
support. Its full-path graph result of **1,172 original nodes retained and four
added** and targeted CVar dependency conclusion also carry forward. No demo
map/render activation or wider config comparison was needed.

The retained L01/L02/L05 technical passes combine with this closure of the
L03/L04 routing defects and the L06 focused-evidence gap. **Technical review of
the corrected candidate passes.** Source/build evidence still does not establish
visual equivalence. Owner Play judgment remains for directional starts/stops and
turns, source rifle/aim transitions and alignment, actual mobile fire/crouch/lean,
local hit feel, knockdown/get-up/death/corpse responses, and reset/slowdown through
those transitions. Packaging and multiplayer remain outside this review.

Review evidence is limited to
[applicability-evidence.json](../Saved/GASPALSLocomotion01/ReviewCorrection01/applicability-evidence.json),
[closure-source-excerpts.txt](../Saved/GASPALSLocomotion01/ReviewCorrection01/closure-source-excerpts.txt)
and [inspect_correction.py](../Saved/GASPALSLocomotion01/ReviewCorrection01/inspect_correction.py).
The script performs identity/extraction comparisons only. This report and that
evidence directory are the sole reviewer-authored outputs. No implementation,
asset, original review, candidate, editor, profile, task state, registry, staging
or commit was changed; no PIE, gameplay, firing, world simulation or performance
test was run.
