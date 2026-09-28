"""Verify placement, unchanged reference/unrelated actors, and structural bounds."""
import json
import re
from pathlib import Path
import unreal as u

OUT=Path('D:/devgames/MeridianSquad/Saved/LobbyColumns01')
before=json.loads((OUT/'before.json').read_text())
source=json.loads((OUT/'source.json').read_text())
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
by_path={a.get_path_name():a for a in actors}
changed={r['label'] for r in source['columns']}|{'Floor','FloorStrip_-1','FloorStrip_1','RC01_ReinforcedColumn'}
def vec(v): return [v.x,v.y,v.z]
def normalize(s): return re.sub(r'0x[0-9A-Fa-f]+','PTR',s)
errors=[]
for row in before['actors']:
    if row['label'] in changed: continue
    a=by_path.get(row['path'])
    assert a, row['label']
    current=dict(label=a.get_actor_label(),location=vec(a.get_actor_location()),scale=vec(a.get_actor_scale3d()),rotation=str(a.get_actor_rotation()),tags=[str(t) for t in a.tags],components=[])
    for m in a.get_components_by_class(u.StaticMeshComponent):
        current['components'].append(dict(name=m.get_name(),mesh=m.static_mesh.get_path_name() if m.static_mesh else None,materials=[x.get_path_name() if x else None for x in m.get_materials()],transform=str(m.get_world_transform())))
    for key,value in current.items():
        if normalize(json.dumps(value,sort_keys=True)) != normalize(json.dumps(row[key],sort_keys=True)):
            errors.append([row['label'],key])
assert not errors, errors
columns=[a for a in actors if a.actor_has_tag('LobbyColumns01')]
assert len(columns)==16
details=[]
for a in columns:
    gc=a.get_component_by_class(u.GeometryCollectionComponent)
    center,extent,_=u.SystemLibrary.get_component_bounds(gc)
    assert abs(center.z-extent.z)<.02 and abs(center.z+extent.z-840)<.02,(a.get_actor_label(),center,extent)
    rebar=next(m for m in a.get_components_by_class(u.StaticMeshComponent) if m.static_mesh and m.static_mesh.get_name()=='SM_ConcretePillar_Square_5m_REBAR')
    c,e,_=u.SystemLibrary.get_component_bounds(rebar)
    assert c.z-e.z<0 and c.z-e.z>=-40 and abs(c.z+e.z-840)<1,(c,e)
    cladding=json.loads(a.get_component_by_class(u.DemoColumnCladding).get_state())
    details.append(dict(label=a.get_actor_label(),concrete_z=[center.z-extent.z,center.z+extent.z],rebar_z=[c.z-e.z,c.z+e.z],cladding=cladding))
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not u.EditorLoadingAndSavingUtils.get_dirty_content_packages()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
floor_checks=[]
for row in source['columns']+[dict(label='unchanged_finish',location=[0,600,0])]:
    x,y,_=row['location']
    x+=60; y+=-20 if y>0 else 20
    hit=u.SystemLibrary.line_trace_single(world,u.Vector(x,y,50),u.Vector(x,y,-10),u.TraceTypeQuery.ECC_VISIBILITY,True,columns,u.DrawDebugTrace.NONE,True).to_dict()
    assert hit['blocking_hit'] and hit['hit_actor'].get_actor_label()=='Floor',row['label']
    material,section=hit['hit_component'].get_material_from_collision_face_index(hit['face_index'])
    expected='M_PainterFloor01_Floor' if row['label']=='unchanged_finish' else 'MI_ConcreteInner_5m'
    assert material.get_name()==expected,(row['label'],material.get_path_name())
    assert abs(hit['impact_point'].z)<.01
    floor_checks.append(dict(column=row['label'],material=material.get_path_name(),z=hit['impact_point'].z))
result=dict(columns=details,floor_checks=floor_checks,reference_unchanged=True,unrelated_actors_unchanged=True,dirty_packages=0)
(OUT/'scene-verified.json').write_text(json.dumps(result,indent=2))
print(json.dumps(dict(columns=len(columns),reference_unchanged=True,unrelated_actors_unchanged=True,rebar_z=details[0]['rebar_z'])))
