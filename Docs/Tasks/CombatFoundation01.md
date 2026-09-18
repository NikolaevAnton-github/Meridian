# CombatFoundation01: meaningful rifle hits and ammunition

Multica issue: **MSQ-68**.
Stage 1 of [CombatSlice01](CombatSlice01Plan.md). Prerequisite: inspect the live
PurchasedArms06 baseline and preserved PurchasedArms02 source limitations.
Implementation authorized by the owner's
[projectile/time policy and start instruction](../Approvals/CombatFoundation01-OwnerScope01.json).
The controller dispatches this child only; successor tasks remain undispatched.

## Scope

- Implement one authoritative shot event for the existing rifle: validate fire
  mode/state/ammunition, consume one round and launch one finite-flight bullet.
  Apply damage once at collision, not immediately along the aim ray. Keep existing
  firing cadence, recoil, sound, muzzle flash and paired animations. Sweep travel
  in gameplay world coordinates with an aim-consistent muzzle/near-cover policy;
  the FP rendering scale is not ballistics. A mathematical projectile is sufficient;
  no per-bullet rigid-body model is required.
- Provide an explicit projectile simulation-time seam for later world slowdown
  and exact stop. All bullets, including the player's, follow world time; the
  player will retain normal movement. At zero scale bullets retain position and
  velocity for resumption. Their simulation age must not advance as world time.
  Collision must still detect a moving player crossing a suspended bullet.
  Retain shot/shooter attribution without permanent owner immunity: own bullets
  may damage their shooter after bounded geometric launch clearance. Verify the
  self-hit event contract now; player health remains in PlayerSurvival01.
- Add a resettable damageable target with health, clear hit/destruction response
  and minimal impact feedback for existing stone/metal surfaces. Effects must
  have bounded lifetime/count and must not edit accepted surface materials.
- Replace the demo counter underflow reset, reload non-refill and independent
  V empty-fire mode together. V selects implemented firing modes; an empty
  magazine determines dry fire. Preserve the 30-round magazine as the initial
  prototype capacity; expose reserve, damage and other balance values as tuning.
- Define partial/empty reload accounting, the single transfer notify, interruption
  and action-lock policy. R selects the appropriate reload; reconcile Q/E variants
  with the same ammunition state so none can create rounds. Magazine inspection
  is read-only. Reloads transfer only available reserve and never exceed capacity.
- Provide a minimal readable ammo/reserve display and target feedback, explicitly
  a prototype UI. Document bindings and a small repeatable lobby target setup.

## Acceptance

1. A valid semi/automatic shot consumes exactly one round and launches one bullet,
   with finite travel before at most one damaging collision. Misses, thin walls
   and near-cover obstruction behave consistently in hip/ADS, including high-speed
   travel. No duplicate damage from paired animation notifies.
2. Zero ammunition prevents damaging shots and plays bounded empty feedback;
   held fire cannot auto-refill the magazine or create effects indefinitely.
3. Partial, empty, low-reserve and no-reserve reloads have correct accounting.
   Repeated input and interruptions cannot duplicate transfer; blocked shots
   during reload do not apply damage. Relevant moving/aimed transitions still work.
4. Target health/death/reset, magazine presentation and prototype UI agree with
   authoritative values. Reloading saved packages retains the implementation.
5. Focused development probes at projectile time scales 1, a reduced value and
   exactly 0 demonstrate travel scaling, frozen position/age, clean resumption,
   and at-most-once collision with a player moving through a suspended bullet.
   Own-shot damage events are eligible after launch clearance, without immediate
   spawn self-hit. This is a foundation probe, not the later time ability.
6. Projectile/effect lifetimes and counts are bounded; reset/end of PIE removes
   transient state. Capacity or safety policies are explicit and cannot create
   phantom damaging shots, unbounded allocation or silent ammunition refill.

No enemies, player health, abilities, new weapons or physical destruction here.
Follow the shared execution, preservation, focused verification and closure rules
in the parent plan. Deliver `Docs/CombatFoundation01.md` and scoped Saved evidence.

## Execution and handoff

Use the existing Multica Unreal executor, Astra/max/standard, concurrency one.
Verify actual native settings as well as the saved profile. Confirm live project,
map, PIE and dirty packages through official Epic MCP before mutations; preserve
owner-owned unsaved work. Snapshot affected files before edits. The pre-existing
`Config/DefaultEngine.ini` edit belongs to the owner and must remain byte-identical.
Keep the retained lobby geometry, materials, atmosphere and source history intact.
Prefer temporary gameplay actors spawned for the prototype over map authoring.

Worker owns source/Blueprint integration, a narrow reusable task verification
adapter if needed, and `Docs/CombatFoundation01.md`. Reuse existing tooling and
perform only affected-behavior checks, including relevant moving/aimed/airborne
fire transitions. Do not run a full animation matrix or introduce a new harness.
Record chosen tuning, reload commit/interruption rules, collision/time policy,
controls, sources, disk growth, changed paths/hashes and precise evidence under
`Saved/CombatSlice01/CombatFoundation01/Worker/`. Leave a saved, verified lobby
ready for Play, preserving owner session state. Controller owns review, issue
administration, registry decisions, closure and local commit; worker does not
dispatch successors or commit. Continue through bounded corrections.
