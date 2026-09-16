# LobbyMaterials-Complete01 / Correction03: causal glass render calibration

Finish the owner's complete lobby material request and Review01 R1. Do not
repeat blind brightness/scattering changes or a skipped reflection capture.
Correction02 supplies a real neutral far field while preserving every existing
binding, but fixed glass remains too uniform. A focused read-only audit found:

- Correction02 Setup02 used runtime_capture=true while r.ReflectionCapture.Runtime=0.
  Installed ReflectionCaptureComponent.cpp:97-101,790-797 skips that combination.
- Existing Layout03NeutralExposure has both the local front-layer override and
  lumenFrontLayerTranslucencyReflections false. Global Enable=0, Allow=1,
  EnableForProject=0. Installed FrontLayerTranslucency.cpp:70-75 allows the
  postprocess flag OR global Enable, subject to Allow.
- Current glass supports translucent SurfacePerPixelLighting and allows front
  layer translucency. Fixed albedo .92/transmission .70/roughness .50 is above
  the current maximum reflection-tracing roughness .40 and very highly scattering.

These are actual rendering/input causes, warranting a changed diagnostic approach.
Use the now-present far field and calibrate glass with a working local reflection
path. Candidate LobbyMaterials-Complete01/Correction03, Multica Environment
Artist, Astra/high/standard, subscription only, concurrency one, English.

## Narrow superseding scope

This controller task extends prior override restrictions only to the existing
Layout03NeutralExposure volume's two front-layer translucency reflection flags,
plus six glass component bindings to new native material variants. This is a
material-rendering correction needed for the requested full result, not a final
lighting/atmosphere task or new owner family gate. No global cvar/config changes.
Preserve all other existing postprocess values, light values, exposure, renderer
configuration, neutral far-field actor/material, geometry, routes, collision,
gameplay, corrected broad-wall response, floor, metal, ceiling, all17 accepted
bindings and exact shoulder match. No added/removed scene actors in this pass.

Read Correction02 task, report/manifest, actual final and support-off/on images,
Review01 R1/R2 and both actual OwnerReferences01 PNGs. Recheck live editor project,
sole current PainterStone01 map, PIE/dirty state and controller-bound current
map/manifest hashes before mutation. Preserve any later owner edits/unsaved work.
Verify exact rollback archive in Controller/BeforeOptics01/archive.json.
Preserve initial, Correction01, Correction02, Review01 and all earlier evidence,
native sources/assets/helpers/reports exactly; archive old map identities only.

## Three small causal comparisons

Use the existing whole-entrance and near oblique interior cameras, unchanged far
field and exposure. Existing Correction02 current-glass/local-off captures are
the baseline. Reuse guarded current capture tools through new output paths.

1. Current glass, local front-layer ON only. Set the two exact discovered
   postprocess fields (override and value) after live schema/readback inspection.
   Warm up and record actual effective path evidence/settings with native frames.
2. New native glass variants, local front-layer OFF. Reuse earlier neutral optics
   as causal starting preset: fixed albedo .45, transmission .90, roughness .32;
   leaf albedo .04, transmission .94, roughness .09; F0 .04. Copy/build only NEW
   graphs under the correction namespace; no history byte edits. Retain sensible
   existing etch microstructure if it supports believable glass, not coarse noise.
3. Those new variants, local front-layer ON. Compare actual angular reflected
   scene, transmitted gradient, recognizable pane bodies, fixed/leaf distinction,
   frame clarity and whole-entrance resemblance. Verify whether the .40 roughness
   cutoff explains current/off differences. Do not infer success from flags or
   brightness alone. No more runtime reflection sphere capture actors.

These comparisons isolate two interacting causes using the existing real far
field. Select the best physically coherent combination. One justified final
fine adjustment to the new glass constants is allowed only if actual comparison
identifies the remaining issue; record why and preserve comparison evidence.
The expected final should have true dielectric transmission, soft fixed panes,
clearer readable leaves, actual scene reflection and restrained mineral context.
No fake pane emission, painted reflections, opaque substitute, backing, arbitrary
color patches, added scenery/lighting, refraction gimmick or acceptance by assertion.

Only the six pane assignments and the two specified local volume flags may differ
from Correction02. All other existing properties and108 effective bindings
(107 lobby plus separately inventoried far-field sphere) stay exact except those
six new glass assignments. If local flags are not needed in chosen final, restore
them exactly. No global/project/user configuration or global cvar modification.
Use only official Epic MCP and guarded small helpers; no DCC texture regeneration
is needed for unchanged Painter families.

New UE assets /Game/OpeningLobby/MaterialsComplete01/Correction03/;
new editable native recipe Assets/Source/OpeningLobby/MaterialsComplete01/Correction03/;
new helpers Scripts/OpeningLobby/materialscomplete01_optics*.py;
new evidence Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03/;
new report Docs/OpeningLobbyMaterialsComplete01Correction03.md.

## Final verified handoff

Save full property/file baseline and exact six binding/flag plan before mutation.
Audit native compiled graph/source/dependencies, saved/reloaded packages and final
optical values. Use unchanged accepted texture/SPP readback and regeneration
evidence through exact hashes; no repeated .spp save/export or full movement suite.
Check real transmission with the existing far-field and meaningful hidden-pane/
opaque controls if changed glass invalidates old controls. Record/refute causal
diagnostic conclusions, including a negative comparison if flags have no effect.

Capture final 1920x1080 HFOV90 standing whole/near/oblique entrance, whole hall,
side aisle, bays, terminal wall, ceiling, checkpoint and elevator contexts. Reuse
exact earlier poses, explicit local reflection condition and true runtime metadata.
Judge R1 and R2 plus material regressions. No processed/composited screenshots.
Save/reopen chosen map and graphs, verify full107coverage plus support and all
protected bytes. Property comparison permits only six named overrides and two
local flags; geometry/world/lighting/exposure/collision/source/history remain exact.
Restore capture/diagnostic state, PIE off, clean current map loaded.

Deliver unique nonempty path/bytes/SHA-256 manifest.json and identity.json binding
current map, new native graphs/recipe, existing Ceiling.spp link, exact rollback,
diagnostics, final images, complete coverage and preservation. Report final local
flag values and chosen optical constants, actual R1/R2 outcome and remaining
limitations honestly. Aim <=80 MB growth, total task <=400 MB and lobby <=2.4 GB,
hard250 GB project cap. No user/history deletion, downloads/installs, paid usage,
delegation, comments/task administration, registry, commits/pushes or later dispatch.
The controller obtains combined fresh independent Review02 after this handoff.
