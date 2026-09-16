"""Existing real-input route with candidate configuration and explicit mass contacts."""
import hashlib
import json
import time
import types
from reworka01_data import ROOT,OUT,MAP

_module=globals().get('_module')
_scope=globals().get('_scope','full')

def configuration(root):
    from layout03_verification import configuration as baseline_configuration
    config=baseline_configuration(root)
    plan=list(config['plan'])
    index=next(i for i,s in enumerate(plan) if s[1]=='longitudinal_start')
    assert plan[index]==('move','longitudinal_start',-2850,-300)
    plan[index]=('move','longitudinal_start',-2750,-300)
    run_out=OUT
    if _scope.startswith('entrance'):
        run_out=OUT/('EntranceRecheckResume' if _scope=='entrance_resume' else 'EntranceRecheck');run_out.mkdir(exist_ok=True)
        plan=plan[:4]+[
            ('move','checkpoint_inbound',-2300,-105),('move','checkpoint_bypass',-2300,-300),
            ('move','entrance_clear_floor',-2750,-300),('move','crossover_align',-2700,-300),
            ('move','west_terminal_crossover',-2700,-1000),('move','west_adjacent_aisle',-1800,-1000),
            ('move','west_terminal_return',-2700,-1000),('move','east_terminal_crossover',-2700,1000),
            ('move','east_adjacent_aisle',-1800,1000),('move','east_terminal_return',-2700,1000)]
    plan+=[('move','A_contact_clear',-2700,-105)]
    contacts={}
    for sign in [-1,1]:
        suffix=str(sign)
        front_tests=[('portal_front',350,-2840)]
        if _scope=='full':front_tests += [('shoulder_front',510,-2960),('end_pier_front',680,-2880)]
        for name,y,surface in front_tests:
            tag=name+'_'+suffix
            plan += [('move',tag+'_approach',-2700,sign*y),('contact',tag,'S',2.3,0,surface,1),
                     ('move',tag+'_leave',-2700,sign*y)]
            contacts[tag]=dict(axis=0,surface_cm=surface,expected_capsule_center_cm=surface+34)
        if _scope=='full':
            tag='first_pier_front_'+suffix
            plan += [('contact',tag,'W',2.3,0,-2220,-1),('move',tag+'_leave',-2700,sign*680)]
            contacts[tag]=dict(axis=0,surface_cm=-2220,expected_capsule_center_cm=-2254)
        tag='mid_return_'+suffix
        plan += [('move',tag+'_align',-2700,sign*190),('move',tag+'_approach',-2860,sign*190),
                 ('contact',tag,'D' if sign>0 else 'A',1.5,1,sign*290,-sign),('move',tag+'_leave',-2700,sign*190)]
        contacts[tag]=dict(axis=1,surface_cm=sign*290,expected_capsule_center_cm=sign*256)
        # Enter the actual 1.0 m inner return beside the human door. This catches
        # an incorrect single-box jamb collider which would fill its recess.
        tag='inner_reveal_'+suffix
        plan += [('move',tag+'_align',-2700,sign*190),('move',tag+'_approach',-2950,sign*190),
                 ('contact',tag,'D' if sign>0 else 'A',1.5,1,sign*260,-sign),
                 ('move',tag+'_leave',-2700,sign*190)]
        contacts[tag]=dict(axis=1,surface_cm=sign*260,expected_capsule_center_cm=sign*226)
    plan += [('move','door_centre_align',-2700,0),('contact','closed_entrance_plane','S',2.3,0,-3000,1),
             ('move','door_approach_return',-2700,0),('move','final_detector_align',-2700,-105),
             ('move','A_final_checkpoint_inbound',-2300,-105),('move','A_final_checkpoint_outbound',-2700,-105),
             ('jump','A_entrance_jump_land',1.8),('move','A_final_entrance_return',-2850,-105)]
    contacts['closed_entrance_plane']=dict(axis=0,surface_cm=-3000,expected_capsule_center_cm=-2966)
    if _scope=='entrance_resume':
        first=next(i for i,step in enumerate(plan) if step[1]=='mid_return_-1_align')
        plan=[('wait','resume_grounded',1),('look','resume_look',0,0),('move','resume_clear',-2700,-190)]+plan[first:]
        contacts={name:item for name,item in contacts.items() if any(step[1]==name for step in plan)}
    config.update(map=MAP,out=run_out,plan=plan,view_plan=plan)
    (run_out/'route-contract.json').write_text(json.dumps(dict(map=MAP,scope=_scope,steps=plan,contacts=contacts,
        longitudinal_start_cm=[-2750,-300],longitudinal_target_cm=[2850,-300],longitudinal_expected_distance_m=56,
        adjustment_reason='Historical X -28.5/Y -3 lies inside approved A jamb; moved to clear X -27.5.',
        unchanged_verifier_sha256=hashlib.sha256((ROOT/'Scripts/OpeningLobby/verify_lobby.py').read_bytes()).hexdigest()),indent=2))
    return config

def start(scope='full'):
    global _module,_scope
    assert scope in ['full','entrance','entrance_resume'];_scope=scope
    assert _module is None or _module._run is None or _module._run.done
    source=(ROOT/'Scripts/OpeningLobby/verify_lobby.py').read_text()
    old="'layout03_verification' if revision == 'Layout03' else 'layout02_verification'"
    assert source.count(old)==1
    source=source.replace(old,"'reworka01_walk' if revision == 'Layout03' else 'layout02_verification'")
    _module=types.ModuleType('reworka01_existing_verifier')
    exec(compile(source,str(ROOT/'Scripts/OpeningLobby/verify_lobby.py'),'exec'),_module.__dict__)
    base=_module.WalkCheck

    class CandidateWalk(base):
        def update(self):
            step=self.plan[self.index]
            if step[0]!='contact':
                return super().update()
            now=time.monotonic();s=_module.state();self.validate_identity(s)
            assert s['walking'] and s['walkable_floor']
            if now-self.last_sample>.1:
                self.samples.append(dict(t=now-self.started,step=step[1],**s));self.last_sample=now
            age=now-self.step_started
            assert age<8,step
            _,name,key,duration,axis,surface,offset=step
            if self.settled is None:
                if name.startswith('mid_return_'):
                    assert -2865<s['location'][0]<-2845,dict(step=name,reason='Start inside main return but ahead of reveal by more than capsule radius',x=s['location'][0])
                self.contact_start=s['location'][axis];self.settled=now
            self.keys([key])
            if age>duration:
                expected=surface+offset*s['capsule_radius'];actual=s['location'][axis]
                assert abs(s['velocity'][axis])<1 and abs(actual-expected)<=3,dict(step=name,actual=actual,expected=expected,state=s)
                assert abs(actual-self.contact_start)>10,dict(step=name,reason='Contact requires actual movement')
                self.advance(dict(axis=axis,surface_cm=surface,expected_cm=expected,actual_cm=actual,tolerance_cm=3,
                                  distance_m=abs(actual-self.contact_start)/100,key=key))

    _module.WalkCheck=CandidateWalk
    return _module.start(revision='Layout03')

def status():
    global _module
    if _module is None:
        # Recover the one live callback after the existing verifier reloads its
        # configuration module. Preserve already executed input and route data.
        import gc
        runs=[o for o in gc.get_objects() if type(o).__name__=='CandidateWalk' and getattr(o,'target_map',None)==MAP]
        if len(runs)==1:
            run=runs[0]
            ns=type(run).__mro__[1].__init__.__globals__
            _module=types.SimpleNamespace(_run=run,status=run.report,state=ns['state'])
            (OUT/'verifier-monitor-recovery.json').write_text(json.dumps(dict(recovered=True,step=run.plan[run.index][1],
                events_preserved=len(run.events),reason='Existing verifier reloads configuration module; preserved module state and recovered live callback without restarting movement'),indent=2))
    report=_module.status() if _module else dict(done=True,passed=False,error='Not started')
    return {k:v for k,v in report.items() if k not in ['initial','events']}
