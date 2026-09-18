# CombatFoundation01: meaningful rifle hits and ammunition

Multica issue: **MSQ-68**.
Stage 1 of [CombatSlice01](CombatSlice01Plan.md). Prerequisite: inspect the live
PurchasedArms06 baseline and preserved PurchasedArms02 source limitations.
Preparation only; no run is dispatched by this document.

## Scope

- Implement one authoritative shot event for the existing rifle: validate fire
  mode/state/ammunition, consume one round, perform bounded hit detection and
  deliver damage once. Keep existing firing cadence, recoil, sound, muzzle flash
  and paired animations. Use an aim-consistent world-space trace with a defined
  muzzle/near-cover obstruction policy; the FP rendering scale is not ballistics.
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

1. A valid semi/automatic shot consumes exactly one round and applies at most one
   hit; misses, walls and near-cover obstruction behave consistently in hip/ADS.
2. Zero ammunition prevents damaging shots and plays bounded empty feedback;
   held fire cannot auto-refill the magazine or create effects indefinitely.
3. Partial, empty, low-reserve and no-reserve reloads have correct accounting.
   Repeated input and interruptions cannot duplicate transfer; blocked shots
   during reload do not apply damage. Relevant moving/aimed transitions still work.
4. Target health/death/reset, magazine presentation and prototype UI agree with
   authoritative values. Reloading saved packages retains the implementation.

No enemies, player health, abilities, new weapons or physical destruction here.
Follow the shared execution, preservation, focused verification and closure rules
in the parent plan. Deliver `Docs/CombatFoundation01.md` and scoped Saved evidence.
