"""Same native camera tools, new outputs, no global cvar changes."""
import types,json
import unreal as u
from materialscomplete01_optics_unreal import ROOT,OUT,MAP,SOURCE,guard,write,settings,path_evidence
p=ROOT/'Scripts/OpeningLobby/materialscomplete01_capture.py'
s=p.read_text().replace('from materialscomplete01_unreal import','from materialscomplete01_optics_unreal import')
s=s.replace("'Final','Transmission'","'Final','Transmission','CurrentOn','NewOff','NewOn','Hidden','Opaque'")
# The inherited Slate cvar workaround is not permitted in Correction03.
s=s.replace("u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Slate.bAllowThrottling 0')",'pass')
s=s.replace("u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'Slate.bAllowThrottling '+str(throttle))",'pass')
base=types.ModuleType('optics_capture');exec(compile(s,str(p),'exec'),base.__dict__)
saved=[]
pane='true glass'
def run(op,arg):
    global saved,pane
    folder,_,view=arg.partition(':')
    if op=='control':
        guard(True,True,pie=True);assert not saved and view in ['hidden','opaque']
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor):
            c=a.static_mesh_component
            if '/Correction03/M_C03_Glass' in c.get_material(0).get_path_name():
                if view=='hidden':saved.append((c,'visibility',c.get_editor_property('visible')));c.set_visibility(False)
                else:saved.append((c,'material',c.get_material(0)));c.set_material(0,u.load_asset('/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01'))
        assert len(saved)==6;pane=view
        return write(folder+'/control-start',dict(control=view,components=[c.get_path_name() for c,k,v in saved],scope='PIE only; no save'))
    if op=='control_restore':
        guard(True,True,pie=True);assert len(saved)==6
        for c,k,v in saved:
            if k=='visibility':c.set_visibility(v);assert c.get_editor_property('visible')==v
            else:c.set_material(0,v);assert c.get_material(0)==v
        saved=[];pane='true glass';return write(folder+'/control-restored',dict(passed=True))
    if op=='restore':assert not saved
    result=base.run(op,arg)
    if op=='shoot':
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        result.update(optical_path=path_evidence(world),environment=dict(support='unchanged Correction02 far field',pane_state=pane),lighting='Existing lights/exposure and global renderer unchanged. Explicit local front-layer flags recorded separately.')
        (OUT/folder/(view+'-camera.json')).write_text(json.dumps(result,indent=2))
    return result
