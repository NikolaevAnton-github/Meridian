# MeridianSquad agent instructions

- Latest owner direction, 2026-09-16: close all current lobby tasks and defer
  their remaining work until gameplay has been integrated; the owner will then
  provide a new list. See Docs/Approvals/LobbyDeferred01-OwnerClosure01.json and
  Docs/OpeningLobbyDeferred01.md. MSQ-4/6/7/14/20/28/30 are administratively
  closed as cancelled, with disposition CLOSED_BY_OWNER_DEFERRAL. This closes
  their pending work/owner-review gates without rejecting retained assets,
  granting new visual acceptance or declaring deferred verification complete.
  UpperVoid01 acceptance and done MSQ-31/32 remain unchanged. Preserve current
  scene/assets/sources, owner edits, gameplay and all historical evidence.
  Earlier active/backlog/in-review directions below are historical; do not
  resume lobby work or dispatch from them. Wait for the owner's new scope.
  This administrative request does not dispatch gameplay implementation.

- Latest owner acceptance, 2026-09-16: the owner is satisfied with the current
  UpperVoid01 height-corrected atmosphere and explicitly requested closure.
  See Docs/Approvals/LobbyUpperVoid01-Acceptance01.json and
  Docs/OpeningLobbyUpperVoid01Review.md. MSQ-31 and MSQ-32 are done. Accepted
  live bytes are HeightCorrection03, restored exactly during HeightCorrection04;
  its spatial trial remains rejected history. The close-view HC-R1 residual is
  closed by owner acceptance, not technically eliminated; preserve all failed
  reviews and evidence unchanged. Do not resume this correction or dispatch
  another task without a new owner instruction. All 107 bindings, owner geometry,
  original sources and glass/support are preserved. Glass and unrelated final
  walkthrough work remain outside this acceptance. Profiles are restored; no run
  is active. Current map SHA-256 is
  b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f.

- Latest owner correction, 2026-09-16: continue UpperVoid01, raising darkness
  to the yellow section mark around 14 m, affecting only the main 18 m ceiling.
  Do not darken the spaces under the walkways behind columns; preserve readable
  aisle ceilings/soffits and depth. See Docs/Approvals/LobbyUpperVoid01-HeightDirection01.json
  and Docs/Tasks/OpeningLobbyUpperVoid01HeightCorrection01.md. Correct the existing
  low 3.5–8.5 m fade and its lighting consequences via Multica Astra/high/standard,
  fresh independent review and necessary bounded correction. Preserve exact
  previous evidence and current materials, geometry, glass/support and gameplay.

- Latest owner direction, 2026-09-15: execute the next atmosphere task with the
  upper lobby gradually disappearing into complete darkness and central columns
  vanishing upward, so no ceiling is perceived. See
  Docs/Approvals/LobbyUpperVoid01-Direction01.json and
  Docs/Tasks/OpeningLobbyUpperVoid01.md. This explicitly authorizes that bounded
  lighting/atmosphere pass despite older MSQ-7 deferrals. Use existing geometry
  first; preserve all current material/source bytes, 107 bindings, owner geometry,
  collision/gameplay, current glass/support and exact history. Native level-local
  lights/atmosphere/postprocess and dedicated new atmosphere graphs are allowed.
  Glass remains deferred. No dressing/new models or retrospective acceptance of
  SlabLayout01 is implied. Multica Astra/high/standard production, fresh independent
  review and required bounded correction; controller stays through handoff.

- Latest material scope, 2026-09-15: the owner deferred glass and requested
  large-format stone slabs on walls/columns with the accepted column gloss.
  See Docs/Approvals/LobbyMaterialsComplete01-GlazingDeferred01.json and
  LobbyMaterialsComplete01-StoneSlabs01.json. These supersede the earlier glass
  closure gate, quiet-wall R2 target and four protected stone bindings solely
  for slab variants. MSQ-28 completed LobbyMaterials-Complete01/SlabLayout01;
  fresh MSQ-29/Review02 passed all nine included opaque-material criteria.
  Glass criterion 6 and R1 remain DEFERRED_BY_OWNER, not accepted or corrected.
  See Docs/OpeningLobbyMaterialsComplete01Review.md for exact identity and
  documented administrative/global-configuration exceptions. Current sole map
  SHA-256 is c94331250d378e950ac7780c20bfee0e10145990fb28ac300b38c42477b0b62a.
  All 44 stone bindings now use slab variants; 63 nonstone assignments and
  13 accepted floor/metal bindings, old sources and owner geometry are preserved.
  Working slabs are 120 x 240 cm / 5 mm joints, not exact owner-approved sizes.
  New slab scope uses 450 MB batch / 2.4 GB lobby planning limits; hard project
  cap remains 250 GB. Both profiles and task arguments are restored; no active
  run. The opaque candidate is ready for owner viewing, not owner accepted.
  Retain current glass; do not resume its deferred task or final atmosphere
  without subsequent owner instruction. Preserve frozen candidates/history.


- On 2026-09-15 the owner accepted all current lobby materials, including
  LobbyPainter-Metal01/WorkerCandidate01, and explicitly requested all remaining
  materials together, expecting the lobby fully covered with materials. See
  Docs/Approvals/LobbyPainterMetal01-Acceptance01.json. This supersedes prior
  serial material-direction gates and deferrals of broad stone, entrance
  metal, ceiling/soffit and glazing materials. Execute the complete batch via
  Docs/Tasks/OpeningLobbyMaterialsComplete01.md, Multica Astra/high/standard,
  in place on the current map, with fresh independent review and required
  bounded corrections. Do not stop for individual family approval. Preserve
  all 17 accepted bindings, accepted source/assets, owner geometry and exact
  history. The new task adjusts the old 2 GB lobby planning target to 2.4 GB
  for full material completion; the hard 250 GB project cap remains. New
  geometry and final atmosphere remain outside this material-only request.

- On 2026-09-15 the owner accepted LobbyPainter-Floor01/WorkerCandidate01
  after viewing the materials and instructed us to continue. See
  Docs/Approvals/LobbyPainterFloor01-Acceptance01.json for the exact verified
  identity. This closes the floor-direction gate; historical pending wording
  in Floor01 evidence is superseded without changing those bytes. Continue
  via Docs/Tasks/OpeningLobbyPainterMetal01.md: one bounded native Painter
  metal family for ten checkpoint/service-door/elevator component slots,
  in place on the current map, Multica Astra/high/standard, fresh review and
  bounded correction. Preserve accepted stone/floor, owner edits and exact
  history. Other material rollout and final atmosphere remain pending.
  MSQ-26 subsequently completed LobbyPainter-Metal01/WorkerCandidate01;
  fresh MSQ-27 Review01 passed all eight criteria with no required correction.
  See Docs/OpeningLobbyPainterMetal01Review.md for exact reviewed identity.
  The current map has ten new metal bindings, with accepted stone/floor and
  owner geometry preserved. Current map SHA-256 is
  abc72118717b8333a109fdeeaf1583485a3e7b35badced84204e9fcc130ebc92.
  Profiles and task-local arguments are restored; no run remains active.
  New metal is ready for owner direction review, not owner accepted.

- On 2026-09-15 the owner approved LobbyPainter-Stone01/Correction01
  after viewing it, authorized removing previous lobby levels and retaining only
  /Game/Maps/L_OpeningLobby_PainterStone01, and requested the next materials.
  See Docs/Approvals/LobbyPainterStone01-Acceptance01.json and
  Docs/Tasks/OpeningLobbyPainterFloor01.md. This supersedes older map-retention
  and new-map-copy instructions: archive exact retired-map bytes outside Content,
  keep only the current lobby map and work on it in place with a bounded rollback
  snapshot. Preserve accepted stone, owner geometry/edits and non-map history.
  The next bounded native Painter floor/black-strip pair uses Multica
  Astra/high/standard with fresh independent review and bounded correction.
  Other families and final atmosphere remain pending.
  MSQ-24 subsequently completed LobbyPainter-Floor01/WorkerCandidate01; fresh
  MSQ-25 Review01 passed all eight criteria with no required correction. See
  Docs/OpeningLobbyPainterFloor01Review.md for exact identity. Nine obsolete maps
  are now archived outside Content and removed; both startup defaults target the
  surviving PainterStone01 map. It contains the three new floor/strip bindings,
  with approved stone and owner geometry preserved. Current map SHA-256 is
  5cc84cac736d24cfe0dedf4c4d1dd0413b3d07f081c9e82e5dd4ab2ca0ae9270.
  All task-local profiles/arguments are restored; no run remains active. The new
  floor pair is ready for the owner's direction decision, not owner-accepted.

- Use Russian only in the owner's direct chat with Codex. A Multica run is an
  internal project execution context: its progress messages, task discussions
  and final reports must be in English, even when dispatched from Russian chat.
  Write all project content in English, including documentation, code comments,
  names and commit messages.
- Budget: the user's existing $200/month Codex subscription only. Do not add paid
  API usage, paid cloud generation, extra credits or paid services. Local models
  are allowed, subject to available RAM/VRAM and project disk space.
- Project disk budget is at most 250 GB, including generated data, local version
  history and project-specific services. Avoid duplicated Unreal worktrees and
  unrestricted caches. Never delete user assets to reclaim space.
- Optimize for a verified result including rework. Use Astra for difficult work;
  select other models only when appropriate and available. Prefer standard speed;
  set reasoning effort to the task rather than routinely using the maximum.
- Delegate bounded independent tasks only. Keep context focused: locate files,
  read relevant sections, return concise findings and save full logs under Saved/.
- One writer per running Unreal/Blender/Substance instance. Coordinate the whole
  editing operation, not just individual MCP calls. Run one memory-heavy build,
  bake, render or local model workload at a time until measurements justify more.
- Prefer the official Epic MCP for Unreal editor operations. Its Codex entry is
  unreal_epic, address http://127.0.0.1:8000/mcp. Discover needed toolsets on demand.
  Confirm the project and editor state before mutations. Rider tools remain
  useful for code work and debugging; their connection is independent of Epic MCP.
- Check actual capabilities and installed versions before using a DCC bridge.
  Do not assume a working connection just because configuration exists.
- Define acceptance criteria, make a bounded change, and verify the result.
  Repeat failed actions only when new evidence warrants it. After two equivalent
  failed attempts, change the diagnostic approach. Avoid redundant passing tests.
- Source code, configuration, accepted decisions and asset source files belong
  in Git; binary assets use Git LFS. Generated data and large logs stay outside Git.
  Never put credentials in tracked files or tool output.
- For game/level requirements, use Docs/Design/GameBrief.md. For narrative work,
  also read Docs/Design/StoryCanon.md and preserve fixed facts, working proposals
  and unresolved details as separate categories. The first playable milestone
  is the lobby walkthrough specified in Docs/Tasks/OpeningLobby.md.
- Before environment layout or model production, create a separate concept-art
  task and obtain the owner's explicit approval of an identified art version.
  Technical prototype acceptance and a request for the next task are not visual
  approval. LobbyArt-Review02 and LobbyScale-Review01 are now owner-approved;
  follow Docs/Tasks/OpeningLobbyLayout03.md for the authorized neutral blockout.
  The rejected Stage1/Layout02 maps remain unapproved historical prototypes.
- After the owner's rejection of MSQ-9 scale, environment preproduction must
  include dimensioned plans/sections with human scale, approved as a named
  package before renewed 3D work. Follow Docs/VisualAcceptance.md and
  Docs/Tasks/OpeningLobbyScaleReview.md. An independent visual reviewer must
  inspect the actual art and comparable views; technical checks cannot grant
  visual acceptance. The owner requires at least twice Layout02's architectural
  scale. On 2026-09-14 the owner approved LobbyScale-Review01's exact dimensions
  and human-scale exceptions; the identified immutable manifest and external
  approval record are linked in Docs/OpeningLobbyScaleReview.md. Layout03 /
  MSQ-11 passed technical and independent visual review after Correction01.
  On 2026-09-14 the owner explicitly accepted its in-game scale, deferred detail
  assessment and authorized continuing. See Docs/Approvals/LobbyLayout03-Scale01.json.
  MSQ-6 architecture/material production now follows Docs/Tasks/OpeningLobbyArchitecture01.md,
  preserving that scale. Detail acceptance remains pending; MSQ-7 stays backlog.
- On 2026-09-14 the owner rejected the current lobby's overall architectural
  quality and authorized a skills-assisted architectural rework study. Follow
  Docs/Tasks/OpeningLobbyArchitectureRework01.md for the entrance/colonnade 2D
  alternatives and independent review. Retain approved overall scale, but do not
  treat old proxy envelopes as limits on proposed secondary architecture; label
  dimensional changes for owner review. A named package must be approved before
  its 3D production. Earlier detail passes do not establish overall likeness.
- On 2026-09-14 the owner reviewed the new drawings and selected Variant A of
  LobbyArchitecture-Rework01 / Candidate01. The unchanged package identity and
  selection scope are recorded in Docs/Approvals/LobbyArchitectureRework01-VariantA.json.
  After executor clarification, the owner explicitly requested max reasoning and
  instructed us to proceed. Follow Docs/Tasks/OpeningLobbyArchitectureReworkA01.md
  for the bounded neutral 3D assembly, independent review and correction through
  Multica at Astra/max/standard. Owner acceptance of 3D quality remains pending.
  MSQ-14's WorkerCandidate01 subsequently passed technical and fresh MSQ-15 visual
  review with no required correction remaining; see
  Docs/OpeningLobbyArchitectureReworkA01Review.md and its exact candidate identity.
  The neutral candidate is ready for the owner walkthrough. Do not treat that
  review as owner acceptance or start full-hall detailing/atmosphere from it.
- On 2026-09-14 the owner walked through ReworkA01 and gave positive feedback,
  requesting four terminal room-like colonnade infills (inner doors facing the
  hall, entrance doors facing the aisles), a full-width two-lane checkpoint,
  and a large inner elevator with the high window replaced by an opaque future
  name/logo field. Retain remaining architecture and scale. See
  Docs/Approvals/LobbyArchitectureReworkA01-Walkthrough01.json and the focused
  Docs/Tasks/OpeningLobbyFunctionalRevision01.md drawing task. New dimensions
  require named-package approval before 3D; final look/atmosphere is not accepted.
  MSQ-16's LobbyFunctional-Revision01/Candidate01 now passed fresh MSQ-17 visual
  and technical review with no required correction. Exact identity and five
  sheets are in Docs/OpeningLobbyFunctionalRevision01.md. Owner approval of
  the new dimensions, central-only checkpoint and route deltas remains pending;
  no 3D changes were made. Both profiles returned to their prior settings.
- Later on 2026-09-14 the owner rejected FunctionalRevision01's interpretation
  and supplied yellow plan markup. Four terminal rooms must extend to the outer
  walls, closing terminal side aisles; entrance service doors move to transverse
  caps facing the remaining corridors, inner doors stay hall-facing. Add four
  central columns reaching the main ceiling. Follow
  Docs/Tasks/OpeningLobbyFunctionalRevision02.md and
  Docs/Approvals/LobbyFunctionalRevision02-OwnerMarkup01.json. The markup
  supersedes prior terminal-aisle preservation. Prepare/review the revised named
  dimensioned package before 3D; retain the old package and review as history.
  MSQ-18's LobbyFunctional-Revision02/Candidate01 now passed fresh MSQ-19 visual
  and technical review with no required correction. See
  Docs/OpeningLobbyFunctionalRevision02.md for its immutable identity, five
  sheets, exact dimensions and the columns' substantial sightline effect.
  The owner subsequently approved this latest package and instructed us to start.
  See Docs/Approvals/LobbyFunctionalRevision02-Production01.json for exact identity
  and Docs/Tasks/OpeningLobbyFunctionalBuild01.md for authorized neutral 3D
  production, fresh independent review and bounded correction through Multica.
  The approved scope includes the scheduled room/door/roof dimensions, column
  thickness/spacing and sightline density, checkpoint/elevator and route changes.
  Preserve the frozen drawings; their pending wording is historical. Acceptance
  of resulting 3D bytes and final atmosphere remains pending. MSQ-16 is cancelled
  as superseded; MSQ-18's drawing approval gate is closed and MSQ-19 is done.
  MSQ-20 subsequently produced LobbyFunctional-Build01/WorkerCandidate01; fresh
  MSQ-21 passed all ten visual/technical criteria with no required correction.
  See Docs/OpeningLobbyFunctionalBuild01Review.md for exact reviewed identity.
  The owner then edited the current FunctionalBuild01 map and confirmed it in
  direct chat. Preserve that edit; do not overwrite it from the historical worker
  archive or rebaseline the old manifest. The review applies to pre-edit bytes.
  See Docs/Approvals/LobbyFunctionalBuild01-OwnerEdit01.json. Owner confirmation
  of authorship is not final 3D/atmosphere acceptance. Both profiles are restored.
- On 2026-09-15 the owner requested Astra/max/standard for the next lobby task's
  Spatial Designer, Environment Artist and Visual Reviewer. All three profiles
  and native reasoning arguments were set to max for this task. Execution,
  independent review and bounded correction/recheck are now complete at the
  owner material-direction gate; all three profiles and original instructions
  were restored to the saved high baseline. See Docs/VisualAcceptance.md and
  Saved/OpeningLobby/NextTaskMax01/Controller/. No run was dispatched by this
  administrative setting change.
- The owner then instructed us to execute the next lobby task. Follow
  Docs/Tasks/OpeningLobbyMaterialIntegration01.md for the bounded MSQ-6 opaque
  material integration on a separate copy of the current owner-edited map,
  Astra/max/standard production and fresh independent review. Preserve the
  owner's source, geometry, glazing and lighting; final atmosphere remains later.
  During MSQ-22 the owner explicitly required remaking the old materials from
  scratch. This supersedes the initial reuse approach: author fresh opaque graphs,
  texture content and editable sources, with no old opaque material/texture
  dependencies. The cancelled inspection run remains historical; renewed work
  uses WorkerFresh01. Follow the revised task, with independent provenance and
  visual review at max. Technical bridges/validators may be reused.
- The owner then rejected the new NumPy-authored pilot as not resembling stone
  and explicitly requested Painter. Both pre-Painter MSQ-22 runs are cancelled
  and preserved.
  Continue via Docs/Tasks/OpeningLobbyPainterStone01.md: genuine new native Painter
  layer/resource authoring and .spp source for one stone sample, shown on existing
  geometry, with fresh independent review at Astra/max/standard before broad
  rollout. See Docs/Approvals/LobbyMaterialIntegration01-Rejection01.json. Do not
  reuse rejected texture pixels or wrap them in a ceremonial Painter project.
  Task-local advanced Painter tools/path roots are authorized; preserve project
  and global configuration. User material-direction acceptance remains pending.
- MSQ-22's native Painter WorkerCandidate01 passed technical checks but failed
  MSQ-23 Review01 on stone likeness, mineral hierarchy and conspicuous repetition.
  The bounded Docs/Tasks/OpeningLobbyPainterStone01Correction01.md correction
  produced LobbyPainter-Stone01/Correction01. MSQ-23 Review02 passed all eight
  visual/technical criteria, closed R1/R2 and left no required correction or
  critical unverified requirement. See Docs/OpeningLobbyPainterStone01Review.md
  for the exact current manifest/.spp identity and residual highlight detail.
  The map is /Game/Maps/L_OpeningLobby_PainterStone01; its map hash stayed the
  same while material/source bytes changed, so use the correction manifest.
  Preserve the original Worker evidence, Review01 and BeforeCorrection01 archive.
  Owner FunctionalBuild01 and its edit remain unchanged. This is one stone sample
  ready for the owner material-direction decision, not whole-lobby material or
  atmosphere acceptance; other families remain pending and MSQ-7 remains backlog.
  The max trial is complete and all three profiles are restored to Astra/high/
  standard. Task-only advanced Painter overrides are removed; Docs/PainterWorkflow.md
  records the verified native authoring route for future scoped tasks.
- Multica passed a complete Blender/Painter/Unreal asset task and a direct-Codex
  comparison using subscription authentication. Keep concurrency at one and use
  the existing project directory. The owner selected Multica as the default
  execution route for project implementation tasks. Direct chat handles task
  clarification, dispatch, review and small administrative updates. Use Multica's
  `suppress_run=true` for administrative status/assignment updates; dispatch
  intended runs explicitly. The direct controller must remain active through
  the dispatched run, handoff review and required bounded corrections until a
  verified result or a concrete owner decision gate. Successful dispatch and
  background execution alone do not complete the controller's work. Do not build a competing dispatcher
  or separate task database. Reuse the existing validators; do not rebuild the
  benchmark harness or repeat A/B runs for routine assets. Track native input,
  cache and output separately; Multica 0.4.43 adds reasoning to output again.
  Shared preparation was the largest experiment cost. Asset metadata is now in
  the separate local PostgreSQL database meridian_assets. Use the register,
  inspect and validate commands documented in Docs/AssetRegistry.md. Preserve
  accepted fingerprints and relationship uncertainty; registration is not
  approval of changed asset bytes. See Docs/AssetRegistryAcceptance.md and
  Docs/AgentDevelopment.md for evidence and the next stage.
