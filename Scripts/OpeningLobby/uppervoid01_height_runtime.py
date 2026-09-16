"""Bounded real runtime sampling and input walkthrough; no permanent defaults."""
import json,time,statistics,traceback
import unreal as u
from uppervoid01_height_unreal import ROOT,OUT,MAP,guard,write,settings
from stage1_tools import state
from verify_lobby import WalkCheck
sample=None
walkrun=None
class PerfSample:
    def __init__(self,tag):
        self.tag=tag;self.start=time.monotonic();self.rows=[];self.done=False;self.error=None
        self.world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pc=u.GameplayStatics.get_player_controller(self.world,0)
        names=['r.VSync','t.MaxFPS','r.ScreenPercentage','r.DynamicRes.OperationMode','r.AntiAliasingMethod','sg.ViewDistanceQuality','sg.ShadowQuality','sg.GlobalIlluminationQuality','sg.ReflectionQuality','sg.PostProcessQuality','sg.TextureQuality','sg.EffectsQuality','sg.ShadingQuality','Slate.bAllowThrottling','r.Streamline.DLSSG.Enable','r.FidelityFX.FI.Enabled']
        self.config=dict(renderer=settings(),cvars={n:u.SystemLibrary.get_console_variable_float_value(n) for n in names},viewport=str(pc.get_viewport_size()),state=state(),frame_generation='No frame generation plugin enabled in project; unavailable plugin cvars read as zero',cpu_gpu='Per-stage CPU/GPU timings unavailable through this bounded Python probe; wall/game-frame timing only',screenshots_during_sample=False)
        self.handle=u.register_slate_post_tick_callback(self.tick)
    def tick(self,dt):
        age=time.monotonic()-self.start
        if age>=5:self.rows.append(dict(t=age,slate_dt=float(dt),game_dt=u.GameplayStatics.get_world_delta_seconds(self.world),world_seconds=u.GameplayStatics.get_time_seconds(self.world)))
        if age>=25:
            u.unregister_slate_post_tick_callback(self.handle);self.done=True
            vals=[r['game_dt'] for r in self.rows];wall=[r['slate_dt'] for r in self.rows]
            value=dict(passed=True,tag=self.tag,warmup_seconds=5,sample_seconds=age-5,frames=len(vals),fps=len(vals)/sum(vals),mean_frame_ms=statistics.mean(vals)*1000,p95_frame_ms=sorted(vals)[int(len(vals)*.95)]*1000,slate_mean_ms=statistics.mean(wall)*1000,config=self.config,rows=self.rows)
            write('Performance/'+self.tag,value)

class AtmosphereWalk(WalkCheck):
    def validate_identity(self,s):
        self.target_map=MAP;return super().validate_identity(s)
    def __init__(self):
        folder=OUT/'Movement';folder.mkdir(exist_ok=True)
        super().__init__(output_dir=folder)
        self.config=dict(refresh_held_input=True);self.last_frame=0;self.frames=[]
        self.plan=[('wait','spawn',2),('move','entrance_clear',-2700,-105),('move','lane_align',-2700,465),('move','lane_inbound',-1900,465),('move','axis_align',-1900,0),('move','enter_hall',-1600,0),('move','central_route',0,0),
            ('look','central_up',25,78),('capture','sustained_up',6),('look','floor_look',0,-30),('wait','floor_reflection',3),
            ('look','restore_for_walk',0,0),('move','column_align',-1560,0),('move','near_column',-1560,240),('look','near_column_up',0,75),('capture','close_column_up',6),
            ('look','restore_column',0,0),('move','east_bay_align',-1680,240),('move','cross_to_east',-1680,980),('move','east_route',1680,980),
            ('look','aisle_up',180,65),('capture','aisle_up_hold',6),('look','restore_east',0,0),
            ('move','inner_center',1680,0),('look','turn_back',180,12),('wait','inner_back_view',3),('look','restore_inner',0,0),
            ('move','cross_to_west',1680,-980),('look','west_aisle_up',0,65),('capture','west_aisle_up_hold',6),('look','restore_west',0,0),('move','west_return',-1680,-980),('move','center_return',-1680,0),('move','return_axis',-1900,0),('move','return_lane_align',-1900,-465),('move','return_lane_out',-2700,-465),('move','return',-2800,0)]
    def tick(self,dt):
        if self.done:return
        try:
            age=time.monotonic()-self.started
            if age-self.last_frame>=6:
                self.last_frame=age;n='motion-'+str(len(self.frames)).zfill(3)
                world=self.world;manager=u.GameplayStatics.get_player_camera_manager(world,0)
                row=dict(t=age,world_seconds=u.GameplayStatics.get_time_seconds(world),step=self.plan[self.index][1],state=state(),camera_xyz=str(manager.get_camera_location()),camera_rotation=str(manager.get_camera_rotation()),hfov=manager.get_fov_angle(),resolution=[960,540],image=n+'.png')
                self.frames.append(row)
                u.SystemLibrary.execute_console_command(world,'HighResShot 960x540 filename="'+str(self.out/(n+'.png'))+'"')
            super().tick(dt)
        except Exception:self.finish(traceback.format_exc())
    def finish(self,error=None):
        super().finish(error)
        if hasattr(self,'frames'):write(self.out.relative_to(OUT).as_posix()+'/frame-sequence',dict(frames=self.frames,method='Native time-sampled frames during continuous actual input; no video or interpolated frames'))

def action(operation,argument):
    global sample,walkrun
    if operation=='perf_start':
        guard(True,True,pie=True);assert sample is None or sample.done
        sample=PerfSample(argument);return dict(started=True,warmup=5,sample=20)
    if operation=='perf_status':return dict(done=sample.done,rows=len(sample.rows))
    if operation=='walk_start':
        guard(True,True,pie=True);assert walkrun is None;walkrun=AtmosphereWalk();return dict(started=True,plan=walkrun.plan)
    if operation=='walk_status':return walkrun.report()
    raise ValueError(operation)
