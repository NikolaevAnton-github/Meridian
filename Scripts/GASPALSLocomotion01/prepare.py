"""Capture pre-edit identities and capacity before the MSQ-121 local intake."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/GASPALSLocomotion01/Worker'
SOURCE = Path('D:/devgames/GASPALS_UE58')

def files(root):
    for base, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if not (os.lstat(Path(base) / d).st_file_attributes & 0x400)]
        for name in names:
            yield Path(base) / name

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'Before/identity.json').exists(), 'Preservation is immutable'
    sizes = {}
    for p in ROOT.iterdir():
        if p.is_dir() and not (p.lstat().st_file_attributes & 0x400):
            sizes[p.name] = sum(f.stat().st_size for f in files(p))
            print(json.dumps(dict(scanned=p.name, bytes=sizes[p.name])), flush=True)
    source_size = sum(f.stat().st_size for f in files(SOURCE / 'Plugins/GASPALS'))
    capacity = dict(project_bytes=sum(sizes.values()), directories=sizes,
                    source_plugin_bytes=source_size, disk_free_bytes=shutil.disk_usage(ROOT).free,
                    ceiling_bytes=250_000_000_000)
    assert capacity['project_bytes'] + source_size * 3 < capacity['ceiling_bytes'], capacity
    assert capacity['disk_free_bytes'] > source_size * 3 + 5_000_000_000, capacity
    (OUT / 'capacity-before.json').write_text(json.dumps(capacity, indent=2))
    before = OUT / 'Before'
    before.mkdir()
    inputs = [ROOT / 'Config/DefaultEngine.ini', ROOT / 'MeridianSquad.uproject', ROOT / '.gitattributes']
    inputs += list(files(ROOT / 'Source/MeridianSquad'))
    inputs += [f for folder in ('Plugins/GASPEnemyFoundation01', 'Plugins/GASPALSEnemy01')
               for f in files(ROOT / folder) if f.suffix in ('.uasset', '.umap', '.uplugin')]
    inputs += [ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap']
    rows = []
    with zipfile.ZipFile(before / 'active-inputs.zip', 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1) as z:
        for f in inputs:
            if not f.is_file():
                continue
            rel = f.relative_to(ROOT).as_posix()
            rows.append(dict(path=rel, bytes=f.stat().st_size, sha256=sha(f)))
            z.write(f, rel)
    for f in inputs[:3]:
        target = before / f.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
    (before / 'identity.json').write_text(json.dumps(dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
        head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT,text=True).strip(), files=rows), indent=2))
    subprocess.run(['git','status','--short'], cwd=ROOT, stdout=(before/'git-status.txt').open('w'), check=True)
    settings = ROOT / 'Saved/GASPALSLocomotion01/Controller/worker-process.json'
    shutil.copy2(settings, before/'execution-settings.json')
    print(json.dumps(dict(capacity=capacity, preserved_files=len(rows))))

if __name__ == '__main__':
    main()
