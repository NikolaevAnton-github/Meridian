# EnemyPrototype01: reusable enemy asset and damage contract

Multica issue: **MSQ-69**.
Stage 2 of [CombatSlice01](CombatSlice01Plan.md).
Predecessor: [CombatFoundation01](CombatFoundation01.md).

## Scope

Audit already available, lawfully reusable character/animation sources and select
one explicitly identified temporary enemy representation. Verify skeleton, scale,
locomotion, weapon hold/fire, hit/death response and physics compatibility in the
installed engine. The purchased FP arms and paused original protagonist are not
an assumed enemy asset source. Keep immutable sources and document provenance.

Prepare one enemy actor with collision, hit regions, health/damage receiver and
minimal animation/physics presentation; AI and player damage follow separately.
Produce `EnemyPrototype01-Contract01`: asset paths and fingerprints, region/bone
mapping, collision policy, animation coverage, and measured suitability for later
limb separation with closed surfaces and stable physics, including any bounded
segmentation/capping adaptation required for the selected reusable source. A
lawfully editable imported source is sufficient; a pre-existing native DCC file
or already-severable mesh is not mandatory. Do not claim that a
capsule/mannequin proves a final enemy appearance or body-destruction capability.

Use the existing damageable-target firing path to exercise idle/moving hit and
death presentation. Record replacement boundaries so later art does not force a
rewrite of combat logic. Final enemy styling and custom model production are not
part of this asset-reuse task.

## Acceptance and asset gate

- One repeatable prototype loads and can receive rifle damage, show a hit and die
  without invalid poses, runaway physics or FP assets used as a complete body.
- The contract distinguishes verified reuse, missing animations and unsupported
  damage regions. EnemyCombat01 can use a clearly labelled technical placeholder.
- Built-in primitive debug actors are allowed to prove technical behavior, but
  do not satisfy an unsupported body-destruction or final-art claim.
- EnemyBodyDamage01 additionally requires an actually suitable, editable source
  or verified feasible bounded adaptation under this asset contract.
  If none exists, report concrete options and the missing capability for owner
  scope/selection; do not purchase, download unrestricted content, resume paused
  modeling or manufacture approval. New model work needs a separate named concept
  and production scope under the standing rules.

Follow the parent plan's focused review, preservation and closure requirements.
Deliver `Docs/EnemyPrototype01.md`, the contract and visual/runtime evidence under
the task's Saved directory. No AI behavior, new enemy faction canon or final-art
acceptance is implied.
