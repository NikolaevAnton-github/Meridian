# Opening lobby Layout02: walkthrough from approved art

Multica task: MSQ-9, a child of MSQ-4.

Current disposition on 2026-09-14: cancelled and superseded by MSQ-10/MSQ-11;
preserve this prototype and its technical evidence. The owner accepted the
resulting Layout03 scale and authorized MSQ-6, with detail assessment deferred.
See [the scoped decision](../Approvals/LobbyLayout03-Scale01.json).
Requirements and pending gates below are historical, not current dispatch authority.

Status: owner reviewed and rejected the architectural scale of MSQ-9.
The owner requires monumentality and at least twice the architectural scale.
Prepare the separate [scale drawings](OpeningLobbyScaleReview.md) and obtain
approval before renewed 3D work. Historical technical verification remains valid.
The saved `/Game/Maps/L_OpeningLobby_Layout02` is the rejected review baseline.
See [Layout02 handoff](../OpeningLobbyLayout02.md) for controls, views, measured
proportions and verification. Owner layout acceptance is rejected.

The owner explicitly approved LobbyArt-Review02 for transition to layout.
MSQ-8 is accepted; this is a separate bounded implementation task under MSQ-4.
MSQ-6 (detailed architecture/materials) and MSQ-7 (atmosphere) remain in backlog
until this revised walkthrough has been reviewed. Use the existing project and
one Multica Astra worker with medium reasoning and standard speed.

## Visual authority and bounded output

Inspect all three approved images, not only their text descriptions:

- `Assets/Concepts/OpeningLobby/OwnerReferences01/01-InnerEnd.png`
- `Assets/Concepts/OpeningLobby/OwnerReferences01/02-EntranceSecurity.png`
- `Assets/Concepts/OpeningLobby/Review02/03-SecurityOblique.png`

The first two are opposite views of the same hall. They control the architecture;
the third clarifies the checkpoint and its relation to the aisle. Approval hashes
are in `Assets/Concepts/OpeningLobby/Review02/approval.json`. Read GameBrief and
StoryCanon for product scope and narrative limits. Review01-A/B/C and the
rejected Stage 1 dimensions are not design constraints.

Create a new saved map, proposed `/Game/Maps/L_OpeningLobby_Layout02`, with
prototype geometry and enough material/light definition to assess the approved
space from standing eye height. Preserve `/Game/Maps/L_OpeningLobby`, its saved
materials and all Stage 1 evidence. Use dedicated Layout02 asset paths. Reuse
the existing first-person character/game mode, controls and movement values.
Do not build final Blender/Painter modules, combat, destruction, narrative events
or a packaged executable. No new services or paid assets are needed.

## Architectural acceptance

- Reconstruct a long, ordered central hall with symmetrical square stone piers,
  narrower continuous side aisles, heavy lintels and a higher central volume.
  Match the reference proportions at human scale; do not retain the old broad
  room, column spacing or coffered/luxury-lobby ideas by default.
- Use the human-scale door and checkpoint as scale cues. State the selected
  room, column, bay, aisle and height dimensions as implementation estimates,
  not measurements extracted with certainty from images. Choose a coherent
  spatial interpretation and compare both end views before detailed production.
- The entrance end has tall narrow mullioned glazing, entry glazing below and
  a compact dark-metal screening checkpoint. Looking toward the entrance,
  the station is left of its detector frame. Both directions through the
  checkpoint and its connection to a side aisle must remain traversable.
- The opposite end has one small opaque door beneath a high narrow window.
  Do not install the superseded three-elevator wall or explain where the door
  leads. Boundaries can remain closed beyond the lobby without narrative claims.
- Provide the two black parallel strips on the green-grey floor, distinguish
  dark stone, metal and glazing, and use restrained cool side-aisle linear
  lighting. Keep midtones readable for spatial review. Simple reusable Unreal
  materials are sufficient here; no texture pipeline or final art pass is needed.
- Avoid ornamental ceiling coffers, plants, artwork, extra security stations,
  large damage or clutter. Keep collision and visual dressing separable.

## Verification and evidence

1. Before editor changes confirm the MeridianSquad project, current map, PIE
   and dirty packages. Preserve unrelated unsaved work. The controller may have
   started the same project; do not launch another editor or restart without need.
   Prefer official Epic MCP. If native tools are not exposed, use the existing
   official HTTP endpoint and project client patterns; Rider is a fallback for
   tool registration and read diagnostics, not another orchestration service.
2. Reuse and narrowly parameterize the existing `Scripts/OpeningLobby` verifier
   for map identity, output directory, waypoints, capture labels and new collision
   expectations. Keep Stage 1 defaults and reports intact. Do not run old hardcoded
   coordinates against the new layout, overwrite Stage 1 evidence or build another
   independent acceptance harness. No C++ changes appear necessary.
3. Verify real PIE possession, walking/gravity, mouse input and grounding using
   the existing controller input-event path. Traverse entrance to inner door,
   both side aisles, checkpoint passage and return. Test a wall, column and jump/
   landing. Derive collision contact expectations from measured blocking surfaces
   and capsule dimensions; record bounded tolerances. Teleports and editor-camera
   movement are not runtime route evidence. Normalize PIE map prefixes and reject
   the wrong map before sending input.
4. Save evidence under `Saved/OpeningLobby/Layout02`, including reference-aligned
   eye-level entrance-to-inner-door and reverse views, a security oblique view,
   a center view, an overhead plan, selected dimensions and runtime samples/results.
   Restore temporary ceiling visibility and camera/lighting inspection changes
   before saving. Avoid overwriting the normal captures with alternate-view runs.
5. Save and reopen the new map, verify its game mode and clean saved state, and
   leave it open with PIE stopped, ready for the owner to play. Document the map,
   controls, reproducible tool calls, file paths, estimated dimensions, visual
   limitations and disk growth in `Docs/OpeningLobbyLayout02.md`.

## Preservation and resource limits

Preserve all approved concept bytes, benchmark/source assets, original map,
unrelated dirty work, AGENTS.md and the pre-existing `.codex/config.toml` exactly.
Keep movement/input unchanged unless a concrete blocker requires a bounded fix.
Do not change default-map configuration merely for convenience; leave the new
map open and provide its path. Preserve legacy dirty-material preservation tools
and their historical manifest paths when parameterizing verification output.

Use one editor writer and one heavy workload. Prefer no build for this geometry
task. Keep new map/assets/evidence bounded within the 2 GB lobby planning cap and
250 GB project cap, measure growth, and never remove user assets for space.
Use existing Git LFS rules. Draft layout files are not final registry entries;
do not rebaseline any asset fingerprints. Keep task state in Multica; use
`suppress_run=true` for administrative edits and dispatch the one intended run
explicitly. The worker returns a concise English handoff and does not commit,
push, post comments, change issue status, delegate or start later stages.
