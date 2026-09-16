"""Original editable architecture kit. Run inside the verified local Blender bridge."""
import json
from pathlib import Path
import bpy
import numpy as np

ROOT=Path('D:/devgames/MeridianSquad')
SRC=ROOT/'Assets/Source/OpeningLobby/Architecture01'
OUT=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'

def build():
    assert not (SRC/'LobbyArchitecture01.blend').exists(), 'Preserve existing native source.'
    for p in [SRC/'Textures',OUT/'FBX']:
        p.mkdir(parents=True,exist_ok=True)
    scene=bpy.data.scenes.new('LobbyArchitecture01')
    scene.unit_settings.system='METRIC'
    scene.unit_settings.scale_length=1
    bpy.context.window.scene=scene
    materials={}
    for name,color in [('Stone',(.10,.14,.125)),('Floor',(.16,.21,.18)),('Metal',(.065,.075,.072)),('Glass',(.25,.40,.37)),('Checkpoint',(.08,.11,.10))]:
        m=bpy.data.materials.new('M_A01_'+name)
        m.diffuse_color=(*color,1)
        materials[name]=m
    inventory={}

    def part(name,center,size,mat,bevel=.002):
        bpy.ops.mesh.primitive_cube_add(size=1,location=center)
        obj=bpy.context.object
        obj.name=name
        obj.dimensions=size
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        obj.data.materials.append(materials[mat])
        if bevel:
            mod=obj.modifiers.new('Manufactured edge radius','BEVEL')
            mod.width=bevel
            mod.segments=3
            bpy.ops.object.modifier_apply(modifier=mod.name)
        # Dominant-axis UV0 encodes metres; the Painter panel is unwrapped below.
        uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name='UV_Metres')
        uv.name='UV_Metres'
        for face in obj.data.polygons:
            axis=max(range(3),key=lambda i:abs(face.normal[i]))
            indices=([1,2],[0,2],[0,1])[axis]
            for index in face.loop_indices:
                co=obj.data.vertices[obj.data.loops[index].vertex_index].co
                uv.data[index].uv=(co[indices[0]],co[indices[1]])
        return obj

    def asset(name,parts,unique=False):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in parts: obj.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]
        bpy.ops.object.join()
        obj=bpy.context.object
        obj.name='SM_A01_'+name
        scene.cursor.location=(0,0,0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        if unique:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(island_margin=.025)
            bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.calc_loop_triangles()
        export=OUT/'FBX'/(obj.name+'.fbx')
        bpy.ops.export_scene.fbx(filepath=str(export),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Y',axis_up='Z',use_space_transform=True,bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=True,bake_anim=False,add_leaf_bones=False)
        inventory[name]=dict(object=obj.name,dimensions_m=list(obj.dimensions),vertices=len(obj.data.vertices),triangles=len(obj.data.loop_triangles),slots=[m.name for m in obj.data.materials],uv_layers=len(obj.data.uv_layers),uv_mode='unique 0-1 Painter atlas' if unique else 'metres per UV unit; UE world projection preserves fitted panel scale',source=str((SRC/'LobbyArchitecture01.blend').relative_to(ROOT)),export=str(export.relative_to(ROOT)))
        return obj

    # Four closed slabs fit within a 2.4 m square envelope. Seams are inset.
    parts=[]
    for sign in [-1,1]:
        parts.append(part('Pier face',(0,sign*1.17,0),(2.4,.06,2.796),'Stone',.002))
        parts.append(part('Pier return',(sign*1.17,0,0),(.06,2.276,2.796),'Stone',.002))
    asset('PierCourse',parts)
    for name,size,mat,bevel in [
        ('WallPanel',(2.4,.04,2.8),'Stone',.0015),
        ('Lintel',(2.4,2.4,2.8),'Stone',.003),
        ('CeilingPanel',(2.4,4,.04),'Stone',.001),
        ('FloorTile',(1.198,1.198,.04),'Floor',.0005),
        ('FloorStrip',(1.2,.64,.002),'Floor',.00025),
        ('EndPanel',(.01,2.4,2.8),'Stone',.001),
        ('Mullion',(.04,.04,1),'Metal',.001),
        ('GlassPane',(.01,1,1),'Glass',.0004),
        ('DoorLeaf',(.01,1.04,2.18),'Metal',.001),
        ('EntryLeaf',(.01,1.04,2.64),'Glass',.001),
        ('DetectorPost',(.55,.16,2.28),'Checkpoint',.004),
        ('DetectorHeader',(.55,1.46,.14),'Checkpoint',.004),
        ('StationBody',(.85,2.2,.96),'Checkpoint',.004),
        ('StationWorktop',(.95,2.3,.06),'Metal',.003),
        ('Trim',(1,.025,.04),'Metal',.001),
        ('Hardware',(.02,.025,.4),'Metal',.002)]:
        asset(name,[part(name,(0,0,0),size,mat,bevel)])
    # Small original atlas for repeatable detector enclosure faces; Painter owns its finish.
    asset('CheckpointPanel',[part('Inset front',(0,0,0),(.008,.12,.72),'Checkpoint',.002)],True)
    bpy.data.libraries.write(str(SRC/'LobbyArchitecture01.blend'),{scene},fake_user=True,compress=True)
    (OUT/'kit.json').write_text(json.dumps(dict(blender=bpy.app.version_string,assets=inventory),indent=2))
    print(json.dumps(dict(assets=len(inventory),source=str(SRC/'LobbyArchitecture01.blend'))))

def textures(revision=False):
    if revision:
        import shutil
        archive=OUT/(revision if isinstance(revision,str) else 'Preview01Textures');archive.mkdir(exist_ok=False)
        for p in (SRC/'Textures').glob('*.png'):shutil.copy2(p,archive/p.name)
    else:
        assert not (SRC/'Textures/T_A01_Stone_BaseColor.png').exists()
    n=1024
    y,x=np.mgrid[0:n,0:n].astype(np.float32)/n
    rng=np.random.default_rng(190614)
    def noise(start,end,count):
        # Dense isotropic spectrum avoids the crosshatching of a few plane waves.
        freq=np.fft.fftfreq(n)*n
        radius2=freq[:,None]**2+freq[None,:]**2
        spectrum=np.fft.fft2(rng.standard_normal((n,n)))
        band=np.exp(-radius2/(end*end))*(1-np.exp(-radius2/max(start*start,1)))
        a=np.fft.ifft2(spectrum*band).real
        return (a/max(a.std(),1e-8)).astype(np.float32)
    coarse=noise(1,6,24); medium=noise(10,70,40); fine=noise(100,380,48)
    veins=np.exp(-np.abs(coarse+.18*medium)*42)
    fineveins=np.exp(-np.abs(noise(4,18,24)+.1*medium)*65)
    def write(name,rgb):
        if rgb.ndim==2: rgb=np.repeat(rgb[:,:,None],3,axis=2)
        rgba=np.concatenate((np.clip(rgb,0,1),np.ones((n,n,1),np.float32)),axis=2).astype(np.float32)
        im=bpy.data.images.new(name,width=n,height=n,alpha=True,float_buffer=False)
        im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(rgba.ravel())
        im.filepath_raw=str(SRC/'Textures'/(name+'.png'))
        im.file_format='PNG'; im.save()
        bpy.data.images.remove(im)
    for kind,base,amount,rough in [('Stone',(.245,.29,.265),.035,.32),('Floor',(.245,.31,.275),.25,.145)]:
        detail=.009*medium+.01*fine+.022*coarse+amount*veins+.035*fineveins
        rgb=np.stack([np.clip(b+detail,0,1) for b in base],axis=2)
        write('T_A01_'+kind+'_BaseColor',rgb)
        r=np.clip(rough+.02*medium-.035*veins,.12,.5)
        write('T_A01_'+kind+'_ORM',np.stack([np.ones_like(r),r,np.zeros_like(r)],axis=2))
        height=.004*medium+.004*fine+.003*veins
        dx=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.14
        dy=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.14
        norm=np.stack([-dx,dy,np.ones_like(dx)],axis=2)
        norm/=np.linalg.norm(norm,axis=2)[:,:,None]
        write('T_A01_'+kind+'_Normal',norm*.5+.5)
    (OUT/'texture-design.json').write_text(json.dumps(dict(size=[n,n],seed=190614,period_m=4,normal='DirectX',channels='ORM: R ambient occlusion, G roughness, B metallic',source='Original periodic Fourier fields; no downloaded or reference pixels',reuse='Two shared 1024 texture sets; world-space 4 m period plus low-frequency variation'),indent=2))
    print('Saved six original periodic 1024 PNG source textures.')

def finalize_source():
    """Keep editable preview shaders and packed canonical texture inputs in the native kit."""
    import shutil
    source=SRC/'LobbyArchitecture01.blend'
    archive=OUT/'GeometryOnly-LobbyArchitecture01.blend'
    assert source.exists() and not archive.exists()
    shutil.copy2(source,archive)
    scene=bpy.data.scenes['LobbyArchitecture01']
    for mat in {m for ob in scene.objects if ob.type=='MESH' for m in ob.data.materials}:
        mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
        shader=nodes.new('ShaderNodeBsdfPrincipled');output=nodes.new('ShaderNodeOutputMaterial');links.new(shader.outputs['BSDF'],output.inputs['Surface'])
        shader.inputs['Base Color'].default_value=mat.diffuse_color
        kind='Stone' if mat.name.endswith('Stone') else ('Floor' if mat.name.endswith('Floor') else None)
        if not kind:
            shader.inputs['Metallic'].default_value=.65 if mat.name.endswith(('Metal','Checkpoint')) else 0
            shader.inputs['Roughness'].default_value=.3
            continue
        coord=nodes.new('ShaderNodeTexCoord');scale=nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.25
        links.new(coord.outputs['UV'],scale.inputs[0])
        for suffix in ['BaseColor','ORM','Normal']:
            image=bpy.data.images.load(str(SRC/'Textures'/('T_A01_'+kind+'_'+suffix+'.png')),check_existing=False)
            image.colorspace_settings.name='sRGB' if suffix=='BaseColor' else 'Non-Color';image.pack()
            node=nodes.new('ShaderNodeTexImage');node.image=image;links.new(scale.outputs['Vector'],node.inputs['Vector'])
            if suffix=='BaseColor':links.new(node.outputs['Color'],shader.inputs['Base Color'])
            elif suffix=='ORM':
                split=nodes.new('ShaderNodeSeparateColor');links.new(node.outputs['Color'],split.inputs['Color'])
                links.new(split.outputs['Green'],shader.inputs['Roughness']);links.new(split.outputs['Blue'],shader.inputs['Metallic'])
            else:
                # Convert saved DirectX green to Blender's OpenGL tangent normal convention.
                split=nodes.new('ShaderNodeSeparateColor');join=nodes.new('ShaderNodeCombineColor');invert=nodes.new('ShaderNodeMath');invert.operation='SUBTRACT';invert.inputs[0].default_value=1
                links.new(node.outputs['Color'],split.inputs['Color']);links.new(split.outputs['Green'],invert.inputs[1])
                links.new(split.outputs['Red'],join.inputs['Red']);links.new(invert.outputs[0],join.inputs['Green']);links.new(split.outputs['Blue'],join.inputs['Blue'])
                normal=nodes.new('ShaderNodeNormalMap');links.new(join.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    bpy.data.libraries.write(str(source),{scene},fake_user=True,compress=True)
    print(json.dumps(dict(source=str(source),bytes=source.stat().st_size,packed_texture_inputs=6,geometry='unchanged')))

if __name__=='__main__': build(); textures(); finalize_source()
