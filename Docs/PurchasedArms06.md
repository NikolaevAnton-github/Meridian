# PurchasedArms06 / MSQ-66: brighter rifle muzzle flame

2026-09-18. The existing red muzzle effect uses a modest **1.20x RGB intensity**.
Focused hip/ADS shooting and release evidence passes controller review. This is
technical/visual review, not owner acceptance. The scope is
[PurchasedArms06](Tasks/PurchasedArms06.md).

## Saved change

Only one gameplay asset changed:
`Content/InfimaGames/TacticalFPSAnimations/Common/VFX/Systems/NS_TFA_MuzzleFlash.uasset`.
Official Epic Niagara tools edited the system's authored stack inputs:
`Flame > ParticleSpawnScript > InitializeParticle > Color > RandomRangeLinearColor`.

| Input | Before RGBA | Saved RGBA |
| --- | --- | --- |
| Minimum | `(1, 0, 0, 0.0030000000260770321)` | `(1.2000000476837158, 0, 0, 0.0030000000260770321)` |
| Maximum | `(1, 0, 0, 0.0070000002160668373)` | `(1.2000000476837158, 0, 0, 0.0070000002160668373)` |

The float readback represents the intended 1.20 multiplier. Alpha, its random
range, RGB ratios, flame size/lifetime/count, smoke inputs, renderer settings and
firing logic retain their authored values. The existing Flame sprite and light
renderers both use `Particles.Color`, so the existing transient muzzle light also
receives the brighter RGB. No light was added; lobby lights/exposure were not
edited.

The flame material has no separate emissive multiplier. Its `Density Smoke`
scalar multiplies texture RGBA before separate emissive and opacity branches;
using it would also change opacity. The material, instances, textures and source
emitters therefore remain byte-identical. No gameplay/native code changed or was
rebuilt.

The complete exported system, emitter topology, module inputs and renderer data
have two authored numeric differences. Another 28 exported differences are
`bBindingExistsOnSource` flags refreshed from false to true by Niagara's native
compilation/cache population; their binding targets and renderer scales match.
The original snapshot is preserved, not rebaselined.

## Verification and evidence

All worker evidence is under `Saved/PurchasedArms06/Worker/`.

- `Video/Before01.mp4` and `Before01.json`: baseline, 13 hip shots and 14 aimed
  shots. `Video/After120-03.mp4` and `After120-03.json`: changed asset, 13 hip and
  13 aimed shots. Camera starts at `(-1600, 0, 172.15)` cm, zero rotation, with
  90-degree hip and 78-degree ADS FOV in both takes. Average shot spacing is
  approximately 0.086/0.085 seconds. The baseline's extra last shot coincides
  with its delayed release event.
- `Review/Comparison-hip.png`, `Review/Comparison-aim.png` and the original
  `Before01-{hip,aim}-sheet.png` / `After120-03-{hip,aim}-sheet.png` show multiple
  actual flash samples. The red effect is more prominent, the front post and
  aperture remain readable, and no opaque bloom or persistent glow remains
  after release. The MP4s retain the shooting/recovery context.
- The capture samples roughly 12 fps and does not resolve every flash peak.
  Variants, alpha and sampled phases differ. Red-pixel ranking locates visible
  frames; it does not measure brightness. The exact 20% claim comes from authored
  RGB values, not display luminance. Before01's capture/telemetry alignment is
  approximate because it predates absolute monotonic timestamps in the adapter.
- After120-03 lost foreground after the required sequence: 134 decoded frames,
  PTS span 0-10.967 seconds, approximately case time 10.904 at its last frame.
  Both bursts, LMB release, RMB release and hip recovery are present. Its partial
  MP4 is not represented as a completed planned 13-second recording. Timestamp
  recovery is explicitly recorded in `Video/After120-03.recovered.json`.
- `After120-Final.json` and its complete normal-launch video independently verify
  saved-asset hip firing and cessation: 1,138 telemetry samples, 26 shots, stable
  ammo 17/4 after the respective releases, and no shots after case time 7.35.
  Synthetic ADS cleared before its second burst. Its helper-generated `aim`
  sheet names a scheduled interval, not actual ADS, and is excluded as aimed
  evidence. After120-03 supplies the valid ADS evidence.
- `niagara-before.json`, `niagara-after-120.json` and `niagara-saved-reloaded.json`
  preserve full readbacks. Native package reload succeeded; the latter two
  snapshots have an empty diff. All eight Niagara scripts report UpToDate with
  no compilation errors or warnings. In-process reload logged replacement
  warnings for discarded generated Niagara curve/runtime objects; the subsequent
  ordinary cold launch and shooting produced no affected-asset/material warnings
  or errors. Both logs are retained.

The controller independently reviewed the source contract, original sheets,
additional full video frames and fire-release telemetry. Its scoped pass is
`Saved/PurchasedArms06/Controller/visual-review.md`. No jump, movement, reload or
full animation/feature regression was run for this brightness change.

## Preservation and execution

`Rollback/` contains the original VFX packages before editing.
`hashes-before.json`, `preservation-after.json` and the starting Git status record
the baseline. Of 44 checked files, only the system above changed; no files are
missing. The original vendor VFX files still match the baseline. Existing owner
and controller changes remain outside the worker's edits.

| File | SHA-256 |
| --- | --- |
| Muzzle system before | `5f390b6ce592b738e8712616049f78600c82b9139708aa11b842840355907310` |
| Muzzle system saved | `e6a74ae3ef8e9f49abb695cd83b324578a7061fe3cc4774a3d8948bdb962e166` |
| Owner `Config/DefaultEngine.ini`, unchanged | `f3caa33c2d9a10d7e4626cdd6c3b2791fbbfa0a425f7af29f419b837f0c71bbf` |
| Retained lobby map, unchanged | `b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f` |

`native-settings-verified.json` confirms actual Astra/max turn context and native
process arguments: subscription login, default service tier, fast mode disabled.
No profile settings were changed. Official Epic MCP verified the live project,
clean packages and stopped PIE before authoring. Rider was used only to bootstrap
the narrow Python adapter. Niagara tools were temporarily enabled with the
editor command line; the final editor was restarted with the original ordinary
launch arguments and no project/plugin configuration edit. Background throttling
was restored. Measured project storage was 28.18 GB against the 250 GB cap.

Task files are the system asset, this report, `Scripts/PurchasedArms06/tools06.py`
and `Scripts/PurchasedArms06/run06.py`. The adapters reuse the existing Epic
transport, native input probe and video recorder. They refuse pre-existing PIE,
record capture failures, and validate actual ADS/FOV before accepting an aimed
take. The later held-RMB refresh was not exercised because the owner resumed
manual Play; it is not part of the evidence claimed above. Diagnostic takes and
failed attempts remain preserved.

## Final editor exception

The worker's normal-launch check ended with PIE stopped and no dirty content/maps
(`editor-state-handoff.json`). Subsequently an independent manual PIE session
was active, with a moving pawn away from the capture spawn. The controller's
2026-09-18 19:11:25 local instruction in comment
`01a0b549-76c2-71a3-930b-94bb9909a389` explicitly supersedes the original stopped-PIE
handoff requirement: treat this as owner-owned, leave it untouched, finish from
the already passing evidence, and do not repeat captures.

Final02 had already encountered pre-existing PIE and its earlier cleanup stopped
that session; this is recorded rather than hidden. The owner resumed Play. The
precondition was moved outside capture cleanup, so Final03 refused the existing
session without touching it. No editor calls or forced inputs were made after
the controller instruction. The final owner-active PIE exception is intentional;
the saved asset is verified and there are no unsaved worker asset changes.

Registry revision, task/approval/state administration, acceptance, issue closure
and the local task commit remain with the controller.
