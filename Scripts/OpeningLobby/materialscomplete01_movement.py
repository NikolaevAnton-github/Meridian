"""Bounded forward/return reuse of the existing real-input route driver."""
import time
from verify_lobby import WalkCheck
from materialscomplete01_unreal import OUT,MAP,guard
from stage1_tools import state
run=None
class ShortWalk(WalkCheck):
    def validate_identity(self,s):
        self.target_map=MAP
        return super().validate_identity(s)
    def advance(self,result):
        self.keys([])
        self.events.append(dict(step=self.plan[self.index][1],elapsed=time.monotonic()-self.started,state=state(),result=result))
        self.index+=1;self.step_started=time.monotonic();self.settled=None
        if self.index>=len(self.plan):
            s=state();assert s['walking'] and s['walkable_floor'] and s['move_binding_samples']>self.initial['move_binding_samples']
            assert abs(self.events[0]['state']['location'][0]-self.initial['location'][0])>100
            assert abs(s['location'][0]-self.initial['location'][0])<45
            self.finish()
def start():
    global run
    guard(True,True,pie=True);assert run is None
    s=state();assert abs(s['rotation'][1])<.1 and abs(s['location'][1])<1
    path=OUT/'Movement';path.mkdir(exist_ok=True)
    run=ShortWalk(output_dir=path);x=s['location'][0]
    run.config=dict(refresh_held_input=True)
    run.plan=[('move','forward',x+180,0),('move','return',x,0)]
    return dict(started=True,input='Existing probe_key FInputKeyEventArgs, real CharacterMovement ticks',plan=run.plan)
def status():return run.report()
