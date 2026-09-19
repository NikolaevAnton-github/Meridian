# EnemyPrototype01 / MSQ-69

Worker candidate prepared on 2026-09-19 over MSQ-82 commit `be8d2ae`.
One removable Manny prototype now receives the existing rifle's finite-flight
damage, reacts, dies through ragdoll physics and resets. It is a technical
placeholder with scripted motion preview, not enemy AI or an approved enemy design.
Independent review, controller acceptance, registry decisions and the closure
commit remain with the controller. No successor is dispatched.

Scope: [task](Tasks/EnemyPrototype01.md),
[owner start](Approvals/EnemyPrototype01-OwnerStart01.json).
The named contract is `Docs/EnemyPrototype01-Contract01.json`.
Evidence paths below are relative to
`Saved/CombatSlice01/EnemyPrototype01/Worker/`.

## Play and implementation

Open `/Game/Maps/L_OpeningLobby_PainterStone01` and Play. The projectile manager
spawns one `AEnemyPrototypeCharacter` at `(-1100, 0, 100)` cm, yaw 180 degrees.
Its capsule settles on the retained floor. The original three targets remain;
the central target is behind the enemy. All these actors are transient.

| Control | Behavior |
| --- | --- |
| LMB / RMB / V / R | Existing finite-ammunition firing, aiming, mode and reload. |
| F6 | Clear projectiles/feedback and reset enemy/targets. Ammunition is unchanged. |
| F7 | Toggle the enemy's bounded left/right movement preview; this is not AI. |
| Stop / Play | Clean world teardown and a fresh 100-health enemy, 30/90 player ammunition. |

Prototype tuning is 100 health and the retained 25-damage rifle: four hits kill.
All supported regions currently use the same damage. Preview speed is 95 cm/s,
with reversal around +/-100 cm from its initial lateral position. A hit plays the
0.7-second template response and pauses translation, then returns to the selected
idle/walk. Sequence transitions are immediate; no locomotion blend tree, turn,
crouch or production foot-placement system is claimed. `PreviewFire` is an
explicit presentation probe with no enemy shot, muzzle effect or player damage.

`UCombatRifleComponent::TryShot` remains authoritative. The aim query additionally
considers the enemy's bone volumes at the shot birth time and chooses the nearer
world obstruction or enemy. It applies no damage. The projectile manager consumes
finite-flight bullets on the earliest swept world/character contact, then delivers
ordinary point damage carrying the region's representative `BoneName`.

The movement capsule is not the enemy's damage shape. There are **28 sampled
spheres** bound to head, spine, pelvis, arms, hands, legs and feet. The manager
interpolates their centers between rendered-frame bone samples at each existing
birth/substep boundary. Its per-bullet birth snapshot prevents contacts with limb
motion before the bullet existed. Moving limbs can cross stopped bullets. This
is a bounded sphere approximation with linear pose history, not triangle-accurate
skin collision or an angular subframe animation simulation. The contract specifies
the radii and unsupported detail. Existing player capsule/self-hit behavior stays
on its retained path; the full firing-timing matrix was not repeated.

At zero health the capsule and damage volumes turn off, movement stops, and the
unchanged template physics asset simulates against WorldStatic only. The corpse
does not block bullets or the pawn, cannot take more damage, and is put to sleep
after six world seconds. A bounded pelvis impulse uses the incoming shot direction.
Reset clears rigid-body linear/angular velocity, disables simulation, reattaches
the mesh, refreshes its idle pose and restores health. No severed bodies are created.

## Source selection and coverage

The chosen body is the complete installed UE **Manny Simple**, with its template
`SK_Mannequin` skeleton, `PA_Mannequin`, materials and textures. It was already
preserved in the PurchasedArms01 archive; the copied bytes remain identical.
The source engine resource is
`D:/UE_5.8/Templates/TemplateResources/High/Characters/Content/Mannequins/`.
This is generic template reuse, not resumed original-protagonist production.
The UE EULA identifies Templates as Examples and permits modifying Licensed
Technology under its terms: [official UE EULA](https://www.unrealengine.com/eula/unreal).
This task uses the installed content inside the existing Unreal project.

The owner-supplied Infima pack also contains full TP Manny meshes and additive
idle/fire sequences. They were audited, but the template provides a coherent
body locomotion/hit set without changing the active FP skeleton. Unselected audit
copies are preserved in `ExcludedAuditCopies/`; their source archives are untouched.
The existing `SK_TFA_AR` is attached to the enemy's right hand as a visual rifle
core. It has no weapon logic or collision. The enemy does not include the complete
FP modular attachment/magazine assembly. The owner's purchase statement remains
the local provenance evidence; the receipt/tier is not in the source directory.
See [vendor product](https://www.fab.com/listings/1ae386ab-4a40-4a0f-ac17-621e2d9d1028)
and the existing [source audit](PlayerAnimationAudit01.md). No new content was
downloaded and no broader asset redistribution entitlement is asserted.

| Coverage | Evidence and boundary |
| --- | --- |
| Complete mesh / scale / skeleton | UE 5.8.1 loads the actual body with 89 mesh bone entries; FBX contains 88 exported bones. Measured bind height 180.524 cm. |
| Idle / weapon hold | Template rifle idle, actual lobby views in `Video/Candidate06-HoldFirePresentation*`. Rifle-core attachment is a temporary presentation; full modular weapon dressing is absent. |
| Left/right locomotion | Template walk copies, in-place settings; actual F7 movement at 30 FPS in `Candidate06-MovingHits.json` and video. |
| Fire presentation | Template fire copy plays and returns to idle; zero enemy bullets and unchanged player ammunition. |
| Hit | One front light hit clip, including hit-to-idle and moving-hit-to-walk recovery. No directional or region-specific authored hit library is claimed. |
| Death / reset | Actual ragdoll, stable rest, repeated-hit safety, F6 and fresh Play. No authored death montage is selected. |
| Other locomotion | Back/forward locomotion, turns, crouch, jumps and AI transitions are not integrated in this prototype. Existing source availability is not runtime coverage. |

Five project-owned animation copies live at `/Game/Development/EnemyPrototype01/`.
They retain their template skeleton and raw tracks, use non-additive playback,
disable root motion and force root lock. Source packages are unchanged. This
allows the authored full pose to play through a single-node instance; additive
data is not accidentally used as an absolute delta pose. The final hard game
dependency closure contains 18 packages including those five copies. Optional
Quinn/control-rig previews and exploratory vendor TP packages are inactive.

## Editable source and later body damage

`Assets/Source/EnemyPrototype01/SKM_Manny_Simple_Export02.fbx` is the selected,
unaltered export of the actual template mesh. `Export01` is the earlier vendor
comparison and is not the selected source. `mesh-topology-audit02.json` records
Blender 5.2.1 LTS importing Export02 with skin groups and armature: 48,705 vertices,
92,178 triangular faces, 88 bones. Its 5,142 open edges are export seam splits;
a disposable merge of coincident vertices at 0.0001 local units yields zero
boundary and nonmanifold edges.

A disposable lower-left-arm selection, plane cut and hole-fill calculation
produces 7,582 vertices / 13,914 faces, 14 cap faces, zero boundary/nonmanifold
edges and about 0.001358 cubic metres of signed closed volume magnitude. This
establishes editable geometry and a feasible bounded cap operation. It is not a
saved, skinned or accepted damage asset. The trial does not establish cap UVs,
interior materials, absence of self-intersection, the retained-body counterpart,
deformed cut-seam continuity or separated-piece runtime physics. The entire-body
ragdoll evidence is not evidence of those missing capabilities.

For EnemyBodyDamage01, use a bounded forearm adaptation of this identified
source: reconcile seam vertices while preserving normals/UVs/weights, prepare
matching stump and detached surfaces, triangulate/validate caps, assign interior
material and a reviewed rigid collision body, then test detachment and reset in
Unreal. Other cuts need their own topology checks. No asset purchase or new-model
selection gate was found for this bounded technical route. Final enemy styling
and new model production still require their separate named concept/owner scope.

## Focused evidence and limitations

`verification-summary01.json` passes **71 checks over 2,403 actual-frame rows**
plus the native collision results. `Candidate06` supplies stationary hits/death/reset, moving hits and
weapon-pose playback. `Candidate07-ActiveRagdollReset` covers resetting a still
moving ragdoll, then killing/resetting it again after explicitly clearing physics
velocity. All final actual-frame cases start with fresh ammunition and run without
simulation overloads or arbitrary-geometry barriers. Passing baseline timing and
purchased-animation checks are reused.

`collision-probe-02.json` verifies seven region mappings, finite-flight damage,
head-volume misses, suspended-bullet contact, birth-history exclusion, six queued
hits producing one death and post-death/reset safety. Its initial thin-cover check
had an invalid test fixture: Unreal rejected assigning a mesh to a Static component
during play. `collision-probe-cover03.json` supersedes only that check after setting
the fixture Movable; the gameplay collision code did not change.

`Video/Candidate06-*` and `Video/Candidate07-*` are the comparable ordinary-speed
gameplay evidence, with real-time frame timestamps and runtime telemetry. Earlier
Candidate01/03 runs exposed recorder/API mistakes. Candidate02 verified early hit
and movement behavior but its nominal death case fired only two semiautomatic
shots; one video lost foreground. Candidate04's official viewport captures show
the editor world and are unsuitable gameplay evidence. Candidate05's native game
screenshots are actual gameplay, but screenshot stalls triggered three known
overload protections. None of these earlier attempts replaces the final ordinary
frame evidence. All are retained unchanged.

`build07.log` is the final successful Development Editor build. The final editor
reload uses the reduced saved asset subset; `handoff-final.json` records clean
packages, stopped PIE and no leaked enemy actors in the editor map. Retained
vendor startup socket/audio warnings are identified in the log; no enemy-specific
animation/physics error remains after the corrected test fixture.

The final candidate/source/evidence SHA-256 lists, storage totals, exact verified
native Astra/max/default settings and controller-facing limitations are recorded
in `handoff.json`, `candidate-manifest.json`, `preservation-after.json`,
`storage-after.json` and `native-settings-verified.json`. Owner Config bytes,
the lobby, original art, purchased FP assets and historical sources are preserved.
