"""Seal a concrete unresolved-limit handoff, never visual acceptance."""
import datetime,json,hashlib,re
from collections import Counter
from pathlib import Path
from uppervoid01_volume_check import ROOT,OUT,PREV,CTRL,entry,read,walk,write,storage,m
assert not (OUT/'manifest.json').exists()
checks=['archive-verification','property-preservation','graph-verification','protected-after','history-verification','capture-verification','performance-verification','movement-verification','handoff-verification']
for n in checks:assert read(OUT/(n+'.json'))['passed'],n
configs=read(ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Review01/configuration-audit.json');config_rows=[]
for r in configs:
    data=Path(r['path']).read_bytes();actual=hashlib.sha256(data).hexdigest();assert len(data)==r['bytes'] and actual==r['sha256']
    config_rows.append(dict(**r,matches_prior_review=True))
write('configuration-verification',dict(passed=True,records=config_rows))
start=datetime.datetime.fromtimestamp((OUT/'initial-live-state.json').stat().st_mtime,datetime.timezone.utc).strftime('%Y.%m.%d-%H.%M.%S')
lines=(ROOT/'Saved/Logs/MeridianSquad.log').read_text(encoding='utf-8',errors='replace').splitlines()
warnings=[s for s in lines if s.startswith('[') and s[1:20]>=start and re.search(r'Error:|Warning:|Failed to compile',s)]
counts=Counter(re.sub(r'^\[[^]]+\]\[[^]]+\]','',s) for s in warnings)
errors=[s for s in warnings if 'Failed to compile' in s]
assert read(OUT/'compile-verification.json')['passed'] and len(errors)==1,errors
assert '21.57.48:414' in errors[0],errors
write('error-audit',dict(start_utc=start,matching_lines=len(warnings),unique_messages=[dict(message=k,count=v) for k,v in counts.items()],material_compile_warnings_during_construction=errors,completed_graph_compile=entry(OUT/'compile-verification.json'),scope='One temporary missing CameraCm compile warning during node creation before input connection; completed saved/reopened graph passed explicit official recompile. Early simulation pawn capture failed, recovered with official StartPIE possessed mode. Offline validators corrected for added graph node and honest performance pose mismatch.'))
assessment=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection03',selected_trial='Trial02',representative_setups=2,isolations=2,HC_R1='UNRESOLVED_AUTHOR_ASSESSMENT',owner_review_ready=False,owner_accepted=False,independent_recheck_pending=True,visual_finding='Both isolated stages and both representative methods retain paired apparent terminal silhouettes at the failed pose. Restored six central fills improve lower readability but restore conspicuous highlights. Roof concealed and side ceilings readable. No further scalar retries authorized.',glass='DEFERRED_BY_OWNER')
write('author-assessment',assessment)
report=ROOT/'Docs/OpeningLobbyUpperVoid01HeightCorrection03.md'
perf=read(OUT/'performance-verification.json');motion=read(OUT/'movement-verification.json');maps=entry(ROOT/m.MAPFILE)
report.write_text(f'''# UpperVoid01 HeightCorrection03: bounded diagnostic limit

**HC-R1 remains unresolved.** Two isolated-stage diagnostics and both permitted
representative methods retain the paired apparent terminal edge at the required
close-column pose. This is an exact handoff for fresh independent review of a
concrete limit, not an owner-ready visual completion or acceptance.

## Current identity

- Candidate: `LobbyAtmosphere-UpperVoid01/HeightCorrection03`, retained Trial02.
- Map: `{maps['path']}` ({maps['bytes']:,} bytes), SHA-256 `{maps['sha256']}`.
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

Real-input approach and turn completed in {motion['elapsed']:.3f} seconds,
{motion['samples']} monotonic telemetry samples; upward hold {motion['hold_seconds']:.3f} seconds.
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

One bounded frame sample: {perf['frames']} frames over {perf['seconds']:.3f} seconds
after five-second warmup, {perf['mean_ms']:.4f} ms mean / {perf['p95_ms']:.4f} ms p95,
{perf['fps']:.3f} FPS. Renderer/cvars/1920x1082 viewport match the predecessor.
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
''',encoding='utf-8')
storage()
files=[p for p in walk(OUT) if p.name not in ['manifest.json','manifest-receipt.json']]
files.extend(ROOT/p for p in m.ALLOWED);files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection03'))
files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_volume_*.py'));files.append(report)
rows=[entry(p) for p in sorted(set(files))]
manifest=dict(candidate=assessment['candidate'],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),map=maps,selected_trial='Trial02',status='CONCRETE_LIMIT_HANDOFF_HC_R1_UNRESOLVED',owner_accepted=False,owner_review_ready=False,independent_review_pending=True,glass='DEFERRED_BY_OWNER',rollback_receipt=entry(CTRL/'BeforeCorrection/archive.json'),prior_manifest=entry(PREV/'manifest.json'),history_resolution=entry(OUT/'history-verification.json'),native_assets=m.ALLOWED[1:],entries=rows,remaining=['HC-R1 persists after stage isolation and two distinct methods.','Performance sample has unmatched actual pose; no comparative conclusion.','15MB/100MB/2.4GB planning variances.'])
write('manifest',manifest)
for r in rows:assert entry(ROOT/r['path'])==r
s=read(OUT/'storage.json');delta=(OUT/'manifest.json').stat().st_size
receipt=dict(manifest=entry(OUT/'manifest.json'),entries_verified=len(rows),map=maps,all_run_owned_operations_finished=True,measurement_note='Snapshot plus manifest bytes; excludes this receipt and future review/controller growth.',**{k:v for k,v in s.items() if k!='scope'})
for k in ['project_bytes','lobby_bytes','combined_correction_bytes','new_correction_bytes','lobby_overage_bytes','combined_planning_overage_bytes']:receipt[k]+=delta
write('manifest-receipt',receipt);print(json.dumps(receipt))
