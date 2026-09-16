"""Approved-route adapter of the unchanged actual key-input PIE verifier."""
import hashlib
import json
import time
import types
from functionalbuild01_data import ROOT,OUT,MAP
_module=globals().get('_module')
_scope=globals().get('_scope','full')

def configuration(root):
    plan=[('wait','spawn',1),('mouse','mouse_yaw',30,0),('mouse','mouse_pitch',0,20),('look','restore_look',0,0)]
    def move(name,x,y):plan.append(('move',name,x,y))
    def contact(name,key,axis,surface,offset,duration=2):plan.append(('contact',name,key,duration,axis,surface,offset))
    move('entrance_clear',-2700,-105)
    for sign in [-1,1]:
        y=sign*465;tag=str(sign)
        move('lane_'+tag+'_outside_align',-2700,y)
        move('lane_'+tag+'_inbound',-2300,y)
        move('lane_'+tag+'_outbound',-2700,y)
    move('lane_final_align',-2700,465);move('lane_final_inbound',-2300,465)
    move('axis_start',-2300,0);move('full_hall_axis_end',2850,0)
    contact('elevator_closed_leaves','W',0,3000,-1)
    move('elevator_leave',2850,0)
    for sign in [-1,1]:
        tag=str(sign);move('inner_door_'+tag+'_align',2610,0);move('inner_door_'+tag+'_approach',2610,sign*480)
        contact('inner_door_'+tag+'_closed','D' if sign>0 else 'A',1,sign*584,-sign)
        move('inner_door_'+tag+'_leave',2610,0)
        # Old X27 transverse bypass is now deliberately blocked by room hall face.
        move('inner_terminal_'+tag+'_align',2700,0)
        contact('inner_terminal_'+tag+'_no_bypass','D' if sign>0 else 'A',1,sign*560,-sign,2.2)
        move('inner_terminal_'+tag+'_leave',2700,0)
    move('inner_open_bay_axis',1680,0)
    for sign in [-1,1]:
        tag=str(sign)
        move('aisle_'+tag+'_inner_open_bay',1680,sign*1000)
        contact('inner_blind_cap_'+tag,'W',0,1980,-1)
        move('inner_cap_'+tag+'_leave',1680,sign*1000)
        move('aisle_'+tag+'_full_return',-1680,sign*1000)
        move('service_door_'+tag+'_approach',-1880,sign*1000)
        contact('service_door_'+tag+'_closed','S',0,-2004,1)
        move('service_door_'+tag+'_leave',-1680,sign*1000)
        move('aisle_'+tag+'_entrance_open_bay',-1680,0)
        move('aisle_'+tag+'_axis_return',1680,0)
    # All three actual floor passages at each new pair, both side gaps plus axis.
    move('pair_checks_start',-1680,0)
    for x in [-1260,1260]:
        for y in [-460,0,460]:
            tag=str(x)+'_'+str(y)
            move('passage_'+tag+'_axis_align',x-300,0)
            move('passage_'+tag+'_approach',x-300,y)
            move('passage_'+tag+'_through',x+300,y)
            move('passage_'+tag+'_leave',x+300,0)
        for sign in [-1,1]:
            tag=str(x)+'_'+str(sign)
            move('shaft_'+tag+'_align',x-300,0);move('shaft_'+tag+'_approach',x-300,sign*240)
            contact('shaft_'+tag+'_block','W',0,x-120,-1)
            move('shaft_'+tag+'_leave',x-300,sign*240);move('shaft_'+tag+'_axis',x-300,0)
    move('return_axis',-2300,0)
    contact('checkpoint_joined_desk_block','S',0,-2415,1)
    move('checkpoint_desk_leave',-2300,0);move('return_lane_align',-2300,-465)
    move('return_lane_outbound',-2700,-465)
    for sign in [-1,1]:
        tag=str(sign);move('entrance_terminal_'+tag+'_align',-2700,0)
        contact('entrance_terminal_'+tag+'_no_bypass','D' if sign>0 else 'A',1,sign*560,-sign,2.2)
        move('entrance_terminal_'+tag+'_leave',-2700,0)
        move('checkpoint_post_'+tag+'_approach',-2700,sign*370)
        contact('checkpoint_post_'+tag+'_block','W',0,-2505,-1)
        move('checkpoint_post_'+tag+'_leave',-2700,sign*370)
    move('jump_clear',-2700,0);plan.append(('jump','jump_and_landing',1.8))
    move('return_to_entrance',-2900,0)
    run_out=OUT
    if _scope=='elevator':
        run_out=OUT/'ElevatorRecheck';run_out.mkdir(exist_ok=True)
        plan=[('wait','spawn',1),('mouse','mouse_yaw',30,0),('mouse','mouse_pitch',0,20),('look','restore_look',0,0),
              ('move','clear_entrance',-2700,-105),('move','lane_align',-2700,465),('move','lane_inbound',-2300,465),
              ('move','axis_align',-2300,0),('move','elevator_approach',2850,0),
              ('contact','elevator_centre_seam_block','W',2,0,3000,-1),('move','elevator_leave',2850,0)]
    config={'map':MAP,'out':run_out,'plan':plan,'view_plan':plan,'refresh_held_input':True,'contact_tolerance_cm':3}
    (run_out/'route-contract.json').write_text(json.dumps({'map':MAP,'steps':plan,
        'source_verifier_sha256':hashlib.sha256((ROOT/'Scripts/OpeningLobby/verify_lobby.py').read_bytes()).hexdigest(),
        'active_routes':'X +/-16.8 open bays replace closed historical X +/-27 terminal crossovers; their blocking is tested explicitly.',
        'movement':'Only key and mouse input from possessed PlayerStart spawn; no actor transforms'},indent=2))
    return config

def start(scope='full'):
    global _module,_scope
    assert scope in ['full','elevator'];_scope=scope
    assert _module is None or _module._run is None or _module._run.done
    source=(ROOT/'Scripts/OpeningLobby/verify_lobby.py').read_text()
    old="'layout03_verification' if revision == 'Layout03' else 'layout02_verification'"
    assert source.count(old)==1
    source=source.replace(old,"'functionalbuild01_walk' if revision == 'Layout03' else 'layout02_verification'")
    _module=types.ModuleType('functionalbuild01_existing_verifier')
    exec(compile(source,str(ROOT/'Scripts/OpeningLobby/verify_lobby.py'),'exec'),_module.__dict__)
    base=_module.WalkCheck
    class FunctionalWalk(base):
        def update(self):
            step=self.plan[self.index]
            if step[0]!='contact':return super().update()
            now=time.monotonic();s=_module.state();self.validate_identity(s)
            assert s['walking'] and s['walkable_floor']
            if now-self.last_sample>.1:
                self.samples.append(dict(t=now-self.started,step=step[1],**s));self.last_sample=now
            age=now-self.step_started;assert age<8,step
            _,name,key,duration,axis,surface,offset=step
            if self.settled is None:self.contact_start=s['location'][axis];self.settled=now
            self.keys([key])
            if age>duration:
                expected=surface+offset*s['capsule_radius'];actual=s['location'][axis]
                assert abs(s['velocity'][axis])<1 and abs(actual-expected)<=3,dict(step=name,actual=actual,expected=expected,state=s)
                assert abs(actual-self.contact_start)>10,dict(step=name,reason='Contact requires actual movement')
                self.advance(dict(axis=axis,surface_cm=surface,expected_cm=expected,actual_cm=actual,tolerance_cm=3,distance_m=abs(actual-self.contact_start)/100,key=key))
    _module.WalkCheck=FunctionalWalk
    return _module.start(revision='Layout03')

def status():
    report=_module.status() if _module else {'done':True,'passed':False,'error':'Not started'}
    return {k:v for k,v in report.items() if k not in ['initial','events']}
