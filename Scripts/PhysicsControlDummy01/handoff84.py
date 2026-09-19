"""Immutable task-scoped source, preservation and storage handoff; never stages Git."""
import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path
from preserve84 import sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/PhysicsControlDummy01/Worker'

def write(name, value):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')

def row(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=sha(path))

def run():
    baseline = json.loads((OUT / 'preservation-before.json').read_text())
    allowed = {'Source/MeridianSquad/' + name for name in (
        'CombatProjectileWorld.cpp', 'CombatProjectileWorld.h', 'CombatRifleComponent.cpp',
        'CombatRifleComponent.h', 'MeridianSquad.Build.cs')}
    allowed.add('MeridianSquad.uproject')
    changed = [r['path'] for r in baseline if not (ROOT / r['path']).is_file() or sha(ROOT / r['path']) != r['sha256']]
    assert set(changed) <= allowed, changed
    before = (OUT / 'MeridianSquad.uproject.before').read_bytes()
    after = (ROOT / 'MeridianSquad.uproject').read_bytes()
    prior = json.loads(before)
    current = json.loads(after)
    plugin = [p for p in current['Plugins'] if p.get('Name') == 'PhysicsControl']
    assert plugin == [dict(Name='PhysicsControl', Enabled=True)], plugin
    current['Plugins'] = [p for p in current['Plugins'] if p.get('Name') != 'PhysicsControl']
    assert current == prior, 'Only the PhysicsControl plugin entry may differ'
    # Preserve the owner's descriptor text, including its existing plugin additions.
    extra = b',\n\t\t{\n\t\t\t"Name": "PhysicsControl",\n\t\t\t"Enabled": true\n\t\t}'
    descriptor_bytes_preserved = after.replace(extra, b'', 1) == before
    if not descriptor_bytes_preserved:
        extra = extra.replace(b'\n', b'\r\n')
        descriptor_bytes_preserved = after.replace(extra, b'', 1) == before
    assert descriptor_bytes_preserved, 'Descriptor bytes outside the task insertion changed'
    candidate = json.loads((OUT / 'Candidate09/manifest.json').read_text())
    assert all(sha(ROOT / r['path']) == r['sha256'] for r in candidate), 'Candidate09 changed'
    previous = json.loads((OUT / 'Candidate08/manifest.json').read_text())
    assert all(sha(ROOT / r['path']) == r['sha256'] for r in previous if r['path'] != 'MeridianSquad.uproject')
    for p in (ROOT / 'Scripts/PhysicsControlDummy01').glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
    for name in ('probe-Candidate08.json', 'probe-baselineCandidate08.json'):
        probe = json.loads((OUT / name).read_text())
        assert not probe.get('error') and not any(v is False for v in probe.values()), name
    editor = json.loads((OUT / 'handoff-Candidate08.json').read_text())
    assert not any(editor[k] for k in ('pie', 'dirty_maps', 'dirty_content', 'dummy_leaks'))
    write('preservation-final09.json', dict(baseline_files=len(baseline), unchanged_files=len(baseline)-len(changed),
        changed_only_task_files=changed, config_content_enemy_sources_preserved=True,
        descriptor_only_physics_control_insertion=True, descriptor_other_bytes_exact=True,
        candidate09_source_and_dll_match=True, candidate08_cpp_dll_evidence_applies=True, final_editor=editor))
    sources = [r for r in baseline if r['path'].startswith(('Content/Characters/Mannequins/', 'Assets/Source/EnemyPrototype01/'))
               or r['path'] == 'Content/Development/EnemyPrototype01/A_EnemyTemplate_Idle.uasset']
    write('source-inventory09.json', dict(new_binary_assets=[], reused_unchanged=sources,
        source_contract='Installed Manny template and retained EnemyPrototype01 assets; no new external download or accepted fingerprint replacement.'))
    files = [*ROOT.glob('Source/MeridianSquad/PhysicsControlDummy*'),
             *[ROOT / p for p in sorted(allowed)],
             *sorted((ROOT / 'Scripts/PhysicsControlDummy01').glob('*.py')),
             ROOT / 'Docs/PhysicsControlDummy01.md', ROOT / 'Binaries/Win64/UnrealEditor-MeridianSquad.dll']
    evidence = ['build11.log', 'probe-Candidate08.json', 'probe-baselineCandidate08.json',
                'metrics06.json', 'metrics07.json', 'freefall08.json', 'finalmetrics08.json', 'cost07.json',
                'Candidate06-LivingRegions.json', 'Candidate06-DeathCorpseReset.json', 'Candidate06-SleepWake.json',
                'Candidate06-ActiveReset.json', 'Candidate06-SleepReset.json',
                'Candidate07-TimeNormal.json', 'Candidate07-TimeQuarter.json', 'Candidate07-SlowActiveReset.json',
                'Candidate07-BeforeFireToggle.json', 'Candidate08-FreefallNormal.json', 'Candidate08-FreefallQuarter.json',
                'Candidate08-ClearComparison.json', 'MSQ84-Candidate07-Cost.csv',
                'Video/Candidate06-LivingRegions.mp4', 'Video/Candidate06-DeathCorpseReset.mp4',
                'Video/Candidate08-ClearComparison.mp4', 'Video/Candidate08-SleepContact-excerpt.mp4',
                'Video/Candidate07-TimeNormal.mp4', 'Video/Candidate07-TimeQuarter.mp4']
    write('handoff-manifest09.json', dict(candidate='Candidate09', files=[row(p) for p in files],
        evidence=[row(OUT / p) for p in evidence],
        applicability='Candidate06 motor/body behavior unchanged; Candidate07 fixes only F8/F9 lookup; Candidate08 adds only explicit PIE verification helpers; Candidate09 restores owner descriptor whitespace with identical parsed values. Ground-contact path correspondence is a retained failed check.'))
    total = 0
    for parent, dirs, names in os.walk(ROOT):
        for name in names:
            try: total += (Path(parent) / name).stat().st_size
            except FileNotFoundError: pass  # Runtime logs may rotate during this read-only census.
    local = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    start = json.loads((OUT / 'storage-before.json').read_text())['bytes']
    write('storage-final09.json', dict(project_bytes=total, start_bytes=start, measured_growth_bytes=total-start,
        worker_evidence_bytes=local, limit_bytes=250000000000, within_limit=total<250000000000,
        note='Logical file sizes including history, generated files and services. Growth also includes concurrent controller/reviewer evidence and logs; no deletion or duplicate project.'))
    assert total < 250000000000
    (OUT / 'git-status-final09.txt').write_bytes(subprocess.check_output(['git','status','--short'],cwd=ROOT))
    print(json.dumps(dict(candidate='Candidate09', preserved=len(baseline)-len(changed), task_changed=changed,
                         project_bytes=total, growth_bytes=total-start, worker_evidence_bytes=local)))

if __name__ == '__main__':
    run()
