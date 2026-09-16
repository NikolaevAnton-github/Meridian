"""Seal exact correction evidence; do not grant visual acceptance."""
import json,datetime,re,hashlib
from pathlib import Path
from collections import Counter
from uppervoid01_soft_check import ROOT,OUT,PREV,CTRL,ALLOWED,entry,read,walk,write,storage
assert not (OUT/'manifest.json').exists()
checks=['archive-verification','property-preservation','graph-verification','protected-after','history-verification','capture-verification','performance-verification','movement-verification','handoff-verification']
for n in checks:assert read(OUT/(n+'.json'))['passed'],n
configs=read(PREV.parent/'Review01/configuration-audit.json');config_rows=[]
for r in configs:
    p=Path(r['path']);data=p.read_bytes();actual=hashlib.sha256(data).hexdigest()
    assert len(data)==r['bytes'] and actual==r['sha256'],r['path']
    config_rows.append(dict(path=r['path'],bytes=len(data),sha256=actual,matches_predecessor_review=True))
write('configuration-verification',dict(passed=True,records=config_rows))
start=datetime.datetime.fromtimestamp((OUT/'initial-live-state.json').stat().st_mtime,datetime.timezone.utc).strftime('%Y.%m.%d-%H.%M.%S')
lines=(ROOT/'Saved/Logs/MeridianSquad.log').read_text(encoding='utf-8',errors='replace').splitlines()
warnings=[s for s in lines if s.startswith('[') and s[1:20]>=start and re.search(r'Error:|Warning:|Failed to compile',s)]
counts=Counter(re.sub(r'^\[[^]]+\]\[[^]]+\]','',s) for s in warnings)
errors=[s for s in warnings if 'Failed to compile' in s];assert not errors,errors
write('error-audit',dict(start_utc=start,matching_lines=len(warnings),unique_messages=[dict(message=k,count=v) for k,v in counts.items()],material_compile_errors=errors,scope='Native editor log from initial state through clean handoff; repeated identical warnings counted, not duplicated.'))
write('author-assessment',dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection02',selected_trial='Trial02',trials=2,HC_R1='UNRESOLVED_AUTHOR_ASSESSMENT',owner_review_ready=False,owner_accepted=False,independent_recheck_pending=True,visual_finding='Bright upper pool reduced but compact apparent common terminal silhouettes remain. Review lower central shaft readability after reduced central fills.',glass='DEFERRED_BY_OWNER'))
storage()
report=ROOT/'Docs/OpeningLobbyUpperVoid01HeightCorrection02.md'
files=[p for p in walk(OUT) if p.name not in ['manifest.json','manifest-receipt.json']]
files.extend(ROOT/p for p in ALLOWED)
files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection02'))
files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_soft_*.py'));files.append(report)
rows=[entry(p) for p in sorted(set(files))]
manifest=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection02',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),map=entry(ROOT/ALLOWED[0]),selected_trial='Trial02',status='INDEPENDENT_RECHECK_HANDOFF_HC_R1_UNRESOLVED',owner_accepted=False,owner_review_ready=False,independent_review_pending=True,glass='DEFERRED_BY_OWNER',rollback_receipt=entry(CTRL/'BeforeCorrection/archive.json'),prior_manifest=entry(PREV/'manifest.json'),history_resolution=entry(OUT/'history-verification.json'),native_assets=ALLOWED[1:],entries=rows,remaining=['HC-R1 apparent common terminal edge remains in author assessment.','Assess central-shaft readability after dimming six central fills.','15 MB new-data aim and 2.4 GB cumulative lobby planning target exceeded; combined100MB allowance has little headroom.'])
write('manifest',manifest)
for r in rows:assert entry(ROOT/r['path'])==r
# Add sealing bytes to the immediately measured totals without another expensive walk.
s=read(OUT/'storage.json');delta=(OUT/'manifest.json').stat().st_size
receipt=dict(manifest=entry(OUT/'manifest.json'),entries_verified=len(rows),map=manifest['map'],all_run_owned_operations_finished=True,measurement_note='Storage snapshot plus manifest bytes; excludes this small receipt and future controller/review growth.',**{k:v for k,v in s.items() if k!='scope'})
for k in ['project_bytes','lobby_bytes','combined_correction_bytes','new_correction_bytes','lobby_overage_bytes']:receipt[k]+=delta
assert receipt['combined_correction_bytes']<100000000
write('manifest-receipt',receipt)
print(json.dumps(receipt))
