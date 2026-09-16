# PainterFloor01 editable sources

Two new native Painter projects: `Floor.spp` and `Strip.spp`, authored in
Painter 12.1.4 / Python API 0.3.5. Each has three editable Fill layers.
No smart material was inserted and no texture pixels were imported.
Installed native SBSAR resources supply the mineral content.

The inherited texture-set name `PainterStone01` comes solely from the material
slot of the unchanged 240 cm authoring plane. These are newly created projects,
not copies or recolorings of the approved column-stone project. The task copy
of the mesh is hash-identical to its original; `Worker/authoring-mesh.json`
records both paths and identities.

## Final stacks

- Floor: customized `marble_veined` body with green-grey base and pale mineral
  fractures; independent `marble_veins` secondary structure blended with Screen
  at 0.08; uniform dielectric cut-surface polish at roughness 0.24 / metallic 0.
- Strip: near-black uniform mineral body at roughness 0.22 / metallic 0;
  `marble_fine` BaseColor structure blended with Screen at 0.065; independent
  fine roughness variation blended at 0.045. Flat polished normal response.

`Floor-final-recipe.json` and `Strip-final-recipe.json` contain final reopened
layer IDs, active channels, native resource URLs, parameter metadata/readbacks,
projection transforms and blend overrides. Files without `final` describe the
initial author trial. `History/FloorInitial.spp` is the bridge-required backup
made when creating the second project; it is not the final floor source.

## Export and physical mapping

Use the installed `Unreal Engine (Packed)` preset, PNG, 8-bit, size_log2 11.
Canonical channels under `Channels/` are exact copies of final reopened exports:
BaseColor is sRGB; Normal is DirectX; ORM is linear R=AO, G=roughness, B=metallic.
AO is neutral 1, metallic is 0. Smooth planar normals retain export quantization;
there is no invented surface displacement or swollen normal relief.

The complete floor tile covers 360 cm in Unreal and the strip tile 240 cm.
On the authoring plane they cover 240 cm; the floor's explicit 1.5 scale increase
is part of its mineral-size design, not a scene geometry change. Final Painter
UV rotations are zero and scales are integer (body 1, secondary floor 2,
fine strip 5) to retain periodic borders. World-space color sampling reuses the
reviewed triangular phase-blending shader to reduce repeated motifs. It samples
only these new Painter exports, with no tint or external generated pixels.

Only the current map's Floor and two FloorStrip component slot overrides changed.
See `Docs/OpeningLobbyPainterFloor01.md` and the task manifest for full evidence.
