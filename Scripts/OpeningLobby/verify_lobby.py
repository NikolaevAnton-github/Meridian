"""PIE acceptance driven by controller key events, never actor transforms.

Started by Epic MCP. Caller must poll to completion and stop PIE before handoff.
"""
import json
import math
import time
import traceback
import unreal as u
from stage1_tools import OUT, state

_run = None

class WalkCheck:
    def __init__(self, views=False):
        self.world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        self.pawn = u.GameplayStatics.get_player_pawn(self.world,0)
        self.held = set()
        self.index = 0
        self.started = time.monotonic()
        self.step_started = self.started
        self.settled = None
        self.events = []
        self.samples = []
        self.last_sample = 0
        self.done = False
        self.finished = None
        self.output_prefix = 'view-' if views else ''
        self.error = None
        self.max_z = 0
        self.fell = False
        self.plan = [
            ('wait','spawn',1),
            ('capture','entrance',1),
            ('mouse','mouse_yaw',30,0),
            ('mouse','mouse_pitch',0,20),
            ('look','restore_look',0,0),
            ('move','center',0,0),
            ('capture','center',1),
            ('move','elevator',1500,0),
            ('capture','elevator',1),
            ('move','west_side',1500,-850),
            ('move','west_return',-900,-850),
            ('move','cross_to_east',-900,850),
            ('move','east_route',1500,850),
            ('hold','wall_collision','D',2.0),
            ('move','leave_wall',1500,0),
            ('move','column_approach',300,0),
            ('hold','column_collision','D',2.0),
            ('move','leave_column',300,0),
            ('jump','gravity_jump',1.8),
            ('move','return_to_entrance',-1630,0),
        ]
        if views:
            self.plan = [('move','elevator_view_position',1450,0),
                         ('look','look_back_along_lobby',160,0),
                         ('capture','elevator',2),
                         ('look','restore_look',0,0),
                         ('move','return_to_entrance',-1630,0)]
        initial = state()
        assert initial['possessed'] and initial['pawn_class']=='/Script/MeridianSquad.OpeningLobbyCharacter', initial
        self.initial = initial
        self.handle = u.register_slate_post_tick_callback(self.tick)

    def keys(self, wanted):
        wanted = set(wanted)
        for key in self.held-wanted:
            self.pawn.probe_key(key,0.,False)
        for key in wanted-self.held:
            self.pawn.probe_key(key,1.,True)
        self.held = wanted

    def advance(self, result):
        self.keys([])
        self.events.append(dict(step=self.plan[self.index][1], elapsed=time.monotonic()-self.started, state=state(), result=result))
        self.index += 1
        self.step_started = time.monotonic()
        self.settled = None
        if self.index >= len(self.plan):
            final=state()
            assert final['walking'] and final['walkable_floor'] and final['move_binding_samples'] > 100 and final['look_binding_samples'] > 0
            self.finish()

    def finish(self, error=None):
        self.keys([])
        self.done = True
        self.finished = time.monotonic()
        self.error = error
        u.unregister_slate_post_tick_callback(self.handle)
        (OUT/(self.output_prefix+'runtime-verification.json')).write_text(json.dumps(self.report(),indent=2))
        (OUT/(self.output_prefix+'runtime-samples.json')).write_text(json.dumps(self.samples,indent=2))

    def report(self):
        return dict(done=self.done, passed=self.done and not self.error, error=self.error,
                    elapsed=(self.finished or time.monotonic())-self.started, step=self.plan[min(self.index,len(self.plan)-1)][1],
                    input_method='FInputKeyEventArgs through PlayerController; real CharacterMovement ticks; no teleport or direct movement calls',
                    initial=self.initial, events=self.events, sample_count=len(self.samples))

    def tick(self, dt):
        try:
            self.update()
        except Exception:
            self.finish(traceback.format_exc())

    def update(self):
        now=time.monotonic()
        s=state()
        if now-self.last_sample > .1:
            self.samples.append(dict(t=now-self.started,step=self.plan[self.index][1],**s))
            self.last_sample=now
        age=now-self.step_started
        step=self.plan[self.index]
        kind,name=step[:2]
        assert age < 40, 'Timed out at '+name
        if kind in ('wait','capture'):
            self.keys([])
            if self.settled is None:
                self.settled=now
                if kind=='capture':
                    u.SystemLibrary.execute_console_command(self.world,'HighResShot 1 filename="'+str(OUT/(name+'.png'))+'"')
            if age > step[2]:
                assert s['walking'] and s['walkable_floor']
                self.advance('grounded')
        elif kind=='mouse':
            if self.settled is None:
                self.before_rotation=s['rotation']
                self.pawn.probe_key('MouseX',float(step[2]),True)
                self.pawn.probe_key('MouseY',float(step[3]),True)
                self.settled=now
            if age > .5:
                axis=1 if step[2] else 0
                assert abs(s['rotation'][axis]-self.before_rotation[axis]) > 1, 'Mouse binding did not rotate camera'
                self.advance(dict(before=self.before_rotation,after=s['rotation']))
        elif kind=='look':
            pitch,yaw,_=s['rotation']
            yaw=(yaw-step[2]+180)%360-180
            pitch=(pitch-step[3]+180)%360-180
            if abs(yaw)<.1 and abs(pitch)<.1:
                self.advance('look restored by mouse input')
            else:
                self.pawn.probe_key('MouseX',float(-yaw/2.5),True)
                self.pawn.probe_key('MouseY',float(-pitch/2.5),True)
        elif kind=='move':
            x,y,z=s['location']; vx,vy,vz=s['velocity']
            dx,dy=step[2]-x,step[3]-y
            if abs(dx)<45 and abs(dy)<45 and abs(vx)+abs(vy)<5:
                self.advance(dict(target=step[2:],distance_cm=math.hypot(dx,dy)))
                return
            keys=[]
            for error,velocity,positive,negative in [(dx,vx,'W','S'),(dy,vy,'D','A')]:
                stop=10+velocity*velocity/3600 if error*velocity>0 else 10
                if abs(error)>stop:
                    keys.append(positive if error>0 else negative)
            self.keys(keys)
        elif kind=='hold':
            self.keys([step[2]])
            if age > step[3]:
                x,y,z=s['location']
                assert abs(s['velocity'][1])<1, 'Collision did not stop movement'
                if name=='wall_collision':
                    # The 20 cm inward plinth is the first blocking wall surface.
                    assert 1040<y<1050, s
                else:
                    # Capsule may step onto the 30 cm base before meeting the shaft.
                    assert 390<y<420, s
                self.advance('held D stopped against blocking geometry')
        elif kind=='jump':
            if self.settled is None:
                self.base_z=s['location'][2]
                self.max_z=self.base_z
                self.settled=now
                self.keys(['SpaceBar'])
            if age>.15:
                self.keys([])
            self.max_z=max(self.max_z,s['location'][2])
            self.fell=self.fell or (s['falling'] and s['velocity'][2]<-1)
            if age>step[2]:
                assert self.max_z-self.base_z > 20 and self.fell and s['walking'] and s['walkable_floor'], s
                assert abs(s['location'][2]-self.base_z)<3
                self.advance(dict(rise_cm=self.max_z-self.base_z,falling_with_negative_z_velocity=self.fell,landed=True))

def start(views=False):
    global _run
    assert _run is None or _run.done, 'Verification already active'
    _run=WalkCheck(views)
    return 'PIE key-input verification started; collect status to completion before ending the run.'

def status():
    return _run.report() if _run else dict(done=True,error='Not started',passed=False)
