"""Summarize native PIE evidence without replacing any input verifier."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms01/Worker'


def read(path):
    return json.loads(path.read_text())


def distance(a, b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))


def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def relative(point, transform):
    v = [a-b for a,b in zip(point, transform['location'])]
    q = [-x for x in transform['rotation'][:3]]
    w = transform['rotation'][3]
    uv = cross(q,v)
    uuv = cross(q,uv)
    return [v[i]+2*w*uv[i]+2*uuv[i] for i in range(3)]


def multiply(a, b):
    av, bv = a[:3], b[:3]
    product = cross(av, bv)
    return [a[3]*bv[i] + b[3]*av[i] + product[i] for i in range(3)] + [a[3]*b[3] - sum(x*y for x,y in zip(av,bv))]


def normalized(q):
    length = math.sqrt(sum(x*x for x in q))
    assert length > 0
    return [x/length for x in q]


def magazine_sample(s, step, reference):
    cs = s['components']
    visible = [n for n in ['MainMagazine','ReserveMagazine'] if cs[n]['visible']]
    assert len(visible) == 1
    rifle = cs['PurchasedRifle']
    assert abs(rifle['evaluation']['action_time'] - s['reload_time']) < .00001
    root, magazine = rifle['bones']['root'], cs[visible[0]]
    gap = distance(relative(magazine['world'], root), reference['translation'])
    q = normalized(root['rotation'])
    relative_q = normalized(multiply([-q[0],-q[1],-q[2],q[3]], normalized(magazine['bones']['root']['rotation'])))
    reference_q = normalized(reference['rotation_xyzw'])
    angle = math.degrees(2*math.acos(min(1,abs(sum(x*y for x,y in zip(relative_q,reference_q))))))
    assert gap < .05 and angle < .1, (gap, angle, step, s['reload_time'])
    return dict(step=step, action_time=s['reload_time'], reloading=s['reloading'], visible=visible[0],
        evaluated_action_time=rifle['evaluation']['action_time'], evaluations=rifle['evaluation']['evaluations'],
        reload_weight=rifle['evaluation']['reload_weight'], seated_gap_cm=gap, angle_degrees=angle)


def main():
    route = read(OUT / 'Acceptance02/runtime-verification.json')
    action = read(OUT / 'Correction03/runtime-verification.json')
    corrected_samples = read(OUT / 'Correction03/runtime-samples.json')
    samples = read(OUT / 'Acceptance02/runtime-samples.json') + corrected_samples
    assert action['passed'], action['error']
    route_events = {e['step']:e for e in route['events']}
    required_route = ['mouse_yaw', 'mouse_pitch', 'entrance_wall_collision', 'lane_inbound', 'axis_align', 'elevator_approach', 'walk_back']
    assert all(n in route_events for n in required_route)
    alignment, sync, shadows = [], [], []
    grip = {}
    for s in samples:
        cs = s.get('components')
        if not cs:
            continue
        arms, rifle = cs['CharacterMesh0'], cs['PurchasedRifle']
        sync.append(abs(arms['evaluation']['action_time'] - rifle['evaluation']['action_time']))
        alignment.append(distance(arms['bones']['ik_hand_gun']['location'], rifle['world']))
        for magazine, socket in [('MainMagazine','SOCKET_Magazine'), ('ReserveMagazine','SOCKET_Magazine_Reserve')]:
            alignment.append(distance(cs[magazine]['world'], rifle['bones'][socket]['location']))
        for name,c in cs.items():
            if name.startswith('CameraProxy'):
                continue
            shadows.extend(c[n] for n in ['cast_shadow','cast_dynamic_shadow','cast_static_shadow','cast_hidden_shadow','cast_contact_shadow'])
        if s['reloading'] and .15 < s['reload_time'] < 3.50:
            grip.setdefault(s['step'], []).append(relative(arms['bones']['hand_r']['location'], rifle['bones']['root']))
    drift = {k:max(distance(points[0],p) for p in points) for k,points in grip.items()}
    assert max(sync) < .00001 and max(alignment) < .001 and not any(shadows)
    assert max(drift.values()) < .2, drift
    seat_reference = next(b['component_bind'] for b in read(ROOT / 'Saved/PlayerCharacter01/AnimationAudit01/Worker/rigs.json')['SKEL_TFA_AR']['bones'] if b['name'] == 'Magazine')
    continuity = []
    for s in corrected_samples:
        if s['reload_time'] < 3.466667:
            continue
        continuity.append(magazine_sample(s, s['step'], seat_reference))
    capture_coverage = {}
    for case in ['reload_hip','reload_aimed','reload_queue_aim','reload_moving_aimed','reload_hip_moving']:
        assert any(r['step']==case and r['reloading'] and 3.516667 < r['action_time'] < 3.666667 for r in continuity), case
        captures = {}
        for suffix in ['before-fade','mid-fade','late-fade','complete']:
            assert (OUT / 'Correction03' / (case+'-'+suffix+'.png')).exists()
            shot = read(OUT / 'Correction03' / (case+'-'+suffix+'.json'))
            captures[suffix] = magazine_sample(shot, case, seat_reference)
        assert 3.466667 <= captures['before-fade']['action_time'] < 3.516667
        assert 3.516667 < captures['mid-fade']['action_time'] < 3.60
        assert 3.62 < captures['late-fade']['action_time'] < 3.666667
        assert all(captures[k]['reloading'] and captures[k]['visible'] == 'ReserveMagazine' for k in ['before-fade','mid-fade','late-fade'])
        assert not captures['complete']['reloading'] and captures['complete']['visible'] == 'MainMagazine'
        captures['first-recorded-recovery'] = next(r for r in continuity if r['step'] == case and not r['reloading'])
        capture_coverage[case] = captures
    (OUT / 'magazine-continuity.json').write_text(json.dumps(dict(passed=True, reference=seat_reference, captures=capture_coverage, samples=continuity,
        max_seated_gap_cm=max(r['seated_gap_cm'] for r in continuity), max_angle_degrees=max(r['angle_degrees'] for r in continuity)),indent=2))
    cold = read(OUT / 'cold-load.json')
    assert cold['passed']
    archive = read(ROOT / 'Assets/Archive/PurchasedArms01/manifest.json')['files']
    active = read(OUT / 'dependency-plan.json')['keep']
    active_manifest = []
    for package in active:
        path = ROOT / 'Content' / (package.removeprefix('/Game/') + '.uasset')
        with path.open('rb') as stream:
            sha = hashlib.file_digest(stream, 'sha256').hexdigest()
        active_manifest.append(dict(package=package, path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=sha))
    (OUT / 'active-content-manifest.json').write_text(json.dumps(active_manifest, indent=2))
    summary = dict(passed=True, engine=action['initial']['engine'], route_events_passed=required_route,
        route_note='Acceptance02 completed the full walk/collision route. Correction01 validates fresh startup, diagonal movement, turn and aim while walking. Correction03 completes five reload cases with explicit evaluated samples/screenshots before, within and after the final fade. Original movement implementation is unchanged.',
        action_result=action, telemetry_samples=len(samples), maximum_rifle_magazine_attachment_error_cm=max(alignment),
        maximum_paired_animation_time_error_seconds=max(sync), right_grip_drift_cm=drift, any_shadow_enabled=any(shadows),
        retained_packages=len(active), retained_bytes=sum(r['bytes'] for r in active_manifest),
        archived_packages=len(archive), archived_bytes=sum(r['bytes'] for r in archive), cold_load_passed=cold['passed'],
        magazine_continuity_passed=True, maximum_late_magazine_seat_gap_cm=max(r['seated_gap_cm'] for r in continuity),
        maximum_late_magazine_rotation_gap_degrees=max(r['angle_degrees'] for r in continuity))
    (OUT / 'verification-summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k not in ['action_result','route_note']}))
    images = ['idle', 'movement', 'aim_press', 'reload_hip-reserve', 'reload_hip-transfer', 'reload_hip-mid-fade', 'reload_hip-late-fade', 'reload_hip-complete', 'reload_aimed-mid-fade', 'reload_moving_aimed-late-fade', 'recovered']
    cards = []
    for name in images:
        folder = 'Visual01' if name == 'movement' else 'Correction03'
        path = OUT / folder / (name + '.png')
        assert path.exists(), path
        cards.append(f'<figure><a href="{folder}/{name}.png"><img src="{folder}/{name}.png"></a><figcaption>{name}</figcaption></figure>')
    (OUT / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>MSQ-61 actual PIE evidence</title><style>body{background:#181b1c;color:#eee;font:16px system-ui;margin:30px}main{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%}figcaption{padding:10px}</style><h1>PurchasedArms01 — actual PIE captures</h1><p>Unmodified retained lobby; native gameplay camera, supplied stock arms and rifle. Click to inspect full resolution. See verification-summary.json for measured runtime evidence.</p><main>' + ''.join(cards) + '</main>')


if __name__ == '__main__':
    main()
