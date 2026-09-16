"""Correction01-only native operations; previous modules used read-only."""
import json, types, importlib
from pathlib import Path
import unreal as u
from stage1_tools import state
from architecture01_lightstudy import props
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/MaterialsComplete01/Worker/Correction01'
ASSETS='/Game/OpeningLobby/MaterialsComplete01/Correction01'
MAP='/Game/Maps/L_OpeningLobby_PainterStone01'
SOURCE=MAP
legacy=types.ModuleType('correction_properties')
p=ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py'
legacy.__file__=str(p)
exec(compile(p.read_text(),str(p),'exec'),legacy.__dict__)
legacy.OUT=OUT;legacy.MAP=MAP;legacy.SOURCE=MAP;legacy.ASSETS=ASSETS
guard=legacy.guard;write=legacy.write;snapshot=legacy.snapshot;actors=legacy.actors;settings=legacy.settings
LIB=u.MaterialEditingLibrary

def diagnose():
    guard(True,True)
    schemas={};records={}
    for role in ['Fixed','Leaf']:
        m=u.load_asset('/Game/OpeningLobby/MaterialsComplete01/Materials/M_MC01_Glass'+role)
        records[role]=dict(material=props(m,schemas),editor_data=props(m.get_editor_property('editor_only_data'),schemas),nodes={n.get_name():dict(properties=props(n,schemas),inputs=list(LIB.get_material_expression_input_names(n)),connected=[c.get_name() if c else None for c in LIB.get_inputs_for_material_expression(m,n)]) for n in LIB.get_material_expressions(m)})
    records['geometry']=[]
    for a in actors():
        if any(x in a.get_actor_label() for x in ['Glazing','Sidelight','DoorLeaf','Overlight']):
            for c in a.get_components_by_class(u.StaticMeshComponent):
                mesh=c.get_editor_property('static_mesh')
                records['geometry'].append(dict(label=a.get_actor_label(),transform=str(a.get_actor_transform()),bounds=str(a.get_actor_bounds(False)),mesh=mesh.get_path_name(),mesh_bounds=str(mesh.get_bounds()),component=props(c,schemas)))
    write('diagnosis-live',records);write('diagnosis-schemas',schemas)
    return dict(roles=['Fixed','Leaf'],panes=len(records['geometry']),state=state())

def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='snapshot':
        assert not (OUT/argument/'all-properties.json').exists()
        return snapshot(argument,True)
    if operation=='diagnose':return diagnose()
    if operation.startswith('capture_'):
        import materialscomplete01_correction_capture as c
        if operation=='capture_prepare':c=importlib.reload(c)
        return c.run(operation[8:],argument)
    import materialscomplete01_correction_material as m
    return getattr(importlib.reload(m),operation)(argument)
