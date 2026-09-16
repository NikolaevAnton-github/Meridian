"""Matched native views with verified ticks and reversible runtime diagnostics."""
import types,json
import unreal as u
from materialscomplete01_unreal import ROOT,OUT,MAP,guard,write
p=ROOT/'Scripts/OpeningLobby/paintermetal01_capture.py'
s=p.read_text().replace('from paintermetal01_unreal import','from materialscomplete01_unreal import')
s=s.replace("['Before','Trial01','Final']","['Before','Trial01','Final','Transmission']")
base=types.ModuleType('complete_capture');exec(compile(s,str(p),'exec'),base.__dict__)
base.cap.VIEWS={'entrance-90':(-1850,0,180,12),'inner-90':(1850,0,0,3),
 'side-aisle-90':(-1150,980,0,0),'bays-context-90':(-700,200,35,15),
 'stone-oblique-90':(-1500,420,145,18),'ceiling-up-90':(-500,180,20,55),
 'soffit-up-90':(-1710,925,165,35),'entrance-glass-90':(-2590,260,188,18),
 'checkpoint-90':(-1690,170,198,-12),'elevator-90':(2620,-170,22,0),
 'whole-hall-90':(1800,0,180,6),'transmission-90':(-3180,0,0,8),
 'without-panes-90':(-3180,0,0,8),'opaque-control-90':(-3180,0,0,8),'entrance-whole-90':(-1450,0,180,24),
 'movement-start-90':(0,0,0,0)}
throttle=None
hidden=None
diagnostic_pose=None
opaque=None
def runtime():return base.runtime()
def run(op,arg):
    global throttle,hidden,diagnostic_pose,opaque
    folder,_,view=arg.partition(':')
    if op=='prepare':
        result=base.run(op,arg)
        throttle=u.SystemLibrary.get_console_variable_int_value('Slate.bAllowThrottling')
        write(folder+'/slate-before',dict(value=throttle))
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Slate.bAllowThrottling 0')
        return result
    if op=='restore':
        guard(True,True)
        assert hidden is None
        u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Slate.bAllowThrottling '+str(throttle))
        return base.run(op,arg)
    if op=='camera' and folder=='Transmission':
        guard(True,True,pie=True)
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn=u.GameplayStatics.get_player_pawn(world,0);movement=pawn.get_component_by_class(u.CharacterMovementComponent)
        if diagnostic_pose is None:diagnostic_pose=(pawn.get_actor_transform(),movement.movement_mode)
        movement.set_movement_mode(u.MovementMode.MOVE_FLYING)
        result=base.run(op,arg)
        pawn.set_actor_location(u.Vector(-3180,0,90),False,True)
        result['pose_scope']='Diagnostic only, temporarily flying pawn beyond entrance to view existing hall through actual glass; camera eye remains 172 cm. No scenery or light added.'
        (OUT/folder/(view+'-camera.json')).write_text(json.dumps(result,indent=2))
        return result
    if op=='diagnostic_restore':
        guard(True,True,pie=True);assert diagnostic_pose is not None
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();pawn=u.GameplayStatics.get_player_pawn(world,0)
        pawn.set_actor_transform(diagnostic_pose[0],False,True)
        pawn.get_component_by_class(u.CharacterMovementComponent).set_movement_mode(diagnostic_pose[1])
        diagnostic_pose=None
        return write('Transmission/pose-restored',dict(passed=True))
    if op=='glass_hidden':
        guard(True,True,pie=True);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        if view=='on':
            assert hidden is None
            hidden=[]
            for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor):
                c=a.static_mesh_component
                if '/MaterialsComplete01/Materials/M_MC01_Glass' in c.get_material(0).get_path_name():
                    hidden.append((c,c.get_editor_property('visible')));c.set_visibility(False)
            assert len(hidden)==6
            return write('Transmission/temporarily-hidden',dict(components=[c.get_path_name() for c,v in hidden],scope='PIE only; compare actual pane transmission with same existing scene through absent panes; no backing, light, geometry or texture created.'))
        assert hidden is not None
        for c,v in hidden:c.set_visibility(v)
        hidden=None;return write('Transmission/restored',dict(passed=True))
    if op=='opaque_control':
        guard(True,True,pie=True);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        if view=='on':
            assert opaque is None;opaque=[]
            for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor):
                c=a.static_mesh_component
                if '/MaterialsComplete01/Materials/M_MC01_Glass' in c.get_material(0).get_path_name():opaque.append((c,c.get_material(0)))
            assert len(opaque)==6
            stone=u.load_asset('/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01')
            for c,m in opaque:c.set_material(0,stone)
            return write('Transmission/opaque-control-start',dict(components=[c.get_path_name() for c,m in opaque],scope='PIE-only negative transmission control: accepted opaque stone temporarily on the same six pane meshes. No asset/scene save or geometry/light changes.'))
        assert opaque is not None
        for c,m in opaque:c.set_material(0,m)
        opaque=None;return write('Transmission/opaque-control-restored',dict(passed=True))
    result=base.run(op,arg)
    if op=='shoot' and folder=='Transmission':
        result['pose_scope']='Transmission diagnostic, temporary exterior flying pawn at 172 cm eye height. Existing hall is viewed through the leaf and fixed panes. No standing/walkthrough claim for this diagnostic.'
        result['diagnostic_state']='PIE-only opaque negative control on six pane meshes' if opaque is not None else 'Six panes temporarily invisible in PIE' if hidden is not None else 'All six final optical panes visible'
        (OUT/folder/(view+'-camera.json')).write_text(json.dumps(result,indent=2))
    return result
