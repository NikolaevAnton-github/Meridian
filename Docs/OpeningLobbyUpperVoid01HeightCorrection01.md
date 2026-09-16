# UpperVoid01 / HeightCorrection01 author handoff

Candidate: **LobbyAtmosphere-UpperVoid01/HeightCorrection01**, 2026-09-16.
One purposeful author setup, Trial01. Saved/reopened and ready for fresh independent
review, with an unresolved cumulative storage planning overrun. This is not an
independent pass or owner acceptance. Glass remains **DEFERRED_BY_OWNER**.

## Exact identity

- Sole map: `/Game/Maps/L_OpeningLobby_PainterStone01`.
- Map SHA-256: `9e0b3c61af5b67510fa7bbdd74b6e806331c69c0be4880905c8dfeefe6d151dc`.
- [Manifest](../Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker/manifest.json)
  and [digest receipt](../Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker/manifest-receipt.json).
- [Controller rollback](../Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Controller/BeforeHeightCorrection01/archive.json)
  resolves the changed map and two atmosphere assets. Its five entries verified
  against current pre-edit bytes and archived bytes. No whole-map restoration.
- [Editable recipe](../Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection01/recipe.json),
  unchanged quintic HLSL formula alongside it, and native graphs under
  `/Game/OpeningLobby/UpperVoid01/`. Original source/recipe/helpers remain exact.

## Change and visual findings

The actual yellow markup places onset above the 8.4-11.2 m beam tier. Both existing
native graphs now fade from **14 to 17.5 m**, with zero extinction below 14 m.
The main 18 m roof disappears; the 9.2 m side ceilings remain visible.

| Property | Six centre fills | Twelve side fills |
| --- | --- | --- |
| Height restored from original pre-atmosphere scene | 14 m | 6.5 m |
| Intensity restored, native units | 100000 | 45000 |
| Attenuation radius restored | 26 m | 19 m |
| Indirect scale | 0.2 retained | Restored to 1 |
| Specular scale | 0.2 retained | 0.2 retained |

All other light properties and existing manual exposure bias -5 remain unchanged.
The postprocess actor, surface materials, dimensions and gameplay are unchanged.

Author inspected all 12 final native views, four trial views, all 15 sampled
movement frames and four upward-hold captures. Main roof/contact detail is absent
in axial, corner and steep-up views. Both aisles retain lit ceilings, separate
walls, column sides and visible depth. Lower stone, floor strips, checkpoint and
elevator remain readable, with strong inherited point-light pools.

**Review focus:** the near-column upward view foreshortens the 3.5 m fade into a
compact transition beside a bright fill highlight. Inspect `Movement/close_column_up.png`
and `motion-005.png` for a perceived cut-top/common-band impression. Smooth native
parameters alone cannot establish visual acceptance. No bright main roof was
identified in the inspected floor/stone reflections; bright lower soffits are
intentional. The unchanged glass appearance is outside this correction.

## Evidence and preservation

Evidence root: `Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker/`.

- `Before/` and `Final/`: **12 genuine matched pairs**, 1920x1080, HFOV90,
  standing eye 172.15 cm, actual poses and renderer recorded. Both aisle views
  use pitch 55 degrees. Lighting intentionally differs.
- Original `UpperVoid01/Worker/Before/` remains unchanged: ten poses also match
  the new final set; its aisle views use 12-degree pitch and are explicitly
  identified as unmatched context. The rejected old final set is also preserved.
- `Movement/`: fresh normal PlayerStart, **95 seconds**, **852 telemetry samples**,
  **15 native 960x540 frames**, plus four 1920x1082 hold captures. Key/mouse events
  pass through PlayerController and CharacterMovement; no route teleports.
  Sampled upward holds: centre 5.765 s, close column 5.671 s, east 5.672 s,
  west 5.703 s. Both aisle transitions and checkpoint return complete.
  No roof reveal or exposure pumping identified in sampled images. This is
  continuous telemetry plus sampled frames, not continuous video; unsampled
  transients are not exhaustively excluded.
- `property-preservation.json`: all **129 actors / 150 components**, **107 lobby
  bindings** and separate support component audited. **84 scheduled live deltas**,
  **42 pre-atmosphere deltas**, zero unexplained changes. All geometry, owner edits,
  visibility, collision, gameplay and glass/support properties preserved.
- `graph-verification.json`: four scalar threshold changes across two graphs;
  topology/formula unchanged. Only transient object addresses normalized when
  comparing expression-input repr; full paths/types retained.
- `protected-after.json` and `history-verification.json`: **4151 protected file
  entries** checked, only current map and two archived atmosphere assets changed.
  Prior manifests, material/source bytes, original worker evidence, old helpers,
  project configuration and instructions remain exact.
- `handoff-verification.json`: saved/reopened properties equal post-walk properties;
  PIE off, no dirty packages, temporary capture/throttle controls restored,
  inputs released, callbacks finished, gameplay FOV90 preserved.

The native property audit covers fields exposed by the existing Epic JSON
reflection primitive. Delegate/event fields report unsupported schema types;
their serialized values cannot be independently compared through this API.
Unchanged source/configuration and successful real-input traversal corroborate
gameplay preservation. `error-audit.json` retains native warnings: no material
compile failures; schema warnings, audio sample-rate conversion, unavailable
frame-generation CVars, FOV console lookup and an element-reference warning on
reload. Reload and the final clean property comparison nevertheless succeeded.

## Performance and remaining gate

Matching floating-PIE stationary samples use five seconds warmup then 20 seconds
measurement, actual viewport 1920x1082. Before: **119.987 FPS / 8.334 ms**; final:
**119.900 FPS / 8.340 ms**. Lumen hardware ray tracing, Substrate, TSR and quality
3 are recorded; VSync and frame cap are zero, no enabled frame-generation plugin.
These are game-frame/Slate wall measurements near a 120 Hz plateau of unresolved
origin. No separate GPU/CPU-stage, 1440p, standalone or worst-case-route claim.

The correction remains below its **100 MB** allowance and the project below the
**250 GB hard cap**. However, the cumulative lobby **2.4 GB planning requirement
is not met**: pre-correction usage was already 2.384 GB; final evidence pushes it
to approximately 2.46 GB. Exact bounded measurements are in `storage.json` and
the manifest receipt. No history or user assets were deleted. This requires a
controller/owner planning disposition; the worker does not grant an exception.

Fresh independent review must judge height placement, near-column transition,
aisle depth, reflections and temporal evidence from the actual images before
reading these author conclusions. Storage is an explicit failed planning check,
not an unreported PASS. No task administration, later-stage dispatch, registry
write, commit, push, paid API or global configuration change was performed.
