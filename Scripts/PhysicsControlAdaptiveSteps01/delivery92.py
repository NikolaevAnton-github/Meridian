"""Freeze the final source/build and exact focused evidence; never rebaseline."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlAdaptiveSteps01/Worker'
DEST = OUT / 'Candidate06'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

assert not DEST.exists(), 'Candidate06 already frozen'
checks = json.loads((OUT/'self-checks04.json').read_text())
assert checks['passed'] == checks['total'] == 208 and not checks['failures']
native = [r for r in json.loads((OUT/'Candidate05/manifest.json').read_text())
          if r['path'].startswith(('Source/','Binaries/','Content/'))]
assert all(digest(ROOT/r['path']) == r['sha256'] for r in native)
paths = {ROOT/r['path'] for r in native}
paths.add(ROOT/'Docs/PhysicsControlAdaptiveSteps01.md')
paths.update((ROOT/'Scripts/PhysicsControlAdaptiveSteps01').glob('*.py'))
paths.update((ROOT/'Scripts/PhysicsControlAdaptiveSteps01').glob('*.json'))
# Retain the existing harness dependency sources as evidence, without edits.
for folder in ['OpeningLobby','PurchasedArms02','CombatFoundation01','PhysicsControlDummy01',
               'PhysicsControlVariants01','PhysicsControlBalance01','PhysicsControlStepping01',
               'PhysicsControlLegPose01','PhysicsControlRecoverability01']:
    paths.update((ROOT/'Scripts'/folder).glob('*.py'))
for name in checks['records'].values():
    paths.update(OUT.glob(name+'.json'))
    paths.update(OUT.glob(name+'-*.json'))
    paths.update((OUT/'Video').glob(name+'.*'))
    paths.update((OUT/'Video'/(name+'-Frames')).glob('*.png'))
for name in ['baseline-identity01.json','native-execution01.json','preservation-before01.json',
             'preservation-after01.json','storage-after01.json','writer-lease01.json','writer-release01.json',
             'state-initial01.json','state-candidate05.json','handoff-candidate06.json',
             'build06.log','self-checks04.json','evidence-applicability02.json','selected-views01.json',
             'visual-self-check01.json']:
    paths.add(OUT/name)
rows = []
for path in sorted(paths):
    assert path.is_file(), path
    relative = path.relative_to(ROOT).as_posix()
    frozen = ('Evidence/'+path.relative_to(OUT).as_posix()) if path.is_relative_to(OUT) else relative
    target = DEST/frozen
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path,target)
    sha = digest(path)
    assert digest(target) == sha
    rows.append(dict(path=relative,frozen_path=frozen,bytes=path.stat().st_size,sha256=sha))
manifest = DEST/'manifest.json'
with manifest.open('x',encoding='utf-8') as stream:
    json.dump(rows,stream,indent=2)
archive = OUT/'MSQ92-Candidate06-Evidence.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as package:
    for path in sorted(DEST.rglob('*')):
        if path.is_file():
            package.write(path,path.relative_to(DEST).as_posix())
with zipfile.ZipFile(archive) as package:
    assert package.testzip() is None
    assert len(package.namelist()) == len(rows)+1
    for row in rows:
        assert hashlib.sha256(package.read(row['frozen_path'])).hexdigest() == row['sha256']
result = dict(candidate='Candidate06', native_identical_to='Candidate05 / build06',files=len(rows),
    bytes=sum(r['bytes'] for r in rows),manifest_sha256=digest(manifest),all_current_and_frozen_match=True,
    archive=archive.name,archive_bytes=archive.stat().st_size,archive_sha256=digest(archive),archive_verified=True,
    storage_upper_bound_GB=(json.loads((OUT/'storage-after01.json').read_text())['bytes']+
        sum(r['bytes'] for r in rows)+manifest.stat().st_size+archive.stat().st_size)/1e9)
assert result['storage_upper_bound_GB'] < 250
with (OUT/'candidate06-validation01.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,indent=2)
print(json.dumps(result))
