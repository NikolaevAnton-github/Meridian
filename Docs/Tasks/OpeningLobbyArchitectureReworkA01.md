# LobbyArchitecture-ReworkA01: approved A representative 3D assembly

Owner-authorized in direct chat on 2026-09-14: after reviewing the drawings and
selecting A, the owner explicitly requested max reasoning and instructed us to
proceed. Execute through the existing Multica Environment Artist, Astra/max,
standard service, subscription authentication and concurrency one. The controller
remains active through implementation, independent review and bounded correction.

## Authority and result

Read this specification, Docs/Design/GameBrief.md, Docs/VisualAcceptance.md and
Docs/Approvals/LobbyArchitectureRework01-VariantA.json. Explicitly load the assigned
`.agents/skills/environment-architecture-production/SKILL.md` and report its path.
The authoritative design is Variant A of LobbyArchitecture-Rework01/Candidate01:
`Assets/Concepts/OpeningLobby/ArchitectureRework01/design.json`, sheets 03-05 and
the README. Manifest SHA-256 is
`fb0f306ff60011d01a1008345017d9029964301b2365d81d8ca5d5eba686a4df`.
Verify the frozen package with its existing `freeze.mjs --verify`. Pending fields
inside immutable drawings/reports are historical; the external owner decision
and subsequent direct instruction authorize this 3D task.

Inspect the actual primary OwnerReferences01 images, the owner entrance detail
in ArchitectureRework01Inputs and the subordinate Review02 security image.
Inspect actual A drawings before constructing. Preserve LobbyArt-Review02,
LobbyScale-Review01 and LobbyLayout03-Scale01. Approved A secondary deltas
supersede Architecture01's old proxy-envelope limits and its former no-coffer
restriction only for the expressly drawn final-bay perimeter. Do not flatten A
to fit old cladding or introduce B's bridge, glazing change or cross rib.

Deliver one saved, walkable representative assembly: the full entrance portal,
both adjoining terminal side bays, engaged end piers, first free pier pair and
their beam/upper-wall/soffit connections, within the complete approved neutral
hall context. Preserve all six free pier pairs and the remaining context. Apply
A's continuous upper-wall setback along both colonnades and close it coherently
at the existing inner end as specified in the drawings. Do not expand this into
the full hall's final detail/material pass. It is a geometry acceptance candidate.

Create `/Game/Maps/L_OpeningLobby_ArchitectureReworkA01`, using the accepted
Layout03 neutral map as the contextual starting point. Dedicated new assets go
under `/Game/OpeningLobby/ArchitectureReworkA01/`. Preserve all earlier maps and
asset bytes. Existing source/assets may be inspected and referenced read-only;
duplicate writable materials into the new namespace. Keep the same gameplay
class, controls and configuration. No default-map changes.

## Geometry contract

Before editing, write a short assembly contract in the worker evidence directory:
authorities, primary/secondary dimensions, essential depth order, module/junction
plan, unresolved hidden connections and evidence cameras. Use common dimension
data for construction and measured comparison; convert metres to Unreal cm.

- Hall 60 x 24 x 18 m; six free pier pairs at X -21, -12.6, -4.2, +4.2, +12.6,
  +21 and Y +/-6.8. Shafts 2.4 x 2.4 x 8.4 m; central floor width 11.2 m,
  side aisles 4 m, beam section 2.4 x 2.8 m at Z 8.4-11.2. Preserve all fixed
  scheduled human elements and checkpoint placements. Primary tolerance 0.05 m.
- A portal face X -28.4, glass/door plane X -30, inner reveal X -29.0;
  continuous jamb each 1.7 m wide at abs(Y) 2.9-4.6; shoulder X -29.6 at
  abs(Y) 4.6-5.6; engaged end pier front X -28.8. Terminal gap to first free
  pier front X -22.2 is 6.6 m. Build real returns and thickness, not applied bands.
- Upper-wall inner abs(Y) 6.2 above Z 11.2, providing 0.6 m setback and
  12.4 m upper central clear width. Beam-to-wall ledge and end bearing must read
  from human-height oblique views. Keep floor routes and beam bounds unchanged.
- Upper glazing 5.2 m wide, sill Z 5.4, head Z 17.8; lower field 5.2 x 5.28 m.
  A datum 5.2 x 0.12 m with 1.6 m depth is a thin architectural splice, not an
  engineered lintel. Close the 0.2 m zone to the ceiling. Door leaves remain
  1.04 x 2.64 m each with the specified 0.6 m collar, 0.14 m side jambs and
  0.24 m head. Keep the threshold flush; door operation/destination unresolved.
- Final side-bay ceiling field Z 9.2, 0.35 m perimeter with underside Z 8.4,
  closing at side wall, beam, terminal pier and first free pier. Other side-bay
  ceiling fields stay at baseline. No B cross rib or new floor/room/route.
- Detector X -24.6/Y -1.05, clear opening 1.14 x 2.28; station X -24.6/Y +0.95,
  worktop 0.95 x 2.3 at Z 1.02. Crossovers X +/-27, aisle centre routes Y +/-10.
  The drawing's 1.06 m capsule margin for A is analytic, not a runtime test.

Use design.json for all remaining profiles/bounds. Record consequential ambiguity
as a specific unresolved item; do not invent structural engineering, door action
or off-camera destinations. Keep tertiary detail subordinate. Avoid floaters,
coplanar remnants, holes, slivers, visible duplicate proxy surfaces and seams
that flatten the large forms. New projecting floor masses need appropriate
collision; do not rely only on the old remote wall shells.

## Production and permitted writes

One worker owns the whole editing operation. Confirm actual project, version,
map, PIE and dirty packages before mutation. Controller preflight found UE
5.8.1, GlassReview01 loaded, PIE stopped and no dirty packages; recheck live.
Prefer official Epic MCP for scene mutations, imports, saving, PIE and captures.
Reuse the existing bounded Python tool registration pattern; Rider bootstrap may
register a narrowly scoped toolset when necessary. Discover actual capabilities.
No duplicate app instance or discarded unsaved work. Change diagnostic approach
after two equivalent failed attempts.

Use an economical reusable modular kit with editable source. Blender is available
through the existing local bridge; verify version/connection, launch the existing
app only if needed per Docs/AgentDevelopment.md. If authoring in Blender, deliver
the native .blend with meaningful reusable parts, transforms, normals, UVs and
material slots, plus reproducible scripts. Reuse existing geometry/import validators;
do not rerun/rebuild the asset benchmark. Painter is unnecessary for this neutral
phase. Do not start texture authoring, paid generation, installs or asset downloads.

Allowed writes:
- the new map and dedicated asset namespace named above;
- `Assets/Source/OpeningLobby/ArchitectureReworkA01/` for editable source;
- new `Scripts/OpeningLobby/reworka01_*.py` helpers only;
- `Saved/OpeningLobby/ArchitectureReworkA01/Worker/` for exports, logs, captures,
  measurement reports, assembly contract and manifest;
- `Docs/OpeningLobbyArchitectureReworkA01.md` for the concise worker handoff.

Do not change historical helpers/verifier defaults to make this map pass. A narrow
new-map adapter may reuse verify_lobby.py, layout03_verification/capture and
architecture01 patterns. Protect approved source art/designs, source/configuration,
old assets, task docs, AGENTS.md, skills, registry fingerprints and user settings.
Generated data stays outside Git; use existing LFS rules for new binary source/assets.
Measure project storage without following junctions: total <=250 GB, aim for <1 GB
new output. No deletion of user assets, worktree duplication or broad caches.

## Acceptance and evidence

1. Verify measured saved/reopened A primary and secondary geometry against the
   approved common source and baseline. Identify each intended A delta explicitly.
   Verify modular assets, transforms, normals, slots, collision and preservation.
2. Use readable neutral materials and retained neutral lighting/exposure. Dark
   frame/light glazing differentiation is allowed to show depth; no material look
   development, glass shader investigation, fog, grading or final atmosphere.
   Depth must be legible under neutral lighting, including in context.
3. Capture native 1920 x 1080 in-engine images, with camera poses/HFOV, eye height,
   exposure, map identity and hashes: C2 axial entrance at 75 and 90; approved A
   oblique (-14,+3.5,1.72 m, yaw 192, pitch +16, HFOV 106) and that pose at gameplay
   HFOV 90; C3-context at 90 for checkpoint/aisle; C1 at 90 for contextual regression.
   Add a useful walking-distance terminal-junction/side-soffit view. Use baseline
   poses from existing capture helpers for C1/C2/C3-context. Label the 106-degree
   view as drawing comparison, not gameplay. An optional diagnostic editor section
   must be labelled separately. Do not replace a full view with a flattering crop.
4. Inspect actual images at useful resolution before handoff. Assess continuous
   portal silhouette, depth planes, terminal shoulder separation, beam/upper-wall
   ledge, final-bay soffit closure and human elements against A and the source art.
   Fix geometry/camera/lighting causes separately; technical passes alone are not
   architectural acceptance. Record limitations honestly.
5. Reuse the real PIE route verifier with a scoped adapter. Test the entrance
   approach/return, checkpoint both ways, both new terminal crossovers and adjacent
   aisle segments, new pier/portal contacts, plus a full hall route/context regression.
   Include possession, look, grounding, jump and landing. Actual movement evidence
   is required; camera motion/teleports do not count. Retain speed 360 cm/s,
   capsule radius/half-height 34/88 cm, eye approx. 1.72 m and gameplay HFOV 90.
   Repeat only failed/affected checks after corrections.
   The historical longitudinal start X -28.5/Y -3 m is inside A's new jamb:
   move that candidate-scoped start into genuinely clear floor (e.g. X -27.5),
   adjust the expected distance and record the reason. Do not disable collision
   or alter historical route defaults to force a pass. Likewise, adapt old
   EntranceEndBand and terminal-ceiling assertions to A's explicit approved deltas.
6. Save/reopen, verify GameMode, stop PIE, restore temporary capture/throttle
   settings, leave the candidate loaded and no dirty packages. Provide exact map,
   source, exports, captures, runtime report, reproduction and artifact hash manifest.

Write a concise English handoff separating technical results, actual visual
judgement and unresolved scope. State skills actually loaded, model/effort as
configured, key decisions and size growth. No status/comment/assignment changes,
delegation, commits/pushes, registry changes or further task dispatch by the worker.

The controller verifies handoff and protected bytes, then dispatches an independent
Multica Visual Reviewer in a fresh issue/session using the architecture-review skill,
Astra/max/standard and concurrency one. The reviewer inspects actual approved art,
A drawings and candidate images before worker conclusions, then audits the technical
evidence. It may write only its own Saved review directory. Per-criterion
PASS/FAIL/UNVERIFIED; any critical failed/unverified requirement blocks readiness.
Plan one initial implementation, one independent review and at most one bounded
production correction with focused recheck. Change approach after equivalent
failures; present a concrete owner decision if that bounded process cannot resolve
the issue. Owner acceptance of this 3D assembly remains pending; MSQ-6 is incomplete
and MSQ-7 remains backlog. No full-hall final detailing or look development dispatch.
