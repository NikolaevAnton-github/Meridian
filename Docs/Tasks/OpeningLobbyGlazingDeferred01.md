# Entrance glazing refinement: deferred by owner

Status: backlog, no run authorized by this record. On2026-09-15 the owner said
to skip glass for now and work on it separately later. See
../Approvals/LobbyMaterialsComplete01-GlazingDeferred01.json. This deferred task
must not delay the current opaque-material/large-format stone slab delivery.

Current glass is technically verified native Substrate but its visual R1 remains
unresolved, not passed or accepted. Preserve the latest current map and glazing
while working on other materials. Do not revert to earlier map bytes.

## Bound current evidence

Glass-last-edited candidate LobbyMaterials-Complete01/Correction03, MSQ-28.
Manifest: Saved/OpeningLobby/MaterialsComplete01/Worker/Correction03/manifest.json,
SHA-256 ed6b3c105b8f2b22536707e668e7db7ba3cff720b7938ed7899a091b985f520a,
678entries. Current map at that handoff:
b4cc37e0dd8281fddd250183c5e878f20fec35babcdefc520d3b09929857cb73.
Later slab work changes the map identity; use its final manifest for the complete
scene and Correction03 only as exact glass history. No acceptance implied.

Six slot0 panes, StaticMeshActor94-99, use new Correction03 fixed/leaf graphs.
The existing Layout03NeutralExposure front-layer override and value were restored
false. One neutral far-field sphere remains; no support light/reflection actor.
Correction03 Final, NewOn/NewOff/CurrentOn and Hidden/Opaque controls preserve
actual native images and runtime metadata. Read its report/recipe for exact
final constants and fine micro-slope adjustment; do not infer them from trial IDs.

## Remaining observation and future diagnostic lead

Current fixed panels still read too uniformly, with little identifiable scene
reflection. Three optical/local-flag comparisons do not establish that the path
is inactive. Native graph audit found valid slab-to-FrontMaterial, F0=.04,
world-space normal and MFP transmission wiring. The near view is only about20deg
off the pane normal, so dielectric reflection is weak against far-field horizon
radiance12. Final effective GPU front-layer pass execution was not proven.

A read-only audit suggested a future minimal isolation: hide only the far-field
sphere temporarily in PIE and compare unchanged final glass/localON versus OFF
under matched pose/exposure, then restore all state. This would separate visible
reflection from bright transmission without changing the BSDF. A diagnostic-only
low-transmission graph is a fallback, not a final glass material. No such new
control was dispatched after the owner's deferral. This is an investigative lead,
not a verified root cause or guaranteed fix. Avoid further blind optical tuning.

When the owner resumes this work, recheck actual live map/user edits, establish
a bounded new task and exact rollback, retain current opaque materials and source
history, and obtain independent visual review. Do not start new architecture,
exterior scenery or final atmosphere implicitly from this backlog entry.
