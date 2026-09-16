# LobbyMaterials-Complete01 / Correction01

**Technical verification passes. R2 is addressed within the authorized broad-field scope. R1 is improved but remains partially unresolved after two optical candidates.** This package is a focused Review02 handoff, not owner-review readiness or acceptance.

The current sole map is `/Game/Maps/L_OpeningLobby_PainterStone01`. Exact map, graph, source and evidence identities are in [Correction01/identity.json](../Saved/OpeningLobby/MaterialsComplete01/Worker/Correction01/identity.json) and [manifest.json](../Saved/OpeningLobby/MaterialsComplete01/Worker/Correction01/manifest.json). Initial WorkerCandidate01 and Review01 remain unchanged. The initial map resolves through the controller's exact BeforeCorrection01 archive; its historical manifest was not rewritten.

## Changes and review responses

### R1 — glass body and entrance readability: partial, unresolved

New native `M_C01_GlassFixed` and `M_C01_GlassLeaf` graphs replace only the six authorized pane bindings. Live inspection found closed 2 cm pane boxes with one-sided, thin Substrate SimpleVolume materials. The original fixed/leaf scattering albedos were .45/.04, transmission .90/.94 and roughness .32/.09. The leaves disappeared against the dark exterior; fixed panes showed broad surface highlights and uniform grey body.

Candidate01 increased scattering and roughness while retaining actual MFP-based volume transmission and dielectric F0 .04. Matched images showed visibly stronger door-leaf body and a quieter fixed-pane highlight, but a smooth sheet-like appearance remained. Its exact graph bytes, recipes and six images are retained in `Correction01/Trial01/`.

Final optical Candidate02 uses fixed/leaf scattering albedo .92/.85, neutral transmission .70/.82 and roughness .50/.25. A native editable micro-slope node adds filtered, low-amplitude surface variation at 2 cm spacing; it drives only the surface normal. Slopes fade below pixel resolution. There are no new texture pixels, colour patterns, emission, backing, lights or geometry. The material remains genuinely translucent, with F0 .04 and the original consistent Substrate thickness defaults. This is not a calibrated thick-glass refraction solution.

Actual final entrance-whole, entrance and near-oblique entrance-glass images show readable leaf bodies and etched fixed surfaces. However, the large fixed panes still read as fairly uniform grey sheets, especially at whole-entrance distance. **These improvements do not establish full R1 closure.** No third optical candidate was attempted.

The diagnostic approach then changed to inspect the existing background. Two same-pose interior controls with the six panes hidden show an almost entirely black exterior. Fresh reverse-side visible/absent/opaque controls demonstrate real transmission through the final leaves and fixed sidelights. Native renderer sidecars also record front-layer Lumen translucent reflections disabled under the preserved renderer settings. Those facts explain constraints; they do not grant a visual pass or prove that no other material solution exists.

Evidence: `Correction01/Final/entrance-whole-90.png`, `entrance-90.png`, `entrance-glass-90.png`; `InteriorDiagnostic/`; `Transmission/`; `diagnosis-live.json`; `graph-audit-final.json`; `transmission-verification.json`.

### R2 — broad wall glare: addressed for independent recheck

New native `M_C01_BroadStone` references the accepted Painter stone textures read-only. Roughness is `0.57 + 0.35 × accepted ORM.G`; specular is .35, corresponding to dielectric F0 .028. Accepted BaseColor, normal, AO, metallic, 240 cm projection and mineral phase-blending code remain exact. No texture/source regeneration was needed.

The explicit subset contains 19 of the 40 newly rolled-out stone slots:

- Both SideWall, EntranceAisleEnd, InnerAisleEnd and InnerEndBand fields.
- Both RA01_UpperWall, RA01_Beam and RA01_EntranceBacking fields.
- Four FB01 terminal composite shells and FB01_InnerOpaqueWall.

Adjacent overhead beams use the same restrained response because their undersides showed the same distracting highlights. Composite shell slots are preserved. Structural piers/columns, portal/datum surfaces, the accepted samples and exact shared shoulder assignment retain their original bindings.

Matched side-aisle, bays-context and soffit-up views show the terminal-wall white disc removed and mineral detail retained across broader wall/beam fields. The side wall retains a broad oblique sheen; untouched structural piers and the protected accepted sample still show bright highlights. The hall is not claimed free of highlights. One stone response candidate was used. R2 closure is proposed only within this exact material-only scope, pending fresh independent review.

## Verification

- Exact comparison: 127 actors, 148 components, 107 visible mesh components; only 25 named component overrides differ. All other reflected scene/world/renderer properties remain exact.
- All 17 accepted bindings, nine ceiling bindings, shoulder counterpart match and owner checkpoint transform are preserved. Full coverage remains 44 stone, three floor/strip, 45 metal, nine ceiling and six glass; zero proxy/error bindings.
- All 3,302 protected preexisting baseline files verify byte-for-byte. The current map is the authorized exception; three correction helpers created before the snapshot are explicitly task-owned exclusions. Initial batch and three accepted-family manifests verify all 789 entries using exact historical map archives.
- All three new material packages saved and reloaded from disk; graph compilation, dependencies, actual node links and emission absence checked. Twelve accepted stone graph nodes match after only editor-position and duplicated-node namespace accounting. This accounting does not normalize scene-property comparisons.
- Twelve final 1920×1080 HFOV90 standing captures exactly match prior camera poses, FOV and renderer settings, including whole hall, ceiling, checkpoint, elevator and floor contexts. Actual images were inspected. Three reverse-side controls verify transmission and two interior controls establish the visible background constraint.
- The optional third interior diagnostic was interrupted before shooting when PIE was stopped early. Its unshot camera request and error remain identified in `capture-verification.json`; neither is claimed as image evidence. All twelve required final images and the two useful interior controls are complete. Capture/visibility/material/pose state is restored; current map clean, PIE off.
- Prior route evidence is reused narrowly because collision, gameplay, meshes and transforms match exactly. No new route or performance claim is made.

Measured correction growth is approximately **54.9 MB**, total batch growth **211.4 MB**, cumulative lobby storage **2.057 GB**, and project storage **13.479 GB**. These fit the 150 MB correction, 400 MB batch, 2.4 GB lobby and 250 GB project limits. No user/history data was deleted.

## Handoff

Review02 should inspect R1 honestly as partially unresolved and independently assess the proposed R2 closure, then verify changed graph/binding evidence and regressions. The artist has not dispatched review or changed task administration. No owner acceptance, full visual success, final atmosphere or architectural acceptance is claimed.

Editable sources: [Correction01 recipes](../Assets/Source/OpeningLobby/MaterialsComplete01/Correction01/recipe.json), native UE graphs under `/Game/OpeningLobby/MaterialsComplete01/Correction01/`, and correction-prefixed helpers under `Scripts/OpeningLobby/`. The initial native ceiling and accepted Painter sources remain unchanged and linked through verified historical receipts.
