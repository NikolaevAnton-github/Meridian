# GrenadePrototype01: direct player grenade prototype

2026-09-29. Implemented directly under the [owner scope and workflow override](Approvals/GrenadePrototype01-OwnerScope01.json): no Multica task and no independent review.

G starts the existing purchased-arms quick-throw montage. Its evaluated progress
releases one sphere at 0.65 seconds; holding G does not repeat. The reusable
prototype has no inventory UI. The sphere is the existing NGD `BP_Grenade`, with
its two-second world-time fuse, sound, explosion, camera shake and strain field.
The launcher uses the vendor bouncing projectile movement, 1200 cm/s throw speed,
240 cm/s upward bias, and a 400 cm blast radius. At most eight transient grenade
actors may coexist. Hidden grenade movement stops on detonation; the remaining
effect actor expires four seconds later.

The launcher preserves source action locks and ignores G during reload/busy
actions. Release follows the actual montage instance; an interrupted gesture
cannot release later. A sphere sweep prevents release through a nearby wall.
F6 retires pending throws, grenades, their fields and queued Chaos commands before
the existing specimen reset. PIE end also clears transient state. No new enemy
damage/health system or debris optimizer is included. Blast strain retains the
vendor spherical behavior; this prototype does not add wall-occluded explosion
damage or navigation/cover integration.

## Focused self-check and preservation

- `Saved/GrenadePrototype01/build03.log`: Development Editor build passed. Loaded
  DLL SHA-256: `6b5a3125dd69a84052f798805c062cd10d71c4abdc523f3537b3b619a28564a3`.
- `throw02.json`: real G held for five seconds produced one release and one
  explosion; the action lock recovered and the hidden grenade remained stationary.
  The measured field scale is 4 (vendor base radius 100 cm).
- `blast03.json` identifies a runtime-only blast fixture: after initial free
  flight the grenade was parked beside an owner-added column. Python break-event
  callbacks did not provide usable counts. Native NGD adapter state subsequently
  confirmed fractured owner-added columns; see `native-blast-result.json`.
  The owner also made manual throws/shots during this PIE session, so its aggregate
  counts are mixed input evidence, not an isolated grenade benchmark.
- `after-reset.json`: no pending throw, no live grenades, and no busy action lock
  at the observation after F6. Slowdown timing has not been separately measured.
- Before restart, 155 editor actors/placements were captured and owner changes
  saved. The same inventory was confirmed after reopen. Map bytes still matched
  `owner-map-saved.umap` at final disk verification. No saved test actors were added.
  An already-dirty `BP_Grenade` package encountered during inspection was snapshotted
  before saving; its working bytes, the owner map and `Config/DefaultEngine.ini`
  remain excluded from this code commit. Do not restore old bytes over these edits.

The owner began manual play during checks. Further input automation was stopped;
current editor/play state was left under owner control. Owner play judgement is
separate from these focused self-checks.
