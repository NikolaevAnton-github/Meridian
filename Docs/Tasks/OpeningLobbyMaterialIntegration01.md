# LobbyMaterial-Integration01: opaque materials rebuilt from scratch

**Superseded after owner rejection.** The owner rejected the NumPy-authored pilot
as not resembling stone and requested Painter. Follow
OpeningLobbyPainterStone01.md and the recorded
../Approvals/LobbyMaterialIntegration01-Rejection01.json decision. Preserve this
task, its cancelled runs and all artifacts as history; do not continue its rollout.

On 2026-09-15 the owner requested the next lobby task, selected maximum reasoning,
and instructed the controller to execute it. This is a bounded continuation of
MSQ-6, using the existing Multica Environment Artist and fresh Visual Reviewer on
Astra/max/standard, subscription authentication and concurrency one. The controller
remains active through implementation, independent review and one bounded correction
plus focused recheck if required. MSQ-7 and final atmosphere remain later work.

Owner steering during MSQ-22 supersedes the initial reuse approach: all opaque
materials in this pass must be authored from scratch. The first run was cancelled
during source inspection/captures, before creating the candidate map. Preserve its
Worker evidence as history. New execution evidence belongs in WorkerFresh01.

## Authority and deliverable

Read AGENTS.md, Docs/Design/GameBrief.md, Docs/VisualAcceptance.md,
Docs/OpeningLobbyFunctionalBuild01Review.md and
Docs/Approvals/LobbyFunctionalBuild01-OwnerEdit01.json. Inspect the actual two
Assets/Concepts/OpeningLobby/OwnerReferences01 PNGs as the material reference.
Current owner changes supersede the historical worker map; the old MSQ-21 PASS
does not certify those edited bytes. Never restore the old map or rebaseline its
manifest. This task does not grant owner acceptance of geometry or finished look.

Create /Game/Maps/L_OpeningLobby_MaterialIntegration01 from the current saved
/Game/Maps/L_OpeningLobby_FunctionalBuild01, preserving that source map. Controller
preflight found it clean with PIE stopped and SHA-256
46972ef30ef07f5a5aaa8cad0f8c026302c1269f1b5e08828e6f87795d168d31. Recheck live
project, map, dirty state and source bytes. Record later owner changes rather than
overwriting them. Do not discard dirty work or save unrelated packages. Compare the
current source with historical scene evidence only to identify owner deltas; retain
them in the new map. Any owner-authored nonneutral material override is excluded
from automatic replacement and must be documented explicitly.

Deliver a coherent opaque material pass across the existing hall: green-grey stone
columns/walls/portal/room shells, polished veined floor, the two black strips,
restrained ceiling/soffit finish, dark metal checkpoint and door/elevator surfaces.
Use material/component overrides, not mesh-default edits. Preserve all geometry,
actor/component transforms, collision, room/door/roof dimensions, paths, labels,
lighting/postprocess, glazing, gameplay and the blank inner logo field. No new
panels, seams cut into geometry, decals, props, signs, interiors or atmosphere.
The surface finish should preserve the architecture's depth and quiet hierarchy.

Author new native material graphs and new texture content for every opaque role
under /Game/OpeningLobby/MaterialIntegration01/. Do not reference or derive from
the old lobby's opaque materials, parents, material functions or texture families.
Renaming, recoloring, resampling, repacking or duplicating the old set does not meet
the owner's request. Stock engine math/projection functions, technical bridges,
capture utilities and validators may be reused. Historical material PASS findings
provide no acceptance for this new set. Do not import historical geometry, glass
experiments or diagnostic lighting. Glass B3 remains outside this opaque pass.

Use the actual approved reference pair to author differentiated surface families:
dense low-contrast irregular mineral structure for stone, larger branching veins
and calm polished reflections for the floor, near-black strips with restrained
fine structure, readable subdued metal and quieter ceiling/soffits. Avoid one
generic noise family for all roles, repeated isolated islands, worm/loop patterns,
uniform stone groundmass, exaggerated normal relief and wet/plastic reflections.
Do not introduce a new architectural panel system through texture authoring.

Keep new editable source and canonical input maps under
Assets/Source/OpeningLobby/MaterialIntegration01/. Record new recipes/seeds, channel
meanings, texture dimensions and physical projection scales. Procedural generation
from newly authored local source is allowed; inspect its actual output. A changed
hash alone does not prove new authorship. New native Unreal graphs can themselves
be editable source for engine-procedural work. If Blender/Painter contributes,
retain the new native .blend/.spp as well as the recipe and exports. Verify live
versions/bridges before using an installed DCC; use it when it materially helps.
One writer per instance and one heavy workload; no forced DCC round trip merely
to create a source-file name. No paid generation, downloads campaign or installs.

## Bounded production and evidence

1. Write WorkerFresh01/assembly-contract.md with current-source identity, owner deltas,
   material-role decisions and preserved exceptions. Snapshot current actor,
   component and world properties. Classify every target component and slot with
   explicit old/new material paths; avoid broad name heuristics without coverage
   checks. Invisible collision shells and glass must retain their original values.
2. Copy the saved map through the proven new_level_from_template path. Test the
   intended palette on one entrance/room/column assembly plus adjoining floor.
   Inspect real eye-level and oblique images before propagating bindings. Keep
   texture scale physically coherent on horizontal/vertical faces, avoid stretched
   projections and conspicuous repetitive motifs, and retain dark strip continuity.
3. Apply the verified new material set throughout the copied hall. After initial
   authoring, allow at most two purposeful complete palette trials before handoff;
   technical API fixes are not visual trials. Reuse no old authored texture content.
   Use official Epic MCP for editor changes; discover tools on demand. Reuse the
   existing bounded Python tool registration pattern only if needed.
4. Save/reopen and compare complete live source/candidate actor/component/world
   properties, normalizing only the copied map name and documented material
   override fields. No other unexplained delta may pass. Verify historical asset,
   source and configuration bytes, native material parents/textures/slots, shader
   persistence and assignment coverage. Audit source-to-export-to-Unreal dependency
   paths and hashes, including graph dependencies proving no old opaque parents,
   material functions or textures are used. Verify color space, masks/roughness,
   normal convention, mipmaps and real scale. Reuse relevant texture/channel checks.
5. Capture fresh matched before/after views with original lighting/exposure:
   entrance-90, inner-90, context-90 and aisle-90 from functionalbuild01_capture.py,
   plus stone-column, floor/strip, checkpoint-metal and elevator/service-door
   details. Native 1920x1080, actual pose/FOV/exposure/renderer metadata, no image
   edits or cosmetic crops substituted for context. Capture before under
   WorkerFresh01/Before and final under WorkerFresh01/Final, with exact inventories.
6. Verify actual standing PIE possession and a short forward/return movement
   smoke check on this candidate with the original character settings. Complete
   collision/property preservation carries only the unchanged material-pass scope;
   do not claim a fresh full route certification of owner edits. If a regression
   appears, diagnose within the allowed scope or report it. Restore capture/FOV/
   throttle settings; leave the new candidate clean, loaded, and PIE stopped.

Reuse functionalbuild01_capture.py and the complete property-comparison pattern
in architecture01_lightstudy.py as components with new guarded output paths.
Do not call historical creation/correction flows or write to their default paths.
Reuse existing no-junction storage/inventory and usage tools; no new framework.
Estimate source/export size before authoring; target <=750 MB fresh growth and
report actual growth, retaining the cumulative 2 GB lobby/250 GB project limits.
Delete no user files. Keep generated exports/logs in Saved and avoid duplicated
texture sets for every repeated mesh.

Allowed new files: this task's map and /Game/OpeningLobby/MaterialIntegration01/,
Scripts/OpeningLobby/materialintegration01_*.py, new editable asset source
under Assets/Source/OpeningLobby/MaterialIntegration01/, Worker evidence under
Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01/, and
Docs/OpeningLobbyMaterialIntegration01.md. Historical files, cancelled Worker
evidence and this task spec are read-only. The materialintegration01_* helpers may
be completed or replaced for fresh authoring; pre-steering versions are preserved
under Controller/ReuseAttempt01. Registration bootstrap may load new tools without changing existing
helpers. No AGENTS/config/skill edits, task administration/comments, delegation,
registry writes, commits, pushes or subsequent dispatch by the worker.

Handoff: candidate LobbyMaterial-Integration01/WorkerCandidate01; map path and
hash; standard manifest with relative path, SHA-256 and bytes for map, new native
assets/source, scripts and evidence; material mapping; preservation results;
actual before/final images; limitations and clean final state. Store full logs in
WorkerFresh01, return a concise English report. Include a fresh-authorship inventory
for every role. A native .blend/.spp is needed for each actual DCC contribution.

## Independent review

Use a fresh Multica Visual Reviewer session with environment-architecture-review,
Astra/max/standard. Before author/controller conclusions, inspect the actual
owner reference pair and current before/final images, recording first-look.md.
Then audit the bound map/manifest identity and evidence. Write only the assigned
Review01 directory; no editor operation or candidate mutation.

Judge separately: (1) owner-source preservation; (2) fresh authored graphs/textures,
explicit opaque mapping, provenance and protected glass/collision exceptions;
(3) stone scale and restrained
surface response; (4) polished floor/black strip distinction and repetition;
(5) coherent metal/ceiling/door material response; (6) whole-hall depth/readability
at walking height under unchanged light; (7) exact native/source preservation and
saved/reopened assignments; (8) matched genuine captures, limited PIE evidence,
settings restoration and honest remaining scope. PASS/FAIL/UNVERIFIED with actual
image/data citations, required_corrections, critical_unverified_requirements and
owner_review_ready. A PASS is scoped to this opaque integration; glass B3, final
architecture/detail acceptance, atmosphere and performance are not closed.
