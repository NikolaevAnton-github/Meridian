"""Phase-matched output-pose analysis, independent of paired montage clocks."""
import json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2] / 'Saved/PurchasedArms02/Worker'

def arm(r):
    return next(p for p in r['parts'] if p['component']=='CharacterMesh0')

def phase(r):
    players = [p for p in arm(r)['evaluation']['players'] if 'BlendSpacePlayer' in p['node']]
    return max(players,key=lambda p:p['weight'])['phase']

def main():
    summaries = []
    for path in sorted(ROOT.glob('Recovery02-*Reload.json')) + sorted(ROOT.glob('Recovery02-*Empty.json')):
        data = json.loads(path.read_text())
        control_name = path.stem.replace('Reload','Control').replace('Empty','Control')
        control_path = ROOT/(control_name+'.json')
        control = [r for r in json.loads(control_path.read_text())['rows'] if r['t']>1.3]
        phases = np.array([phase(r) for r in control])
        rows = [r for r in data['rows'] if r['t']>1.3]
        matches = []
        for row in rows:
            diff = np.abs(phases-phase(row))
            i = int(np.argmin(np.minimum(diff,1-diff)))
            sample = arm(row)['bones']['ik_hand_gun']
            expected = arm(control[i])['bones']['ik_hand_gun']
            delta = np.array(sample['p'])-expected['p']
            matches.append({'t':row['t'],'phase':phase(row),'residual_cm':float(np.linalg.norm(delta)),
                'delta_cm':delta.tolist(),'action':row['reload_time'], 'reloading':row['reloading']})
        action_end = max(r['t'] for r in rows if r['reloading'])
        recovered = [r for r in matches if r['t']>action_end+.25]
        tail = [r for r in matches if 2.08+2.95 < r['t'] < action_end]
        # A phase-matched moving control detects a frozen output even if all clocks advance.
        windows = []
        for start in np.arange(5.15,9.65,.15):
            indexes = [i for i,r in enumerate(rows) if start<=r['t']<start+.15]
            if len(indexes)<4: continue
            actual = np.array([arm(rows[i])['bones']['ik_hand_gun']['p'] for i in indexes])
            expected = np.array([actual[j]-matches[i]['delta_cm'] for j,i in enumerate(indexes)])
            energy,reference = np.linalg.norm(np.std(actual,axis=0)),np.linalg.norm(np.std(expected,axis=0))
            windows.append(dict(start=float(start),motion_cm=float(energy),control_cm=float(reference),ratio=float(energy/max(reference,1e-9))))
        evaluation_ids = [arm(r)['evaluation']['evaluations'] for r in rows]
        result = dict(case=path.stem, samples=len(data['rows']), action_end=action_end,
            max_delta=max(r['delta'] for r in rows), min_moving_speed=min(np.linalg.norm(r['velocity']) for r in rows),
            repeated_evaluation_ids=sum(a==b for a,b in zip(evaluation_ids,evaluation_ids[1:])),
            shadows=any(any(p['shadow_flags']) for r in rows for p in r['parts']),
            recovery_residual_max_cm=max(r['residual_cm'] for r in recovered),
            recovery_residual_p95_cm=float(np.percentile([r['residual_cm'] for r in recovered],95)),
            tail_residual_max_cm=max((r['residual_cm'] for r in tail),default=None),
            freeze_windows=[w for w in windows if w['control_cm']>.001 and w['ratio']<.1],
            windows=windows)
        summaries.append(result)
        (ROOT/(path.stem+'-residuals.json')).write_text(json.dumps(matches,separators=(',',':')))
    (ROOT/'recovery-analysis02.json').write_text(json.dumps(summaries,indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k!='windows'} for r in summaries],indent=2))

if __name__=='__main__': main()
