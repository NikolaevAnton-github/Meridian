"""Reuse native graph/import/audit implementation with scoped floor bindings."""
import json
import types
import unreal as u
from painterfloor01_unreal import ROOT,OUT,ASSETS,MAP,guard,actors,write

def adapter(family):
    assert family in ['Floor','Strip']
    p=ROOT/'Scripts/OpeningLobby/painterstone01_material.py'
    source=p.read_text().replace('from painterstone01_unreal import','from painterfloor01_unreal import')
    source=source.replace("for channel in (['BaseColor'] if existed else ['BaseColor','ORM','Normal']):","for channel in ['BaseColor','ORM','Normal']:")
    source=source.replace("'M_PainterStone01',ASSETS", "'M_PainterFloor01_"+family+"',ASSETS")
    source=source.replace("'T_PainterStone01_'+channel", "'T_PainterFloor01_"+family+"_'+channel")
    source=source.replace('default_value=240','default_value='+('360' if family=='Floor' else '240'))
    source=source.replace('physical_coverage_cm=240','physical_coverage_cm='+('360' if family=='Floor' else '240'))
    source=source.replace('240 cm matches the native Painter authoring plane','Native Painter export projected over '+('360' if family=='Floor' else '240')+' cm')
    source=source.replace("source='Scripts/OpeningLobby/painterstone01_material.py'","source='Scripts/OpeningLobby/painterfloor01_material.py'")
    module=types.ModuleType('floor_graph_'+family);module.__file__=str(p)
    exec(compile(source,str(p),'exec'),module.__dict__)
    module.SRC=ROOT/'Assets/Source/OpeningLobby/PainterFloor01/Channels'
    module.MAT=ASSETS+'/Materials/M_PainterFloor01_'+family
    module.OUT=OUT/family
    module.write=lambda name,data:write(family+'/'+name,data)
    # Reuse reviewed triangular phase variation for this new color texture.
    module.COLOR_CODE=module.VARIED_COLOR_CODE
    return module

def material():
    guard(True,True)
    return {family:adapter(family).material() for family in ['Floor','Strip']}
def audit():
    guard(True,True)
    return {family:adapter(family).audit() for family in ['Floor','Strip']}
def bind():
    guard(True,True)
    assert not (OUT/'bindings.json').exists()
    targets={'StaticMeshActor_0':('Floor','Floor'),'StaticMeshActor_11':('FloorStrip_-1','Strip'),'StaticMeshActor_22':('FloorStrip_1','Strip')}
    source=json.loads((OUT/'Before/inventory.json').read_text())
    lookup={(a.get_name(),c.get_name()):c for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
    rows=[]
    for row in source:
        if row['actor'] not in targets:continue
        label,family=targets[row['actor']]
        assert row['label']==label and row['component']=='StaticMeshComponent0' and len(row['materials'])==1
        c=lookup[(row['actor'],row['component'])]
        assert c.get_owner().get_actor_label()==label and c.get_material(0).get_path_name()==row['materials'][0]
        mat=u.load_asset(ASSETS+'/Materials/M_PainterFloor01_'+family);assert mat
        rows.append(dict(actor=row['actor'],label=label,component=row['component'],slot=0,old=row['materials'][0],new=mat.get_path_name(),source_overrides=row['overrides']))
        c.set_material(0,mat)
    assert len(rows)==3
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    return write('bindings',dict(rows=rows,state=guard(True,True)))
