"""Matched standing views and PIE-only controls with exact restoration."""
import types,json
import unreal as u
from materialscomplete01_support_unreal import ROOT,OUT,MAP,SOURCE,guard,write,settings,LABEL
p=ROOT/'Scripts/OpeningLobby/materialscomplete01_capture.py'
s=p.read_text().replace('from materialscomplete01_unreal import','from materialscomplete01_support_unreal import')
s=s.replace('/MaterialsComplete01/Materials/M_MC01_Glass','/MaterialsComplete01/Correction01/M_C01_Glass')
s=s.replace("'Final','Transmission'","'Final','Transmission','SupportOff','Setup01','Setup02','Hidden','Opaque'")
base=types.ModuleType('support_capture');exec(compile(s,str(p),'exec'),base.__dict__)
saved=[]
support='on'
pane='true glass'
def run(op,arg):
    global saved,support,pane
    folder,_,view=arg.partition(':')
    if op=='control':
        guard(True,True,pie=True);assert not saved
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor):
            c=a.static_mesh_component
            if view=='support_off' and a.get_actor_label()==LABEL:
                saved.append((c,'visibility',c.get_editor_property('visible')));c.set_visibility(False)
            elif view in ['hidden','opaque'] and '/Correction01/M_C01_Glass' in c.get_material(0).get_path_name():
                if view=='hidden':saved.append((c,'visibility',c.get_editor_property('visible')));c.set_visibility(False)
                else:saved.append((c,'material',c.get_material(0)));c.set_material(0,u.load_asset('/Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01'))
        assert len(saved)==(1 if view=='support_off' else 6)
        support='off' if view=='support_off' else 'on';pane=view if view in ['hidden','opaque'] else 'true glass'
        return write(folder+'/control-start',dict(control=view,components=[c.get_path_name() for c,k,v in saved],scope='PIE only; no save'))
    if op=='control_restore':
        guard(True,True,pie=True)
        assert saved
        for c,k,v in saved:
            if k=='visibility':c.set_visibility(v);assert c.get_editor_property('visible')==v
            else:c.set_material(0,v);assert c.get_material(0)==v
        saved=[];support='on';pane='true glass'
        return write(folder+'/control-restored',dict(passed=True))
    if op=='restore':assert not saved
    result=base.run(op,arg)
    if op=='shoot':
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        reflections=u.GameplayStatics.get_all_actors_of_class(world,u.SphereReflectionCapture)
        result.update(environment=dict(support=support,setup='Setup02' if reflections else 'Setup01',new_support_actors=2 if reflections else 1,new_lights=0,reflection_actors=len(reflections),pane_state=pane),lighting='Existing lights/exposure/renderer unchanged. Explicit provisional neutral far-field exception; support-off/on are different environments.')
        (OUT/folder/(view+'-camera.json')).write_text(json.dumps(result,indent=2))
    return result
