# MSQ-121 / GASPALSLocomotion01 independent technical review

Date: 2026-09-24. Candidate: **Candidate01**, frozen
`2026-09-24T11:24:33.050901+00:00`. Verdict: **CHANGES REQUIRED**.

Two high-priority integration defects prevent technical acceptance. The complete
source CMC/animation migration is present, but the new pawn is incompatible with
two retained production consumers: projectile target classification and proposed
stance geometry. These are active paths made incorrect by the migration, not
requests to revise archived movement code or unrelated AI policy.

This is the sole primary independent review of L01-L06, after production completed.
`Controller/worker-completion.json` records exit 0; the frozen manifest identifies
completed delivery. Authority is the [brief](Tasks/GASPALSLocomotion01.md) and
[OwnerStart02](Approvals/GASPALSLocomotion01-OwnerStart02.json), following
[ProjectState](ProjectState.md). Direct execution did not waive review. Native
Astra/max/default, fast-disabled settings verification belongs to the controller
as specified in the review assignment.

## Findings

### GL01-R1 — P1: the new movement capsule can consume a bullet before its skeletal damage receiver

Locations: [CombatProjectileWorld.cpp:214](../Source/MeridianSquad/CombatProjectileWorld.cpp#L214),
lines 455-525 and 562-584 in the same file;
[GASPALSLocomotionFixture.cpp:148](../Source/MeridianSquad/GASPALSLocomotionFixture.cpp#L148).
Affected criteria: L03, L04, L06.

`ResetDummy` now spawns an `ACharacter`. `SampleCapsules` includes every query-enabled
`ACharacter`, with no exclusion for a source pawn owned by `AGASPEnemyFixture`.
The new enemy therefore enters both the generic character-capsule path and the
existing skeletal-body path. During ordinary locomotion its movement capsule is
enabled; the source capsule defaults are radius 50 cm and half-height 86 cm.

`AdvanceSegment` tests that capsule at lines 498-508 and produces a hit whose actor
is the **source character**, with no bone identity. A later skeletal contact can
replace it only if its contact time is strictly earlier (lines 524-525). Whenever
the capsule is entered first, the bullet is retired at the capsule. `ResolveHit`
casts the victim directly to `APhysicsControlDummy`; that cast fails for the source
character, so it calls generic `ApplyPointDamage` instead of the wrapper's
`ReceiveBullet`. The source Character graph has no damage-forwarding event, and
the adapter binds no such receiver. Wrapper health, localized impulse, accumulated
knockdown damage and lethal transition are consequently bypassed for these hits.
An ordinary center-body shot can exhibit this defect; contacts outside the capsule
and source ragdolls with their capsule disabled follow different eligibility.

The generic shooter-capsule exemption also compares the character directly with
`Bullet.Shooter`, while enemy fire supplies the wrapper. A muzzle inside its source
pawn's capsule can therefore be intercepted by its own otherwise unrelated generic
capsule entry. This is the same missing ownership classification.

**Focused closure:** give an owned source character one authoritative projectile
representation. Exclude its movement capsule from generic capsule damage/history
where the fixture's skeletal representation owns contacts, or implement an
equivalent explicit ownership adapter. Preserve actual bone/impact data and one
damage/impulse application; merely forwarding a capsule hit with `BoneName=None`
does not satisfy the skeletal receiver. Keep ordinary player/prototype capsule
handling, wrapper/source shooter immunity, finite-flight ordering, reset history
and corpse-body eligibility coherent. Supply bounded production-routing evidence
for the owned CMC pawn versus an ordinary character, and for nearest skeletal
contact/launch ownership. A pure native routing/arbitration check is sufficient;
no PIE, firing or gameplay simulation is requested.

### GL01-R2 — P1: proposed stance geometry still requires Mover, rejecting CMC tactics and mobile steps

Location: [EnemyCombatCover.cpp:63](../Source/MeridianSquad/EnemyCombatCover.cpp#L63),
especially lines 67-74. Consumers:
[EnemyCombatTactics.cpp:42](../Source/MeridianSquad/EnemyCombatTactics.cpp#L42),
lines 70-85 and 112-125;
[EnemyCombatMobile.cpp:48](../Source/MeridianSquad/EnemyCombatMobile.cpp#L48).
Affected criteria: L04, L06.

`PoseCapsuleSize` searches `Foundation` for `UCharacterMoverComponent`, then requires
its `UStanceSettings`. The new Foundation is the source CMC character and has no
such component. `Settings` is null and the function returns false for **both**
standing and crouched proposals.

This helper remains on the active production route. `TacticalGround` and
`TacticalWalk` reject explicit stance requests when it fails. Every assessed
protected position supplies an explicit stance. Both standing lean-edge and
low-cover choices call `CoverCapsule`; mobile strafe/cautious-approach attempts call
`TacticalGround(..., 0)` and `TacticalWalk(..., 0)`. These requests therefore fail
before their intended clearance/routing checks can complete, even with otherwise
usable geometry. The animation lean node and walking-fire gate alone cannot
preserve the owner-visible behaviors because their AI movement/cover producers
cannot select them.

**Focused closure:** obtain proposed standing/crouched capsule dimensions through
the active movement stack. For CMC, use the actual source character's standing
capsule defaults, CMC crouch half-height and current component scale, following
CMC's radius/height rules. Preserve achieved-capsule reads and fail-closed collision
checks. Do not replace this with guessed shared dimensions or require a dummy
Mover component. Verify standing and crouched proposals, including a standing
proposal while currently crouched, and show that the affected mobile/cover route
can reach its real clearance checks. Reuse the unchanged policy tests; a bounded
check of the production geometry adapter and consumer wiring is enough.

Both findings are derived from actual source and exports, without executing a
game world. Numbered, hashed excerpts are in
[finding-source-excerpts.txt](../Saved/GASPALSLocomotion01/Review/finding-source-excerpts.txt).
The relevant retained consumers have no working-tree diff, which explains why
checking only the migration's changed files missed these new incompatibilities.

## L01-L06 disposition

| Criterion | Result | Supported evidence and limits |
| --- | --- | --- |
| L01: source identity and parity | PASS for inspected technical identity/wiring | Exact `/GASPALS/Blueprints/CBP_SandboxCharacter` parent, canonical `ABP_SandboxCharacter`, source overlay inheritance, choosers, databases and explicit Masculine/Rifle defaults are retained locally. Original source pawn bytes and sampled layer/chooser bytes match source. Final graph changes are bounded as described below. This does not establish visual equivalence. |
| L02: active stack, commands and speeds | PASS for movement-stack wiring | One-opponent and fixture creation use `AGASPALSLocomotionFixture`; its `ResetDummy` spawns the source child. Commands populate `CharacterInputState`, aim input, controller rotation, CMC crouch and movement input before source PreCMC/CMC. Source functions own gait, directional caps, acceleration, braking, friction and rotation. The old 360 override is outside this path. Tactical request production has the separate GL01-R2 blocker. |
| L03: remove balance; retain physical lifecycle | NOT SATISFIED | Historical balance tick/input/hit handoff is disconnected. The new receiver has localized parent-space control and source ragdoll/get-up/death/corpse paths. GL01-R1 prevents the production projectile path from reliably reaching that receiver. Physical response quality and get-up reliability are also unplayed. |
| L04: existing combat compatibility | NOT SATISFIED | Achieved CMC stance/velocity/gait, source Aiming state weight, actual barrel/muzzle and lean sockets feed the retained consumers. GL01-R1 breaks contact ownership; GL01-R2 disables explicit-stance tactical/mobile proposals. These are technical failures, not deferred owner feel judgments. |
| L05: self-contained data and preservation | PASS for inspected delivery | All 2,094 intake destinations exist; only the declared adapted AnimBP differs in size. Relevant assets and source provenance were directly checked, alongside the recorded local dependency closure and preservation output. Original source AnimBP and pre-edit archive remain present, and checked binaries use LFS. Registry revision input is prepared; acceptance/registration remains controller-owned. |
| L06: build and focused verification | PARTIAL; not sufficient for acceptance | Final Development Editor build succeeds, nine relevant Blueprint statuses/compile-error checks and 21 actual production `FireMotion` assertions pass. They do not exercise the two incompatible production consumers above. Reuse those passing results and close only the affected routing/geometry gaps on a new candidate. |

## Technical evidence retained for closure

The reviewed files are those of the frozen Candidate01. A bounded review script
checked 24 directly relevant production source/package files and the DLL against
the candidate; all match. Sampled unchanged pawn, overlay, chooser and PreCMCTick
packages also match the read-only source intake. The adapted AnimBP is the sole
expected source difference among that sample. This is technical review evidence,
not a repeated controller audit of every archive/registry entry.

The full imported plugin, rather than selected old rifle poses, is present.
The source child inherits `CBP_SandboxCharacter`; its mesh uses the canonical
`ABP_SandboxCharacter`, reparented to `UGASPALSLocomotionAnimInstance`. That keeps
the casts used by the source overlay base/pose and chooser contexts valid. Source
`UpdateOverlayBase` and `UpdateOverlayPose` are reapplied after possession initializes
`CharactersSkeletalMeshes`. Source PlayerController-gated camera/input setup does
not make the non-player command controller a player controller.

The graph comparison was independently repeated using **full graph object paths**:
all **1,172** original non-comment nodes remain, with four added lean nodes. The
only changed original pin sets are the source output/upstream connection and four
CVar-name inputs. The worker's 1,084 count comes from indexing by display graph
name plus node name, which collapses repeated graph names; it is not a complete
unique-node count. The review's full-path comparison closes that evidence gap.
Original and final property exports use different reflection formats, so this
comparison proves retained edges/pin defaults, not every serialized internal
property or visual result. The authoring scripts and actual final node properties
support the declared additive component-space `spine_01` lean adaptation.

Source rifle defaults reference its Relax/Ready/Aim standing and crouched poses,
aim sweeps and original inherited state machine. The transition exports retain
the Ready weight threshold of .25 for aim entry and .75-second minimum source
state time on aim exit. `GetRiflePose` resolves the actual linked rifle machine and
its `Aiming` state, rather than equating an aim request with an achieved pose.
Ready/Relax requests release aim and retain source transition timing; they no
longer force an immediate isolated static pose. Actual pitch/yaw alignment,
transitions and grip quality have not been observed in this review.

The real source/child function results agree: forward/side/back walking
**200/180/150**, running **500/350/300**, crouch **225/200/180**, and sprint
**700/700/700 cm/s**. These are CDO function evaluations, not runtime measured
velocities. Source rotation uses aim/strafe requests; actual velocity direction
feeds `Curve_StrafeSpeedMap`. Its PreCMC update sets source acceleration/braking,
friction and speed. The AI does not request sprint. Mobile fire consumes CMC's
actual speed limit, but GL01-R2 blocks its tactical movement producer.

Ordinary valid skeletal hits leave locomotion authority intact and temporarily
simulate the affected subtree with bounded parent-space drives; no pelvis/world
holding control is created. Strong/clustered hits and get-up interruptions request
source ragdoll. The source snapshot, face-up/down montage selection and CMC
restoration remain, with the adapter's bounded settling/clearance gate. Lethal
damage selects Dead; a post-source tick disables corpse angular motors; corpse
contacts retain impulses. These are supported code paths **conditional on a valid
skeletal contact**, not a passing end-to-end hit test in the presence of GL01-R1.

Reset destroys the owned source pawn/controller and display actors, clears local
controls and increments `PoseEpoch`. The new tick calls `AActor::Tick`, not either
historical balance tick; the inherited recovery physics component starts disabled.
AI deadlines, local-hit/get-up timing and source animation remain on world time.
The existing global slowdown/player compensation and finite-projectile clocks are
unchanged. No runtime reset/slowdown/physical result is claimed.

## Targeted source-config applicability

`ABP_SandboxCharacter.Update_CVarDrivenVariables` has six console reads. The four
scoped reads resolve to source defaults in the final editor evidence:
translation radius **30**, thread-safe animation **true**, experimental state
machine **false**, experimental debug **false**. The radius adaptation is necessary:
the owner's existing global radius default is 0. The scoped values preserve that
owner setting while supplying the source graph its intended value.

The remaining reads are `DDCvar.MMDatabaseLOD`, already defined as 0 in the host
and source config, and `a.AnimNode.OffsetRootBone.Enable`, registered as 1 by the
installed AnimationWarping module (`AnimNode_OffsetRootBone.cpp:19`). No host config
override of the latter was found. The source attribute-root-motion default is also
false in the existing host config. Source camera selection is behind the
PlayerController cast. This targeted dependency trace supplies no reason to
activate the source demo map, game mode or unrelated rendering defaults. It does
not claim an arbitrary live console override or visual presentation was tested.

## Reused checks, review outputs and remaining owner testing

Reused Candidate01 evidence: `Evidence/build-04.json` and `.log`,
`asset-checks-02.json`, `check-cleanup.json`, `final-asset-check.json`,
`source-seams.json`, `motion-gate-check.json`, `motion-gate-build.log`,
`preservation-check.json`, source graph/default exports and the intake/revision
manifests. The final native DLL SHA-256 is
`178c50517627fb835ce07ef0aabce921aa1abe4a6199795d36977d35d06da472`.
Blueprint camera deprecation warnings are retained source warnings; they are not
new enemy camera failures. No build, passing native test, full feature matrix or
historical gameplay run was repeated.

Review-only outputs:

- [technical-evidence.json](../Saved/GASPALSLocomotion01/Review/technical-evidence.json)
  records scoped identities, complete intake presence, full-path graph comparison,
  concrete CVar reads, source speed/default results and dependency boundaries.
- [graph-excerpts.txt](../Saved/GASPALSLocomotion01/Review/graph-excerpts.txt) contains
  readable source movement, overlay transition, ragdoll and CVar wiring.
- [finding-source-excerpts.txt](../Saved/GASPALSLocomotion01/Review/finding-source-excerpts.txt)
  preserves the exact numbered consumer/producer excerpts for the two findings.
- [inspect_candidate.py](../Saved/GASPALSLocomotion01/Review/inspect_candidate.py)
  reproduces these file/export inspections without an editor or game world.

No implementation, assets, profiles, issue/task state, registry, historical
evidence or commits were modified. No editor connection or agent PIE/gameplay,
firing, simulation or performance test was used. Source/artifact preservation and
controller closure responsibilities remain unchanged. Corrections must preserve
Candidate01 and use a new candidate/evidence path; review closure should be limited
to GL01-R1/GL01-R2 and their directly affected seams.

After those technical defects are closed, the owner still judges source motion
equivalence, directional starts/stops/turns, rifle aim transitions and alignment,
actual mobile fire and crouch/lean use, local hit feel, knockdown/get-up/death/corpse
response, and reset/slowdown through those transitions. Build/source PASS cannot
replace that owner Play judgment. Packaging and multiplayer remain outside this
editor-prototype review.
