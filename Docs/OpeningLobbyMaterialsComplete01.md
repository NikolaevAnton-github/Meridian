# LobbyMaterials-Complete01 / WorkerCandidate01

The complete material batch is implemented on the sole current map,
`/Game/Maps/L_OpeningLobby_PainterStone01`, for fresh independent review.
All 90 remaining proxy slots were replaced; the 17 accepted bindings and every
nonmaterial scene property are preserved. New batch bytes and final atmosphere
are not owner accepted.

## Exact package

- Identity: `Saved/OpeningLobby/MaterialsComplete01/Worker/identity.json`.
- Manifest: `Saved/OpeningLobby/MaterialsComplete01/Worker/manifest.json`.
- Map SHA-256: `57dd3a44c1e5e238b14fd7054cd23d05f8411787b91c506711ca466226680d10`.
- New native source: `Assets/Source/OpeningLobby/MaterialsComplete01/Ceiling.spp`.
- SPP SHA-256: `392a4c5bc63756c6c5ad4771c675715fe354475a2555d23e366e7f8cf963849e`.
- Final author revisions: ceiling Initial, glass QARevision01.
- Exact rollback: `Worker/Before/L_OpeningLobby_PainterStone01.umap`, SHA-256
  `abc72118717b8333a109fdeeaf1583485a3e7b35badced84204e9fcc130ebc92`.

The immutable manifest binds the map, editable sources, UE assets, coverage,
preservation checks, native readback, matched images, helpers and rollback.
`manifest-verification.json` records its hash. All evidence paths below are
relative to `Saved/OpeningLobby/MaterialsComplete01/Worker/`.

## Complete coverage

| Family | Final slots | New assignments | Source |
| --- | ---: | ---: | --- |
| Architectural stone and wall | 44 | 40 | Accepted Stone01, unchanged 240 cm stochastic world projection |
| Floor and black strips | 3 | 0 | Accepted Floor01 |
| Charcoal hardware | 45 | 35 | Accepted Metal01, unchanged 120 cm satin coating |
| Ceiling and soffit | 9 | 9 | New native Painter mineral plaster |
| Optical glazing | 6 | 6 | New native UE fixed/leaf graphs |
| **Total** | **107** | **90** | **17 accepted bindings preserved** |

`coverage-plan.json`, `coverage.json` and `coverage.csv` identify all actor,
component and slot identities, original/effective final paths and reasons.
There are no invisible mesh exclusions and no effective proxy/default/error
bindings. All 35 metal replacements belong to the entrance collar, mullions,
transoms and meeting stile. The inner future logo field is blank opaque stone.
RA01_Shoulder_-1 now shares the accepted +1 material exactly.

## Native sources and optics

Painter 12.1.4/API 0.3.5 authored three new Fill layers in one group: an opaque
green-grey plaster base, procedural mineral roughness and procedural microheight.
BaseColor is intentionally calm and uniform; fine structure is in roughness and
normal. The new source uses native `bnw_spots_2`, seed 83, procedural scale 8,
UV repeat 2, authored channel opacities 0.08 roughness and 0.001 height. It is
neither a stock smart-material application nor externally generated pixels.
The accepted source was clean before switching projects. The bridge required a
context backup; `ContextBackup/Metal.spp` is that backup, not a new authored family.

The final .spp was saved, closed/reopened and regenerated without changing its
bytes. BaseColor, DirectX Normal and packed ORM match their original exports
exactly. See `exact-regeneration.json`, `Native/`, canonical `Exports/Final/`,
`Exports/ReopenedFinal/` and the source `recipe.json`. Actual ORM roughness is
192–212/255 (mean 201.53/255), AO 1 and metallic 0. Normal X/Y range 125–130/255;
the very fine relief does not create modeled features.

Native UE5.8.1 Substrate glass uses colored transmittance, thin-surface Simple
Volume Slab BSDF, TransmittanceToMFP and F0 0.04. The four fixed panes use neutral
transmission 0.90, scattering albedo 0.45 and roughness 0.32. The two entry leaves
use neutral transmission 0.94, scattering albedo 0.04 and roughness 0.09.
No emission or texture is connected to either glass graph. QARevision01 removed
a faint mauve cast by neutralizing transmission RGB; `QAInitial/` preserves the
initial images, graphs and graph audit. No ceiling QA revision was needed.

All six new asset packages were reloaded from disk through native
`EditorLoadingAndSavingUtils.reload_packages`. `graphs-reloaded.json`,
`native-material-audit.json`, `glass-audit.json` and `live-material-audit.json`
verify saved graphs, channel import settings, compiled statistics, connected
nodes and allowed dependencies. The scene uses seven effective materials:
stone, floor, strip, metal, ceiling, fixed glass and leaf glass.

## Visual and runtime evidence

Both actual OwnerReferences01 PNGs and all eleven before/final view pairs were
inspected. `Before/` and `Final/` contain native 1920×1080 HFOV90 images with
matched pose, world tick, exposure and renderer metadata. The eleven pairs cover
entrance, inner end, side aisle, repeated bays, stone oblique, ceiling upward,
terminal/service-door upward context, near oblique entrance glass, checkpoint,
elevator and whole hall. `Final/entrance-whole-90.png` adds a complete entrance
elevation from standing height. No image processing or generated presentation
pixels were used.

The broad architecture now shares the accepted dark mineral palette. The ceiling
is quieter and less polished. Existing strong light highlights remain visible,
particularly on the accepted stone response; no light or exposure was altered.
The preserved central columns dominate the whole-hall sightline. The entrance
leaves are dark against the existing empty exterior; fixed panes carry soft
neutral reflection/scattering. This is a material-complete baseline under the
existing lighting, not the final reference atmosphere.

`Transmission/` is a separate diagnostic, not an exterior design or route claim.
A temporary flying pawn at 172 cm eye height looked inward through the existing
panes. The final glass transmits the actual hall; removing pane visibility gives
a closely matching scene; temporarily assigning accepted opaque stone to those
same six PIE mesh slots occludes it. The leaf sample has mean display RGB 39.25
with glass, 40.78 without panes and 0 with the opaque control. The fixed sidelight
sample is 5.62, 6.53 and 0 respectively. These establish scene transmission, not
calibrated optical transmittance or refraction accuracy. All diagnostic visibility,
material and pawn state was restored before PIE ended. See
`transmission-verification.json` and the explicit restoration records.

`Movement/runtime-verification.json` records real PlayerController key input and
CharacterMovement ticks: 169.82 cm forward and return to 9.94 cm from the start,
131 movement binding samples, grounded/possessed throughout, no errors and all
keys/callbacks released. Still-camera placement is separately labeled.

## Preservation, storage and handoff

Exact reflected comparisons cover 127 actors and 148 components, world settings
and renderer state. Only the 90 scheduled override arrays differ. All accepted
bindings, geometry, mesh defaults, collision, owner checkpoint position,
lighting, gameplay and configuration bytes remain unchanged. `accepted-history.json`
resolves the three accepted manifests through their exact historical archives;
no old evidence was edited or rebaselined.

`RestoredFinal/` records the sole clean current map, PIE off. Capture settings and
Slate throttling were restored. Painter remains on the clean new Ceiling source.
`storage.json` records no-junction project/lobby totals, batch growth and limits.
No history or assets were deleted, and no registry, config, task administration,
installation, paid service, commit, push or later dispatch was performed.

The controller can hand this exact package to the fresh independent reviewer
against all ten task criteria. Author verification is not independent review or
owner acceptance.
