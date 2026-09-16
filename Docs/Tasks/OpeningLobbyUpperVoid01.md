# Upper lobby disappearing into darkness

Latest owner correction, 2026-09-16: continue via
`Docs/Tasks/OpeningLobbyUpperVoid01HeightCorrection01.md`. The yellow section
markup places fade near 14 m; only the main 18 m ceiling disappears. Lower side
passages and their ceilings/soffits behind the columns must stay readable.
This supersedes lower fade placement and any blanket ban on visible aisle lids.

## Authority and outcome

The owner authorized the next lighting/atmosphere task on 2026-09-15 and then
specified its main direction: darkness must begin gradually near the upper hall,
become complete, and conceal any perceived ceiling. The four central columns
must disappear upward into it. Visible height may increase if useful, but is not
required. See `Docs/Approvals/LobbyUpperVoid01-Direction01.json`.

This task develops that effect on the existing geometry. It supersedes old
requirements to keep the main ceiling and upper column contacts readable.
Retain useful lower-hall visibility. The new instruction authorizes this bounded
atmosphere pass despite historical MSQ-7 backlog wording; it is not retrospective
owner visual acceptance of SlabLayout01 or acceptance of the resulting bytes.
Glass remains deferred under LobbyMaterialsComplete01-GlazingDeferred01.

The effect suggests the established involuntary spatial distortion. Read
`Docs/Design/StoryCanon.md`; do not establish literal infinite height, conscious
trials, a new power, an escape mechanism or any new narrative event.

## Identity, preservation and execution

- Use Multica Environment Artist, Astra/high/standard, subscription only,
  existing project, one editor writer and one heavy workload at a time.
- Current sole map: `/Game/Maps/L_OpeningLobby_PainterStone01`, edited in place.
  Preparation observed SHA-256
  `c94331250d378e950ac7780c20bfee0e10145990fb28ac300b38c42477b0b62a`.
- Prior candidate: LobbyMaterials-Complete01/SlabLayout01, manifest
  `Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/manifest.json`,
  SHA-256 `9f2c11c022817c871e8215c9eb95abb1664ad78fa4c28bc94391b66de70abdff`.
- Candidate: `LobbyAtmosphere-UpperVoid01/WorkerCandidate01`.
  Work/evidence: `Saved/OpeningLobby/UpperVoid01/Worker/`.
  New native atmosphere assets only: `/Game/OpeningLobby/UpperVoid01/`.
  Editable recipe/source: `Assets/Source/OpeningLobby/UpperVoid01/`.
  New focused helpers: `Scripts/OpeningLobby/uppervoid01_*.py`.
  Author report: `Docs/OpeningLobbyUpperVoid01.md`.
- Recheck actual Epic connection, project, map, dirty state and PIE before any
  mutation. Controller observed UE5.8.1, correct map, clean packages and active
  PIE with a possessed standing pawn. Ending this PIE for the authorized edit
  is allowed; record state first. Preserve unexpected unsaved work rather than
  discarding it. Do not overwrite intervening owner edits from older archives.
- Controller preserves the exact current map outside Content. Verify its
  receipt and capture a complete live baseline before editing. Retain all
  historical sources, manifests, failed trials and exact archived map bytes.

## Allowed implementation

Inspect the actual two OwnerReferences01 PNGs and the current SlabLayout01 views.
The owner's new upper-darkness direction overrides reference ceiling brightness;
the lower architectural/material language remains relevant. Write a short
specific plan with world-space fade heights and a light/property allowlist.
Those heights are working visual parameters, not owner-approved dimensions.

Allow native level-local light adjustments/additions, exposure, postprocess and
atmosphere controls. A dedicated new native postprocess/atmosphere material and
instance are allowed if needed for smooth world-anchored extinction; preserve its
editable graph and exact source recipe. Choose a supported solution after actual
engine capability inspection. The result must work while moving and looking up,
not merely from a staged camera. Screen-space vignette, a black upper-screen
rectangle, a conspicuous opaque lid, a hard horizontal clipping boundary or
bright visible fog do not satisfy the effect.

Resolve ceiling/upper-column illumination and reflected evidence of the roof as
part of the effect. Keep the accepted glossy stone response by preserving all
107 existing material assignments, material/texture/native source bytes, and
the separate current far-field support mesh/material/properties. Existing glass
can naturally appear different under new scene lighting/atmosphere; do not edit
its optics or local reflection flags, run glass diagnostics, or close deferred R1.

Preserve all existing mesh geometry, architectural dimensions, transforms,
visibility, collision, gameplay, input, camera/FOV defaults, doors, checkpoint,
elevator, room layout and owner edits. Do not hide/delete the ceiling mesh or
replace its material. Light/atmosphere actors and explicitly listed postprocess
properties are the only scene-property exceptions. New technical fog/postprocess
volumes are allowed; new visible model/fixture meshes, dressing, damage, exterior
scenery and architecture are outside this task. Do not raise the roof or extend
columns in this task: first prove what current geometry permits. If geometry
change is truly necessary, retain concrete failed-view evidence and a dimensioned
proposal for owner review instead of silently changing approved dimensions.

No project/user/global configuration edits, installs, downloads, new services,
paid APIs, purchased assets, registry writes/rebaseline, commits or pushes.
Use official Epic MCP. Reuse existing snapshot, property-difference, capture,
walk, file/hash, archive and storage primitives with NEW output paths; do not
rewrite frozen helpers or produce a competing verification/dispatch system.
If the focused registered Epic helper is absent, one minimal Rider Python call
to register the inspected bounded helper is authorized, followed by Epic calls
for scene operations. Do not repeatedly retry equivalent failures without new
evidence; after two failures change the diagnostic approach.

## Bounded production and evidence

1. Validate the rollback, current files and live scene; capture before settings,
   full actor/component properties and native before views. Establish original
   versus allowed property changes before applying them.
2. Produce one representative lighting/upper-darkness setup. Judge axial,
   near-column upward, entrance-facing and reflection views before full capture.
   At most two purposeful author revisions before handoff. Save each trial's
   settings and small genuine evidence set. Keep visual review grounded in
   actual images, not luminance thresholds alone.
3. Save/reopen the useful candidate and read back its native light/postprocess/
   atmosphere graphs, assignments and settings. Compare every existing actor
   and component against the baseline; report the exact scheduled deltas and
   zero unexplained differences. Verify all old material/source/history bytes.
4. Capture about 12 matched before/final native views at 1920x1080, HFOV90 and
   actual standing eye height around 172 cm. Include both axial directions,
   checkpoint, elevator, each side-aisle context, central column close-up looking
   steeply up, upper corners, vertical look-up and polished-floor reflection.
   Record true poses/FOV/resolution, renderer and exposure. Lighting/exposure
   intentionally differ; never label them identical. Preserve gameplay FOV.
5. Reuse real-input walkthrough instrumentation. Record continuous actual
   movement/turn/look-up/look-down and a sustained upward gaze (at least five
   seconds), with time-stamped native frames and telemetry. A sampled frame
   sequence plus continuous runtime log is acceptable if honest; camera
   teleport stills alone do not prove movement, temporal stability or exposure.
   Exercise central/side routes and return, including close to a central column.
   Do not broaden this into new gameplay code or a full cinematic recording rig.
6. Measure a bounded before/candidate performance sample after warmup at matching
   settings, preferably 2560x1440, with actual FPS/frame time and CPU/GPU timing
   if accessible. State sampling duration, renderer/scalability, resolution,
   VSync/caps and frame-generation state. The provisional 60 FPS target is a
   reported goal, not permission to hide a measurement limit or change global
   renderer defaults. Separate screenshot overhead from normal play timing.
7. Restore temporary capture controls, stop PIE, leave the sole map clean and
   saved with the intended atmosphere. Write exact manifest and concise report.
   Use the existing standard entries of path/bytes/SHA-256, unique paths and
   candidate identity. The prior material manifest resolves its changed map
   through the exact controller rollback, never by silent rebaseline.

Planning aim: <=70 MB new task source/assets/evidence; <=100 MB task growth and
<=2.4 GB cumulative lobby planning limit. Hard project cap stays 250 GB.
Use compact bounded evidence and no new texture sets or duplicated project/maps.
Measure actual sizes with the existing no-junction walker. Never delete user
assets or historical evidence to fit a budget.

## Independent acceptance criteria

Fresh Multica Visual Reviewer applies `environment-architecture-review` to this
specific direction, using a separate session and first-look report before author
conclusions. Separate visual and technical verdicts. For each criterion record
PASS, FAIL or UNVERIFIED with concrete native evidence.

1. **Absent perceived ceiling:** entrance, centre, aisles and inner end including
   steep upward views reveal no roof surface, ceiling contact, perimeter seam,
   lit upper corner or terminal column cap that establishes a finite lid.
2. **Progressive column disappearance:** readable lower central columns gradually
   lose detail/contrast with height, then vanish. No abrupt cutoff, visible tops,
   conspicuous common horizontal stripe, banding or luminous fog shelf.
3. **Stable spatial darkness:** the effect remains world-anchored during actual
   walking, rotation and pitch changes. Sustained look-up cannot adaptively reveal
   the ceiling. No persistent flicker, pumping or temporary roof reveal.
4. **Readable lower hall/materials:** player-height route, bases, doors, checkpoint
   and elevator remain legible. Glossy stone, slab joints, metal and floor retain
   useful separation; upper disappearance is intentional, not whole-room crush.
5. **Coherent reflections:** changing-angle floor/stone reflection views do not
   expose a bright roof, terminating tops or a sharp reflected fade boundary.
6. **Preservation:** all 107 material bindings and accepted source/material bytes,
   geometry, owner edits, glass/support, collision, gameplay and exact history
   are preserved. Every changed/added scene property belongs to the allowed
   light/atmosphere/postprocess schedule; no unapproved dimensions or config edits.
7. **Genuine comparable evidence/playability:** before/final pose metadata and
   native image provenance are verifiable, actual movement/look evidence covers
   critical views and restoration succeeds. No staged still-only temporal claim.
8. **Performance and reproducibility:** bounded genuine measurement and honest
   limits; no unexplained severe candidate regression. Saved/reopened candidate
   matches evidence/manifest, clean state, disk limits and restored temporary
   settings; editable native atmosphere source retained.

Deferred glass appearance is recorded separately and cannot alone fail this
narrow task. It is not accepted, corrected or complete. New dressing and full
walkthrough acceptance remain later scope. Passing review makes this identified
effect ready for owner viewing, not owner accepted.

The controller stays through production, fresh review and necessary bounded
correction/recheck. Workers/reviewers do not delegate, comment on/update tasks,
edit controller/approval/instruction files, dispatch later stages or claim owner
acceptance. Reviewer writes only its assigned review directory and does not
mutate the candidate or run shared editor operations.
