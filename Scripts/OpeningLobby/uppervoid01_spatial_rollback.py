"""Archive exact failed native trial, then restore only the three named assets."""
import shutil,json,os
from uppervoid01_spatial_check import ROOT,OUT,CTRL,ALLOWED,entry,read,write
from uppervoid01_spatial_client import work
from uppervoid01_spatial_diagnostics import capture_set
s=work('state');assert not s['pie'] and not s['dirty_content'] and not s['dirty_maps'],s
assert read(OUT/'compile-verification.json')['passed']
archive=read(CTRL/'BeforeCorrection/archive.json');rows=[]
assert [r['path'] for r in archive['entries']]==ALLOWED
for r in archive['entries']:
    src=(ROOT/r['path']).resolve();prior=(ROOT/r['archive_path']).resolve()
    assert src.is_relative_to(ROOT.resolve()) and prior.is_relative_to(CTRL.resolve())
    a=entry(prior);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
    dest=OUT/'FailedTrial/files'/r['path']
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    a=entry(dest);b=entry(src);assert (a['bytes'],a['sha256'])==(b['bytes'],b['sha256'])
    rows.append(dict(live_before=entry(src),archive=entry(dest)))
if not (OUT/'FailedTrial/archive.json').exists():write('FailedTrial/archive',dict(entries=rows,source=entry(ROOT/'Assets/Source/OpeningLobby/UpperVoid01/HeightCorrection04/recipe.json'),reason='HC-R1 persists with no clear close/lateral/hold improvement. Preserve single failed field; return to simpler independently evidenced predecessor.'))
for r in archive['entries']:
    live=ROOT/r['path'];a=entry(live)
    if (a['bytes'],a['sha256'])!=(r['bytes'],r['sha256']):
        staged=live.with_suffix(live.suffix+'.hc04restore')
        assert not staged.exists()
        shutil.copy2(ROOT/r['archive_path'],staged)
        os.replace(staged,live)
    a=entry(ROOT/r['path']);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
write('rollback-verification',dict(passed=True,exact_restored_assets=[entry(ROOT/r['path']) for r in archive['entries']],reference=entry(CTRL/'BeforeCorrection/archive.json'),failed_trial=entry(OUT/'FailedTrial/archive.json')))
print(json.dumps(work('audit','rollback-reopen')),flush=True)
print(json.dumps(work('audit','Restored')),flush=True)
capture_set('Restored',['close-column-90'])
print(json.dumps(work('snapshot','Handoff')),flush=True)
for r in archive['entries']:
    a=entry(ROOT/r['path']);assert (a['bytes'],a['sha256'])==(r['bytes'],r['sha256'])
print('Exact rollback remains verified after reopen/capture/handoff',flush=True)
