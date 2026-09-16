# LobbyPainter-Metal01 / WorkerCandidate01

MSQ-26 authored one native Painter charcoal satin metal-coating family on the
existing checkpoint, four service-door frames/leaves and elevator leaves. The
current `/Game/Maps/L_OpeningLobby_PainterStone01` map was edited in place.
Accepted stone and floor remain accepted and unchanged. This new metal candidate
requires fresh independent visual review and the owner's material-direction
decision. No whole-lobby, architectural-detail or atmosphere acceptance is implied.

## Candidate and exact identity

- Candidate: `LobbyPainter-Metal01/WorkerCandidate01`, author `QARevision01`.
- Source: `Assets/Source/OpeningLobby/PainterMetal01/Metal.spp` and `recipe.json`.
- Canonical channels: `Assets/Source/OpeningLobby/PainterMetal01/Channels/`.
- Unreal family: `/Game/OpeningLobby/PainterMetal01/` (one material, three textures).
- Exact identity: `Saved/OpeningLobby/PainterMetal01/Worker/identity.json`.
- Frozen path/bytes/SHA-256 package: `Worker/manifest.json`; verification and
  manifest hash are recorded in `Worker/manifest-verification.json`.
- Exact accepted before-map: `Worker/Before/L_OpeningLobby_PainterStone01.umap`,
  SHA-256 `5cc84cac736d24cfe0dedf4c4d1dd0413b3d07f081c9e82e5dd4ab2ca0ae9270`.

Paths abbreviated as `Worker/` below mean
`Saved/OpeningLobby/PainterMetal01/Worker/`.

## Authored surface

The visible finish is an **opaque satin coating over metal**, not bare conductor.
Its metallic channel is zero; Unreal dielectric specular is 0.5 (F0 4%). Base
color is sRGB (0.205, 0.215, 0.220), exported RGB (52, 55, 56). Native base
roughness is 0.28. The final packed green channel is 69–75/255, mean 0.282.
Neutral AO is 1. DirectX normal red/green span only 126–129/255, blue 255.

Painter 12.1.4 / API 0.3.5 authored three editable Fill layers inside one group:
opaque charcoal base, fine satin roughness, and microscopic coating height.
The two structure layers use native BnW Spots 2, seed 37, scale 8, balance 0.48,
contrast 0.08, disorder 0.31, UV scale (2,2), offset (0.173,0.291). Their opacities
are 0.025 for roughness and 0.0003 for height. No masks, damage, panel grids,
painted seams, stone veins or external generated pixels are used.

2048 exports project over 120 cm using the established world triplanar math.
This gives 0.586 mm per exported texel; the procedural repeat is 60 cm, with
internal native resource scale 8. Fine structure is intentionally subordinate
to the large metal faces; the height contribution changes normals only. Existing
geometric edges and panel joins remain unchanged. The 240 cm authoring FBX is
an exact task-local copy of the prior read-only plane; its `PainterStone01` slot
name is retained only as mesh metadata, not a texture/material dependency.

The new 13-node Unreal graph uses only the three new textures plus engine math.
It has no old opaque dependencies, no displacement, and no parent material.
It compiles at 244 pixel / 148 vertex instructions and four samplers in the
recorded editor audit. Color is sRGB/default; ORM is linear/masks; DirectX normal
is linear/normal-map compression with green flip disabled. `Worker/native-material-audit.json`
records complete graph, import, channel, dependency and material readbacks after
the saved map was reopened.

## Preservation and provenance

`Worker/planned-bindings.json` and `bindings.json` identify exactly ten slot-zero
overrides on `StaticMeshComponent0` of actors 3, 4, 13, 14, 16, 24, 28, 34, 39,
and 41. Exact labels and inherited old materials were checked before mutation.
Mesh defaults remain unchanged. The checkpoint retains owner X = -2090 cm.

Full reflected properties for 127 actors and 148 components were captured in
Before, Final and RestoredFinal. Their only differences are the ten authorized
override arrays. Four accepted stone and three floor bindings, geometry,
collision, lighting/exposure, glazing, gameplay and the blank logo field are
preserved. Config and all protected source/content bytes pass exact checks.
The transient Painter `.painter_lock` is explicitly excluded from asset-byte
preservation; the original open Floor.spp bytes are unchanged.

All 183 accepted Floor01 manifest entries and 154 Stone01 entries resolve exactly.
The Floor01 current-map entry resolves to the new exact Before archive; older
stone/retired maps resolve through the untouched Floor01 archive. Historical
manifests were never edited. Only one current lobby map remains in Content.
See `Worker/approved-history-final-verification.json`.

The previously open clean Floor project was backed up by Painter to
`BeforeOpenFloor.spp` without changing its original. Initial metal source and
exports remain under Worker/Initial and Worker/Exports/Initial. One author QA
revision reduced visible mottling in the elevator highlight; the three actual
Trial01 captures and native change log remain historical. No second revision
was needed for author handoff.

Final source regeneration is recorded in `Worker/exact-regeneration.json`.
The first reopen changed group UI state; a Full save and second close/open left
the final source clean. That final exact .spp regenerates all three exports
byte-for-byte, matching the canonical imported PNGs. Native sources, resource
URLs, parameter metadata, final values, projections and audit are in Worker/Native.

## Actual visual and gameplay evidence

Both actual OwnerReferences01 PNGs were inspected before authoring. The final
three close views show calm charcoal faces, subdued satin highlight bands and
readable edges, with no conspicuous repeating color pattern. The elevator's
initial mottled highlight is substantially quieter after QARevision01. The
finish stays dark under the unchanged lighting. Independent review must judge
whether these existing geometric and lighting cues convey the desired metal.

Five before/final pairs were inspected as actual images: `entrance-90`,
`inner-90`, `checkpoint-metal-90`, `service-door-90`, `elevator-metal-90`.
Each is a genuine 1920x1080 native Unreal PNG at HFOV 90 and standing camera
height 172.15 cm. The wide views show the accepted columns' strong sightline
occlusion; this task does not revise them. The close checkpoint view is oblique;
the service door and elevator views expose whole-face continuity and edge response.
Camera sidecars record exact actual/requested pose, FOV, renderer/exposure and
runtime readiness. The still comparisons use transient pawn placement.

One final capture attempt stalled at world time zero with the camera at origin;
readiness rejected it and no PNG was saved. The established temporary
`Slate.bAllowThrottling` 1→0 workaround enabled actual world ticks. It was restored
to 1 after capture; all play-window/performance settings were restored exactly.
Stalled-attempt metadata is retained. `Final/standing-possession.json` proves a
possessed walking character, grounded at gravity -980, eye height 170 cm above
capsule bottom. Full route traversal was not repeated because geometry and
collision were unchanged. `RestoredFinal/state.json` records clean current map,
no dirty assets and PIE stopped.

## Storage and review handoff

`Worker/storage.json` records measured apparent file bytes, project and cumulative
lobby totals, task growth and correction headroom using the existing no-junction
walker. The target is at most 160 MB growth, under 2 GB cumulative lobby and
250 GB project caps. No assets were deleted to meet the target.

Fresh independent review is pending; the author does not self-grant visual
acceptance. Review the frozen manifest, actual reference/capture pairs and eight
criteria in `Docs/Tasks/OpeningLobbyPainterMetal01.md`. Other materials, entrance
metal rollout, ceiling/soffit, glazing B3, final atmosphere and MSQ-7 remain pending.
No registry writes, task comments/admin, dispatch, installs, downloads, paid usage,
configuration changes, commits or pushes were performed by this author run.
