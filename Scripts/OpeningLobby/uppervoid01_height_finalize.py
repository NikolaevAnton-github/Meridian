"""Seal the completed worker artifact set; no editor/task/controller operations."""
import json,datetime,re
from uppervoid01_height_check import ROOT,OUT,OLD,CTRL,ALLOWED,entry,read,walk,write,usage
assert not (OUT/'manifest.json').exists()
for name in ['archive-verification','capture-verification','graph-verification','property-preservation','protected-after','history-verification','movement-verification','performance-verification','handoff-verification']:
    assert read(OUT/(name+'.json'))['passed'],name
report=ROOT/'Docs/OpeningLobbyUpperVoid01HeightCorrection01.md';assert report.exists()
start=datetime.datetime.fromtimestamp((OUT/'initial-live-state.json').stat().st_mtime,datetime.timezone.utc).strftime('%Y.%m.%d-%H.%M.%S')
lines=(ROOT/'Saved/Logs/MeridianSquad.log').read_text(encoding='utf-8',errors='replace').splitlines()
findings=[line for line in lines if line.startswith('[') and line[1:20]>=start and re.search(r'Error:|Warning:|Failed to compile',line)]
write('error-audit',dict(start_utc=start,lines=findings,material_compile_errors=[s for s in findings if 'Failed to compile' in s],scope='Native editor log since initial live state; engine warning details retained.'))
files=[p for p in walk(OUT) if p.name not in ['manifest.json','manifest-receipt.json']]
files.extend(ROOT/p for p in ALLOWED)
files.extend(walk(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection01'))
files.extend((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_height_*.py'))
files.append(report)
rows=[entry(p) for p in sorted(set(files))]
assert len(rows)==len({r['path'] for r in rows})
manifest=dict(candidate='LobbyAtmosphere-UpperVoid01/HeightCorrection01',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),map=entry(ROOT/ALLOWED[0]),author_setup='Trial01',status='FRESH_INDEPENDENT_REVIEW_HANDOFF_WITH_PLANNING_OVERRUN',owner_accepted=False,independent_review_pending=True,glass='DEFERRED_BY_OWNER',rollback_receipt=entry(CTRL/'BeforeHeightCorrection01/archive.json'),prior_manifest=entry(ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker/SlabLayout01/manifest.json'),history_resolution=entry(OUT/'history-verification.json'),native_assets=ALLOWED[1:],entries=rows,remaining=['Fresh independent visual/technical review, especially near-column foreshortened fade.','Cumulative lobby exceeds 2.4 GB planning target; no exception granted.'])
write('manifest',manifest)
for row in rows:assert entry(ROOT/row['path'])==row,row
now=usage()
correction_files=[p for f in [OUT,ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection01'] for p in walk(f)]
correction_files+=list((ROOT/'Scripts/OpeningLobby').glob('uppervoid01_height_*.py'))+[report]
correction_bytes=sum(p.stat().st_size for p in correction_files)
receipt=dict(manifest=entry(OUT/'manifest.json'),entries_verified=len(rows),map=manifest['map'],measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**now,correction_bytes=correction_bytes,project_under250gb=now['project_bytes']<=250e9,correction_under100mb=correction_bytes<=100e6,lobby_under2400mb=now['lobby_bytes']<=2.4e9,lobby_overage_bytes=max(0,now['lobby_bytes']-int(2.4e9)),measurement_scope='Existing no-junction walker; measurement immediately before writing this small receipt.',all_run_owned_operations_finished=True)
assert receipt['project_under250gb'] and receipt['correction_under100mb']
write('manifest-receipt',receipt)
print(json.dumps(receipt))
