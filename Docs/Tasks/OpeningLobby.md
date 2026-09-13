# Opening lobby walkthrough

Status: planned as Multica parent MSQ-4; no lobby implementation has started.
Child tasks MSQ-5, MSQ-6 and MSQ-7 are unassigned backlog items for stages 1-3.

Owner request: a realistic first-person skyscraper entrance lobby to walk
around, using the lobby from The Matrix (1999) as the architectural reference.
Read [game direction](../Design/GameBrief.md) and the fixed facts and knowledge
constraints in [story canon](../Design/StoryCanon.md). These briefs do not
commission combat or a fully scripted opening mission.

## Milestone structure

One parent deliverable, three sequential implementation tasks. Each task has a
bounded output and a saved handoff; later work builds on the accepted level.
Keep later tasks in backlog while the preceding stage is being assessed.
One suitably configured Multica worker owns the active editor operation.

| Stage | Deliverable | Acceptance gate |
| --- | --- | --- |
| 1. Walkable spatial prototype (MSQ-5) | First-person movement, floor/walls/ceiling, column rhythm, entrance/security area and elevator destination, simple material families and lighting | PIE spawns an on-foot character; the complete route is traversable with working collision and readable scale. |
| 2. Architecture and materials (MSQ-6) | A small modular Blender kit, appropriate Painter materials, UVs/collision and imported Unreal assets replacing the approved prototype shapes | Architecture and surface response hold up at eye level; floor, stone, metal and glass remain distinct under neutral inspection light. |
| 3. Atmosphere and walkthrough acceptance (MSQ-7) | Set dressing, final lighting/exposure, bounded static damage, route verification, performance sample and accepted registry entries | The owner can explore a coherent lobby; evidence demonstrates playability, visual quality, file provenance and measured performance. |

The first stage already provides a playable walkthrough. Spatial layout and
first-person comfort should be reviewed before expensive detail is added.
Completing stage 1 does not mean the realistic visual milestone is finished.

## Working spatial/art direction

The following choices are proposals for this lobby, not new narrative canon:

- Monumental, ordered stone architecture: repeated column bays, tall interior
  openings, geometric floor divisions, stone wall panels and restrained metal.
- A clear entrance-to-elevator axis, flanking circulation and a security/reception
  area. Provide enough lateral space for future first-person combat movement.
- Start with a room approximately 36 x 22 m and a ceiling around 8 m; tune these
  provisional dimensions from first-person views before producing final meshes.
- A dark, realistic atmosphere with readable silhouettes and restrained cool
  green/neutral tones. Avoid using color grading to hide unfinished materials.
- Pending owner preference: localized post-catastrophe disorder and damage
  while the architecture remains readable. This does not establish the specific
  attack sequence or cause of any squad member's death. No staged squad bodies.
- The entrance boundary and upper-floor access can be simple prototype barriers.
  Do not invent a definitive mechanism for the anomaly or a guaranteed exit.
- Build original project assets and an adapted layout. Film frames are visual
  reference, not textures or game content to import.

Visual reference inspected during preparation:
[The Matrix lobby frame](https://flipscreenblog.wordpress.com/wp-content/uploads/2020/01/matrix.jpg),
linked by [Flip Screen](https://flipscreened.com/2020/01/29/the-essential-guide-to-the-wachowskis/).
The local reference copy is ignored under
`Saved/AgentSetup/Lobby/References/MatrixLobby02.jpg`.

## Stage 1: walkable spatial prototype

- Confirm the running editor belongs to MeridianSquad, check PIE and dirty
  packages before changing levels; preserve unrelated work and test assets.
- Create a dedicated level, proposed `/Game/Maps/L_OpeningLobby`. The exact map
  name is an implementation choice; document the final path and how to open it.
- Add a small reusable first-person character/game mode and mouse/keyboard input.
  Walking and looking are required; sprint is optional. The character must have
  gravity, floor contact and collision rather than spectator flight. No weapon,
  arms animation, abilities or elaborate movement system is required yet.
- Suggested eye height is 165-175 cm and initial horizontal FOV about 90 degrees;
  treat these as prototype tuning, not a locked character biography or final feel.
- Establish the full route with columns, side paths, security/reception massing
  and elevator-bank destination. Add basic materials, visible lighting and a
  stable exposure so the room is assessable when walking.
- Verify a real PIE spawn and movement. Inspect pawn possession, gravity and
  collisions, and exercise movement along the route; an editor-camera flythrough
  alone does not pass. Record controls, return path and any unverified behavior.
- Provide eye-level screenshots at the entrance, center and elevator end, plus
  an overview plan. Save full checks under `Saved/OpeningLobby/Stage1`.

## Stage 2: architecture and materials

- Reuse the accepted dimensions. Make a small kit of repeated column, wall,
  floor and ceiling/trim modules; add only the needed entrance and elevator parts.
- Keep structural collision, surface cladding, glass and movable dressing
  separable. Choose pivots and material slots that support later targeted damage.
  Do not fracture every object, build dynamic destruction, or merge the entire
  room into one mesh for this walkthrough.
- Use Blender and Painter where each is useful. Large repeated surfaces should
  use shared/tileable materials; individual objects can use bounded texture sets.
  Designer/Sampler are optional only if a specific material need justifies them
  and their installed capabilities have been checked.
- Inspect scale, UVs, normals, tiling, collision and material response at walking
  distance. Preserve source files and import/export paths. Use Git LFS for binaries.
- Save comparison screenshots and source/export checks under
  `Saved/OpeningLobby/Stage2`. Do not promote filenames alone into verified edges.

## Stage 3: atmosphere and acceptance

- Add restrained dressing that serves the lobby's identity and future gameplay:
  security fixtures, seating, signs, lighting fixtures and localized debris.
  Final density/damage depends on the owner's preference and stage 1 review.
- Tune lighting and exposure from the player's route. Check glass, stone and
  polished floor response; avoid light leaks and excessively crushed shadows.
- Re-run the route in PIE, including side paths and return movement. Ensure
  dressing has not introduced snags or blocked the required paths.
- Capture the same key eye-level views used in previous stages. Record a bounded
  performance sample on the user's PC after warmup, with resolution and renderer
  settings stated. A provisional goal is 60 FPS at 2560 x 1440, without counting
  frame generation; report CPU/GPU frame timing where available and actual limits.
- Register accepted lobby assets/manifests once their bytes and verification
  reports are stable. The current registry deliberately rejects silent rebaseline;
  do not repeatedly register changing drafts or expand this task into a revision
  system. Any required small registry compatibility issue must be reported first.
- Document the map path, controls, evidence, source locations, disk increase and
  limitations. Leave the accepted level ready to open and play in the editor.
  A separately packaged executable is not required for this milestone.

## Resource and orchestration rules

Use the existing local project and subscription. No paid API, store purchases,
new service, duplicate Unreal checkout or unrestricted asset download. Aim for
at most 2 GB of new source/assets/exports for this small lobby; measure actual
growth and stay within the overall 250 GB project cap. This is a planning cap,
not an allocation or permission to delete existing assets.

Run one memory-heavy build, bake, render or local model at a time. Discover Epic
MCP toolsets only as needed. Configure each worker for its stage: the MSQ-3 code
worker has DCC tools disabled and must not be reused unchanged for editor work.
Reuse existing validation/accounting tools. Count native input, cached subset
and output once, including corrections; record controller/reviewer cost separately.
Owner visual/play feedback and machine checks serve different purposes.
