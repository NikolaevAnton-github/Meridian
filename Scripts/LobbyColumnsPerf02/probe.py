"""Bounded, transient PIE evidence. Keep editor visible; collect the result before handoff."""
import json
import time
import traceback
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyColumnsPerf02'

def world():
    w = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert w
    return w

def columns():
    return [a for a in u.GameplayStatics.get_all_actors_of_class(world(), u.Actor)
            if a.actor_has_tag('LobbyColumns01')]

def state():
    rows = []
    for a in columns():
        p = a.get_actor_location()
        rows.append(dict(actor=a.get_name(), location=[p.x,p.y,p.z],
            prop=json.loads(a.get_component_by_class(u.NGDPropComponent).get_state()),
            cladding=json.loads(a.get_component_by_class(u.DemoColumnCladding).get_state())))
    actors = u.GameplayStatics.get_all_actors_of_class(world(), u.Actor)
    shared = [c for a in actors if a.actor_has_tag('LobbyFacingRenderOnly')
              for c in a.get_components_by_class(u.InstancedStaticMeshComponent)]
    query = [c for a in columns() for c in a.get_components_by_class(u.InstancedStaticMeshComponent)]
    simulation=u.GameplayStatics.get_actor_of_class(world(),u.CombatProjectileWorld)
    return dict(columns=rows, blockers=json.loads(simulation.get_combat_state()), shared_components=len(shared),
        shared_instances=sum(c.get_instance_count() for c in shared),
        column_components=len(query), visible_column_components=sum(c.is_visible() for c in query),
        rifle=json.loads(u.GameplayStatics.get_player_pawn(world(),0).get_component_by_class(u.CombatRifleComponent).get_rifle_state()))

def console(command):
    u.SystemLibrary.execute_console_command(world(), command)

def view(reverse=False):
    pawn = u.GameplayStatics.get_player_pawn(world(),0)
    pawn.set_actor_location(u.Vector(2850 if reverse else -2850,-105,90.15),False,True)
    u.GameplayStatics.get_player_controller(world(),0).set_control_rotation(u.Rotator(pitch=0,yaw=180 if reverse else 0,roll=0))

def setup(mode):
    # These variables are recorded/restored by the outer session helper.
    console('msq.Lobby.SharedFacing ' + str(mode))
    console('t.MaxFPS 0')
    console('r.VSync 0')
    u.get_default_object(u.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings')).set_editor_property('bThrottleCPUWhenNotForeground',False)
    view()

def run(name, pilot=False, screenshots=False):
    path = OUT / (name + '.json')
    assert not path.exists()
    events = []
    def event(t, op, *args): events.append((t,op,args))
    event(0,'view')
    event(1,'sample','initial')
    event(3,'csv','intact')
    event(9,'stop')
    event(10,'sample','intact')
    event(10.3,'capture','intact')
    event(11.5,'csv','firing')
    targets = [(-2100,-680),(-1260,-680),(-1260,-240)] if pilot else [(-2100,-680),(-420,-680),(420,-680)]
    for j,(x,y) in enumerate(targets):
        t = 12 + 6*j
        event(t,'position',[x,y+520,90.15])
        event(t+.1,'ammo')
        for k in range(4):
            event(t+.2+1.25*k,'aim',[x-35,y+120,22 if k<2 else 810])
            event(t+.45+1.25*k,'fire',True)
            event(t+.75+1.25*k,'fire',False)
            if k==0: event(t+1.,'sample','first-hit-'+str(j))
        event(t+5.6,'sample','damaged-'+str(j))
    event(30,'stop')
    event(31,'view')
    event(43,'sample','settled-before')
    event(44,'csv','settled')
    event(50,'stop')
    event(51,'sample','settled')
    event(51.3,'capture','settled')
    event(52,'key','F6',True)
    event(52.2,'key','F6',False)
    event(54,'csv','reset')
    event(60,'stop')
    event(61,'sample','reset')
    event(61.3,'capture','reset')
    event(62,'view',True)
    event(64,'csv','reverse')
    event(70,'stop')
    event(71,'sample','reverse')
    event(71.3,'capture','reverse')
    event(72,'view')
    # High-res screenshots can disturb render-thread timing across captures.
    # Collect comparable pictures in a separate run, never inside timing runs.
    if screenshots: events=[e for e in events if e[1] not in ('csv','stop')]
    else: events=[e for e in events if e[1]!='capture']
    return timeline(name,events,73)

def transitions(name):
    actors=columns()
    a=next(a for a in actors if abs(a.get_actor_location().x+2100)<1 and a.get_actor_location().y<0)
    p=a.get_actor_location()
    events=[(0,'sample',('before',)),(1,'move',(a,[p.x+50,p.y,p.z])),
        (2,'sample',('moved',)),(3,'move',(a,[p.x+2200,p.y,p.z])),
        (4,'sample',('cross-cell',)),(5,'move',(a,[p.x,p.y,p.z])),
        (6,'sample',('restored',)),(7,'strain',(a,)),(10,'sample',('external-fracture',)),
        (11,'key',('F6',True)),(11.2,'key',('F6',False)),(13,'sample',('reset',))]
    return timeline(name,events,14)

def first_hits(name):
    events=[(0,'sample',('before',))]
    # Both columns share a render group. The second shot exercises a neighbour
    # after the first column's query/render instance swap-removal.
    for j,x in enumerate([-420,420,-420]):
        t=1+5*j
        events.extend([(t,'position',([x,-160,90.15],)),(t+.1,'ammo',()),
            (t+.2,'aim',([x-35,-560,410],)),(t+1.2,'trace',([x-35,-560,410],)),
            (t+1.5,'fire',(True,)),(t+1.8,'fire',(False,)),(t+3.,'sample',('shot-'+str(j),))])
    events.extend([(17,'key',('F6',True)),(17.2,'key',('F6',False)),(19,'sample',('reset',))])
    return timeline(name,events,20)

def damaged_transitions(name):
    a=next(a for a in columns() if abs(a.get_actor_location().x+420)<1 and a.get_actor_location().y<0)
    p=a.get_actor_location()
    e=[(0,'sample',('before',)),(.1,'position',([-420,-160,90.15],)),(.2,'ammo',()),
       (.4,'aim',([-455,-560,410],)),(2,'fire',(True,)),(2.3,'fire',(False,)),
       (3,'sample',('damaged',)),(4,'move',(a,[p.x+50,p.y,p.z])),(5,'sample',('moved',)),
       (6,'move',(a,[p.x+2200,p.y,p.z])),(7,'sample',('cross-cell',)),
       (8,'move',(a,[p.x,p.y,p.z])),(9,'sample',('restored',)),
       (10,'strain',(a,)),(12,'sample',('external-fracture',)),
       (13,'key',('F6',True)),(13.2,'key',('F6',False)),(15,'sample',('reset',))]
    return timeline(name,e,16)

def timeline(name,events,duration,expected_shots=12):
    path=OUT/(name+'.json')
    assert not path.exists()
    events.sort(key=lambda e:e[0])
    report=dict(name=name,samples={},delta=[],events=[],expected_shots=expected_shots)
    index=0; started=time.monotonic(); handle=None; in_tick=False
    def tick(delta):
        nonlocal index,handle,in_tick
        if in_tick: return
        in_tick=True
        elapsed=time.monotonic()-started
        report['delta'].append(delta)
        try:
            w=world(); pawn=u.GameplayStatics.get_player_pawn(w,0)
            while index<len(events) and elapsed>=events[index][0]:
                at,op,args=events[index]
                if op=='sample': report['samples'][args[0]]=state()
                elif op=='console': console(args[0])
                elif op=='view': view(*args)
                elif op=='position': pawn.set_actor_location(u.Vector(*args[0]),False,True)
                elif op=='aim': assert u.NGDTools.aim_player(w,u.Vector(*args[0]))
                elif op=='trace':
                    start=u.GameplayStatics.get_player_camera_manager(w,0).get_camera_location()
                    point=u.Vector(*args[0]); end=point+(point-start).normal()*30.
                    report.setdefault('traces',[]).append(json.loads(u.NGDTools.sweep(w,start,end,.25)))
                elif op=='ammo': assert pawn.get_component_by_class(u.CombatRifleComponent).probe_ammo(30,90)
                elif op=='fire': assert u.NGDTools.rifle_input(w,args[0])
                elif op=='key': pawn.probe_key(args[0],1. if args[1] else 0.,args[1])
                elif op=='move': args[0].set_actor_location(u.Vector(*args[1]),False,True)
                elif op=='strain':
                    gc=args[0].get_component_by_class(u.GeometryCollectionComponent)
                    gc.apply_external_strain(gc.get_root_index(),args[0].get_actor_location(),1000.,0,1.,1.e9)
                elif op=='csv':
                    console('CsvProfile STARTFILE=LobbyColumnsPerf02-'+name+'-'+args[0]+'.csv')
                    console('CsvProfile START')
                elif op=='stop': console('CsvProfile STOP')
                elif op=='capture': u.AutomationLibrary.take_high_res_screenshot(1280,720,str(OUT/(name+'-'+args[0]+'.png')))
                else: raise ValueError(op)
                report['events'].append(dict(at=at,actual=elapsed,op=op))
                index+=1
            if elapsed>=duration:
                u.NGDTools.rifle_input(w,False)
                report['complete']=True
                path.write_text(json.dumps(report,indent=2))
                u.unregister_slate_post_tick_callback(handle)
        except Exception:
            report['error']=traceback.format_exc()
            try: u.NGDTools.rifle_input(world(),False); console('CsvProfile STOP')
            except Exception: pass
            path.write_text(json.dumps(report,indent=2))
            u.unregister_slate_post_tick_callback(handle)
        finally:
            in_tick=False
    handle=u.register_slate_post_tick_callback(tick)
    print(json.dumps(dict(scheduled=name,duration=duration)))
