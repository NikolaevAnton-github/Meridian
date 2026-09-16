# UpperVoid01 HeightCorrection03: bounded diagnostic limit

**HC-R1 remains unresolved.** Two isolated-stage diagnostics and both permitted
representative methods retain the paired apparent terminal edge at the required
close-column pose. This is an exact handoff for fresh independent review of a
concrete limit, not an owner-ready visual completion or acceptance.

## Current identity

- Candidate: `LobbyAtmosphere-UpperVoid01/HeightCorrection03`, retained Trial02.
- Map: `Content/Maps/L_OpeningLobby_PainterStone01.umap` (260,486 bytes), SHA-256 `b28fa0f6e8bb80dcc71b4789df9c3e2375a3cf8b1da67021225584e4560fd92f`.
- Final immutable identity: `Saved/OpeningLobby/UpperVoid01/HeightCorrection03/Worker/manifest.json` and `manifest-receipt.json`.
- Native atmosphere assets: existing `M_UpperVoid_Extinction` and `M_UpperVoid_LightTransmission` under `/Game/OpeningLobby/UpperVoid01`.
- Editable source: `Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03/`.
- Rollback: `HeightCorrection03/Controller/BeforeCorrection/archive.json`; all three entries verified against live starting bytes and archive before mutation.

## Diagnosis and two different methods

Opened the owner yellow section, original HC-R1 report and actual Correction02
Trial02 close image. Official Epic confirmed UE5.8.1, correct project/map,
clean packages and PIE off. New adapters reused existing capture, property,
actual-input and graph primitives; only one Rider import registered the toolset.

`Worker/IsolatePP` retains the previous exponential postprocess with unity light
transmission; `IsolateLF` retains the previous light function with unity PP.
Both exact 1920x1082 frames retain the paired edge. Each directory contains its
actual shader settings in recipe.json and full camera/renderer metadata.
The appearance therefore cannot be attributed exclusively to either stage.

**Trial01:** a nearly linear post-tonemap transmission across 13.7–17.8 m,
with 6% rounded endpoint shoulders. Its analytic vertical 90–10% interval is
14.21–17.29 m (3.08 m, versus prior exponential 1.49 m). Direct-light suppression
is separately confined to 17.5–17.9 m. Six central lights return to the exact
Correction01 intensity 100000 and specular scale 0.2; all twelve aisle fills
stay exact. The edge moves upward and its tail changes, but remains cap-like.
The restored highlights remain conspicuous; dimming did not solve the edge.

**Trial02, retained:** analytic Beer-Lambert absorption through a world-anchored
upper half-space. Density is zero below 13.7 m, then increases quadratically
with zero onset slope: sigma(z)=0.034*((z-1370)/410)^2 per cm. The PP graph
integrates this density over the actual camera-to-surface ray. CameraPositionWS
is its sole added node/input; no technical mesh or visible geometry was added.
A final 17.8–18 m mask removes residual main-roof signal; roof light suppression
remains separate. This is absorption-only integration in the dedicated native
postprocess graph, not scattering fog or a new Unreal volumetric actor.

Trial02 retains the roof concealment and lower-hall readability, and supplies
the bounded distinct-method feasibility result. Its close silhouette remains
very similar to Trial01. It is retained as the fully checked current handoff;
no claim of a meaningful HC-R1 improvement over Trial01 is made. At this close
pose, the allowed height span occupies only a small foreshortened screen band;
world-height/path attenuation alone did not remove the common apparent end.
This does not prove every possible lighting method impossible. Further work
requires controller disposition of this exhausted two-method bound, not another
unrecorded scalar retry or a lowered fade that damages the protected aisles.

## Actual evidence inspected

All 13 native diagnostic/regression stills were checked. The exact close pose is
(-1551.150808,230.164361,172.15) cm, pitch74.912516/yaw0, HFOV90, 1920x1082.
Regression stills are native 960x540, matching prior camera poses, not matching
prior 1920x1080 pixel dimensions. Trial02 close/west aisle and Final axis,
east aisle, column-up, vertical-up, entrance corner, floor and stone reflections
cover the selected candidate; Final axis repeats the trial axis after reopen.
Main roof/contacts remain hidden. Both lower side ceilings and beam depth are
readable. Floor/stone detail persists, with strong inherited/restored light pools.
No new roof image is apparent in the sampled reflections. Glass remains deferred.

Real-input approach and turn completed in 23.265 seconds,
208 monotonic telemetry samples; upward hold 6.859 seconds.
Three native 960x540 timed frames and one native 1920x1082 hold frame are kept.
The hold image and motion-002 still show HC-R1. Telemetry establishes the turn;
sparse frames are not continuous video or proof against every temporal artifact.
Prior full-route gameplay coverage is referenced through movement-verification.

## Verified preservation and limitations

- Saved/reopened Candidate, Reopened and Handoff properties match exactly.
- 129 actors / 150 components, all 107 surface bindings and separate support mesh preserved.
- Only 12 actor-property deltas: intensity and specular restoration on six central fills.
- Twelve aisle fills, geometry, collision/gameplay, glass/support and fixed exposure exact.
- Both native graphs/source verified; only two custom codes plus the PP camera node/input changed.
- 4,402 protected files audited; only the three allowed map/atmosphere assets changed.
- Ten historical manifests, 3,535 entries resolved through exact archives; old evidence untouched.
- Global/project configurations match prior independent review fingerprints.
- One temporary missing-camera-input compilation warning during construction; completed reopened graph passed explicit official compilation, native package reload restored clean state without changing disk bytes. Error audit retains this warning and recovered diagnostics.
- Capture controls restored, held inputs released, callbacks complete, PIE off, map clean.

One bounded frame sample: 2398 frames over 20.000 seconds
after five-second warmup, 8.3405 ms mean / 8.3335 ms p95,
119.897 FPS. Renderer/cvars/1920x1082 viewport match the predecessor.
**The recorded starting pose differs from the requested axis after settling.**
Cause is not established; no per-frame pose series exists. This is a valid bounded
frame-time observation, not a matched-pose comparison or verified stationary test.
No performance ratio, uncapped headroom, GPU-stage, standalone or worst-route claim.
The unexplained near120Hz plateau persists. No extra sample exceeded the task bound.

## Storage and handoff

Exact totals and measured planning variances are in Worker/storage.json and the
seal receipt. The new 15 MB aim, combined 100 MB correction planning target and
2.4 GB lobby planning target are exceeded; none is marked PASS. Required exact
close diagnostics, hold image and preservation evidence account for this growth.
No history was deleted. The hard 250 GB project cap passes.

Fresh MSQ-32 independent recheck remains pending. Required HC-R1 remains open;
this worker cannot dispatch review or grant acceptance. No owner atmosphere,
architecture, whole-lobby or deferred glass approval is inferred.
