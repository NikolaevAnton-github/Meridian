"""Verify rollback scope, exact candidate identity, and real-input evidence."""
import json
import re
from audit import ROOT, OUT, BASE, MAP, CUSTOM, sha, git, write

checks = []


def check(name, passed, detail=None):
    checks.append({'name': name, 'passed': bool(passed), 'detail': detail})


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8-sig'))


def canonical(value):
    return re.sub(r'0x[0-9A-Fa-f]+', '<address>', json.dumps(value, sort_keys=True))


def scope():
    before = read('Before/manifest.json')['files']
    mutations = read('rollback-manifest.json')['changes']
    preserved = [p for p in before if p not in mutations]
    differences = [p for p in preserved if not (ROOT / p).is_file() or sha(ROOT / p) != before[p]['sha256']]
    check('All unrelated before-snapshot files preserved byte-for-byte', not differences,
          {'count': len(preserved), 'differences': differences})
    vendor = read('Before/vendor-hashes.json')
    changed_vendor = [p for p, h in vendor.items() if sha(ROOT / p) != h]
    check('All 481 vendor packages preserved byte-for-byte', len(vendor) == 481 and not changed_vendor, changed_vendor)
    check('Every active native source matches fd84f4a', not git('diff', BASE, '--', 'Source/MeridianSquad'))
    check('Map is exact fd84f4a bytes', sha(ROOT / MAP) == '94dbedbe2e516fc8cdde2d394f2b4c8c0a4d9573288e94772a6ebefafd54bc57')
    remaining = [p.relative_to(ROOT).as_posix() for folder in CUSTOM for p in (ROOT / folder).rglob('*') if p.is_file()]
    check('No custom assets remain in active Content', not remaining, remaining)
    check('Temporary audit map removed', not (ROOT / 'Content/Maps/L_RollbackBaseline01.umap').exists())
    before_config = (OUT / 'Before/Files/Config/DefaultEngine.ini').read_bytes().splitlines(keepends=True)
    index = next(i for i, line in enumerate(before_config) if line.startswith(b'+Profiles=(Name="MSQDestructionDebris"'))
    del before_config[index - 2:index + 1]
    check('Config differs only by removal of custom debris profile', (ROOT / 'Config/DefaultEngine.ini').read_bytes() == b''.join(before_config))
    build = read('Build01.json')
    check('Full Development Editor build succeeded with exact candidate identities', build['exit_code'] == 0 and
          all((ROOT / p).is_file() and sha(ROOT / p) == h for p, h in build['files'].items()),
          {'dll': build['files']['Binaries/Win64/UnrealEditor-MeridianSquad.dll']})


def scene():
    actual = read('editor-reopened.json')
    baseline = read('Baseline/editor-loaded.json')
    check('Saved reload has exactly 143 actors and 14 specimens', len(actual['actors']) == 143 and len(actual['props']) == 14)
    a = {r['name']: canonical(r) for r in actual['actors']}
    b = {r['name']: canonical(r) for r in baseline['actors']}
    check('Every baseline actor/architecture record matches on saved reload', a == b)
    check('Every specimen transform/configuration/material override matches', canonical(actual['props']) == canonical(baseline['props']))
    vendor = json.loads((ROOT / 'Saved/LobbyPlaytestFix01/Candidate01/demo-inventory.json').read_text())
    signature = lambda p: canonical([p[k] for k in ['config', 'collection', 'materials', 'scale', 'gc_collision', 'gc_damage']])
    check('All 14 distinct default-demo source configurations retained',
          {signature(p) for p in actual['props']} == {signature(p) for p in vendor['instances']})


def runtime():
    initial = read('runtime-initial.json')['state']
    check('Fresh PIE contains 14 ready vendor props', len(initial['props']) == 14 and all(p['ready'] for p in initial['props']))
    concrete = read('rifle-concrete.json')
    glass = read('rifle-glass.json')
    for name, report in [('Concrete', concrete), ('Glass', glass)]:
        check(name + ' real input trace completed', 'after' in report and 'error' not in report)
    c = concrete['after']
    check('Automatic fire spends all 30 rounds through concrete fracture',
          c['rifle']['shots'] - concrete['before']['rifle']['shots'] == 30 and c['rifle']['magazine'] == 0)
    pillar = next(p for p in c['props'] if p['id'] == 'NGD01_ConcretePillar')
    check('Concrete receives real rifle hits and Chaos break events', pillar['delivered_hits'] > 0 and pillar['break_events'] > 0,
          {'hits': pillar['delivered_hits'], 'breaks': pillar['break_events']})
    g = glass['after']
    window = next(p for p in g['props'] if p['id'] == 'LPF01_LargeGlass')
    check('Two semi-auto presses fire two rounds; first breaks glass',
          g['rifle']['shots'] - glass['before']['rifle']['shots'] == 2 and window['delivered_hits'] == 1 and window['break_events'] > 0,
          {'hits': window['delivered_hits'], 'breaks': window['break_events']})
    sources = {p['config']['DataAsset']: p for p in read('editor-reopened.json')['props']}
    for name in ['reset-concrete', 'reset-glass']:
        report = read(name + '.json')
        check(name + ' trace completed', 'after' in report and 'error' not in report)
        props = report['after']['props']
        check(name + ' F6 restores all 14 intact props', len(props) == 14 and all(p['ready'] and not p['root_broken']
              and p['break_events'] == 0 and p['delivered_hits'] == 0 and p['live_fields'] == 0 for p in props))
        check(name + ' retains source materials and overrides', all(p['materials'] == sources[p['data_asset']]['materials'] and
              p['material_overrides'] == sources[p['data_asset']]['config']['Material Overrides'] for p in props))


if __name__ == '__main__':
    import sys
    scope()
    scene()
    runtime()
    write(sys.argv[1] + '.json', {'candidate': 'MSQ-171-Candidate01', 'checks': checks})
    failed = [c for c in checks if not c['passed']]
    print(json.dumps({'checks': len(checks), 'passed': len(checks) - len(failed), 'failed': failed}))
    sys.exit(1 if failed else 0)
