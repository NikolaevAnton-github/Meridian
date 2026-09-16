"""Guarded complete-batch material-only Unreal operations."""
import json,types,importlib
import unreal as u
from stage1_tools import state
from materialscomplete01_evidence import ROOT,OUT,CURRENT,ASSETS,digest
MAP='/Game/Maps/'+CURRENT
SOURCE=MAP
legacy=types.ModuleType('complete_property_validator')
legacy.__file__=str(ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py')
exec(compile((ROOT/'Scripts/OpeningLobby/materialintegration01_unreal.py').read_text(),legacy.__file__,'exec'),legacy.__dict__)
legacy.OUT=OUT;legacy.MAP=MAP;legacy.SOURCE=MAP;legacy.ASSETS=ASSETS
guard=legacy.guard;write=legacy.write;actors=legacy.actors;snapshot=legacy.snapshot;settings=legacy.settings
def baseline():
    guard(True,True)
    for r in json.loads((OUT/'protected-before.json').read_text())['entries']:
        if r['path']=='Content/Maps/'+CURRENT+'.umap' and (OUT/'bindings.json').exists():continue
        assert digest(ROOT/r['path'])==r['sha256'],r['path']
    return state()
def action(operation,argument=''):
    if operation=='state':return state()
    if operation=='snapshot':
        assert argument in ['Before','Final','Restored','RestoredFinal'];assert not (OUT/argument/'all-properties.json').exists()
        return snapshot(argument,True)
    if operation=='bind':
        baseline();assert not (OUT/'bindings.json').exists()
        rows=json.loads((OUT/'coverage-plan.json').read_text())['rows']
        lookup={(a.get_name(),c.get_name()):(a,c) for a in actors() for c in a.get_components_by_class(u.MeshComponent)}
        for r in rows:
            a,c=lookup[(r['actor'],r['component'])]
            assert a.get_actor_label()==r['label'] and c.get_material(0).get_path_name()==r['old']
            assert [m.get_path_name() if m else None for m in c.get_editor_property('override_materials')]==r['source_overrides']
            assert u.load_asset(r['new'])
        changed=[r for r in rows if not r['preserved']];assert len(changed)==90
        for r in changed:lookup[(r['actor'],r['component'])][1].set_material(0,u.load_asset(r['new']))
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
        return write('bindings',dict(rows=changed,changed=90,state=guard(True,True)))
    if operation=='reopen':
        baseline();assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        return snapshot('Final',True)
    if operation=='live_audit':
        baseline();records={};lib=u.MaterialEditingLibrary
        paths=sorted({c.get_material(i).get_path_name() for a in actors() for c in a.get_components_by_class(u.MeshComponent) for i in range(c.get_num_materials())})
        assert len(paths)==7,paths
        opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
        allowed=['/Game/OpeningLobby/'+n+'/' for n in ['PainterStone01','PainterFloor01','PainterMetal01','MaterialsComplete01']]
        for path in paths:
            assert any(path.startswith(p) for p in allowed),path
            m=u.load_asset(path);stats=lib.get_statistics(m)
            assert stats.num_pixel_shader_instructions>0 and stats.num_vertex_shader_instructions>0
            deps=[str(d) for d in (u.AssetRegistryHelpers.get_asset_registry().get_dependencies(m.get_outermost().get_name(),opts) or [])]
            assert all(not d.startswith('/Game/') or any(d.startswith(p) for p in allowed) for d in deps)
            records[path]=dict(statistics={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']},dependencies=deps,textures=[t.get_path_name() for t in lib.get_used_textures(m)],blend_mode=str(m.get_editor_property('blend_mode')))
        return write('live-material-audit',dict(passed=True,materials=records,effective_material_count=len(paths),state=guard(True,True)))
    if operation in ['ceiling','glass','audit','capabilities','reload_graphs','glass_revision']:
        baseline()
        import materialscomplete01_material as m
        return getattr(importlib.reload(m),operation)()
    if operation.startswith('movement_'):
        import materialscomplete01_movement as movement
        return getattr(movement,operation[9:])()
    if operation.startswith('capture_'):
        import materialscomplete01_capture as c
        if operation=='capture_prepare':c=importlib.reload(c)
        return c.run(operation[8:],argument)
    raise ValueError(operation)
