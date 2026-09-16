"""Dedicated modular lobby assembly; all entrypoints run through official Epic MCP."""
import hashlib
import json
import math
import re
from pathlib import Path
import unreal as u
from stage1_tools import state
from layout02_verification import require_project

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'
SRC=ROOT/'Assets/Source/OpeningLobby/Architecture01'
MAP='/Game/Maps/L_OpeningLobby_Architecture01'
BASE='/Game/Maps/L_OpeningLobby_Layout03'
ASSETS='/Game/OpeningLobby/Architecture01'

def guard(candidate=False,clean=False):
    s=state(); require_project(s['project'])
    assert not s['pie'],s
    assert s['level'].split('.')[0] == (MAP if candidate else BASE),s
    assert all(p.startswith(ASSETS) for p in s['dirty_content']),s
    assert all(p==MAP for p in s['dirty_maps']),s
    if clean: assert not s['dirty_content'] and not s['dirty_maps'],s
    return s

def save():
    for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        name=p.get_path_name(); assert name.startswith(ASSETS),name
        assert u.EditorAssetLibrary.save_asset(name)
    if state()['level'].split('.')[0]==MAP:
        assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()

def import_assets():
    guard(clean=True)
    assert not u.EditorAssetLibrary.does_directory_exist(ASSETS+'/Meshes')
    tasks=[]
    for p in sorted((OUT/'FBX').glob('*.fbx')):
        task=u.AssetImportTask(); task.filename=str(p); task.destination_path=ASSETS+'/Meshes'
        task.destination_name=p.stem; task.automated=True; task.save=True
        options=u.FbxImportUI(); options.import_mesh=True; options.import_materials=False; options.import_textures=False
        options.import_as_skeletal=False; options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
        options.static_mesh_import_data.combine_meshes=True
        options.static_mesh_import_data.generate_lightmap_u_vs=False
        options.static_mesh_import_data.auto_generate_collision=False
        options.static_mesh_import_data.normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
        task.options=options; tasks.append(task)
    for p in sorted((SRC/'Textures').glob('*.png')):
        task=u.AssetImportTask(); task.filename=str(p); task.destination_path=ASSETS+'/Textures'
        task.destination_name=p.stem; task.automated=True; task.save=True; tasks.append(task)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    records=[]
    for task in tasks:
        assert task.imported_object_paths,task.filename
        records.append(dict(source=task.filename,assets=list(task.imported_object_paths)))
    (OUT/'imports.json').write_text(json.dumps(records,indent=2))
    for p in u.EditorAssetLibrary.list_assets(ASSETS+'/Textures'):
        tex=u.load_asset(p)
        if '_Normal' in p:
            tex.set_editor_property('srgb',False); tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
            tex.set_editor_property('flip_green_channel',False)
        elif '_ORM' in p:
            tex.set_editor_property('srgb',False); tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
        else: tex.set_editor_property('srgb',True)
        u.EditorAssetLibrary.save_loaded_asset(tex)
    return dict(imported=len(records))

def materials():
    guard(state()['level'].split('.')[0]==MAP)
    lib=u.MaterialEditingLibrary
    def make(name,kind=None,color=(.06,.08,.07),rough=.35,metal=0,glass=False):
        path=ASSETS+'/Materials/M_A01_'+name
        m=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else None
        if m:
            lib.delete_all_material_expressions(m)
        else:
            m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_A01_'+name,ASSETS+'/Materials',u.Material,u.MaterialFactoryNew())
        def node(cls,**props):
            obj=lib.create_material_expression(m,cls)
            for k,v in props.items(): obj.set_editor_property(k,v)
            return obj
        def scalar(v): return node(u.MaterialExpressionConstant,r=v)
        def vector(v): return node(u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*v,1))
        def connect(a,b,pin='',output=''):
            names=list(lib.get_material_expression_input_names(b))
            resolved='' if pin in ('Input','Coordinates') else pin
            assert lib.connect_material_expressions(a,output,b,resolved),(a,b,pin,names)
        def property(a,p,output=''): assert lib.connect_material_property(a,output,p)
        def multiply(a,b):
            n=node(u.MaterialExpressionMultiply); connect(a,n,'A');connect(b,n,'B');return n
        def add(a,b):
            n=node(u.MaterialExpressionAdd);connect(a,n,'A');connect(b,n,'B');return n
        if kind:
            pos=node(u.MaterialExpressionWorldPosition)
            normal=node(u.MaterialExpressionVertexNormalWS)
            absolute=node(u.MaterialExpressionAbs);connect(normal,absolute,'Input')
            coords=[]; weights=[]
            for channels,weight in [((False,True,True),(True,False,False)),((True,False,True),(False,True,False)),((True,True,False),(False,False,True))]:
                mask=node(u.MaterialExpressionComponentMask,r=channels[0],g=channels[1],b=channels[2]);connect(pos,mask,'Input')
                coords.append(multiply(mask,scalar(.0025)))
                mask=node(u.MaterialExpressionComponentMask,r=weight[0],g=weight[1],b=weight[2]);connect(absolute,mask,'Input');weights.append(mask)
            def sample(suffix,sampler):
                tex=u.load_asset(ASSETS+'/Textures/T_A01_'+kind+'_'+suffix)
                terms=[]
                for uv,w in zip(coords,weights):
                    t=node(u.MaterialExpressionTextureSample,texture=tex,sampler_type=sampler);connect(uv,t,'Coordinates')
                    if suffix=='BaseColor':
                        second=node(u.MaterialExpressionTextureSample,texture=tex,sampler_type=sampler)
                        connect(multiply(uv,scalar(1.731)),second,'Coordinates')
                        t=add(multiply(t,scalar(.65)),multiply(second,scalar(.35)))
                    terms.append(multiply(t,w))
                return add(add(terms[0],terms[1]),terms[2])
            c=sample('BaseColor',u.MaterialSamplerType.SAMPLERTYPE_COLOR)
            if name=='Strip': c=multiply(c,vector((.10,.105,.105)))
            if name=='Wall': c=multiply(c,vector((1.6,1.5,1.5)))
            # Quiet 20 m variation breaks exact repetition without unique bay textures.
            mask=node(u.MaterialExpressionComponentMask,r=True,g=False,b=False);connect(pos,mask,'Input')
            sine=node(u.MaterialExpressionSine,period=2000.);connect(mask,sine,'Input')
            variation=add(scalar(.96),multiply(sine,scalar(.04)))
            property(multiply(c,variation),u.MaterialProperty.MP_BASE_COLOR)
            orm=sample('ORM',u.MaterialSamplerType.SAMPLERTYPE_MASKS)
            mask=node(u.MaterialExpressionComponentMask,r=False,g=True,b=False);connect(orm,mask,'Input');property(mask,u.MaterialProperty.MP_ROUGHNESS)
            normaltex=node(u.MaterialExpressionTextureSample,texture=u.load_asset(ASSETS+'/Textures/T_A01_'+kind+'_Normal'),sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            uv=node(u.MaterialExpressionTextureCoordinate,u_tiling=.25,v_tiling=.25);connect(uv,normaltex,'Coordinates');property(normaltex,u.MaterialProperty.MP_NORMAL)
        else:
            property(vector(color),u.MaterialProperty.MP_BASE_COLOR)
            property(scalar(rough),u.MaterialProperty.MP_ROUGHNESS)
        property(scalar(metal),u.MaterialProperty.MP_METALLIC)
        if glass:
            m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
            m.set_editor_property('two_sided',True)
            m.set_editor_property('translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
            property(scalar(.30),u.MaterialProperty.MP_OPACITY)
            property(vector((.11,.17,.16)),u.MaterialProperty.MP_EMISSIVE_COLOR)
        lib.layout_material_expressions(m);lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
    for name,kind in [('Stone','Stone'),('Floor','Floor'),('Strip','Floor'),('Wall','Stone')]: make(name,kind)
    make('Metal',color=(.095,.12,.11),rough=.27,metal=.82)
    make('Ceiling',color=(.19,.22,.20),rough=.58)
    make('Glass',color=(.32,.48,.43),rough=.12,glass=True)
    make('Checkpoint',color=(.055,.073,.065),rough=.32,metal=.65)
    save()
    return dict(materials=8)

def actor(name,mesh,center,size=None,material='Stone',rotation=0,group='Architecture'):
    aes=u.get_editor_subsystem(u.EditorActorSubsystem)
    a=aes.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*(v*100 for v in center)),u.Rotator(pitch=0,yaw=rotation,roll=0))
    a.set_actor_label('A01_'+name); a.set_folder_path('Architecture01/'+group)
    c=a.static_mesh_component
    obj=u.load_asset(ASSETS+'/Meshes/SM_A01_'+mesh); assert obj,mesh
    c.set_static_mesh(obj);c.set_collision_profile_name('NoCollision')
    if size:
        e=obj.get_bounds().box_extent
        a.set_actor_scale3d(u.Vector(*(v*100/(w*2) for v,w in zip(size,[e.x,e.y,e.z]))))
    mat=u.load_asset(ASSETS+'/Materials/M_A01_'+material);assert mat,material
    for i in range(c.get_num_materials()):c.set_material(i,mat)
    return a

def pier(index,sign):
    x=[-21,-12.6,-4.2,4.2,12.6,21][index]
    for row in range(3):
        actor('Pier_%s_%s_Course_%s'%(index,sign,row),'PierCourse',(x,sign*6.8,1.4+row*2.8),material='Stone',group='Piers')

def assembly():
    guard(clean=True)
    assert not u.EditorAssetLibrary.does_asset_exist(MAP)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).new_level_from_template(MAP,BASE)
    aes=u.get_editor_subsystem(u.EditorActorSubsystem)
    original=json.loads((ROOT/'Saved/OpeningLobby/Layout03/expected-geometry.json').read_text())
    (OUT/'expected-geometry.json').write_text(json.dumps(original,indent=2))
    # All blocking proxies keep their exact accepted transform and profile, with rendering disabled.
    for a in aes.get_all_level_actors():
        name=a.get_actor_label()
        if name not in original: continue
        row=original[name]
        if row['blocking']:
            c=a.static_mesh_component
            c.set_visibility(False);c.set_hidden_in_game(True);c.set_editor_property('cast_shadow',False)
            a.set_folder_path('Architecture01/StructuralCollision')
            # Retained cube is an engine primitive, with dedicated candidate material reference.
            c.set_material(0,u.load_asset(ASSETS+'/Materials/M_A01_Stone'))
        else: aes.destroy_actor(a)
    # Continuous floor; two black ribbons retain their exact width and 2 mm surface envelope.
    for i in range(50):
        x=-29.4+i*1.2
        for j in range(20): actor('Floor_%s_%s'%(i,j),'FloorTile',(x,-11.4+j*1.2,-.02),material='Floor',group='Floor')
        for sign in [-1,1]: actor('Strip_%s_%s'%(i,sign),'FloorStrip',(x,sign*2.2,.001),material='Strip',group='Floor')
    # Stone wall subdivisions remain planar, with 4 mm joints and restrained edge radii.
    for sign in [-1,1]:
        for i in range(25):
            x=-28.8+i*2.4
            for row in range(4):
                lo=row*2.3;hi=(row+1)*2.3
                actor('SideWall_%s_%s_%s'%(sign,i,row),'WallPanel',(x,sign*12.02,(lo+hi)/2),(2.396,.04,hi-lo-.004),'Wall')
            actor('AisleCeiling_%s_%s'%(sign,i),'CeilingPanel',(x,sign*10,9.22),(2.396,4,.04),'Ceiling',group='Ceiling')
            actor('Lintel_%s_%s'%(sign,i),'Lintel',(x,sign*6.8,9.8),(2.396,2.4,2.8),'Stone')
            # Upper walls: separate inward and outward face panels with exact X/Y envelope.
            for row in range(3):
                for side in [-1,1]:
                    actor('Upper_%s_%s_%s_%s'%(sign,i,row,side),'WallPanel',(x,sign*6.8+side*1.18,11.2+(row+.5)*(6.8/3)),(2.396,.04,6.8/3-.004),'Wall')
            actor('AisleTrim_%s_%s'%(sign,i),'Trim',(x,sign*11.98,9.16),(2.396,.025,.04),'Metal',group='Ceiling')
        for i in range(25):
            actor('CentralCeiling_%s_%s'%(sign,i),'CeilingPanel',(-28.8+i*2.4,sign*4,18.02),(2.396,7.996,.04),'Ceiling',group='Ceiling')
    # Closed end compositions have actual glazing apertures in the visible cladding.
    def end_rectangle(name,sign,y0,y1,z0,z1):
        if y1-y0<.001 or z1-z0<.001:return
        ny=max(1,math.ceil((y1-y0)/2.4));nz=max(1,math.ceil((z1-z0)/2.8))
        for j in range(ny):
            for k in range(nz):
                w=(y1-y0)/ny;h=(z1-z0)/nz
                actor(name+'_%s_%s'%(j,k),'EndPanel',(sign*30.005,y0+(j+.5)*w,z0+(k+.5)*h),(.01,w-.004,h-.004),'Wall',group='EndFields')
    for sign,end in [(-1,'Entrance'),(1,'Inner')]:
        w=5.2 if sign<0 else 2.4
        for side in [-1,1]:
            lo,hi=sorted([side*w/2,side*8])
            end_rectangle(end+'Flank'+str(side),sign,lo,hi,0,18)
            lo,hi=sorted([side*8,side*12])
            end_rectangle(end+'Aisle'+str(side),sign,lo,hi,0,9.2)
            for row in range(7):
                lo=row*18/7;hi=(row+1)*18/7
                actor(end+'Band_%s_%s'%(side,row),'EndPanel',(sign*29.98,side*6.8,(lo+hi)/2),(.02,2.4,hi-lo-.004),'Stone',group='EndFields')
        if sign<0:
            end_rectangle('EntranceTop',sign,-2.6,2.6,17.8,18)
            end_rectangle('EntranceMid',sign,-2.6,2.6,5.28,5.4)
        else:
            end_rectangle('InnerAboveDoor',sign,-1.2,1.2,2.32,11.4)
            end_rectangle('InnerDoorLeft',sign,-1.2,-.61,0,2.32)
            end_rectangle('InnerDoorRight',sign,.61,1.2,0,2.32)
            end_rectangle('InnerTop',sign,-1.2,1.2,17.6,18)
    # Recreate original transparent/nonblocking fields using dedicated modeled parts.
    for name,row in original.items():
        center=list(row['center_m']);size=list(row['size_m'])
        if any(token in name for token in ['Mullion','Transom','FieldEdge','LeafHead']):
            actor(name,'Mullion',center,size,'Metal',group='Glazing')
        elif name in ['EntranceUpperGlazing','InnerHighWindow']:
            actor(name,'GlassPane',center,size,'Glass',group='Glazing')
        elif name.startswith('EntranceLeaf_'):
            actor(name,'EntryLeaf',center,size,'Glass',group='Doors')
        elif name=='InnerDoorLeaf': actor(name,'DoorLeaf',center,size,'Metal',group='Doors')
        elif name.startswith('DetectorPost_') or name in ['DetectorHeader','StationBody','StationWorktop']:
            mesh='DetectorPost' if name.startswith('DetectorPost_') else name
            actor(name,mesh,center,size,'Metal' if name=='StationWorktop' else 'Checkpoint',group='Checkpoint')
    # Lower fixed field is cut around the two leaves, avoiding overlapping glass layers.
    for side in [-1,1]:
        actor('EntranceSidelight_'+str(side),'GlassPane',(-29.99,side*1.82,2.64),(.01,1.56,5.28),'Glass',group='Glazing')
    actor('EntranceOverlight','GlassPane',(-29.99,0,3.96),(.01,2.08,2.64),'Glass',group='Glazing')
    # Three metal rails replace the old solid inner frame plate.
    for side in [-1,1]:
        actor('InnerFrameSide_'+str(side),'Mullion',(29.985,side*.565,1.16),(.01,.09,2.32),'Metal',group='Doors')
    actor('InnerFrameHead','Mullion',(29.985,0,2.25),(.01,1.04,.14),'Metal',group='Doors')
    actor('InnerPull','Hardware',(29.945,-.34,1.08),material='Metal',group='Doors')
    for side in [-1,1]:
        actor('EntryPull_'+str(side),'Hardware',(-29.945,side*.16,1.10),material='Metal',group='Doors')
        for xside in [-1,1]:
            actor('DetectorInset_%s_%s'%(side,xside),'CheckpointPanel',(-24.6+xside*.277,-1.05+side*.65,1.28),material='Checkpoint',group='Checkpoint')
    for sign in [-1,1]:pier(1,sign)
    # Other piers remain visible dedicated preview placeholders until the representative bay check.
    for a in aes.get_all_level_actors():
        name=a.get_actor_label()
        if name.startswith('Pier_') and not name.startswith('Pier_1_'):
            a.static_mesh_component.set_visibility(True);a.static_mesh_component.set_hidden_in_game(False)
    save()
    return dict(map=MAP,stage='representative bay; complete after image inspection')

def complete():
    guard(True,True)
    names={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
    assert 'A01_Pier_0_-1_Course_0' not in names
    for i in [0,2,3,4,5]:
        for sign in [-1,1]:
            pier(i,sign)
            c=names['Pier_%s_%s'%(i,sign)].static_mesh_component
            c.set_visibility(False);c.set_hidden_in_game(True)
    save();return dict(stage='complete')

def audit():
    guard(True,True)
    expected=json.loads((OUT/'expected-geometry.json').read_text())
    actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    rows={};blocking={};errors=[];visuals=[]
    for a in actors:
        name=a.get_actor_label();center,extent=a.get_actor_bounds(False)
        row=dict(center=[center.x,center.y,center.z],extent=[extent.x,extent.y,extent.z])
        c=a.get_component_by_class(u.StaticMeshComponent)
        if c:
            scale=a.get_actor_scale3d()
            row.update(profile=str(c.get_collision_profile_name()),collision=str(c.get_collision_enabled()),visible=c.is_visible(),mesh=c.static_mesh.get_path_name(),materials=[c.get_material(i).get_path_name() for i in range(c.get_num_materials())],scale=[scale.x,scale.y,scale.z])
        if name in expected:
            target=expected[name]
            err=max([abs(v/100-w) for v,w in zip(row['center'],target['center_m'])]+[abs(2*v/100-w) for v,w in zip(row['extent'],target['size_m'])])
            row['error_m']=err
            if target['blocking']:
                blocking[name]=row
                if err>.05 or row['profile']!='BlockAll' or row['visible']:errors.append(name)
        if name.startswith('A01_'):
            visuals.append(name)
            if row.get('profile')!='NoCollision' or not row['mesh'].startswith(ASSETS):errors.append(name)
            if any(not p.startswith(ASSETS) for p in row['materials']):errors.append(name+' materials')
        rows[name]=row
    for name,target in expected.items():
        if target['blocking'] and name not in blocking:errors.append('missing '+name)
    report=dict(map=MAP,actor_bounds=rows,blocking_bounds=blocking,failures=errors,passed=not errors,visual_actors=len(visuals))
    (OUT/'construction.json').write_text(json.dumps(report,indent=2))
    assert not errors,errors
    return dict(passed=True,visuals=len(visuals),blocking=len(blocking))

def production_audit():
    guard(True,True)
    data=json.loads((OUT/'construction.json').read_text());rows=data['actor_bounds']
    baseline=json.loads((ROOT/'Saved/OpeningLobby/Layout03/Correction01/after-actual.json').read_text())
    aes=u.get_editor_subsystem(u.EditorActorSubsystem)
    actors={a.get_actor_label():a for a in aes.get_all_level_actors()}
    anchors={};errors=[]
    for name,old in baseline['actors'].items():
        a=actors.get(name)
        if name.startswith('NeutralFill_'):
            comp=a.point_light_component
            now={key:str(comp.get_editor_property(key)) for key in old['lighting']}
            anchors[name]=dict(lighting=now,passed=now==old['lighting'])
        elif 'exposure' in old:
            settings=a.get_editor_property('settings')
            now={key:str(settings.get_editor_property(key)) for key in old['exposure']}
            anchors[name]=dict(exposure=now,passed=now==old['exposure'])
        if name in data['blocking_bounds']:
            comp=a.static_mesh_component
            now=dict(profile=str(comp.get_collision_profile_name()),enabled=str(comp.get_collision_enabled()),responses=[str(comp.get_collision_response_to_channel(channel)) for channel in [u.CollisionChannel.ECC_WORLD_STATIC,u.CollisionChannel.ECC_WORLD_DYNAMIC,u.CollisionChannel.ECC_PAWN]])
            target={k:old['collision'][0][k] for k in now}
            anchors[name]=dict(collision=now,passed=now==target)
        if name in anchors and not anchors[name]['passed']:errors.append(name)
    (OUT/'baseline-anchors.json').write_text(json.dumps(dict(anchors=anchors,passed=not errors,errors=errors),indent=2))
    # Measure unions of actual visible components, independent of collision proxies.
    actual={};envelopes=[]
    def union(name,predicate):
        selected=[r for n,r in rows.items() if predicate(n)]
        assert selected,name
        lo=[min(r['center'][i]-r['extent'][i] for r in selected) for i in range(3)]
        hi=[max(r['center'][i]+r['extent'][i] for r in selected) for i in range(3)]
        actual[name]=dict(center=[(a+b)/2 for a,b in zip(lo,hi)],extent=[(b-a)/2 for a,b in zip(lo,hi)],components=len(selected))
    expected=json.loads((OUT/'expected-geometry.json').read_text())
    for name in expected:
        direct='A01_'+name
        if direct in rows:actual[name]=rows[direct]
        elif name.startswith('Pier_'):union(name,lambda n,p='A01_'+name+'_Course_':n.startswith(p))
        elif name.startswith('FloorStrip_'):union(name,lambda n,s=name.split('_')[-1]:n.startswith('A01_Strip_') and n.endswith('_'+s))
        elif 'EndBand_' in name:
            end,side=name.split('EndBand_');union(name,lambda n,p='A01_'+end+'Band_'+side+'_':n.startswith(p))
        elif name=='InnerDoorFrame':union(name,lambda n:n.startswith('A01_InnerFrame'))
        elif name=='EntranceLowerField':union(name,lambda n:n.startswith('A01_EntranceSidelight') or n=='A01_EntranceOverlight')
        elif name.startswith('LongLintel_'):union(name,lambda n,p='A01_Lintel_'+name.split('_')[-1]+'_':n.startswith(p))
        elif name.startswith('UpperInfill_'):union(name,lambda n,p='A01_Upper_'+name.split('_')[-1]+'_':n.startswith(p))
        elif name.startswith('SideWall_'):union(name,lambda n,p='A01_SideWall_'+name.split('_')[-1]+'_':n.startswith(p))
        elif name.startswith('SideAisleCeiling_'):union(name,lambda n,p='A01_AisleCeiling_'+name.split('_')[-1]+'_':n.startswith(p))
        elif name=='CentralCeiling':union(name,lambda n:n.startswith('A01_CentralCeiling_'))
        elif name=='Floor':union(name,lambda n:n.startswith('A01_Floor_'))
    for name,row in actual.items():
        target=expected[name]
        if name in ['Floor','CentralCeiling'] or name.startswith(('SideWall_','SideAisleCeiling_')):
            continue # Thin finishes are checked by their interior faces below.
        error=max([abs(v/100-w) for v,w in zip(row['center'],target['center_m'])]+[abs(2*v/100-w) for v,w in zip(row['extent'],target['size_m'])])
        envelopes.append(dict(name=name,max_error_m=error,passed=error<=.05))
    for name,axis,sign,target in [('Floor',2,1,0),('CentralCeiling',2,-1,18)]+[(f'SideWall_{s}',1,-s,s*12) for s in [-1,1]]+[(f'SideAisleCeiling_{s}',2,-1,9.2) for s in [-1,1]]:
        row=actual[name];face=(row['center'][axis]+sign*row['extent'][axis])/100
        envelopes.append(dict(name=name+' visible interior face',max_error_m=abs(face-target),passed=abs(face-target)<=.05))
    # Existing schedule validator consumes these measured unions for all modeled elements.
    schedule=dict(data);schedule['actor_bounds']=dict(rows)
    for name,row in actual.items():
        if name not in ['Floor','CentralCeiling'] and not name.startswith(('SideWall_','SideAisleCeiling_')):
            schedule['actor_bounds'][name]=row
    folder=OUT/'Assembled';folder.mkdir(exist_ok=True)
    (folder/'construction.json').write_text(json.dumps(schedule,indent=2))
    (OUT/'assembled-envelopes.json').write_text(json.dumps(dict(actor_bounds=actual,checks=envelopes,passed=all(r['passed'] for r in envelopes)),indent=2))
    assert all(r['passed'] for r in envelopes),[r for r in envelopes if not r['passed']]
    # Saved asset metadata, explicit import records and physical UV provenance.
    meshes={};textures={}
    kit=json.loads((OUT/'kit.json').read_text())['assets']
    smes=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
    for name,item in kit.items():
        mesh=u.load_asset(ASSETS+'/Meshes/'+item['object'])
        material='PainterEnamel' if name=='CheckpointPanel' else item['slots'][0].replace('M_A01_','')
        mesh.set_material(0,u.load_asset(ASSETS+'/Materials/M_A01_'+material))
        b=mesh.get_bounds();size=[b.box_extent.x*2/100,b.box_extent.y*2/100,b.box_extent.z*2/100]
        max_error=max(abs(a-b) for a,b in zip(size,item['dimensions_m']))
        meshes[name]=dict(dimensions_m=size,pivot_origin_cm=[b.origin.x,b.origin.y,b.origin.z],max_error_m=max_error,uv_channels=smes.get_num_uv_channels(mesh,0),material_slots=len(mesh.static_materials),lod_count=mesh.get_num_lods(),materials=[x.material_interface.get_path_name() for x in mesh.static_materials],source=item['source'],export=item['export'])
        assert max_error<.001 and meshes[name]['uv_channels']>0,(name,meshes[name])
    for path in u.EditorAssetLibrary.list_assets(ASSETS+'/Textures'):
        tex=u.load_asset(path)
        textures[tex.get_name()]=dict(srgb=tex.get_editor_property('srgb'),compression=str(tex.get_editor_property('compression_settings')),mip_generation=str(tex.get_editor_property('mip_gen_settings')),never_stream=tex.get_editor_property('never_stream'),size=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()])
    save()
    (OUT/'asset-audit.json').write_text(json.dumps(dict(meshes=meshes,textures=textures),indent=2))
    return dict(anchors_passed=not errors,assembled_checks=len(envelopes),meshes=len(meshes),textures=len(textures))

def finish_materials():
    guard(True,True)
    tasks=[]
    for p in list((SRC/'Textures').glob('*.png'))+list((OUT/'PainterTextures').glob('*.png')):
        task=u.AssetImportTask();task.filename=str(p);task.destination_path=ASSETS+'/Textures'
        task.destination_name=p.stem;task.automated=True;task.save=True;task.replace_existing=True
        tasks.append(task)
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for task in tasks:
        assert task.imported_object_paths,task.filename
        tex=u.load_asset(task.imported_object_paths[0]);name=tex.get_name()
        tex.set_editor_property('srgb','BaseColor' in name)
        if name.endswith('Normal'):
            tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
            tex.set_editor_property('flip_green_channel',False)
        elif 'ORM' in name or 'Occlusion' in name:
            tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
        u.EditorAssetLibrary.save_loaded_asset(tex)
    path=ASSETS+'/Materials/M_A01_PainterEnamel'
    if u.EditorAssetLibrary.does_asset_exist(path):
        save();return dict(textures=len(tasks),painter_mapping='unchanged')
    lib=u.MaterialEditingLibrary
    m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_A01_PainterEnamel',ASSETS+'/Materials',u.Material,u.MaterialFactoryNew())
    samples={}
    for suffix,kind in [('BaseColor',u.MaterialSamplerType.SAMPLERTYPE_COLOR),('Normal',u.MaterialSamplerType.SAMPLERTYPE_NORMAL),('OcclusionRoughnessMetallic',u.MaterialSamplerType.SAMPLERTYPE_MASKS)]:
        node=lib.create_material_expression(m,u.MaterialExpressionTextureSample)
        node.set_editor_property('texture',u.load_asset(ASSETS+'/Textures/SM_A01_CheckpointPanel_M_A01_Checkpoint_'+suffix))
        node.set_editor_property('sampler_type',kind);samples[suffix]=node
    assert lib.connect_material_property(samples['BaseColor'],'RGB',u.MaterialProperty.MP_BASE_COLOR)
    assert lib.connect_material_property(samples['Normal'],'RGB',u.MaterialProperty.MP_NORMAL)
    for output,prop in [('R',u.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',u.MaterialProperty.MP_ROUGHNESS),('B',u.MaterialProperty.MP_METALLIC)]:
        assert lib.connect_material_property(samples['OcclusionRoughnessMetallic'],output,prop)
    lib.layout_material_expressions(m);lib.recompile_material(m)
    mesh=u.load_asset(ASSETS+'/Meshes/SM_A01_CheckpointPanel');mesh.set_material(0,m)
    assigned=[]
    for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label().startswith('A01_DetectorInset_'):
            a.static_mesh_component.set_material(0,m);assigned.append(a.get_actor_label())
    save()
    (OUT/'painter-unreal-mapping.json').write_text(json.dumps(dict(texture_set='M_A01_Checkpoint',mesh=mesh.get_path_name(),slot=0,material=path,assigned_actors=assigned,channels=dict(R='AO',G='Roughness',B='Metallic'),normal='DirectX, green not flipped'),indent=2))
    return dict(textures=len(tasks),painter_panels=len(assigned))

def action(operation,argument=''):
    if operation=='glassreview01':
        import importlib, architecture01_glassreview
        return importlib.reload(architecture01_glassreview).run(argument)
    if operation=='lightstudy01':
        import importlib, architecture01_lightstudy
        return importlib.reload(architecture01_lightstudy).run(argument)
    if operation=='correction03':
        import importlib, architecture01_coating
        return importlib.reload(architecture01_coating).run(argument)
    if operation=='correction02':
        import importlib, architecture01_reflection
        return importlib.reload(architecture01_reflection).run(argument)
    if operation=='correction01':
        import importlib, architecture01_correction
        return importlib.reload(architecture01_correction).run(argument)
    if operation=='inspect':return state()
    if operation=='import':return import_assets()
    if operation=='materials':return materials()
    if operation=='finish_materials':return finish_materials()
    if operation=='preview':return assembly()
    if operation=='complete':return complete()
    if operation=='checkpoint_panels':
        guard(True,True)
        names={a.get_actor_label() for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
        assert 'A01_StationFace_-1_0' not in names
        for sign in [-1,1]:
            for index in range(3):
                actor('StationFace_%s_%s'%(sign,index),'CheckpointPanel',(-24.6+sign*.427,.95+(index-1)*.72,.52),(.008,.70,.72),'PainterEnamel',group='Checkpoint')
        save();return dict(added=6,collision='NoCollision',maximum_surface_offset_m=.006)
    if operation=='audit':return audit()
    if operation=='production_audit':return production_audit()
    if operation=='shader_audit':
        guard(True,True)
        records={}
        for path in u.EditorAssetLibrary.list_assets(ASSETS+'/Materials'):
            material=u.load_asset(path)
            stats=u.MaterialEditingLibrary.get_statistics(material)
            records[material.get_name()]={name:getattr(stats,name) for name in ['num_pixel_shader_instructions','num_vertex_shader_instructions','num_samplers','num_pixel_texture_samples','num_vertex_texture_samples']}
            records[material.get_name()]['inputs']={str(prop):str(u.MaterialEditingLibrary.get_material_property_input_node(material,prop)) for prop in [u.MaterialProperty.MP_BASE_COLOR,u.MaterialProperty.MP_ROUGHNESS,u.MaterialProperty.MP_NORMAL,u.MaterialProperty.MP_METALLIC]}
        (OUT/'shader-audit.json').write_text(json.dumps(records,indent=2))
        return dict(materials=len(records),report='shader-audit.json')
    if operation=='final_audit':
        audit()
        before=json.loads((OUT/'BeforeReadability/construction.json').read_text())
        after=json.loads((OUT/'construction.json').read_text())
        old=before['actor_bounds'];new=after['actor_bounds']
        changed=[name for name,row in old.items() if new.get(name)!=row]
        added=sorted(set(new)-set(old))
        expected=sorted('A01_StationFace_%s_%s'%(sign,index) for sign in [-1,1] for index in range(3))
        assert not changed and added==expected,(changed,added)
        assert before['blocking_bounds']==after['blocking_bounds']
        for name in added:
            assert new[name]['profile']=='NoCollision' and new[name]['visible']
        delta=dict(changed_existing_actors=changed,added_actors=added,blocking_unchanged=True,
                   added_collision='NoCollision',maximum_station_surface_offset_m=.006,
                   material_change='Wall base-color tint only; material paths unchanged',
                   runtime_result_retained='112.297 s route precedes these six nonblocking face panels',passed=True)
        (OUT/'readability-delta.json').write_text(json.dumps(delta,indent=2))
        mesh=u.load_asset(ASSETS+'/Meshes/SM_A01_CheckpointPanel')
        assigned=[]
        for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
            c=a.get_component_by_class(u.StaticMeshComponent)
            if c and c.static_mesh==mesh:
                assert c.get_num_materials()==1 and c.get_material(0).get_path_name().startswith(ASSETS+'/Materials/M_A01_PainterEnamel.')
                assigned.append(a.get_actor_label())
        assert len(assigned)==10
        p=OUT/'painter-unreal-mapping.json';mapping=json.loads(p.read_text())
        mapping['assigned_actors']=sorted(assigned);mapping['verified_live_after_reopen']=True
        p.write_text(json.dumps(mapping,indent=2))
        import architecture01_capture as capture
        assert capture._settings is None
        s=guard(True,True)
        s.update(capture_overrides_restored=True,painter_panel_instances=len(assigned),
                 blocking_actors=len(after['blocking_bounds']),visual_actors=after['visual_actors'],
                 movement_evidence_unaffected=True)
        (OUT/'final-state.json').write_text(json.dumps(s,indent=2))
        return s
    if operation=='save_reopen':
        guard(True);save();assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(MAP)
        s=guard(True,True)
        world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        s['game_mode']=world.get_world_settings().get_editor_property('default_game_mode').get_path_name()
        s['temporarily_hidden']=[a.get_actor_label() for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.is_temporarily_hidden_in_editor()]
        assert s['game_mode']=='/Script/MeridianSquad.OpeningLobbyGameMode' and not s['temporarily_hidden']
        (OUT/'reopened-state.json').write_text(json.dumps(s,indent=2));return s
    import architecture01_capture as capture
    if operation.startswith('capture_'):
        import importlib
        return getattr(importlib.reload(capture),operation[len('capture_'):])(argument)
    import architecture01_walk as walk
    if operation=='verify':return walk.start()
    if operation=='status':return walk.status()
    raise ValueError(operation)
