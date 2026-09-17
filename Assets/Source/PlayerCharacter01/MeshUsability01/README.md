# Datum16MeshUsability01 — MSQ-54 diagnostic sources

Use `Datum16_Bind05.blend` / `.fbx` as the final **diagnostic** fit, and
`Datum16_Bind05_DeformationFinal.blend` for the 19 keyed static probes. No mesh
is approved for production or final appearance. Full MSQ-54 remains incomplete.

Every working blend preserves `Revision02_Untouched`, the full donor reference,
the fitted unbound T surface and the bound original garment. The 28,332 source
vertices, 60,797 edges and 32,376 polygon index lists remain unchanged. No
remeshing, decimation, subdivision or retopology was performed.

`Donor/MSQ52_Manny161.fbx` and `.blend` are compatible-rig/weight references only.
The Blender FBX representation has armature object `root` plus 160 bones;
the Unreal round trip restores all 161 contract bones. Do not rename the
armature to `Armature`, automatically reorient bones, or remove helper chains.
The isolated unchanged donor uasset is not the tested garment and retains an
unavailable vendor post-process dependency. Final candidate assets have no
missing hard `/Game` dependencies.

Preserved attempts:

- Bind01: topology-preserving initial donor transfer; excessive digit leakage.
- Bind02: regional hand correspondence and small contract-matrix alignment;
  thumb mask also selected part of the index fingertip, producing spikes.
- Bind03: alternate bounded inverse fit; disproved the singular-matrix hypothesis.
- Bind04: bounded thumb mask removed spikes; independent source-space measurement
  still detected index-edge leakage from middle-finger weights.
- Bind05: measured source digit boundaries correct that leakage. Joint quality,
  thumb/web/cuff fit and rifle-surface contact remain unfinished.

No earlier attempt or owner source was overwritten. Both owner revisions remain
in the separate `AI3D/Tripo/Datum16UndersuitInput01/OwnerExports/` input directory.
The current owner drop is Revision02 and must not be restored to Revision01.

See `Docs/PlayerCharacter01MeshUsability01.md` for regional verdicts and limits.
Evidence is under `Saved/PlayerCharacter01/MeshUsability01/Worker/`; its `index.html`
opens the matched source, gray/wire deformation and actual Unreal playback views.
`manifest.json` identifies exact output bytes after the worker stops changing them.
The controller owns review, registry, task/state records, profile restoration and
the local closure commit. No successor or production model acceptance is implied.
