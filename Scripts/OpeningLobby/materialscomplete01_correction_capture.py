"""Read-only reuse of native matched captures with correction output routing."""
import types,json
import unreal as u
from materialscomplete01_correction_unreal import ROOT,OUT,guard,write
p=ROOT/'Scripts/OpeningLobby/materialscomplete01_capture.py'
s=p.read_text().replace('from materialscomplete01_unreal import','from materialscomplete01_correction_unreal import')
s=s.replace("/MaterialsComplete01/Materials/M_MC01_Glass","/MaterialsComplete01/Correction01/M_C01_Glass")
s=s.replace("'Final','Transmission'","'Final','Transmission','InteriorDiagnostic'")
base=types.ModuleType('correction_capture');base.__file__=str(p)
exec(compile(s,str(p),'exec'),base.__dict__)
interior_hidden=None
def run(op,arg):
    global interior_hidden
    folder,_,view=arg.partition(':')
    if op=='interior_hidden':
        guard(True,True,pie=True)
        if view=='on':
            assert interior_hidden is None;interior_hidden=[]
            world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
            for a in u.GameplayStatics.get_all_actors_of_class(world,u.StaticMeshActor):
                c=a.static_mesh_component
                if '/Correction01/M_C01_Glass' in c.get_material(0).get_path_name():
                    interior_hidden.append((c,c.get_editor_property('visible')));c.set_visibility(False)
            assert len(interior_hidden)==6
            return write('InteriorDiagnostic/hidden',dict(components=[c.get_path_name() for c,v in interior_hidden],scope='PIE-only pane removal to diagnose the available existing exterior radiance. No scene save.'))
        assert interior_hidden is not None
        for c,v in interior_hidden:c.set_visibility(v)
        interior_hidden=None
        return write('InteriorDiagnostic/visibility-restored',dict(passed=True))
    if op=='restore':assert interior_hidden is None
    result=base.run(op,arg)
    if op=='shoot' and folder=='InteriorDiagnostic':
        result['pose_scope']='Diagnostic only: same standing interior pose, six panes hidden in PIE to inspect existing scene beyond entrance.'
        result['diagnostic_state']='six panes hidden' if interior_hidden is not None else 'final panes visible'
        (OUT/folder/(view+'-camera.json')).write_text(json.dumps(result,indent=2))
    return result
