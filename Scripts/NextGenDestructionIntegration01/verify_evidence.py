"""Verify the selected runtime evidence and preservation manifests without starting Unreal."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/NextGenDestructionIntegration01/NGD-01/Candidate01'
checks = []

def read(name):
    return json.loads((OUT / (name + '.json')).read_text(encoding='utf-8-sig'))

def check(name, passed):
    checks.append(dict(name=name, passed=bool(passed)))

def prop(state, identity='NGD01_ConcretePillar'):
    return next(p for p in state['props'] if p['id'] == identity)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def one_shot(r):
    return r['after']['rifle']['shots'] - r['before']['rifle']['shots'] == 1 and r['after']['projectiles']['hits'] - r['before']['projectiles']['hits'] == 1

for name in ['pillar-shot04', 'pillar-shot05', 'pillar-shot07']:
    r = read(name)
    check(name + '_consumed_once', one_shot(r) and prop(r['after'])['delivered_hits'] - prop(r['before'])['delivered_hits'] == 1)
    check(name + '_witness_protected', r['after']['witnesses'][0]['health'] == 100 and r['after']['witnesses'][0]['hits'] == 0)

r = read('pillar-shot08')
check('opening_real_rifle_passage', one_shot(r) and prop(r['after'])['delivered_hits'] == prop(r['before'])['delivered_hits'] and r['after']['witnesses'][0]['health'] == 75 and r['after']['witnesses'][0]['hits'] == 1)
check('opening_finite_sweep', read('opening-after-shot07')['same_sweep_now']['actor'] == 'CombatTarget_1' and read('opening-after-shot07')['same_sweep_now']['radius'] == .5)
r = read('pillar-solid09')
check('remaining_solid_stops_real_round', one_shot(r) and prop(r['after'])['delivered_hits'] == prop(r['before'])['delivered_hits'] + 1 and r['after']['witnesses'][0]['health'] == 75)

for name, identity in [('chair-shot02', 'NGD01_WoodenChair'), ('vase-shot01', 'NGD01_CeramicVase')]:
    r = read(name)
    check(identity + '_real_rifle_break', one_shot(r) and prop(r['after'], identity)['delivered_hits'] == 1 and prop(r['after'], identity)['break_events'] > 0)
    check(identity + '_fragment_collision', len(r['fragments']) > 0 and all(f['hit']['radius'] == 5 for f in r['fragments']))

for name in ['build03-reset-live-field01', 'build03-reset-live-field02']:
    r = read(name)
    check(name, r.get('passed') and sum(p['live_fields'] for p in r['with_live_field']['props']) == 1 and len(r['after']['props']) == 3)
    check(name + '_generation_and_notification', all(prop(r['after'], p['id'])['reset_generation'] == p['reset_generation'] + 1 for p in r['with_live_field']['props']) and all(c['reason'] == 'reset' for c in r['after']['changes']))

r = read('build03-after-reset-shot')
check('build03_real_shot_after_reset', one_shot(r) and prop(r['after'])['delivered_hits'] == 1 and prop(r['after'])['break_events'] > 0)
settled = read('build03-reset-settled')
reset = read('build03-reset-live-field02')['after']
check('delayed_callbacks_absent', settled['projectiles']['firing_clock'] - reset['projectiles']['firing_clock'] > 4 and all(p['break_events'] == 0 and p['live_fields'] == 0 and not p['root_broken'] and p['collision_revision'] == prop(reset, p['id'])['collision_revision'] for p in settled['props']))
clearance = read('build03-reset-clearance')
check('216_reset_clearance_sweeps', sum(r['samples'] for r in clearance) == 216 and all(not r['stale_blockers'] for r in clearance))

before = {a['name']: a for a in read('lobby-before')['actors']}
after = {a['name']: a for a in read('lobby-final')['actors']}
def canonical(row):
    return re.sub(r'0x[0-9A-Fa-f]+', 'ADDRESS', json.dumps(row, sort_keys=True))
changed = [name for name, actor in before.items() if name not in after or canonical(actor) != canonical(after[name])]
check('129_original_actor_inventory_preserved', len(before) == 129 and not changed)
check('exactly_three_removable_props', len(after) == 132 and all('NGD01' in a['tags'] and a['folder'] == 'NGD01_DemoProps' for n, a in after.items() if n not in before))
check('no_witness_in_handoff', not any('Witness' in a['label'] for a in after.values()))
manifest = read('before-hashes')
vendor_changed = [p for p, h in manifest.items() if p.startswith('Content/NextGenDestruction/') and digest(ROOT / p) != h]
check('481_vendor_packages_preserved', len([p for p in manifest if p.startswith('Content/NextGenDestruction/')]) == 481 and not vendor_changed)
check('recoverable_current_map_snapshot', digest(OUT / 'Before/L_OpeningLobby_PainterStone01.umap') == manifest['Content/Maps/L_OpeningLobby_PainterStone01.umap'])
owner = read('Controller/owner-before-hashes')
check('protected_owner_files_preserved', all(digest(Path(row['Path'])).upper() == row['Hash'].upper() for row in owner))
build = read('build03-hashes')
check('build03_source_binary_map_identity', all(digest(Path(row['Path'])).upper() == row['Hash'].upper() for row in build))
final = read('editor-final')
check('saved_open_lobby', final['dirty'] == [] and not final['pie'] and final['actor_count'] == 132 and final['map'].startswith('/Game/Maps/L_OpeningLobby_PainterStone01.'))
check('editor_throttle_restored', final['throttle_cpu_when_not_foreground'])
report = dict(candidate='Candidate01', build='Build03', passed=all(c['passed'] for c in checks), checks=checks,
              changed_original_actors=changed, changed_vendor_packages=vendor_changed,
              final_map_sha256=digest(ROOT / 'Content/Maps/L_OpeningLobby_PainterStone01.umap'),
              source_evidence_reuse='Build02 rifle/local fracture/material/fragment checks remain applicable: Build03 changes only retirement of task-owned queued fields. Build03 rechecks active-field reset twice, delayed callbacks, clearance and a real post-reset shot.',
              authority='NGD01-OwnerStart01 task-scoped independent-review waiver; controller acceptance and commit remain pending.')
(OUT / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'passed': report['passed'], 'checks': len(checks), 'failures': [c['name'] for c in checks if not c['passed']], 'map_sha256': report['final_map_sha256']}))
raise SystemExit(0 if report['passed'] else 1)
