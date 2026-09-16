"""Correction01 only: mineral sources, dedicated material graphs and preservation evidence."""
import json, hashlib, math
from pathlib import Path
ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'
COR=OUT/'Correction01'
SRC=ROOT/'Assets/Source/OpeningLobby/Architecture01'

def native_signature():
    import bpy
    records={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        data=dict(matrix=[list(r) for r in ob.matrix_world],vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv=[[list(v.uv) for v in layer.data] for layer in ob.data.uv_layers])
        records[ob.name]=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
    return records

def author():
    """Rasterize original mineral aggregates and open branching fracture paths in Blender."""
    import bpy
    import numpy as np
    assert Path(bpy.data.filepath)==SRC/'LobbyArchitecture01.blend'
    assert not bpy.data.is_dirty
    before=native_signature()
    n=2048;rng=np.random.default_rng(914601)
    # Jittered cellular grains: nearest seed carries a distinct mineral albedo.
    yy,xx=np.mgrid[:n,:n].astype(np.float32)
    def grains(cells):
        sx=rng.random((cells,cells));sy=rng.random((cells,cells));value=rng.random((cells,cells))
        gx=xx*cells/n;gy=yy*cells/n;ix=gx.astype(int);iy=gy.astype(int)
        nearest=np.full((n,n),100.,np.float32);result=np.zeros((n,n),np.float32)
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                cx=(ix+dx)%cells;cy=(iy+dy)%cells
                dist=(gx-(ix+dx+sx[cy,cx]))**2+(gy-(iy+dy+sy[cy,cx]))**2
                hit=dist<nearest;result[hit]=value[cy,cx][hit];nearest=np.minimum(nearest,dist)
        return result
    aggregate=grains(920);inclusions=grains(310);micro=grains(1500)
    def segment(canvas,a,b,width,amplitude):
        # Wrap complete paths at the texture boundary; no level-set contour loops.
        for sy in [-n,0,n]:
            for sx in [-n,0,n]:
                ax,ay=a[0]+sx,a[1]+sy;bx,by=b[0]+sx,b[1]+sy
                x0=max(0,int(min(ax,bx)-width-2));x1=min(n,int(max(ax,bx)+width+3))
                y0=max(0,int(min(ay,by)-width-2));y1=min(n,int(max(ay,by)+width+3))
                if x0>=x1 or y0>=y1:continue
                y,x=np.mgrid[y0:y1,x0:x1];vx,vy=bx-ax,by-ay
                t=np.clip(((x-ax)*vx+(y-ay)*vy)/max(vx*vx+vy*vy,1e-6),0,1)
                distance=np.sqrt((x-ax-t*vx)**2+(y-ay-t*vy)**2)
                mask=np.clip(width+.7-distance,0,1)*amplitude
                canvas[y0:y1,x0:x1]=np.maximum(canvas[y0:y1,x0:x1],mask)
    def fractures(count,length,width):
        field=np.zeros((n,n),np.float32)
        for _ in range(count):
            start=rng.uniform(0,n,2);angle=rng.uniform(-math.pi,math.pi)
            points=[start];direction=angle
            steps=int(rng.uniform(*length)/9)
            for j in range(steps):
                direction=.78*direction+.22*angle+rng.normal(0,.18)
                end=points[-1]+np.array([math.cos(direction),math.sin(direction)])*rng.uniform(5,14)
                taper=min(1,(j+1)/5,(steps-j)/9)
                segment(field,points[-1],end,width*rng.uniform(.45,1.25)*taper,rng.uniform(.45,1))
                points.append(end)
                if j>3 and rng.random()<.055:
                    branch=direction+rng.choice([-1,1])*rng.uniform(.35,1.05);p=end.copy()
                    for k in range(int(rng.integers(5,19))):
                        branch+=rng.normal(0,.16);q=p+np.array([math.cos(branch),math.sin(branch)])*7
                        segment(field,p,q,width*.4,rng.uniform(.2,.65));p=q
        return field
    stoneveins=fractures(160,(20,200),.65)
    floorveins=fractures(19,(200,1000),1.75)
    floorveins=np.maximum(floorveins,fractures(120,(20,180),.65)*.45)
    def write(name,rgb):
        rgba=np.concatenate([np.clip(rgb,0,1),np.ones((n,n,1))],axis=2).astype(np.float32)
        im=bpy.data.images.new('Correction01 export',width=n,height=n,alpha=True)
        im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.ravel())
        im.filepath_raw=str(SRC/'Textures'/(name+'.png'));im.file_format='PNG';im.save();bpy.data.images.remove(im)
    for kind,veins,base in [('Stone',stoneveins,(.245,.279,.259)),('Floor',floorveins,(.235,.285,.251))]:
        grain=(aggregate-.5)*.047+(micro-.5)*.035+(inclusions-.5)*.019
        mineral=np.maximum(aggregate-.73,0)*.065-np.maximum(.13-inclusions,0)*.10
        detail=grain+mineral+veins*(.095 if kind=='Stone' else .26)
        rgb=np.stack([b+detail for b in base],axis=2)
        write('T_A01_'+kind+'_BaseColor',rgb)
        rough=(.30 if kind=='Stone' else .155)+(aggregate-.5)*(.014 if kind=='Stone' else .003)
        write('T_A01_'+kind+'_ORM',np.stack([np.ones_like(rough),rough,np.zeros_like(rough)],axis=2))
        # A polished plane carries color structure, not pebble displacement.
        normal=np.empty((n,n,3),np.float32);normal[:]=(.5,.5,1)
        write('T_A01_'+kind+'_Normal',normal)
    for im in bpy.data.images:
        if im.name.startswith('T_A01_'):
            path=SRC/'Textures'/im.name
            assert path.exists(),path
            im.filepath=str(path);im.unpack(method='REMOVE');im.reload();im.pack()
    glass=bpy.data.materials['M_A01_Glass']
    shader=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value=(.90,.97,.94,1)
    shader.inputs['Metallic'].default_value=0
    shader.inputs['Roughness'].default_value=.045
    shader.inputs['IOR'].default_value=1.5
    shader.inputs['Transmission Weight'].default_value=1
    text=bpy.data.texts.get('Correction01_MineralAuthor.py') or bpy.data.texts.new('Correction01_MineralAuthor.py')
    text.clear();text.write(Path(__file__).read_text())
    assert native_signature()==before
    # Disable version copies in memory; the exact old native source is already archived.
    old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
    try:bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'LobbyArchitecture01.blend'))
    finally:bpy.context.preferences.filepaths.save_version=old
    report=dict(blender=bpy.app.version_string,geometry_hashes=before,geometry_unchanged=True,method='Jittered cellular mineral aggregates and rasterized open branching fractures; no Fourier/sine or reference pixels',seed=914601,size=[n,n],period_m=4,normal='Flat DirectX polished plane',roughness={'Stone':.30,'Floor':.155},packed=6)
    (COR/'native-authoring.json').write_text(json.dumps(report,indent=2))
    return report

def snapshot(name):
    import unreal as u
    import architecture01_unreal as work
    work.guard(True,True)
    # Reuse the established actor audit while keeping all old records immutable.
    (COR/'expected-geometry.json').write_bytes((OUT/'expected-geometry.json').read_bytes())
    original=work.OUT;work.OUT=COR
    try:work.audit()
    finally:work.OUT=original
    data=json.loads((COR/'construction.json').read_text())
    actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
    anchors=json.loads((OUT/'baseline-anchors.json').read_text())['anchors']
    for label,row in anchors.items():
        a=actors[label]
        if 'lighting' in row:now={k:str(a.point_light_component.get_editor_property(k)) for k in row['lighting']};assert now==row['lighting']
        if 'exposure' in row:now={k:str(a.get_editor_property('settings').get_editor_property(k)) for k in row['exposure']};assert now==row['exposure']
        if 'collision' in row:
            c=a.static_mesh_component
            now=dict(profile=str(c.get_collision_profile_name()),enabled=str(c.get_collision_enabled()),responses=[str(c.get_collision_response_to_channel(ch)) for ch in [u.CollisionChannel.ECC_WORLD_STATIC,u.CollisionChannel.ECC_WORLD_DYNAMIC,u.CollisionChannel.ECC_PAWN]])
            assert now==row['collision']
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    data['state']=work.guard(True,True)
    data['game_mode']=world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
    data['anchors_unchanged']=True
    data['hidden']=[a.get_actor_label() for a in actors.values() if a.is_temporarily_hidden_in_editor()]
    data['transforms']={key:str(a.get_actor_transform()) for key,a in actors.items()}
    data['glass_layers']={key:row for key,row in data['actor_bounds'].items() if any('M_A01_Glass.' in p for p in row.get('materials',[]))}
    data['capabilities']=dict(thin_translucent=str(getattr(u.MaterialShadingModel,'MSM_THIN_TRANSLUCENT',None)),thin_output=hasattr(u,'MaterialExpressionThinTranslucentMaterialOutput'))
    if name!='before':
        import re
        before=json.loads((COR/'before-live.json').read_text())
        def stable(record):
            result=dict(record)
            result['transforms']={k:re.sub(r'0x[0-9A-Fa-f]+','POINTER',v) for k,v in record['transforms'].items()}
            return result
        assert stable(data)==stable(before),'Live scene record changed (excluding transient Transform allocation addresses)'
    (COR/(name+'-live.json')).write_text(json.dumps(data,indent=2))
    return dict(state=data['state'],game_mode=data['game_mode'],hidden=data['hidden'],glass_layers=data['glass_layers'],capabilities=data['capabilities'],unchanged=name!='before')

def run(operation):
    if operation.startswith('early_'):
        import architecture01_capture as capture
        command,_,view=operation[6:].partition(':')
        original=capture.OUT;capture.OUT=COR/'Early';capture.OUT.mkdir(exist_ok=True)
        try:return getattr(capture,command)(view)
        finally:capture.OUT=original
    if operation.startswith('transmission_'):
        import architecture01_capture as capture
        import unreal as u
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
        pawn=u.GameplayStatics.get_player_pawn(world,0)
        movement=pawn.get_component_by_class(u.CharacterMovementComponent)
        command=operation[len('transmission_'):]
        if command=='restore':
            pawn.set_actor_location(u.Vector(-2750,0,100),False,True)
            pawn.set_actor_enable_collision(True);movement.set_movement_mode(u.MovementMode.MOVE_WALKING)
            return 'Diagnostic-only flying/collision overrides restored; pawn returned inside.'
        if command=='camera':
            movement.stop_movement_immediately();movement.set_movement_mode(u.MovementMode.MOVE_FLYING)
            pawn.set_actor_enable_collision(False)
        original=capture.OUT;capture.OUT=COR
        capture.VIEWS['GlassTransmission-90']=(-3050,0,0,0)
        try:
            result=getattr(capture,command)('GlassTransmission-90')
            if command=='camera':pawn.set_actor_location(u.Vector(-3050,0,90.1499996),False,True)
            return result
        finally:
            capture.OUT=original
            del capture.VIEWS['GlassTransmission-90']
    if operation=='before':return snapshot('before')
    if operation=='after':return snapshot('after')
    if operation=='materials':return materials()
    if operation=='reopen':
        import unreal as u
        import architecture01_unreal as work
        work.guard(True,True)
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(work.MAP)
        return snapshot('reopened')
    if operation=='shaders':return shaders()
    if operation=='glass_substrate':return glass_substrate()
    if operation=='reload_schema':
        import unreal as u
        return dict(doc=u.EditorLoadingAndSavingUtils.reload_packages.__doc__,modes=[k for k in dir(u.ReloadPackagesInteractionMode) if k.isupper()])
    if operation=='reload_assets':
        import unreal as u
        import architecture01_unreal as work
        work.guard(True,True)
        paths=[work.ASSETS+'/Materials/M_A01_'+n for n in ['Stone','Wall','Floor','Strip','Glass']]
        paths += [work.ASSETS+'/Textures/'+p.stem for p in sorted((SRC/'Textures').glob('*.png'))]
        packages=[u.load_package(p) for p in paths]
        result=u.EditorLoadingAndSavingUtils.reload_packages(packages,u.ReloadPackagesInteractionMode.ASSUME_NEGATIVE)
        report=dict(paths=paths,reloaded=bool(result[0]),error=str(result[1]))
        (COR/'package-reload.json').write_text(json.dumps(report,indent=2))
        assert result[0] and not str(result[1]),report
        return report
    if operation=='final_state':
        import unreal as u
        import architecture01_unreal as work
        import architecture01_capture as capture
        s=work.guard(True,True);assert capture._settings is None
        textures={}
        for p in sorted((SRC/'Textures').glob('*.png')):
            tex=u.load_asset(work.ASSETS+'/Textures/'+p.stem)
            row=dict(srgb=tex.get_editor_property('srgb'),compression=str(tex.get_editor_property('compression_settings')),mip_generation=str(tex.get_editor_property('mip_gen_settings')),never_stream=tex.get_editor_property('never_stream'),size=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()])
            assert row['size']==[2048,2048] and row['srgb']==('BaseColor' in p.name) and not row['never_stream']
            if 'Normal' in p.name:assert not tex.get_editor_property('flip_green_channel')
            textures[p.stem]=row
        m=u.load_asset(work.ASSETS+'/Materials/M_A01_Glass')
        slab=u.MaterialEditingLibrary.get_material_property_input_node(m,u.MaterialProperty.MP_FRONT_MATERIAL)
        assert isinstance(slab,u.MaterialExpressionSubstrateSlabBSDF)
        assert slab.get_editor_property('sub_surface_type')==u.MaterialSubSurfaceType.MSS_SIMPLE_VOLUME
        s.update(capture_overrides_restored=True,glass_subsurface_type=str(slab.get_editor_property('sub_surface_type')),textures=textures,map_saved=False,route_carried_forward_seconds=112.297)
        (COR/'final-state.json').write_text(json.dumps(s,indent=2));return s
    if operation=='glass_inspect':
        import unreal as u
        import architecture01_unreal as work
        m=u.load_asset(work.ASSETS+'/Materials/M_A01_Glass');lib=u.MaterialEditingLibrary
        row={k:str(m.get_editor_property(k)) for k in ['blend_mode','shading_model','is_thin_surface','two_sided']}
        row['thickness_properties']=[k for k in dir(u.MaterialProperty) if 'THICK' in k]
        for key in ['MP_FRONT_MATERIAL','MP_OPACITY']:
            prop=getattr(u.MaterialProperty,key);node=lib.get_material_property_input_node(m,prop)
            row[key]=str(node)
            if node and isinstance(node,u.MaterialExpressionConstant):row[key+'_value']=node.get_editor_property('r')
        (COR/'glass-live-inputs.json').write_text(json.dumps(row,indent=2));return row
    raise ValueError(operation)

def materials():
    import unreal as u
    import architecture01_unreal as work
    work.guard(True,True)
    tasks=[]
    for p in sorted((SRC/'Textures').glob('*.png')):
        t=u.AssetImportTask();t.filename=str(p);t.destination_path=work.ASSETS+'/Textures';t.destination_name=p.stem
        t.automated=True;t.save=True;t.replace_existing=True;tasks.append(t)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    imports=[]
    for t in tasks:
        assert t.imported_object_paths
        tex=u.load_asset(t.imported_object_paths[0]);name=tex.get_name()
        tex.set_editor_property('srgb','BaseColor' in name)
        tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP if 'Normal' in name else (u.TextureCompressionSettings.TC_MASKS if 'ORM' in name else u.TextureCompressionSettings.TC_DEFAULT))
        if 'Normal' in name:tex.set_editor_property('flip_green_channel',False)
        u.EditorAssetLibrary.save_loaded_asset(tex)
        imports.append(dict(source=t.filename,assets=list(t.imported_object_paths)))
    lib=u.MaterialEditingLibrary
    for name,kind in [('Stone','Stone'),('Wall','Stone'),('Floor','Floor'),('Strip','Floor')]:
        m=u.load_asset(work.ASSETS+'/Materials/M_A01_'+name);assert m
        lib.delete_all_material_expressions(m)
        def node(cls,**props):
            result=lib.create_material_expression(m,cls)
            for k,v in props.items():result.set_editor_property(k,v)
            return result
        def scalar(v):return node(u.MaterialExpressionConstant,r=v)
        def vector(v):return node(u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*v,1))
        def connect(a,b,pin='',output=''):assert lib.connect_material_expressions(a,output,b,pin)
        def prop(a,p,output=''):assert lib.connect_material_property(a,output,p)
        def mul(a,b):
            result=node(u.MaterialExpressionMultiply);connect(a,result,'A');connect(b,result,'B');return result
        def add(a,b):
            result=node(u.MaterialExpressionAdd);connect(a,result,'A');connect(b,result,'B');return result
        if kind:
            pos=node(u.MaterialExpressionWorldPosition);norm=node(u.MaterialExpressionVertexNormalWS)
            absolute=node(u.MaterialExpressionAbs);connect(norm,absolute)
            coordinates=[];weights=[]
            for channels,weight in [((False,True,True),(True,False,False)),((True,False,True),(False,True,False)),((True,True,False),(False,False,True))]:
                mask=node(u.MaterialExpressionComponentMask,r=channels[0],g=channels[1],b=channels[2]);connect(pos,mask)
                coordinates.append(mul(mask,scalar(.0025)))
                mask=node(u.MaterialExpressionComponentMask,r=weight[0],g=weight[1],b=weight[2]);connect(absolute,mask);weights.append(mask)
            def sample(suffix,sampler):
                tex=u.load_asset(work.ASSETS+'/Textures/T_A01_'+kind+'_'+suffix);terms=[]
                for uv,weight in zip(coordinates,weights):
                    t=node(u.MaterialExpressionTextureSample,texture=tex,sampler_type=sampler);connect(uv,t)
                    terms.append(mul(t,weight))
                return add(add(terms[0],terms[1]),terms[2])
            color=sample('BaseColor',u.MaterialSamplerType.SAMPLERTYPE_COLOR)
            if name=='Wall':color=mul(color,vector((1.6,1.5,1.5)))
            if name=='Strip':color=mul(color,vector((.1,.105,.105)))
            prop(color,u.MaterialProperty.MP_BASE_COLOR)
            orm=sample('ORM',u.MaterialSamplerType.SAMPLERTYPE_MASKS)
            mask=node(u.MaterialExpressionComponentMask,r=False,g=True,b=False);connect(orm,mask);prop(mask,u.MaterialProperty.MP_ROUGHNESS)
            prop(vector((0,0,1)),u.MaterialProperty.MP_NORMAL)
            prop(scalar(0),u.MaterialProperty.MP_METALLIC)
        lib.layout_material_expressions(m);lib.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
    glass_substrate()
    assert not work.state()['dirty_maps'],'Material correction must not dirty or save the map'
    (COR/'imports.json').write_text(json.dumps(imports,indent=2))
    return dict(textures=len(tasks),materials=5,map_saved=False)

def shaders():
    import unreal as u
    import architecture01_unreal as work
    work.guard(True,True)
    records={}
    for name in ['Stone','Wall','Floor','Strip','Glass']:
        m=u.load_asset(work.ASSETS+'/Materials/M_A01_'+name)
        stats=u.MaterialEditingLibrary.get_statistics(m)
        row={k:getattr(stats,k) for k in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers']}
        row['properties']={k:str(m.get_editor_property(k)) for k in ['blend_mode','shading_model','two_sided','translucency_lighting_mode','screen_space_reflections']}
        row['inputs']={str(p):str(u.MaterialEditingLibrary.get_material_property_input_node(m,p)) for p in [u.MaterialProperty.MP_BASE_COLOR,u.MaterialProperty.MP_ROUGHNESS,u.MaterialProperty.MP_NORMAL,u.MaterialProperty.MP_OPACITY,u.MaterialProperty.MP_EMISSIVE_COLOR,u.MaterialProperty.MP_FRONT_MATERIAL]}
        assert row['num_pixel_shader_instructions']>0
        records[name]=row
    (COR/'shader-audit.json').write_text(json.dumps(records,indent=2))
    return records

def glass_substrate():
    """Use native Substrate absorption instead of the legacy thin-translucent conversion."""
    import unreal as u
    import architecture01_unreal as work
    work.guard(True)
    m=u.load_asset(work.ASSETS+'/Materials/M_A01_Glass');lib=u.MaterialEditingLibrary
    lib.delete_all_material_expressions(m)
    m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT_COLORED_TRANSMITTANCE)
    m.set_editor_property('two_sided',False)
    m.set_editor_property('is_thin_surface',True)
    m.set_editor_property('screen_space_reflections',True)
    m.set_editor_property('translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    def node(cls):return lib.create_material_expression(m,cls)
    def vector(v):
        n=node(u.MaterialExpressionConstant3Vector);n.set_editor_property('constant',u.LinearColor(*v,1));return n
    def scalar(v):
        n=node(u.MaterialExpressionConstant);n.set_editor_property('r',v);return n
    def connect(a,b,pin,output=''):assert lib.connect_material_expressions(a,output,b,pin)
    slab=node(u.MaterialExpressionSubstrateSlabBSDF)
    slab.set_editor_property('sub_surface_type',u.MaterialSubSurfaceType.MSS_SIMPLE_VOLUME)
    mfp=node(u.MaterialExpressionSubstrateTransmittanceToMFP)
    schema=dict(slab=list(lib.get_material_expression_input_names(slab)),mfp=list(lib.get_material_expression_input_names(mfp)))
    (COR/'glass-node-schema.json').write_text(json.dumps(schema,indent=2))
    connect(vector((0,0,0)),slab,'Diffuse Albedo')
    connect(vector((.04,.04,.04)),slab,'F0')
    connect(scalar(.045),slab,'Roughness')
    connect(vector((.90,.97,.94)),mfp,'TransmittanceColor')
    connect(mfp,slab,'SSS MFP','MFP')
    assert lib.connect_material_property(slab,'',u.MaterialProperty.MP_FRONT_MATERIAL)
    lib.layout_material_expressions(m);lib.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
    return dict(native_substrate=True,schema=schema,map_saved=False)
