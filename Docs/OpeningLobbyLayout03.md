# Opening lobby Layout03 neutral blockout

Correction01 addresses the independent review's two bounded findings in
`/Game/Maps/L_OpeningLobby_Layout03`. The saved map is open in the existing
UE 5.8.1 editor, with PIE stopped, no dirty packages and no temporarily hidden
actors. Game mode remains `/Script/MeridianSquad.OpeningLobbyGameMode`.
Press Play at Default Player Start, then click the viewport: WASD walks,
mouse looks, Space jumps, Escape ends PIE; Shift+F1 releases the cursor.

**Technical review PASS. Independent visual recheck PASS. Owner scale ACCEPTED
on 2026-09-14; detailing NOT ASSESSED.** The owner explicitly accepted the
in-game scale and authorized continuing. See the scoped
[decision record](Approvals/LobbyLayout03-Scale01.json), which identifies the
unchanged Correction01 map hash. MSQ-11 is complete within its neutral scale
scope; [MSQ-6 architecture/material production](Tasks/OpeningLobbyArchitecture01.md)
is authorized. MSQ-7 remains backlog pending later detail review and acceptance.
B1 and B2 are resolved; all six visual criteria pass. The original passing
runtime evidence is carried forward for unchanged blocking geometry/gameplay.
This owner decision does not claim a new owner runtime test or detail acceptance.

The [independent report](../Saved/OpeningLobby/Layout03/Review/report.md) and
[verdict](../Saved/OpeningLobby/Layout03/Review/verdict.json) identify the scope.
The controller verified all 59 candidate files were unchanged by the reviewer,
481 protected historical files match, and runtime-managed AGENTS.md was restored
before this administrative handoff. Final Epic inspection confirmed the correct
map, stopped PIE and clean packages.

## Approved authority and scope

The immutable LobbyScale-Review01 schedule remains authoritative. Manifest
SHA-256 is `e7c113fd8b74ea2106d8af29391cdfece7a1f763db272fb9727da0568a65efb6`;
external approval is `Assets/Concepts/OpeningLobby/Approvals/LobbyScale-Review01.json`.
LobbyArt-Review02 remains the art authority. No approved art/drawings, rejected
maps, materials, gameplay code, configuration or registry records were edited.

The 60 x 24 x 18 m interior, six pier pairs, 2.4 m pier widths, 8.4 m shafts
and pitch, 6 m bay gaps, 11.2 m center, 4 m aisles, lintels, upper infill and
human-size checkpoint remain unchanged. Closed end walls have 0.4 m technical
shell thickness outside the nominal interior. Doors remain noninteractive
opaque proxies with no assigned destination or external route.

## Correction01 geometry and interpretation

Only nine nonblocking proxy transforms changed; Y/Z centers and sizes remain
identical. The source builder and saved map agree. The normal `build()` still
refuses overwriting an existing revision before creating geometry or materials.

| Proxy | Before X center / depth, m | After X center / depth, m |
| --- | --- | --- |
| Entrance bands, both Y rows | -30.01 / 0.02 | -29.98 / 0.02 |
| Inner bands, both Y rows | +30.01 / 0.02 | +29.98 / 0.02 |
| Entrance lower field | -29.975 / 0.04 | -29.99 / 0.01 |
| Both entrance leaves | -29.91 / 0.03 | -29.965 / 0.01 |
| Inner door frame | +29.96 / 0.06 | +29.985 / 0.01 |
| Inner door leaf | +29.92 / 0.03 | +29.965 / 0.01 |

All four visible band faces now lie 0.03 m inside their wall planes, compared
with zero separation before. Width 2.4 m, height 18 m and Y +/-6.8 m remain.

For door placement, the nominal schedule end plane is interpreted explicitly
as a **leaf center-X target** at +/-30 m. Each of the three leaf centers is now
0.035 m from that target, within 0.05 m; the former offsets were 0.08 m inner
and 0.09 m entrance. The 0.01 m corrected proxy depths are technical placeholders,
not approved fabricated depths. Inner wall/frame/leaf and entrance
wall/lower-field/leaf/trim volumes have positive separation in their visible
layer order. Existing entrance trim is unchanged; its depth does not define
the leaf center or the room boundary.

## Evidence and its limits

Evidence root: `Saved/OpeningLobby/Layout03/`.

- `construction.json`: current saved/reopened bounds of 69 geometry actors.
- `schedule-verification.json`: 185 passing checks, including nominal leaf X,
  all four band offsets/alignment/sizes and nine strict layer-separation checks.
  Maximum schedule-target error is 0.035 m at the nominal door planes.
- `Correction01/before-actual.json`, `after-actual.json`, `comparison.json`:
  89 actual actor records; exactly nine nonblocking transforms changed. All
  measured collision profiles, enabled states, recorded Static/Dynamic/Pawn
  responses and material references match. Other actor bounds/transforms,
  player start, game mode, light settings and exposure anchors match. Volatile
  Struct memory addresses alone are normalized when comparing transform text.
- `blocking_bounds` in construction remains a subset selected by expected
  flags, not itself an actual collision-profile inventory. The separate
  Correction01 inventory provides those actual profile observations.
- `runtime-verification.json` and `runtime-samples.json` are carried forward,
  not rerun: 28 events, 1027 samples, 112.266 s, no reported error. The previous
  test exercised both complete aisles, checkpoint both ways, crossovers,
  wall/pier contacts, possession, mouse look, grounding, jump and landing.
  Unobstructed displacement was 56.8015 m in 15.984 s; full-envelope 60/3.6 =
  16.667 s is theoretical. Speed 360 cm/s, capsule 34/88 cm and pawn FOV 90
  remain unchanged. Only nonblocking decorative geometry changed, so a full
  route repeat was neither required nor performed.
- `reopened-state.json`: final saved map, correct game mode, no PIE, dirty
  packages or hidden actors. Capture window overrides were restored in memory
  without saving configuration; every capture session restored FOV 90 before
  stopping. Lighting remains 18 neutral fills, manual -5 EV, physical exposure
  disabled, zero bloom and motion blur. No throttle override was used this run.
- `Review01Preserved/`: individually archived original six PNGs and six camera
  records, inventory, construction/expected/schedule reports, original handoff
  and map, plus the four pre-edit scripts. No historical evidence was deleted.
- `Correction01/preservation-check.json`: original six PNG hashes preserved;
  all six actual camera poses/FOVs match. 481 of 482 historical protected-file
  hashes match; AGENTS.md differs from its old pre-dispatch hash, as already
  disclosed by the reviewer. This correction did not edit AGENTS.md.

## Native image evidence

All eight images are native PIE 1920 x 1080 HighResShot outputs with no resizing,
cropping or postprocessing. Per-frame camera JSONs and `capture-inventory.json`
record actual poses, FOV, resolution and image hashes. Actual eye Z is 1.7215 m
including CharacterMovement floor separation.

| Frame | Camera XYZ, m | Yaw / pitch, degrees | HFOV |
| --- | --- | --- | --- |
| C1-90 | -19, 0, 1.7215 | 0 / 0 | 90 |
| C1-75 | -19, 0, 1.7215 | 0 / 0 | 75 |
| C2-90 | 19, 0, 1.7215 | 180 / 0 | 90 |
| C2-75 | 19, 0, 1.7215 | 180 / 0 | 75 |
| C3-90 | -14, 3.5, 1.7215 | 180 / 0 | 90 |
| C3-context-90 | -12.6, 3.5, 1.7215 | 180 / 15 | 90 |
| EndEntrance-110 | -23.7, 0, 1.7215 | 180 / 25 | 110 |
| EndInner-110 | 23.7, 0, 1.7215 | 0 / 25 | 110 |

The six comparison directions are unchanged. 75 degrees remains the reference
estimate; 110 degrees is only a supplemental band-inspection lens, not gameplay
or reference matching. All use the possessed pawn with component FOV 90 and
transient camera-manager overrides. Roll is zero within floating-point error.

Worker inspection of all eight full images finds dark entrance facings now
visible in C3/C3-context, including the previously missing negative-Y band to
the right of the checkpoint. Both supplemental views show two distinct dark
end facings below the lintels. The entrance detector partly overlaps one facing;
upper architecture and the band bases are cropped in these close supplemental
views. They establish visible surfaces, not full-height elevation coverage or
an alternative architectural-scale comparison. C1/C2 retain pier occlusion of
parts of the distant end bands. Fine glazing/leaf edges remain pale and show
rendering noise; no material-production or rendering-cleanup claim is made.
The original independent NOT READY report is preserved under
`Saved/OpeningLobby/Layout03/Controller/initial-review-report.md`.
The fresh affected-criteria recheck inspected the actual corrected frames and
closed both findings. Supplemental 110-degree images are inspection aids, not
gameplay framing; the owner should judge monumentality in the 90-degree walk.

## Changed files and reproduction

Changed implementation files under `Scripts/OpeningLobby/`:
`build_layout03.py`, `layout03_tools.py`, `layout03_capture.py`,
`check_layout03_evidence.py`. Other changed deliverables are the dedicated
Layout03 map, this document and generated Layout03 evidence only.

Epic Layout03 `action` adds `correction01` and `correction_audit`; correction
refuses dirty/wrong project/map/PIE state and a previously started correction.
Use `save_reopen`, then `dimensions`. Tool registration/reload used the existing
Rider Python bootstrap; all scene mutations, saving, PIE and captures used Epic.
The existing capture tools support the additional view specs. Reproduction of
the correction requires its preserved initial candidate; do not overwrite the
current map or discard evidence to bypass guards.

Local checker: installed Unreal Python with
`Scripts/OpeningLobby/check_layout03_evidence.py --captures`.
Current disk measurement is in `Controller/storage.json`; precise correction
handoff and output-footprint details are in `Correction01/handoff.md`.
No pre-run whole-project size measurement exists, so total disk growth is not
claimed. The correction worker made no delegation, commits, pushes, later
dispatch or task status changes; the controller handles issue administration.

Controller execution record: four completed sequential Multica runs (implementation,
independent review, bounded correction and affected-criteria recheck). Native
usage and verified runtime model/effort are in
`Saved/OpeningLobby/Layout03/Controller/native-usage.json`; input/cache/output
are separate and reasoning is included in output once. Direct controller/helper
preparation and review are excluded from that worker record. Implementation used
Astra/medium/default; independent visual review used Astra/high/default.
Publishing the final image comment also triggered an unintended reviewer run;
the controller cancelled it and removed the assignment. It produced no messages
or candidate/report changes. The usage record includes any available native
usage from that cancelled administrative trigger; no agent run remains active.
