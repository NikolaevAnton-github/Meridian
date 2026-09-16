# Opening lobby Layout03 from approved scale drawings

Multica task: MSQ-11, a separate child of MSQ-4.
Status on 2026-09-14: Correction01 passed technical and independent visual
review; the owner then explicitly accepted its actual in-game scale and
authorized continuing, while deferring detail assessment. The scoped
[decision record](../Approvals/LobbyLayout03-Scale01.json) closes MSQ-11's
neutral scale gate and authorizes [MSQ-6](OpeningLobbyArchitecture01.md).
MSQ-7 remains backlog. Requirements below preserve the historical implementation
scope and evidence; pending-owner instructions are superseded only by this
identified scale decision.
All progress and reports stored in Multica must be in English; Russian is only
for the owner's direct chat with the controller.

Owner approval was recorded on 2026-09-14 for the complete `LobbyScale-Review01`
package after B1 correction. See
[approval record](../../Assets/Concepts/OpeningLobby/Approvals/LobbyScale-Review01.json).
Manifest SHA-256: `e7c113fd8b74ea2106d8af29391cdfece7a1f763db272fb9727da0568a65efb6`.
Historical pending metadata inside the immutable submission is superseded by
that external approval. LobbyArt-Review02 remains the visual authority.

## Bounded implementation

Build only a neutral-light, walkable blockout in the existing project, in new
map `/Game/Maps/L_OpeningLobby_Layout03`, with dedicated assets under
`/Game/OpeningLobby/Layout03/`. Preserve Stage1, Layout02, accepted source art,
the entire scale package and prior verification evidence byte-for-byte.
Do not uniformly scale the old scene: architecture doubles but the approved
human-use exceptions and character remain human size.

One Multica Unreal worker owns the editor operation: GPT-6 Astra, medium
reasoning, standard speed, concurrency one. Inspect actual approved images and
rendered drawings before construction. Read only relevant sections of
`Docs/Design/GameBrief.md`, `Docs/VisualAcceptance.md`, the scale package README
and `schedule.json`, `Docs/OpeningLobbyLayout02.md`, and existing verifier/tools.
Use official Epic MCP, discover current capabilities and confirm project path,
map identity, PIE and dirty packages before mutations. Do not overwrite dirty
user work. Reuse existing bounded tool-registration patterns; no competing
dispatcher or benchmark harness.

Use primitive geometry and simple dedicated neutral material families. No
Blender/Painter production, detailed kit, damage, dressing, combat, narrative,
new services, installations, paid APIs, default-map changes or registry rebaseline.
Keep all existing gameplay C++ and player settings unchanged. Placeholder shell
thickness may remain a documented technical parameter outside the scheduled
interior faces; it does not settle structural design or unseen architecture.
Do not invent an inner-door destination, external route or door interaction.

## Geometry and gameplay acceptance

`Assets/Concepts/OpeningLobby/ScaleReview01/schedule.json` is the dimensional
source. Convert metres to Unreal centimetres once. Report actual saved actor
bounds against the schedule, with primary dimensions within 0.05 m.

- Interior: 60 x 24 x 18 m; X from entrance -30 to inner end +30 m.
- Six pier pairs: X -21, -12.6, -4.2, 4.2, 12.6, 21 m, Y +/-6.8 m;
  2.4 m square, 8.4 m shaft, 8.4 m pitch, 6 m clear gap.
- Central clear width 11.2 m; both continuous aisles 4 m clear, ceiling 9.2 m.
  Lintels 2.4 m wide, 2.8 m vertical depth, underside Z=8.4 m.
- Entrance upper glazing 5.2 x 12.4 m, sill 5.4 m; lower field 5.2 x 5.28 m.
  Inner window 2.4 x 6.2 m, sill 11.4 m. Floor strips width 0.64 m at Y +/-2.2 m.
- Inner leaf 1.04 x 2.18 m, frame 1.22 x 2.32 m. Entrance has two nominal
  1.04 x 2.64 m leaves, with fixed sidelights/overlight in the lower field.
- Detector clear 1.14 x 2.28 m, outer 1.46 x 2.42 m, depth 0.55 m,
  posts 0.16 m, header 0.14 m. Station body depth/width/height 0.85/2.2/0.96 m;
  worktop 0.95 x 2.3 m, thickness 0.06 m, top Z=1.02 m.
- Both checkpoint elements X=-24.6 m; detector Y=-1.05 m, station Y=0.95 m.
  Retain local spacing. Routes use both aisles Y +/-10 and crossovers X +/-27 m.
- Keep speed 360 cm/s, capsule radius 34 cm/half-height 88 cm, eye height
  approximately 172 cm, horizontal gameplay FOV 90 degrees. Do not enlarge the player.

Reuse `Scripts/OpeningLobby/verify_lobby.py` with a narrow Layout03 revision
configuration analogous to `layout02_verification.py`. Preserve Stage1/Layout02
defaults and identity guards. Derive contact expectations from actual blocking
bounds and capsule radius; route contact tolerance remains its existing value.
Exercise real PIE input through entrance/inner/return, both complete side
aisles, checkpoint both ways, crossovers, wall/pier blocking, possession, mouse
look, grounding, jump and landing. Record measured time separately from the
60/3.6 = 16.7 s unobstructed estimate. Restore temporary background throttling.

## Early visual evidence before detailed production

Capture actual 1920 x 1080 gameplay images with neutral readable lighting and
consistent exposure/display settings. Verify PNG dimensions; the existing
`HighResShot 1` inherits viewport size and is insufficient without explicit
viewport/output control. Preserve full reference images and candidate frames.

| Camera | XYZ metres | Yaw | Estimated reference HFOV | Gameplay HFOV |
| --- | --- | --- | --- | --- |
| C1 entrance to inner | -19, 0, 1.72 | 0 | 75 | 90 |
| C2 inner to entrance | 19, 0, 1.72 | 180 | 75 | 90 |
| C3 security | -14, 3.5, 1.72 | 180 | 90 | 90 |

Pitch/roll start at zero. Record actual camera poses, horizontal FOV convention,
eye height, map, resolution, filenames and any documented estimate adjustments.
Temporary capture-only FOV changes are allowed for the 75-degree comparisons;
restore 90 degrees afterward and preserve saved player defaults. C1 must show inner door, upper glazing, pier
rhythm and both aisles. C2 must show entrance glazing, complete checkpoint,
station screen-left of detector, and aisles. C3 must show the complete checkpoint,
adjacent +Y pier, lintel context and the side-aisle connection together, rather
than a cropped equipment close-up. The independent drawing review flagged that
the initial C3 cannot show the full 8.4 m shaft vertically: capture it faithfully,
then add a documented eye-level camera estimate if needed to show required
context. Camera estimates may change with evidence; approved geometry may not.

No detailed material/model work follows until this early blockout is reviewed.
Dimension checks cannot grant a visual verdict. The controller dispatches a
fresh independent Multica Visual Reviewer session after the worker stops.
It inspects actual art, matched views, gameplay-FOV views and drawings without
editing the candidate. Critical or unverified visual criteria require bounded
correction; the owner retains walkthrough acceptance.

## Outputs and handoff

Write new scripts under `Scripts/OpeningLobby/`, map/assets in the dedicated
paths above, and English handoff `Docs/OpeningLobbyLayout03.md`. Generated logs,
captures and reports stay under `Saved/OpeningLobby/Layout03/` (target below
100 MB; avoid unbounded capture/cache growth). Record preservation hashes before
and after. Save and reopen the new map, check correct game mode, no dirty
packages or temporarily hidden actors, stop PIE and leave it ready to play.

Worker may edit only these outputs and the minimal shared verifier extension.
Include controls, measured project/output growth and storage limitations in the
handoff, as required by the parent walkthrough task.
It must not edit task status, comments, AGENTS.md, other documentation, source
art, configuration, registry, or existing maps/assets. No delegation, commits,
pushes, cleanup of user assets or later-stage dispatch. Return concise English
handoff with map, files, technical verdict, capture inventory and limitations.
MSQ-6/MSQ-7 remain backlog until independent review and owner walkthrough acceptance.
