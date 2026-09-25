# MSQ-152: Candidate01 / Build02

2026-09-25. Controller scope/evidence acceptance passed. Independent technical
review is waived by [the later owner instruction](Approvals/LobbyPlaytestFix01-ReviewWaiver01.json);
MSQ-153 was cancelled before execution. Owner play/layout acceptance remains pending.

The saved `/Game/Maps/L_OpeningLobby_PainterStone01` contains **14 distinct default
demo specimens**. Eleven were added; the original three and all 132 original actor
records were preserved. LMB fires, V changes mode, R reloads, Y toggles the existing
slowdown preview, and F6 restores the specimens. Y retains its existing requirement
that the physics preview fixture is enabled (F10).

## Interrupted firing

The reproduced cause was the projectile history guard treating the changing
aggregate bounds of fractured NGD collections as rigid blocker changes. It called
`CancelFiringSession`, inventing a release while Enhanced Input still held LMB.
One concrete hit caused 182 geometry barriers during the original auto trace:
the magazine still contained rounds, the controller key stayed down, and the rifle
latched off. Four semi presses during fresh debris produced only two shots.

`CombatProjectileWorld` now excludes aggregate fragment extents from the rigid
history comparison **only for opted-in NGD geometry collections**. Registration,
collision-response and component-transform barriers remain. Finite sweeps still
query live Chaos collision; the guard never reconstructed per-piece history.

Unsafe intervals now suspend rifle scheduling without clearing the physical hold.
Missed auto rounds are discarded. A pending semi press can resume once at the new
boundary while held; releasing it cancels that deferred intent. Explicit F6/reset
continues to cancel firing. Minimum shot spacing and ammunition debit remain on
the accepted-launch path; cover checks are unchanged.

A second reproduced interruption occurred after an empty magazine was reloaded
while LMB remained held: the dry-fire latch stayed set despite a successful ammo
transfer. A positive committed transfer now clears that latch. It does not create
a new semi press or change reload-notify authority.

## Demo coverage and placement

`DemoMap` contains 21 breakable instances and 14 distinct configurations, grouped
by data asset, behavior properties, collection, materials/overrides, scale and
collision settings. Every group has a matching saved lobby instance. The catalog
also contains `DA_Pillar_Small_Concrete_Simplified` and
`DA_Pillar_Small_NOFXEXAMPLE`; these are performance examples absent from the
default demo, excluded from this assortment. Duplicate chairs, vases and mugs are
not copied repeatedly. The plaster panel and wooden frame are individually
visible specimens in separate bays.

All sources are under `/Game/NextGenDestruction/Blueprints/DataAssets/Destructible/`.
All instance scales are `(1,1,1)`, pitch/roll zero. Coordinates are centimetres.

| Label | Source data asset | Location | Yaw |
| --- | --- | --- | --- |
| `NGD01_ConcretePillar` | `DA_Pillar_Small_Concrete` | -840, 700, 0 | 0 |
| `NGD01_WoodenChair` | `DA_Chair_Wood` | 0, 700, 0 | -90 |
| `NGD01_CeramicVase` | `DA_Vase` | 840, 700, 0 | 0 |
| `LPF01_LargeConcretePillar` | `DA_Pillar_Large_Concrete_Square` | -1900, 700, 0 | 0 |
| `LPF01_WoodDesk` | `DA_Desk_Wood` | -1789.323204, 603.68, 0 | 0 |
| `LPF01_DiningTable` | `DA_DiningTable_Wood` | 1680, 700, 0 | 0 |
| `LPF01_CoffeeTable` | `DA_CoffeeTable_Wood` | 1010, 750, 0 | 0 |
| `LPF01_PlainMug` | `DA_Mug01` | 988, 750, 64.107742 | 0 |
| `LPF01_MarbleMug` | `DA_Mug02` | 1032, 750, 64.107742 | 0 |
| `LPF01_SmallGlass` | `DA_Window_Small` | -1680, -700, 76.102371 | 0 |
| `LPF01_PlasterWall` | `DA_Wall_Plaster` | -968, -700, 0 | -90 |
| `LPF01_WoodFrame` | `DA_Wall_WoodenBeams` | -128, -700, 0 | -90 |
| `LPF01_WoodWall` | `DA_Wall_Wood` | 840, -700, 125 | -90 |
| `LPF01_LargeGlass` | `DA_Window_Large` | 1680, -700, 176.928711 | 0 |

The added actors have the `LobbyPlaytestFix01` tag and
`LobbyPlaytestFix01_DemoProps` folder. Remove those eleven to remove the expansion.
The mugs rest on the vendor coffee table. No architecture, lights or vendor
packages were edited. Conservative actor bounds have no penetrations above
0.25 cm; 45 cm sphere sweeps at Z=100 along X=-1900..1900 are clear at Y=0 and
Y=+/-1000. These are focused placement checks, not a new whole-lobby navigation gate.

The source marble mug uses per-instance material overrides. `NGDPropComponent`
captures those overrides before damage and restores them before replacement actor
construction. `SpawnPropWithMaterials` is the bounded placement entrypoint for
that source configuration. This also preserves the glass's initial materials on
reset after the vendor's material switch during breakage.

## Verification and evidence

Evidence root: `Saved/LobbyPlaytestFix01/Candidate01/`. **42 focused checks pass**
in `focused-checks.json`, including a passing group of 14 native contracts.
`Scripts/LobbyPlaytestFix01/verify.py <new-report-name> --input` reads the evidence
and checks current candidate hashes; it does not rerun gameplay or replace evidence.

| Evidence | Result |
| --- | --- |
| `before-auto-hit.json`, `after-auto-hit.json` | One stopped shot before; 30 sustained rounds after, 85 ms action-clock intervals |
| `before-semi-active-debris.json`, `after-semi-active-debris.json` | Four presses: two shots before, four after |
| `before-empty-reload-held.json`, `after-empty-reload-held.json` | Positive transfer resumes held auto; exactly 2+4 rounds, one transfer, no reserve left |
| `after-auto-hitch-recovery.json`, `after-semi-hitch-held.json`, `after-semi-hitch-released.json` | Auto resumes without debt; held semi emits once; released deferred press emits zero |
| `after-slowdown-transitions-valid.json`, `after-slow-empty-reload-held-valid.json`, `after-mode-semi-slow.json` | World/bullets/rifle 0.25, player movement 0.65; mode switching, repeated semi and finite reload pass |
| `after-glass-near-cover.json` | Safe view-origin launch fractures glass; following shot crosses the opening |
| `after-mug-variant-reset.json` | Actual rifle fractures marble mug; F6 restores all 14 intact specimens and exact materials |
| `native-contracts.json` | Thin collision, contact ordering, explicit reset cancellation, rigid geometry barrier and held-input recovery pass |
| `demo-inventory.json`, `demo-map.t3d`, `placement-final.json` | Complete source/configuration/transform reconciliation |
| `spatial-final.json`, `route-clearance.json` | No specimen/architecture overlap and clear retained circulation strips |
| `final-views.json`, corresponding `*-final.png` | Eleven native editor views show every specimen, including both mug materials |
| `pie-visual-destruction.json`, `pie-concrete-broken.png`, `pie-visual-reset.json`, `pie-concrete-reset.png` | Actual game viewport destruction/reset views |
| `editor-before.json`, `Before/`, `before-hashes.json`, `editor-reopened.json` | Recoverable initial map, preserved original actor records, final saved-map reload |
| `Build02.log`, `Build02.json`, `native-settings.json`, `storage.json` | Successful build, exact source/binary hashes, Astra/max/default with fast disabled, 106.59 GB project footprint |

Runtime inputs enter through PlayerController key events and Enhanced Input;
weapon public-API calls are not the input proof. Ammo probes only prepare explicit
finite test inventories. Enemy combat was temporarily disabled in isolated PIE
cases to prevent unrelated hits; the preview fixture remained enabled for valid
slowdown checks. No fixture/settings changes were saved to the map.

## Fingerprints, limits and review handoff

- Map SHA-256: `94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57`.
- Build02 DLL SHA-256: `dcccb0c3a1ae088c57a3b42e20d852c33e158611c196be8beb0924d642f0fb01`.
- `Build02.json` records all six changed C++ source/header fingerprints;
  `delivery-final-manifest.json` indexes final code, map, scripts, documents and evidence.
- All **481 vendor packages** and five protected pre-existing owner/controller
  files remain byte-identical. The original 132 actor property records match.
  New unrelated controller files are outside this delivery.

One editor-only GeometryCollectionSceneProxy assertion occurred while moving
newly constructed collections and saving (`Build01-editor-crash.log`). The map
finished saving. A full restart recovered it; subsequent save, reload, rendering
and PIE sessions succeeded. This is retained as an editor warning, not an asserted
engine fix. Existing StructUtils deprecation and GASPALS initialization-array
warnings remain outside scope.

The first two slowdown traces had a disabled preview fixture and therefore never
entered slowdown; `verification-isolation.json` identifies them as superseded by
the `-valid` traces. Early end-bay placements were revised because owner wall
shells obscured them. Their images/records remain preserved. The two early
`rifle-concrete-*.png` files captured the editor viewport during PIE, so only the
later `pie-concrete-*.png` images are game-view evidence.
The floating PIE photo session also received additional input between captures
(30 total shots and a reload). Its screenshots illustrate appearance; numerical
ammo/cadence/reset assertions use the bounded verification traces listed above.

The editor handoff is the saved expanded lobby with PIE stopped and temporary
performance settings restored. Owner play/layout judgement remains separate;
independent technical review was subsequently waived for this task. No claim is made about arbitrary
desktop focus/UI capture; the diagnosed interruptions were proved inside the
actual engine input path. No MSQ-150/151 or AI successor work was performed.

Changed production files: `CombatProjectileWorld.cpp`, `CombatRifleComponent.cpp/.h`,
`CombatTimingProbes.cpp`, `NGDPropComponent.cpp/.h`, and the retained lobby map.
Supporting changes are confined to `Scripts/LobbyPlaytestFix01/`, this handoff,
the assigned task document and generated evidence. Controller owns the local commit,
status transition and acceptance.

Controller acceptance is recorded in `Saved/LobbyPlaytestFix01/Controller/acceptance.json`.
All 19 delivered file fingerprints matched before these administrative closure edits.
The 42 evidence checks were re-evaluated. One full-file preservation comparison
needed an explicit lifecycle exception: Multica removed its generated AGENTS runtime
suffix after executor completion. The archived pre-run durable instruction bytes
match the current file and controller-start Git baseline exactly, apart from the
runtime separator's trailing newlines. All other preservation checks pass. Historical
manifests and failed/completed evidence remain unchanged; no rebaseline was performed.
