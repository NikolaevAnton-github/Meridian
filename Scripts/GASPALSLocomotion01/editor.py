"""Bounded editor inspection/authoring only. Never starts Play or simulation."""
from pathlib import Path
import json
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
OUT = ROOT / 'Saved/GASPALSLocomotion01/Worker'
OUT.mkdir(parents=True, exist_ok=True)

def state():
    assert ROOT.resolve() == Path('D:/devgames/MeridianSquad').resolve()
    sub = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    pie = u.EditorLevelLibrary.get_pie_worlds(False)
    world = sub.get_editor_world()
    return dict(project=str(ROOT), engine=u.SystemLibrary.get_engine_version(),
        map=world.get_path_name() if world else None, pie=[w.get_path_name() for w in pie],
        dirty=[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()] +
              [p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],
        command_line=u.SystemLibrary.get_command_line())

def graphs(bp):
    result=[]
    for g in u.BlueprintEditorLibrary.list_graphs(bp):
        ed=u.BlueprintGraphEditor.get_graph_editor(g)
        rows=[]
        for n in ed.list_all_nodes():
            props={}
            if hasattr(u,'GASPALSLocomotionLibrary'):
                props=json.loads(u.GASPALSLocomotionLibrary.inspect_properties(n))
            for prop in ([] if props else ['path','text_path','bindings','property_bindings','node']):
                try: props[prop]=str(n.get_editor_property(prop))
                except Exception: pass
            rows.append(dict(name=n.get_name(), title=n.get_node_title(),
                properties=props,
                text=n.export_text() if hasattr(n,'export_text') else '',
                pins=[dict(name=str(p.get_pin_name()), value=p.get_pin_value(),
                    links=[c.get_owning_node().get_name()+':'+str(c.get_pin_name()) for c in p.list_connected_pins()])
                    for p in n.list_all_pins()]))
        result.append(dict(name=g.get_name(),path=g.get_path_name(),nodes=rows,errors=str(ed.list_nodes_with_errors())))
    return result

def defaults(cdo, extra=()):
    if hasattr(u,'GASPALSLocomotionLibrary'):
        return json.loads(u.GASPALSLocomotionLibrary.inspect_properties(cdo))
    result={}
    for n in set(dir(cdo)) | {str(x) for x in extra}:
        if n.startswith('_'): continue
        try: result[n]=str(cdo.get_editor_property(n))
        except Exception: pass
    return result

def run(operation, argument=''):
    current = state()
    if operation == 'state':
        (OUT / ('editor-state-' + (argument or 'current') + '.json')).write_text(json.dumps(current, indent=2))
        return current
    if operation == 'seams':
        import importlib
        from Scripts.GASPALSLocomotion01 import seams
        importlib.reload(seams)
        return seams.run()
    if operation == 'final_check':
        import importlib
        from Scripts.GASPALSLocomotion01 import final_asset_check
        importlib.reload(final_asset_check)
        return final_asset_check.run()
    if operation == 'cvars':
        import importlib
        from Scripts.GASPALSLocomotion01 import cvars
        importlib.reload(cvars)
        return cvars.run()
    if operation == 'check_cleanup':
        # Only the two task CDOs were touched by pure-function verification.
        # Prove restoration before discarding their resulting package dirty flags.
        assert not current['pie'],current
        evidence=json.loads((OUT/'asset-checks-02.json').read_text())
        paths=['/GASPALS/Blueprints/CBP_SandboxCharacter',
            '/Game/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01']
        assert set(current['dirty']).issubset(paths),current
        for path,key in zip(paths,['source','child']):
            cdo=u.get_default_object(u.load_asset(path).generated_class())
            assert defaults(cdo)==evidence[key+'_defaults'],key+' CDO not restored'
            # The first speed probe held a reflected Vector view, rather than a
            # value copy. Restore its recorded zero CDO velocity before reload.
            assert evidence[key+'_movement_defaults']['Velocity']=='(X=0.000000,Y=0.000000,Z=0.000000)'
            cdo.character_movement.set_editor_property('velocity',u.Vector(0,0,0))
            now=defaults(cdo.character_movement)
            previous=evidence[key+'_movement_defaults']
            delta={k:[previous.get(k),now.get(k)] for k in previous.keys()|now.keys() if previous.get(k)!=now.get(k)}
            assert not delta,(key+' CMC not restored',delta)
        packages=[u.find_object(None,path) for path in current['dirty']]
        result=u.EditorLoadingAndSavingUtils.reload_packages(packages,u.ReloadPackagesInteractionMode.ASSUME_POSITIVE)
        after=state()
        assert not after['dirty'],after
        (OUT/'check-cleanup.json').write_text(json.dumps(dict(restoration_verified=True,reload=str(result),after=after),indent=2))
        return after
    if operation == 'close':
        assert not current['pie'] and not current['dirty'], current
        assert current['map'] == '/Game/Maps/L_OpeningLobby_PainterStone01.L_OpeningLobby_PainterStone01'
        (OUT / ('editor-close-' + argument + '.json')).write_text(json.dumps(current, indent=2))
        u.SystemLibrary.quit_editor()
        return current
    if operation == 'capabilities':
        return {name: str(getattr(u.PluginBlueprintLibrary, name).__doc__) for name in dir(u.PluginBlueprintLibrary)
                if not name.startswith('_') and any(w in name for w in ['mount', 'load', 'enable', 'plugin'])}
    if operation == 'audit':
        assert not current['pie'],current
        registry=u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/GASPALS'],True)
        path=argument
        bp=u.load_asset(path)
        assert bp,path
        data=dict(path=path, class_name=bp.get_class().get_name())
        if isinstance(bp,u.Blueprint):
            data['parent']=u.BlueprintEditorLibrary.get_blueprint_parent_class(bp).get_path_name()
            data['graphs']=graphs(bp)
            cdo=u.get_default_object(bp.generated_class())
            data['defaults']=defaults(cdo,u.BlueprintEditorLibrary.list_member_variable_names(bp,True))
            if isinstance(cdo,u.Character):
                data['movement_defaults']=defaults(cdo.character_movement)
                data['mesh_defaults']=defaults(cdo.mesh)
                data['capsule_defaults']=defaults(cdo.capsule_component)
        else: data['defaults']=defaults(bp)
        target=OUT/'SourceGraph'/ (bp.get_name()+'.json')
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(data,indent=2))
        return dict(path=path,parent=data.get('parent'),graphs=[g['name'] for g in data.get('graphs',[])],
                    defaults={k:v for k,v in data['defaults'].items() if k not in dir(u.Object)},evidence=str(target))
    if operation == 'inventory':
        registry=u.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(['/GASPALS'],True)
        opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
        data=[dict(package=str(a.package_name),class_name=str(a.asset_class_path),
            dependencies=[str(d) for d in registry.get_dependencies(a.package_name,opts)])
            for a in registry.get_assets_by_path('/GASPALS',recursive=True)]
        (OUT/'source-inventory.json').write_text(json.dumps(data,indent=2))
        return dict(packages=len(data),plugin_base=u.PluginBlueprintLibrary.get_plugin_base_dir('GASPALS'))
    if operation == 'node_api':
        bp=u.load_asset('/GASPALS/OverlaySystem/Overlays/Poses/ABP_OverlayPose_Base')
        for g in u.BlueprintEditorLibrary.list_graphs(bp):
            for n in u.BlueprintGraphEditor.get_graph_editor(g).list_all_nodes():
                if 'PropertyAccess' in n.get_name():
                    return dict(node=str(n), api=[m for m in dir(n) if not m.startswith('_')])
    if operation == 'author':
        assert not current['pie'] and not current['dirty'], current
        from Scripts.GASPALSLocomotion01 import author
        return author.run()
    if operation == 'enum_api':
        cdo=u.get_default_object(u.EditorAssetLibrary.load_blueprint_class('/GASPALS/Blueprints/CBP_SandboxCharacter'))
        return {name:dict(value=str(cdo.get_editor_property(name)),options=dir(type(cdo.get_editor_property(name))))
            for name in ['OverlayBase','OverlayPose']}
    if operation == 'reflect':
        obj=u.load_object(None,argument)
        assert obj,argument
        result=json.loads(u.GASPALSLocomotionLibrary.inspect_properties(obj))
        path=OUT/'Reflection'/ (obj.get_name()+'.json')
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(result,indent=2))
        return result
    if operation == 'check':
        assert not current['pie'], current
        from Scripts.GASPALSLocomotion01 import checks
        import importlib
        importlib.reload(checks)
        return checks.run(argument)
    raise ValueError(operation)
