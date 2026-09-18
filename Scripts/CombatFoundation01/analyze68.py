"""Acceptance assertions over actual PIE input, collision and animation telemetry."""
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/CombatSlice01/CombatFoundation01/Worker'
CHECKS = []
CASES = {}

def check(name, passed, detail=None):
    CHECKS.append({'name': name, 'passed': bool(passed), 'detail': detail})

def case(name):
    path = OUT / (name + '.json')
    data = json.loads(path.read_text())
    rows = data['rows']
    CASES[name] = {'samples': len(rows), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    check(name + ': completed input sequence', data['error'] is None and len(data['events']) == len(data['config']['events']))
    expected_total = rows[0]['rifle']['magazine'] + rows[0]['rifle']['reserve'] + rows[0]['rifle']['shots']
    fixtures = iter(e for e in data['events'] if e['key'] == '@ammo')
    fixture = next(fixtures, None)
    conservation = True
    display_errors = []
    for i, row in enumerate(rows):
        rifle, world = row['rifle'], row['ballistics']
        while fixture and fixture['t'] <= row['t'] + 1.e-6:
            expected_total = sum(fixture['value']) + rifle['shots']
            fixture = next(fixtures, None)
        conservation &= rifle['magazine'] + rifle['reserve'] + rifle['shots'] == expected_total
        if any(m['ammo'] != m['expected'] for m in row['magazines']):
            # Fixture writes occur after evaluation in a Slate callback. Only
            # that same-frame sample may still display the pre-fixture count.
            if not any(e['key'] == '@ammo' and abs(e['t'] - row['t']) < 1.e-6 for e in data['events']):
                display_errors.append(row['t'])
    check(name + ': ammunition conserved', conservation)
    check(name + ': one bullet for each consumed round', all(r['rifle']['shots'] == r['ballistics']['launched'] for r in rows))
    check(name + ': every bullet active, hit once, or retired', all(r['ballistics']['launched'] ==
        r['ballistics']['active'] + r['ballistics']['hits'] + r['ballistics']['retired'] for r in rows))
    check(name + ': magazine display agrees after fixture frame', not display_errors, display_errors)
    check(name + ': no shot during locked reload', all(not (a['rifle']['reloading'] and b['rifle']['reloading']) or
        a['rifle']['shots'] == b['rifle']['shots'] for a, b in zip(rows, rows[1:])))
    check(name + ': bounded live counts', all(r['ballistics']['active'] <= 128 and r['ballistics']['impacts'] <= 48 and
        r['rifle']['props'] <= 64 and r['rifle'].get('effects', 0) <= 64 and r.get('niagara_components', 0) <= 64 for r in rows))
    check(name + ': target health and hit count agree', all(t['health'] == max(0, 100 - 25 * t['hits'])
        for r in rows for t in r['ballistics']['targets']))
    return rows

def at(rows, t):
    return next(r for r in rows if r['t'] >= t)

def shots(rows):
    return [b for a, b in zip(rows, rows[1:]) if b['rifle']['shots'] > a['rifle']['shots']]

def main(revision):
    dry = case('AmmoDry01')
    check('held empty fire is bounded', at(dry, 2.5)['rifle']['dry_fire'] == at(dry, 5.9)['rifle']['dry_fire'] == 1)
    check('empty/low-reserve reload and no-reserve rejection', dry[-1]['rifle']['magazine'] == 0 and
        dry[-1]['rifle']['reserve'] == 0 and dry[-1]['rifle']['shots'] == 7 and dry[-1]['rifle']['transfers'] == 1 and
        dry[-1]['rifle']['transferred_rounds'] == 4 and dry[-1]['rifle']['dry_fire'] == 2)
    low = case('PartialLow01')
    check('partial low reserve transfers only one available round', low[-1]['rifle']['magazine'] == 29 and
        low[-1]['rifle']['reserve'] == 0 and low[-1]['rifle']['transfers'] == 1)
    check('hold-R inspection is read-only', any('MagCheck' in r['montage'] for r in low) and
        all(r['rifle']['magazine'] == 29 and r['rifle']['reserve'] == 0 for r in low if 4.2 < r['t'] < 8.8))
    quick = case('QuickCancel01')
    check('Q uses quick partial presentation', at(quick, 1)['rifle']['reload_montage'] == 'Combat_ReloadQuick')
    check('full-magazine E does not reload', at(quick, 4.8)['rifle']['reloads'] == 1)
    check('cancel before notify retains ammunition', at(quick, 6.8)['rifle']['magazine'] == 12 and at(quick, 6.8)['rifle']['reserve'] == 40)
    check('duplicate notify and cancel after commit cannot transfer again', quick[-1]['rifle']['magazine'] == 30 and
        quick[-1]['rifle']['reserve'] == 22 and quick[-1]['rifle']['transfers'] == 2 and quick[-1]['rifle']['canceled_reloads'] == 1)
    empty = case('EmptyVariants01')
    check('R/Q/E select empty presentation from real ammunition', all(at(empty, t)['rifle']['reload_montage'] ==
        'Combat_ReloadEmpty' for t in [1, 6, 9]))
    check('empty cancellation/retry preserves totals', empty[-1]['rifle']['magazine'] == 30 and empty[-1]['rifle']['reserve'] == 30 and
        empty[-1]['rifle']['transfers'] == 2 and empty[-1]['rifle']['canceled_reloads'] == 1 and empty[-1]['rifle']['shots'] == 0)
    stop = case('StoppedSelf01')
    frozen = [r['ballistics']['bullets'][0] for r in stop if .8 < r['t'] < 1.8]
    check('actual stopped bullet position/velocity/age remain exact', frozen and all(b == frozen[0] and b['age'] == 0 for b in frozen))
    check('normal movement crosses suspended own bullet exactly once', stop[-1]['ballistics']['self_hits'] == 1 and
        at(stop, 2.5)['ballistics']['self_hits'] == 1 and max(r['velocity'][0] for r in stop if 2 < r['t'] < 2.6) >= 359)
    a, b = at(stop, 4.2), at(stop, 4.8)
    check('quarter-speed flight in continuous PIE', abs((b['ballistics']['bullets'][0]['age'] - a['ballistics']['bullets'][0]['age']) /
        (b['world_time'] - a['world_time']) - .25) < .001)
    a, b = at(stop, 5.2), at(stop, 5.8)
    check('second stop preserves partially aged bullet', a['ballistics']['bullets'] == b['ballistics']['bullets'])
    a, b = at(stop, 6.2), at(stop, 6.8)
    check('resumption uses normal simulation rate', abs((b['ballistics']['bullets'][0]['age'] - a['ballistics']['bullets'][0]['age']) /
        (b['world_time'] - a['world_time']) - 1) < .001)
    cover = case('NearCover01')
    check('near/offset/thin cover blocks all six hip/ADS shots', at(cover, 8.8)['rifle']['shots'] == 6 and
        at(cover, 8.8)['ballistics']['hits'] == 6 and all(t['health'] == 100 for t in at(cover, 8.8)['ballistics']['targets']))
    check('removing cover restores target damage', sum(t['hits'] for t in cover[-1]['ballistics']['targets']) == 1)
    check('actual ADS and hip cover phases', at(cover, 2.5)['aim_requested'] and at(cover, 8.5)['aim_requested'] and
        not at(cover, 5.5)['aim_requested'] and not cover[-1]['aim_requested'])
    capacity = case('Capacity01')
    check('capacity rejection spends no ammunition and launches nothing', at(capacity, 2.2)['rifle']['magazine'] == 29 and
        at(capacity, 2.2)['rifle']['shots'] == 1 and at(capacity, 2.2)['ballistics']['rejected'] == 1)
    check('reset frees capacity without refund', capacity[-1]['rifle']['magazine'] == 28 and capacity[-1]['rifle']['shots'] == 2 and
        capacity[-1]['ballistics']['retired'] == 1)
    movement = case('MovingAirborne01')
    fired = shots(movement)
    check('aimed moving fire and reload', any(r['aim_requested'] and abs(r['velocity'][0]) > 300 for r in fired) and
        any(r['rifle']['reloading'] and r['aim_requested'] and abs(r['velocity'][0]) > 100 for r in movement))
    check('ordinary jump fires immediately while aimed', any(5 <= r['t'] < 5.12 and r['falling'] and r['aim_requested'] for r in fired))
    check('Shift jump fires immediately while aimed at retained speed', any(7 <= r['t'] < 7.12 and r['falling'] and
        r['aim_requested'] and abs(r['velocity'][0] - 540) < 1 for r in fired))
    check('held fire crosses real landing', any(7.7 < r['t'] < 7.8 and not r['falling'] for r in fired) and
        movement[-1]['jump_starts'] == 2 and movement[-1]['landings'] == 2)
    expiry = case('FeedbackExpiryFinal01')
    times = [r['world_time'] for r in shots(expiry)]
    cadence = statistics.mean(b - a for a, b in zip(times, times[1:]))
    check('source automatic cadence retained', abs(cadence - .085) < .002, {'average_seconds': cadence, 'shots': len(times)})
    check('released fire stops and feedback expires', expiry[-1]['rifle']['shots'] == at(expiry, 3.2)['rifle']['shots'] and
        expiry[-1]['rifle']['props'] == expiry[-1]['rifle']['effects'] == expiry[-1]['niagara_components'] == expiry[-1]['ballistics']['impacts'] == 0)
    surfaces = case('SurfaceResetFinal01')
    check('accepted stone/metal materials select distinct feedback', at(surfaces, 2.2)['ballistics']['last_surface'] == 'stone_or_other' and
        'M_PainterStone01' in at(surfaces, 2.2)['ballistics']['last_material'] and
        at(surfaces, 5)['ballistics']['last_surface'] == 'metal' and 'M_PainterMetal01' in at(surfaces, 5)['ballistics']['last_material'])
    check('reset removes bullets, impacts, casings and VFX without refill', at(surfaces, 8.2)['rifle']['magazine'] == 24 and
        at(surfaces, 8.2)['rifle']['props'] == at(surfaces, 8.2)['rifle']['effects'] == at(surfaces, 8.2)['niagara_components'] ==
        at(surfaces, 8.2)['ballistics']['active'] == at(surfaces, 8.2)['ballistics']['impacts'] == 0 and
        all(t['health'] == 100 and t['hits'] == 0 for t in at(surfaces, 8.2)['ballistics']['targets']))
    attribution = case('SelfAttributionFinal01')
    check('final own-shot event carries identity and unique shot id', attribution[-1]['ballistics']['self_hits'] == 1 and
        attribution[-1]['ballistics']['last_hit_shot'] == 1 and 'BP_TFA_BaseCharacter' in attribution[-1]['ballistics']['last_hit_shooter'])
    native = json.loads((OUT / 'ballistics-Final01.json').read_text())
    for name, value in native.items():
        check('native sweep: ' + name, value if isinstance(value, bool) else value == 0)
    result = {'task': 'MSQ-68', 'checks': CHECKS, 'cases': CASES,
              'passed': all(c['passed'] for c in CHECKS), 'checks_count': len(CHECKS),
              'samples': sum(c['samples'] for c in CASES.values())}
    path = OUT / ('verification-summary' + revision + '.json')
    assert not path.exists(), path
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['passed', 'checks_count', 'samples']}))
    print(json.dumps([c for c in CHECKS if not c['passed']], indent=2))
    assert result['passed']

if __name__ == '__main__':
    main(sys.argv[1])
