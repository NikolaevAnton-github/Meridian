"""Two guarded entrance-only coated finish tests; official Epic MCP entrypoint."""
import json
import unreal as u
import architecture01_unreal as work
import architecture01_reflection as reflection
COR=work.OUT/'Correction03'
PATH=work.ASSETS+'/Materials/M_A01_EntranceCoating'
OLD=work.ASSETS+'/Materials/M_A01_Metal.M_A01_Metal'
LABELS=(['A01_EntranceUpperMullion_'+n for n in ['-2.6','-1.3','0','1.3','2.6']]
    +['A01_EntranceUpperTransom_'+str(n) for n in range(6)]
    +['A01_EntranceLeafMullion_'+n for n in ['-1.04','0','1.04']]
    +['A01_EntranceLeafHead','A01_EntranceFieldEdge_-2.6','A01_EntranceFieldEdge_2.6','A01_EntryPull_-1','A01_EntryPull_1'])
# Opaque pigmented coatings are dielectric at the visible surface. Linear colors.
VARIANTS={'A':dict(color=[.095,.12,.11],roughness=.32,metallic=0.0,specular=.5),
          'B':dict(color=[.055,.067,.061],roughness=.48,metallic=0.0,specular=.5)}

def write(name,data):
    (COR/(name+'.json')).write_text(json.dumps(data,indent=2));return data

def targets():
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    selected=[a for a in actors if a.get_actor_label() in LABELS]
    assert len(selected)==len(LABELS)==19
    for a in selected:
        c=a.static_mesh_component
        assert a.get_actor_location().x < -2900 and c.get_num_materials()==1
        expected='Hardware' if 'EntryPull' in a.get_actor_label() else 'Mullion'
        assert c.static_mesh.get_path_name()==work.ASSETS+'/Meshes/SM_A01_'+expected+'.SM_A01_'+expected
        assert c.get_material(0).get_path_name() in [OLD,PATH+'.M_A01_EntranceCoating']
    return selected

def refl(command):
    old=reflection.COR;reflection.COR=COR
    try:return reflection.run(command)
    finally:reflection.COR=old

def run(command):
    if command=='inspect_finish':
        work.guard(True)
        import re
        before=json.loads((COR/'before-reflection-state.json').read_text())['actors']
        bounds=json.loads((COR/'before-live.json').read_text())['actor_bounds']
        changed=[];original=0
        for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
            name=a.get_actor_label()
            if name not in before:
                assert name==reflection.LABEL
                continue
            original+=1
            row=dict(class_path=a.get_class().get_path_name(),transform=re.sub(r'0x[0-9A-Fa-f]+','POINTER',str(a.get_actor_transform())),hidden=a.is_temporarily_hidden_in_editor())
            if isinstance(a,u.PostProcessVolume):row['postprocess']=a.get_editor_property('settings').export_text()
            assert row==before[name],name
            c=a.get_component_by_class(u.StaticMeshComponent)
            if c:
                mats=[c.get_material(i).get_path_name() for i in range(c.get_num_materials())]
                if mats!=bounds[name]['materials']:
                    assert name in LABELS and mats==[PATH+'.M_A01_EntranceCoating'];changed.append(name)
                assert c.static_mesh.get_path_name()==bounds[name]['mesh']
                assert str(c.get_collision_profile_name())==bounds[name]['profile']
        assert original==len(before) and sorted(changed)==sorted(LABELS)
        m=u.load_asset(PATH);lib=u.MaterialEditingLibrary;inputs={}
        for prop in ['MP_BASE_COLOR','MP_ROUGHNESS','MP_METALLIC','MP_SPECULAR','MP_EMISSIVE_COLOR']:
            n=lib.get_material_property_input_node(m,getattr(u.MaterialProperty,prop))
            inputs[prop]=dict(node=n.get_class().get_name(),value=str(n.get_editor_property('constant' if prop in ['MP_BASE_COLOR','MP_EMISSIVE_COLOR'] else 'r')))
        stats=lib.get_statistics(m)
        return write('tested-live-inputs',dict(original_actor_records_unchanged=original,changed_material_assignments=changed,inputs=inputs,pixel_shader_instructions=stats.num_pixel_shader_instructions,cvars=reflection.settings()))
    if command=='before':
        work.guard(True,True)
        assert not u.EditorAssetLibrary.does_asset_exist(PATH)
        data=[]
        for a in targets():
            c=a.static_mesh_component
            assert c.get_material(0).get_path_name()==OLD
            data.append(dict(label=a.get_actor_label(),actor=a.get_path_name(),component=c.get_path_name(),slot=0,mesh=c.static_mesh.get_path_name(),before=OLD,candidate=PATH,source='Scripts/OpeningLobby/architecture01_coating.py',native_geometry_source='Assets/Source/OpeningLobby/Architecture01/LobbyArchitecture01.blend'))
        write('assignment-mapping',data)
        return dict(preflight=refl('inspect'),snapshot=refl('before'),assignments=len(data),variants=VARIANTS)
    if command in ['variant:A','variant:B']:
        work.guard(True)
        variant=command[-1];recipe=VARIANTS[variant]
        assert not (COR/('variant-'+variant+'.json')).exists(),'Variant already attempted'
        selected=targets();lib=u.MaterialEditingLibrary
        m=u.load_asset(PATH) if u.EditorAssetLibrary.does_asset_exist(PATH) else None
        if m:lib.delete_all_material_expressions(m)
        else:m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_A01_EntranceCoating',work.ASSETS+'/Materials',u.Material,u.MaterialFactoryNew())
        assert m
        for prop,value in [('MP_BASE_COLOR',recipe['color']),('MP_ROUGHNESS',recipe['roughness']),('MP_METALLIC',recipe['metallic']),('MP_SPECULAR',recipe['specular']),('MP_EMISSIVE_COLOR',[0,0,0])]:
            vector=isinstance(value,list)
            n=lib.create_material_expression(m,u.MaterialExpressionConstant3Vector if vector else u.MaterialExpressionConstant)
            n.set_editor_property('constant' if vector else 'r',u.LinearColor(*value,1) if vector else value)
            assert lib.connect_material_property(n,'',getattr(u.MaterialProperty,prop))
        lib.layout_material_expressions(m);lib.recompile_material(m)
        for a in selected:a.static_mesh_component.set_material(0,m)
        return write('variant-'+variant,dict(recipe=recipe,material=PATH,actors=LABELS,cvars=reflection.settings(),saved=False,blend_mode=str(m.get_editor_property('blend_mode'))))
    if command=='frontlayer_add':
        # Same proven two-field override; admit only this run's unsaved coating.
        state=work.guard(True)
        assert all(p==PATH for p in state['dirty_content'])
        targets()
        assert reflection.settings()['r.Lumen.TranslucencyReflections.FrontLayer.Allow']==1
        sub=u.get_editor_subsystem(u.EditorActorSubsystem)
        assert not any(a.get_actor_label()==reflection.LABEL for a in sub.get_all_level_actors())
        a=sub.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0));a.set_actor_label(reflection.LABEL)
        a.set_folder_path('Architecture01/ReflectionSupport')
        a.set_editor_property('unbound',True);a.set_editor_property('priority',10.0)
        pp=a.get_editor_property('settings')
        pp.set_editor_property('override_lumen_front_layer_translucency_reflections',True)
        pp.set_editor_property('lumen_front_layer_translucency_reflections',True)
        a.set_editor_property('settings',pp)
        return write('frontlayer-delta',dict(actor=a.get_path_name(),label=reflection.LABEL,unbound=True,priority=10,settings=pp.export_text(),cvars=reflection.settings(),saved=False))
    if command.startswith('capture:'):
        import architecture01_capture as capture
        _,folder,op,view=command.split(':')
        assert folder in ['LiveBefore','A','B','AFrontLayer','BFrontLayer','Reopened']
        assert op in ['camera','shoot'] and view in capture.VIEWS
        old=capture.OUT;capture.OUT=COR/folder;capture.OUT.mkdir(exist_ok=True)
        try:
            result=getattr(capture,op)(view)
            if op=='shoot':write(folder+'-'+view+'-renderer',reflection.settings())
            return result
        finally:capture.OUT=old
    if command=='discard':
        work.guard(True)
        # Discard only this correction's actor overrides/support; disk map stays untouched.
        actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
        before=json.loads((COR/'before-reflection-state.json').read_text())['actors']
        added=[a for a in actors if a.get_actor_label() not in before]
        assert all(a.get_actor_label()==reflection.LABEL for a in added)
        for a in added:assert u.get_editor_subsystem(u.EditorActorSubsystem).destroy_actor(a)
        assert u.EditorLoadingAndSavingUtils.load_map(str(work.ROOT/'Content/Maps/L_OpeningLobby_Architecture01.umap'))
        if u.EditorAssetLibrary.does_asset_exist(PATH):assert u.EditorAssetLibrary.delete_asset(PATH)
        return refl('discard_diagnostics')
    if command=='final':
        import architecture01_capture as capture
        import architecture01_correction as correction
        assert capture._settings is None
        old=correction.COR;correction.COR=COR
        try:result=correction.snapshot('after')
        finally:correction.COR=old
        before=json.loads((COR/'before-reflection-state.json').read_text())
        after=json.loads((COR/'restored-reflection-state.json').read_text())
        assert before==after
        return write('final-state',dict(state=work.guard(True,True),cvars=reflection.settings(),capture_restored=True,unchanged=result['unchanged'],map_saved=False))
    raise ValueError(command)
