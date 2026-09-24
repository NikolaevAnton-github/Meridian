"""Preserve correction inputs; no changes to Candidate01, review or owner files."""
from pathlib import Path
import hashlib,json,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Saved/GASPALSLocomotion01/Worker/Correction01'

def sha(path):
    value=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):value.update(chunk)
    return value.hexdigest()

if __name__=='__main__':
    OUT.mkdir(exist_ok=False)
    protected=[ROOT/'Docs/GASPALSLocomotion01.md',ROOT/'Docs/GASPALSLocomotion01Review.md',
        ROOT/'Assets/Source/GASPALSLocomotion01/intake-manifest.json',
        ROOT/'Assets/Source/GASPALSLocomotion01/revision-Candidate01.json',
        ROOT/'Scripts/AssetRegistry/manifests/GASPALSLocomotion01-Candidate01.json']
    for folder in ['Saved/GASPALSLocomotion01/Worker/Candidate01','Saved/GASPALSLocomotion01/Review']:
        protected += [p for p in (ROOT/folder).rglob('*') if p.is_file()]
    records=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),size_bytes=p.stat().st_size) for p in protected]
    (OUT/'historical-before.json').write_text(json.dumps(records,indent=2))
    inputs=['.gitattributes','Config/DefaultEngine.ini','MeridianSquad.uproject',
        'Content/Maps/L_OpeningLobby_PainterStone01.umap',
        'Source/MeridianSquad/CombatProjectileWorld.cpp','Source/MeridianSquad/EnemyCombatCover.cpp']
    with zipfile.ZipFile(OUT/'before.zip','x',zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p in inputs:z.write(ROOT/p,p)
    (OUT/'inputs-before.json').write_text(json.dumps([dict(path=p,sha256=sha(ROOT/p)) for p in inputs],indent=2))
    shutil.copy2(ROOT/'Saved/GASPALSLocomotion01/Controller/correction-process.json',OUT/'execution-settings.json')
    state=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
    (OUT/'git-before.txt').write_text(state)
    print(json.dumps(dict(protected=len(records),preserved_inputs=len(inputs))))
