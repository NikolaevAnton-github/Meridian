# LobbyMaterials-Complete01 / Correction03

**The bounded calibration and verification are complete. R1 remains unresolved: the glass still lacks convincing reflected scene structure and fixed/leaf distinction. This is a technically verified candidate for combined fresh Review02, not a completed visual finish.** R2's corrected broad-wall response is preserved pending independent recheck.

Exact bytes are identified by [identity.json](../Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03/identity.json) and [manifest.json](../Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03/manifest.json). Evidence references below are relative to `Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03/`.

## Scope and final selection

The sole current map remains `/Game/Maps/L_OpeningLobby_PainterStone01`. Six components now use two new native Substrate glass materials in `/Game/OpeningLobby/MaterialsComplete01/Correction03/`. No actor was added or removed. The existing Correction02 neutral far field remains exact.

| Final graph | Scattering albedo | Transmission | Roughness | F0 | Etch slope |
| --- | ---: | ---: | ---: | ---: | ---: |
| M_C03_GlassFixed | .45 | .90 | .32 | .04 | .0045 |
| M_C03_GlassLeaf | .04 | .94 | .09 | .04 | .0025 |

All color constants are neutral RGB. Both materials retain thin-surface Simple Volume optics, translucent colored transmittance, SurfacePerPixelLighting and the native filtered 2 cm normal field. The pane graphs have no emission, texture pixels, painted reflections or opaque backing. Editable constants, normal code, dependencies and compiled statistics are in [recipe.json](../Assets/Source/OpeningLobby/MaterialsComplete01/Correction03/recipe.json).

Both local flags on `Layout03NeutralExposure` finish **false**, exactly as before: `bOverride_LumenFrontLayerTranslucencyReflections=false` and `lumenFrontLayerTranslucencyReflections=false`. Enabling them showed no convincing visual benefit in the bounded comparisons, so their original state was restored. Global renderer variables, project configuration, exposure and lights were never changed.

## Three comparisons and one fine adjustment

The Correction02 final captures provide current-glass/local-off baseline. Every new pair uses the same whole-entrance and near-oblique standing cameras, HFOV90, native 1920x1080 output, unchanged far field and exposure. The actual reference PNGs `01-InnerEnd.png` and `02-EntranceSecurity.png`, prior support-off/on images, all six comparison images, twelve final images and four controls were inspected.

1. **CurrentOn:** only the two local flags enabled. Whole and near glass remain nearly indistinguishable in visual structure from the baseline. The high-scattering fixed panes retain their grey-sheet response.
2. **NewOff:** neutral lower-scattering preset, local flags off. The upper fixed panes become darker and the existing broad surface highlight becomes more distinct. Lower glass continues to transmit the neutral field. The near view exposes coarse-looking etch highlights. This comparison varies albedo, transmission and roughness together; it cannot isolate roughness as the cause.
3. **NewOn:** identical new graphs, local flags on. No recognizable added reflected architecture appears in either inspected image. Whole-image pane sample mean absolute differences between NewOff and NewOn are only approximately 0.29–0.58 levels on a 0–255 luminance scale. These small differences include rendering variation and do not prove a useful reflection contribution.

**One final adjustment:** reduce only EtchSlope tenfold (.045/.025 to .0045/.0025), justified by the coarse normal highlights visible in both new-preset oblique images. Final near glass is smoother and the distracting grain is reduced. This does not solve missing reflected structure or the broad fixed-pane highlight. The comparison native packages and recipe were archived exactly under `ComparisonArchive/` before this adjustment; `fine-adjustment.json` records the reason and values. No further optical trial was performed.

### Render-path conclusion and its limits

Readbacks confirm local flags changed in both editor and PIE. The installed 5.8.1 source allows the local flag OR global Enable, subject to Allow and view Lumen-reflection show flags (`FrontLayerTranslucency.cpp:70–75`); material eligibility additionally requires translucent surface lighting and `bAllowFrontLayerTranslucency` (`MaterialShared.cpp:2189–2195`). The audited graphs satisfy those material conditions. Global Enable and EnableForProject remain 0; Allow remains 1. `r.ReflectionCapture.Runtime` remains 0; no reflection-capture actor was created or retried.

The roughness console override actually reads **-1**, meaning defer to postprocess, whose recorded roughness threshold is approximately **.40** (`LumenReflections.cpp:424–431`). Current fixed roughness .50 is above that input threshold; new fixed .32 is below. However, the actual on/off comparison does **not** establish that crossing the threshold supplies recognizable reflected scene structure. Therefore the proposed cutoff explanation is not validated as the sufficient cause of the observed failure. These are input/schema observations, not a GPU-pass execution trace or proof of a working reflection contribution. The reason for the negligible local-flag effect remains undetermined within this scope. No broader renderer experiment was performed.

## Visual findings

**R1 — unresolved.** `Final/entrance-whole-90.png`, `entrance-90.png` and `entrance-glass-90.png` show legible dark framing, nonblack entry leaves and continuous neutral transmission. Fixed panes remain sheet-like, with a broad highlight and insufficient recognizable reflected scene structure; the clearer leaf material does not create a strong enough visible body distinction. The whole entrance does not yet match the reference's diffusing glass hierarchy. No visual acceptance is claimed from brightness, native graph validity, or flag settings.

**Real transmission — demonstrated.** Matched final/hidden/opaque triplets at the whole and near-oblique poses keep the far field and all lighting fixed. Hiding the six panes reveals a continuous horizon/zenith gradient. Applying opaque accepted stone to those same six meshes blocks it. Final glass transmits the field, with a remaining surface highlight. Named lower-fixed and leaf samples are more than 20 luminance levels brighter than opaque controls; final named pane samples do not clip. Controls existed only in PIE and were restored without saving. This is causal transmission evidence, not calibrated optical measurement, refraction accuracy or R1 closure.

**R2 — corrected response retained; independent recheck pending.** All 19 corrected broad-stone assignments and their native/source bytes remain exact. The terminal service-door wall retains mineral detail without a dominant white disc. Side walls still have broad sheen, and accepted samples/untouched structural elements retain conspicuous highlights visible in the bays, stone-oblique and ceiling contexts. Correction03 shows no observed material regression attributable to glass calibration. It does not claim a highlight-free hall. Nine ceiling assignments, accepted floor/strip/metal, exact shoulders, blank opaque inner field and owner geometry remain unchanged.

## Verification

- Fresh `ResumeBefore` readback exactly matches both the existing preparation `Before` snapshot and Correction02 restored properties. Controller map SHA-256 `27351b91d05441dbee4d75c4ef1ec3719a213ce541f60cb86a8c2566b73a4940`, all 536 prior manifest entries, rollback archive and archived preparation bytes verified before mutation.
- Complete reflected-property comparison covers 128 actors, 149 components, world settings and renderer. Exactly six material override references differ. The two local flags are restored. No geometry, collision, light, exposure, gameplay, route or far-field property differs. Final/reloaded and post-diagnostic snapshots match exactly.
- All 107 lobby components remain covered: stone 44, floor/strips 3, metal 45, ceiling 9, glass 6. The unchanged far-field mesh is inventoried separately as component 108. All 17 accepted bindings remain exact; 102 effective bindings including support remain unchanged.
- Both native graphs and the map were saved/reloaded. Full connectivity, compiled shader statistics, texture/dependency audit and final optical defaults pass. The fine adjustment changes only one scalar node per graph. Existing Ceiling.spp and regeneration evidence remain linked through exact hashes; no redundant Painter export or source resave was performed.
- All 22 captures pass resolution, actual camera/FOV, possession, standing, world-time and matched renderer/exposure checks. Capture settings and all diagnostics were restored; Slate throttle remained 1 throughout. PIE is off and the current map is clean.
- Six historical manifests verify 1,723 entries using only exact archived map resolutions. Previous candidate, review, source, asset and helper history remains intact. The 4,588-file protection check records two externally updated controller files separately: its live `artist-messages-current.json` and `Controller/status.py` (1261 to 1269 bytes). This worker did not edit them or overwrite the controller's newer bytes. Exact before/after hashes and the initially detected change are retained in `protected-after.json` and `protected-external-change-observed.json`; this is an explicit administrative exception, not an assertion of universal byte equality.

Storage measurements and targets are in `storage.json`: <=80 MB correction growth target, <=400 MB total batch growth, <=2.4 GB lobby and <=250 GB project limits. No user/history data was deleted.

The single authorized Rider Python call registered the new guarded Epic MCP toolset only. All scene mutations and captures then used official Epic MCP. No task comments/administration, delegation, installations/downloads, paid services, registry changes, commits/pushes or later dispatch were performed. The controller receives this exact candidate for combined fresh Review02 with **owner_review_ready=false**, R1 unresolved and R2 retained pending independent recheck.
