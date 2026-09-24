"""Local, self-contained GASPALS intake. Never writes the source project."""
from pathlib import Path
import json, shutil, subprocess
from prepare import ROOT, OUT, SOURCE, files, sha

def main():
    capacity = json.loads((OUT / 'capacity-before.json').read_text())
    assert capacity['project_bytes'] + capacity['source_plugin_bytes'] * 3 < capacity['ceiling_bytes']
    assert (OUT/'Before/identity.json').is_file()
    dest = ROOT / 'Plugins/GASPALS'
    assert not dest.exists(), 'Do not overwrite an earlier intake'
    src = SOURCE / 'Plugins/GASPALS'
    originals = ROOT / 'Assets/Source/GASPALSLocomotion01'
    originals.mkdir(parents=True, exist_ok=True)
    rows=[]
    for f in files(src):
        rel=f.relative_to(src)
        # Source demo startup/render settings must not replace the retained lobby/player.
        target = originals/'SourceConfig/DefaultEngine.ini' if rel.as_posix()=='Config/DefaultEngine.ini' else dest/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f,target)
        digest=sha(f)
        assert sha(target)==digest
        rows.append(dict(source=str(f), source_relative=f.relative_to(SOURCE).as_posix(),
                         destination=target.relative_to(ROOT).as_posix(), bytes=f.stat().st_size, sha256=digest))
    project=ROOT/'MeridianSquad.uproject'
    before=(OUT/'Before/MeridianSquad.uproject').read_bytes()
    assert project.read_bytes()==before
    marker=b'\t"Plugins": [\r\n'
    if marker not in before: marker=b'\t"Plugins": [\n'
    assert before.count(marker)==1
    nl=b'\r\n' if b'\r\n' in marker else b'\n'
    addition=nl.join([b'\t\t{',b'\t\t\t"Name": "GASPALS",',b'\t\t\t"Enabled": true',b'\t\t},'])+nl
    project.write_bytes(before.replace(marker, marker+addition,1))
    manifest=dict(source_project=str(SOURCE), source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),
        adaptation='Exact local content intake. Demo DefaultEngine.ini archived instead of activated; existing retained project settings remain.', files=rows)
    (originals/'intake-manifest.json').write_text(json.dumps(manifest,indent=2))
    (OUT/'intake-result.json').write_text(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),
        owner_project_before=sha(OUT/'Before/MeridianSquad.uproject'), owner_project_after=sha(project)),indent=2))
    print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows))))

if __name__=='__main__': main()
