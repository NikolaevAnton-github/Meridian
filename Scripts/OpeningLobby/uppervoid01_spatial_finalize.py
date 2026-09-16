"""Seal the failed spatial experiment and exact-restored clean final identity."""
import datetime,json,hashlib,re
from collections import Counter
from pathlib import Path
from uppervoid01_spatial_check import ROOT,OUT,PREV,CTRL,ALLOWED,entry,read,walk,write,storage
assert not (OUT/'manifest.json').exists()
checks=['archive-verification','diagnostic-response','property-preservation','graph-verification','protected-after','history-verification','capture-verification','performance-verification','movement-verification','handoff-verification','rollback-verification','compile-verification']
for n in checks:assert read(OUT/(n+'.json'))['passed'],n
configs=read(ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Review01/configuration-audit.json');config_rows=[]
for r in configs:
    data=Path(r['path']).read_bytes();assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
    config_rows.append(dict(**r,matches_prior_review=True))
write('configuration-verification',dict(passed=True,records=config_rows))
carried=[PREV/'manifest.json',PREV/'compile-verification.json',PREV/'movement-verification.json',PREV/'performance-verification.json',PREV.parent/'Review02/report.md',PREV.parent/'Review02/verdict.json',PREV.parent/'Review02/audit.json',ROOT/'Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Review01/report.md']
write('carried-evidence',dict(passed=True,entries=[entry(p) for p in carried],scope='Exact restored HC03 final state: carry unchanged architecture/material/gameplay/full-route, sampling limits, roof/aisle/reflection and explicit completed compilation evidence. HC-R1 remains failed. Trial rechecked changed atmosphere pixels,source,graphs,movement and performance independently of final rollback.'))
start=datetime.datetime.fromtimestamp((OUT/'initial-live-state.json').stat().st_mtime,datetime.timezone.utc).strftime('%Y.%m.%d-%H.%M.%S')
lines=(ROOT/'Saved/Logs/MeridianSquad.log').read_text(encoding='utf-8',errors='replace').splitlines()
warnings=[s for s in lines if s.startswith('[') and s[1:20]>=start and re.search(r'Error:|Warning:|Failed to compile',s)]
counts=Counter(re.sub(r'^\[[^]]+\]\[[^]]+\]','',s) for s in warnings)
compile_errors=[s for s in warnings if 'Failed to compile' in s];assert not compile_errors,compile_errors
write('error-audit',dict(start_utc=start,matching_lines=len(warnings),unique_messages=[dict(message=k,count=v) for k,v in counts.items()],material_compile_errors=compile_errors,completed_trial_compile=entry(OUT/'compile-verification.json'),recovered_offline_errors=['Pillow absent in authorized UE Python; used Windows System.Drawing read-only pixel sampling, no install.','Initial exact rollback attempted writing the unchanged loaded map and received PermissionError before mutation. Verified map was already exact; changed only atmosphere files using staged atomic replacement and native reload.'],scope='Native log warnings retained by unique message/count; no failed material compile during HC04. Prior HC03 construction warning is historical.'))
assessment=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection04',representative_experiments=1,diagnostics=3,HC_R1='UNRESOLVED_AUTHOR_ASSESSMENT',owner_review_ready=False,owner_accepted=False,independent_recheck_pending=True,selected_state='Exact HeightCorrection03 rollback',trial_result='No clear progressive-disappearance improvement at exact close,100cm lateral,and true-input hold. Paired cap-like ends persist. No pronounced new wavy caps,patchiness or lower haze observed; simpler previously evidenced state retained.',diagnostic_result='Both-disabled reference exposes roof/shaft junction. Rendered surface Z and evaluated PP transmission are continuous across the narrow upper projected band; no implementation/sampling defect established.',glass='DEFERRED_BY_OWNER')
write('author-assessment',assessment)
maps=entry(ROOT/ALLOWED[0]);perf=read(OUT/'performance-verification.json');motion=read(OUT/'movement-verification.json')
report=ROOT/'Docs/OpeningLobbyUpperVoid01HeightCorrection04.md'
report.write_text(f'''# UpperVoid01 HeightCorrection04: spatial experiment and exact rollback

**HC-R1 remains unresolved.** The single authorized spatial absorption field does
not clearly improve the apparent paired column ends at the exact close pose,
nearby lateral pose or true-input upward hold. The failed native trial and source
are archived. The current map and both atmosphere assets are restored **byte for
byte to HeightCorrection03**. This is a concrete limit for fresh independent
review and controller disposition, not owner acceptance or owner-review readiness.

## Exact final identity

- Map: `{maps['path']}`, SHA-256 `{maps['sha256']}`.
- Extinction material: `c27017638cf6de56eafa3eb6bd1ebafba1ee51c20a723f19c86c10c41c8eea1a`.
- Light-transmission material: `45aa97a5d26d10561411fc23d8c4a5f9d62217910a5f2a67dae945a476d684da`.
- Final manifest and seal: `Saved/OpeningLobby/UpperVoid01/HeightCorrection04/Worker/manifest.json` and `manifest-receipt.json`.
- Exact rollback authority: `HeightCorrection04/Controller/BeforeCorrection/archive.json`.
- Failed native trial: `Worker/FailedTrial/archive.json`; extinction SHA-256 `ac4e0f8e0093552cbfa04874986a929a1080aa0f4eac85ed4d74e6519d3b8ddc`.
- Failed editable source: `Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04/`.
- Current editable source remains the unchanged sibling `HeightCorrection03/`.

All `Worker/` paths below refer to this correction. Read fresh HC03/Review02 and
actual prior close/hold pixels before work. Official Epic confirmed UE5.8.1,
correct project/map, clean packages and PIE off. Verified the controller's three
archive entries against live bytes before any native mutation. One minimal Rider
import registered the dedicated helper; editing and capture used official Epic.

## Rendered diagnostic, completed first

Three native 1920 x 1082 captures at the exact failed pose are retained under
`Disabled`, `WorldZ` and `Transmission`. Both atmosphere stages output unity for
the disabled reference. WorldZ temporarily emits surface Z/2000 directly;
Transmission temporarily emits the actual previous integrated PP transmission
directly, with the light-function stage at unity. These bypass scene-color
multiplication only for diagnostic output. Graph readbacks and recipes record
each configuration; all diagnostic output connections were restored.

The unattenuated scene exposes the actual roof/shaft junction around y 387.
Rendered height rises continuously to that junction. At x 960, WorldZ samples
at y 388/400/412/420 are 227/205/189/179 (8-bit grayscale); evaluated transmission
is 2/104/232/255. Roof pixels above the junction show height 230 and transmission 0.
Thus the working extinction occupies a narrow projected upper-shaft strip;
the paired apparent ends track that strip near the physical roof junction.
Source highlights also remain conspicuous below it. This does not establish
an implementation/sampling defect or one exclusive lighting cause.

`diagnostic-response.json` retains raw Windows System.Drawing pixel reads and an
independent camera-ray/box estimate using recorded shaft bounds. The latter is
an approximate check subject to native sampling, AA and 8-bit quantization;
it is not exact GBuffer reconstruction. No diagnostic image pixels were edited.
No source-formula smoothness was substituted for inspection of rendered output.

## Single representative spatial method

With no established sampling defect, tested one static 3D absorption field.
Three oblique sinusoidal components of approximately 3/4/5 m wavelength, weighted
0.55/0.30/0.15, vary onset continuously from 13.7 to 15.1 m and vary density across
shaft width and between shafts. Sixteen midpoint samples integrate the field
along the camera-to-surface ray within the region above 13.7 m. Absorption is
exactly zero below 13.7 m; a separate smooth terminal mask reaches zero transmission
at 17.9 m. No constant per-column offset, time input, new fog actor or geometry.
The interpretation of mild irregularity was a controller working assumption,
not owner approval of an exact visual design.

All current lights, including 12 aisle fills, remained fixed. The trial changed
only the existing PP custom code; the previous light-function code was restored
after diagnostics. Saved/reopened graph topology and input connections match
the predecessor. Both fully wired trial graphs passed the official recompile
tool, which reports shader failure; no HC04 material compiler error occurred.

**Observed failure:** close/lateral/hold views still read as paired truncated
shafts. Variation is too subtle to establish convincing progressive loss; no
clear improvement justifies retaining its extra complexity. No pronounced new
wavy caps, cloudy patches or lower haze is apparent in sampled views. Roof
concealment and readable aisle ceilings remain. The failed trial was preserved
before exact rollback; no second aesthetic field or scalar retry was attempted.

## Evidence and preservation

Inspected all 12 new native stills and 4 movement images. Three diagnostic stills,
the trial close and lateral stills, and restored close are 1920 x 1082. Six compact
trial regression views are 960 x 540: axis, both aisles, vertical-up, floor reflection
and stone reflection. Close eye = (-1551.150808, 230.164361, 172.15) cm,
pitch 74.912516 / yaw 0 / HFOV 90; lateral eye is 100 cm farther in Y with identical rotation.
No obvious main roof or roof contact appears in the trial/reflection samples;
both lower aisle ceilings, soffits and lower materials remain readable. Inherited
strong highlight pools remain visible. Glass remains deferred.

True-input approach/upward-look/turn lasted {motion['elapsed']:.3f} s with
{motion['samples']} monotonic grounded/possessed telemetry samples. The hold lasts
{motion['hold_seconds']:.3f} s, with three 960 x 540 timed images and one 1920 x 1082 hold
image. The hold reproduces HC-R1. This is sampled imagery plus input telemetry,
not continuous video or exhaustive temporal-artifact proof. Final exact-restored
state carries the unchanged predecessor movement/full-route evidence.

- 129 actors / 150 components and all 107 surface bindings plus separate support exact.
- Zero scene-property deltas across Before, trial, Candidate, reopen, rollback, Handoff.
- All lights, owner geometry, collision/gameplay, glass/support, fixed exposure exact.
- 4,514 protected files match starting bytes at handoff; no live asset delta remains.
- Eleven historical manifests / 3,637 entries verified through exact archives.
- Project/global configuration fingerprints match the independent baseline.
- Trial save/reopen, official graph compile, and final exact rollback/native reload verified.
- Restored close pixels inspected; PIE off, packages clean, capture controls restored,
  inputs released and all callbacks complete. No run-owned operation remains.

`carried-evidence.json` identifies prior passing scope and compilation evidence by
hash. HC-R1 is explicitly carried as failed. The restored assets' exact identity
does not convert the predecessor's visual failure into acceptance.

## Performance and storage

One bounded observation of the spatial trial: {perf['frames']} frames / {perf['seconds']:.3f} s
after 5 s warmup; {perf['mean_ms']:.4f} ms mean, {perf['p95_ms']:.4f} ms p95,
{perf['fps']:.3f} FPS. Recorded pawn start = (-1850, 0, 90.15) cm, rotation = (10, 0, 0),
HFOV 90; renderer/cvars and actual 1920 x 1082 viewport recorded. No continuous pose
series, matched-view performance ratio, uncapped/GPU-stage or worst-route claim.
The near 120 Hz plateau remains. This sample belongs to the archived trial;
final performance evidence is carried from the exact-restored predecessor.

Exact bytes and numerical 15 MB / 100 MB / 2.4 GB planning misses are recorded in
`storage.json` and the seal receipt. Native close/lateral/hold/restored images,
required diagnostics and exact preservation records account for bounded growth.
Planning misses are not marked PASS. No history was deleted; hard 250 GB cap passes.

Recovered tooling issues are recorded in `error-audit.json`: missing Pillow was
handled with read-only native Windows pixel access; an attempted redundant write
to the loaded unchanged map was denied, then verified unnecessary. Restoring the
two changed atmosphere files used staged atomic replacement plus native reload.
No installation, configuration edit, task administration, comment, delegation,
registry operation, commit, push or later dispatch was performed.

**Handoff:** fresh independent bounded recheck pending. HC-R1 is unresolved;
owner_review_ready=false. The controller should review this specific evidenced
limit. No atmosphere, architecture, whole-lobby or deferred-glass acceptance.
''',encoding='utf-8')
storage()
files=[p for p in walk(OUT) if p.name not in ['manifest.json','manifest-receipt.json']]
files.extend(ROOT/p for p in ALLOWED);files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04'))
files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_spatial_*.py'));files.append(report)
rows=[entry(p) for p in sorted(set(files))]
manifest=dict(candidate=assessment['candidate'],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='SINGLE_SPATIAL_TRIAL_FAILED_EXACT_HC03_ROLLBACK',selected_state='HeightCorrection03 exact bytes',HC_R1='UNRESOLVED',owner_review_ready=False,owner_accepted=False,independent_review_pending=True,glass='DEFERRED_BY_OWNER',map=maps,rollback_receipt=entry(CTRL/'BeforeCorrection/archive.json'),failed_trial_archive=entry(OUT/'FailedTrial/archive.json'),prior_manifest=entry(PREV/'manifest.json'),entries=rows)
write('manifest',manifest)
for r in rows:assert entry(ROOT/r['path'])==r
s=read(OUT/'storage.json');delta=(OUT/'manifest.json').stat().st_size
receipt=dict(manifest=entry(OUT/'manifest.json'),entries_verified=len(rows),all_run_owned_operations_finished=True,measurement_note='Storage snapshot plus manifest bytes; excludes this receipt and later platform/controller/review growth.',**{k:v for k,v in s.items() if k!='scope'})
for k in ['project_bytes','lobby_bytes','combined_correction_bytes','new_correction_bytes','new_aim_overage_bytes','combined_planning_overage_bytes','lobby_planning_overage_bytes']:receipt[k]+=delta
write('manifest-receipt',receipt);print(json.dumps(receipt))
