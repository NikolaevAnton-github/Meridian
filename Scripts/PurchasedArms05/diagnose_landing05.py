"""Name the evaluated Run End player and compare preserved before/after evidence."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'Saved/PurchasedArms05/Worker'

def players(row):
    part=next(p for p in row['parts'] if 'hand_l' in p.get('bones',{}))
    return part['evaluation']['players']

def run():
    data=json.loads((OUT/'Correction02-CancelRecovery.json').read_text())
    asset_map={}
    for row in data['rows']:
        for p in players(row):
            if p.get('asset'): asset_map.setdefault(p['node'],set()).add(p['asset'])
    run_end=next(node for node,assets in asset_map.items() if any('Run_End' in a for a in assets))
    assert run_end=='AnimGraphNode_SequencePlayer_7', (run_end,asset_map)
    comparison={}
    for name in ['Final01-ShiftHeldADS','Final01-ShiftReleasedADS','Correction01-ShiftHeldADS','Correction01-ShiftReleasedADS']:
        rows=json.loads((OUT/(name+'.json')).read_text())['rows']
        land=next(r['t'] for r in rows if r['jump_starts']==1 and not r['falling'] and r['landings']==1)
        active=[r for r in rows if land<=r['t']<land+.5 and r['aim_requested']]
        values=[next(p for p in players(r) if p['node']==run_end) for r in active]
        maximum=max(p['weight'] for p in values)
        if name.startswith('Correction'): assert maximum<.00001,(name,maximum)
        else: assert maximum>.95,(name,maximum)
        comparison[name]=dict(contact_t=land,aimed_samples=len(values),
            run_end_max_weight=maximum,
            phase_range=[min(p['phase'] for p in values),max(p['phase'] for p in values)],
            guard_all=all(r['animation_jump_base'] for r in active))
    rows=data['rows']
    canceled=next(r for r in rows if r['canceled_jump_requests']==1)
    assert canceled['walking'] and canceled['jump_starts']==0 and not canceled['jump_active']
    assert not canceled['jump_request_pending'] and not canceled['jump_pending_landing']
    assert canceled['running'] and canceled['jump_z_velocity']==320 and not canceled['busy']
    jumped=next(r for r in rows if r['jump_starts']==1)
    assert jumped['falling'] and jumped['jump_z_velocity']==352 and not jumped['jump_request_pending']
    assert jumped['t']-canceled['t']<.09
    assert rows[-1]['jump_requests']==2 and rows[-1]['canceled_jump_requests']==1
    assert rows[-1]['jump_starts']==rows[-1]['landings']==1
    assert any(r['ammo']==29 and r['aim_requested'] and r['falling'] for r in rows)
    assert all(not r['jump_pending_landing'] for r in rows if r['t']<jumped['t'])
    result=dict(runtime_player=run_end,assets=sorted(asset_map[run_end]),comparison=comparison,
        cancellation=dict(canceled_t=canceled['t'],canceled_frame=canceled['frame'],
            same_frame_input=[e for e in data['events'] if .79<e['t']<.85],
            still_running=canceled['running'],pending=False,presentation=False,montage_active=False,
            restored_jump_z=canceled['jump_z_velocity'],recovery_takeoff_t=jumped['t'],
            recovery_delay_ms=1000*(jumped['t']-canceled['t']),actual_takeoffs=1,
            request_count=2,cancel_count=1,immediate_airborne_aim_and_shot=True))
    dest=OUT/'Correction02/run-end-and-cancellation.json'
    assert not dest.exists()
    dest.write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__': run()
