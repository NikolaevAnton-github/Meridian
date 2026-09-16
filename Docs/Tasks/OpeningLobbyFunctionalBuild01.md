# LobbyFunctional-Build01: approved functional revision in neutral 3D

The owner approved LobbyFunctional-Revision02/Candidate01 and instructed us to
start on 2026-09-14. Execute through the existing Multica Environment Artist,
Astra/high/standard, subscription authentication, concurrency one, existing project.
The direct controller stays active through production, fresh independent review,
and at most one bounded correction and focused recheck.

## Authority and assembly contract

Read AGENTS.md, Docs/Design/GameBrief.md, Docs/VisualAcceptance.md and
Docs/Approvals/LobbyFunctionalRevision02-Production01.json. Explicitly load
`.agents/skills/environment-architecture-production/SKILL.md`. Inspect the actual
five FunctionalRevision02 PNG sheets and original owner markup before construction.
Inspect primary OwnerReferences01 art and retained A views as needed for context.
Avoid unrelated task/benchmark histories. The complete authoritative dimension
source is Assets/Concepts/OpeningLobby/FunctionalRevision02/design.json, README,
geometry.mjs.txt and retained-functions.mjs.txt. Manifest SHA-256:
440064e9a1df1180cec92cc3e43be78034b7de30a6e94ef94d0a9d0534b0ecd1.
Verify it read-only with its existing freeze.mjs --verify. Historical pending
wording in frozen files is superseded by the external owner decision.
Active rooms/columns/checkpoint/elevator/routes override historical shared and
retained_A fields. Do not build the historical detector/station/window or test
old X +/-27 terminal crossovers as active requirements.

Create `/Game/Maps/L_OpeningLobby_FunctionalBuild01` from the saved ReworkA01 map
(SHA-256 71cfc087c80510313054255d784d1b43c45395d6400c9e0b75e9f64d7be944d0).
Preserve all old maps/assets/source bytes. Reuse unchanged assets read-only; new
or writable assets use `/Game/OpeningLobby/FunctionalBuild01/`. No default-map,
gameplay code, project configuration or user-setting changes.

Before editing, write a short assembly contract under Worker: authoritative
dimensions, intended baseline deltas, module/junction plan, collision strategy,
and evidence cameras. Use common approved data, converting metres to Unreal cm.
Primary dimensional tolerance is 0.05 m; scheduled openings must retain clearance.

- Preserve the 60 x 24 x 18 m hall, twelve original shafts at six stations,
  retained A portal/beam/upper setback and floor strips. Four terminal original
  piers are integrated into rooms; eight original piers remain free-standing.
- Build all four rooms: entrance X -30..-19.8, inner X 19.8..30, absolute Y
  5.6..12; gross 10.2 x 6.4 m. No obsolete partition at absolute Y 8 and no
  terminal aisle bypass. Hall-facing infill joins existing masses coherently.
- Walls 0.36 m; stepped closure absolute Y 5.6..8 at Z 8.04..8.4 and absolute
  Y 8..12 at Z 8.84..9.2, joined against existing beam. Avoid gaps, duplicate
  coplanar faces, floating trim or accidental accessible upper floors.
- Entrance doors on X -19.8 caps at Y +/-10 face +X. Entrance hall walls blind.
  Inner doors at X 26.1, Y +/-5.6 face Y=0; inner transverse caps blind.
  Closed 1.2 x 2.4 m doors, 0.24 m recess, frame 0.12, leaf 0.06, flush threshold.
  No interiors, staircases, destinations or door operation.
- Four new shafts: X +/-12.6, Y +/-2.4, section 2.4 x 2.4, Z 0..18. Full-section
  ceiling contact, no capitals or new ceiling holes. Actual gaps 2.4 m on axis
  and 2.0 m to original shafts; floor strips stay beneath them as drawn.
- Replace old checkpoint arrangement with the approved common-source assembly
  at X -24.6. Exactly two floor-level accessible 1.5 m openings: Y -5.4..-3.9
  and 3.9..5.4, within 11.2 m control width. Desk/posts/barriers join room walls
  without a walkable bypass. This is geometry/circulation, not security gameplay
  or anti-jump certification. Use the exact retained-functions source dimensions.
- Replace inner small door/high window with a single 3.6 x 4.2 m elevator opening,
  0.6 m reveal, closed leaves and opaque upper wall/blank future branding field.
  Remove obsolete visible remnants in this new map only. No logo or cab/shaft.
  Remove all superseded high glazing/mullions/transoms. Outer frame 4.4 x 4.6 m;
  visible leaf at X30, backing X30.06. The 6 x 6 m branding reservation is only
  an annotation; build flush opaque wall, not a raised sign or outlined panel.

## Production and permitted writes

One worker owns the whole Blender/Unreal editing operation. Verify actual app
versions/connections, correct project, map, PIE and dirty packages before mutation.
Apps were stopped at controller preflight. You may launch the installed UE 5.8.1
editor at D:/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe with the existing
MeridianSquad.uproject, and existing Blender if needed; no second app instance.
Use Start-Process -WindowStyle Hidden for helpers. Do not discard unsaved work.
Prefer official Epic MCP http://127.0.0.1:8000/mcp; discover needed toolsets.
Reuse existing narrowly scoped Python registration and reworka01/layout03 helpers,
including their saved/reopened, profile, capture and actual PIE verification patterns.
If initial MCP startup occurred before editor launch, reconnect using existing local
client patterns rather than changing shared configuration. After two equivalent
failures change diagnostic approach. No new benchmark harness or broad framework.

Keep an economical reusable neutral kit and editable source/reproduction. Existing
meshes may be reused; if authoring new modules with Blender keep a meaningful native
.blend plus reproducible scripts. Validate transforms, normals, UVs, material slots,
imported profiles and collision. Real visible projections need matching collision.
Painter, texture work, atmosphere, installs, downloads and paid generation are out
of scope. Preserve neutral materials, lighting and exposure for comparison.

Allowed writes only:
- new map and new asset namespace specified above;
- Assets/Source/OpeningLobby/FunctionalBuild01/;
- new Scripts/OpeningLobby/functionalbuild01_*.py helpers;
- Saved/OpeningLobby/FunctionalBuild01/Worker/ for contract, exports, logs,
  actual captures, measurements, runtime reports and frozen manifest;
- Docs/OpeningLobbyFunctionalBuild01.md for a concise English worker handoff.

No historical helper/verifier edits, task/approval/skill/config/AGENTS edits,
registry changes, status/comment/assignment changes, delegation, commits/pushes
or further dispatch. Generated output stays outside Git; existing LFS rules cover
binary source/assets. Project <=250 GB without following junctions; aim <1 GB new
output. Never remove user assets or duplicate the Unreal checkout.

## Acceptance and evidence

1. Measure saved/reopened scene against approved common source: all rooms, door
   normals/clear dimensions, roof joins, new column sections/positions/ceiling
   contact, checkpoint openings and elevator/opaque field. Separately verify
   unchanged A architecture and hall scale. Audit new assets and protected hashes.
2. Actual readable 1920 x 1080 in-engine neutral images, matching four sheet-05
   camera poses at HFOV 90: entrance (-16,3.5,1.72; yaw180 pitch13), inner
   (16,0,1.72; yaw0 pitch18), full hall (-29,0,1.72; yaw0 pitch20), positive
   aisle (-10,10,1.72; yaw180 pitch13). Add negative service-door approach,
   inner hall doors, checkpoint context and a useful eye-height oblique showing
   room/beam/top closure and full column contact. Record poses, FOV, exposure,
   map identity and image hashes. Add a labelled technical section if a hidden
   joint cannot be judged from playable views; it does not replace context views.
   Include gameplay HFOV 90 context regression using retained baseline cameras
   where clear. Do not crop away the new columns' approved sightline density.
3. Inspect actual images before handoff. Assess composition and depth separately
   from technical numbers: wall/pier integration, meaningful door recesses,
   room/beam/soffit joints, new shaft ceiling contacts, checkpoint/entrance and
   elevator focal field. No final atmosphere claim. Fix causes at their form level.
4. Reuse actual input-driven PIE movement with a scoped adapter. Test both lanes
   both ways; both remaining aisles via open bays near X +/-16.8; all four closed
   door approaches; all three floor passages at each new pair; full-hall route;
   blocking contacts at new rooms/shafts/checkpoint and elevator leaves. Verify
   no ground-level terminal bypass. Include possession, look, grounding, jump
   and landing. Preserve speed360 cm/s, capsule34/88 cm, eye~172 cm, HFOV90.
   Analytic samples and teleports are not real movement verification. Adapt old
   terminal routes to approved closures explicitly; do not disable collision or
   change old tests to force PASS. Avoid start points inside A jambs/new solids.
5. Save/reopen, verify GameMode, stop PIE, restore temporary capture/throttle
   settings, leave new candidate loaded and no dirty packages. Provide exact
   source/map/scripts/captures/runtime evidence with relative paths/sizes/SHA-256
   in manifest.json plus digest sidecar. Distinguish current evidence from failed
   diagnostics. Preserve accepted fingerprints; registration is not in scope.

Return concise handoff: technical outcome, actual visual judgement, identity,
reproduction, limitations, skills actually loaded and storage growth. The fresh
Multica Visual Reviewer then applies environment-architecture-review with an
image-first independent reading on Astra/high/standard, writing only Review01.
PASS/FAIL/UNVERIFIED per criterion; critical gaps block readiness. Controller owns
one bounded correction/focused recheck if needed. Owner acceptance of resulting
3D bytes is a later walkthrough gate; MSQ-6 remains incomplete, MSQ-7 backlog.
