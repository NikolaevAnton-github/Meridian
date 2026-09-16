"""Native editable physical slab joints over the unchanged accepted Painter face graph."""
import json
import unreal as u
from materialscomplete01_slabs_unreal import ROOT,OUT,ASSETS,STONE,LIB,guard,write

# Dominant geometric plane selects one grid. Integral box filtering preserves
# the true subpixel joint area instead of widening distant lines to one pixel.
LAYOUT_CODE='''
float3 p = WorldCm - OriginCm;
float3 a = abs(GeometryNormal);
int plane = a.x >= a.y && a.x >= a.z ? 0 : (a.y >= a.z ? 1 : 2);
float2 uv = plane == 0 ? p.yz : (plane == 1 ? p.xz : p.xy);
float2 module = float2(WidthCm, HeightCm);
float2 enabled = float2(1,1);
if (plane == 2) {
    bool alongX = ExtentCm.x >= ExtentCm.y;
    uv = alongX ? p.xy : p.yx;
    module = float2(HeightCm,HeightCm); enabled.y = 0;
}
if (LayoutMode > 0.5 && LayoutMode < 1.5) { uv = p.xz; module.x=HeightCm; enabled.y=0; }
if (LayoutMode > 1.5 && LayoutMode < 2.5) { uv = p.yz; module.x=HeightCm; enabled.y=0; }
if (LayoutMode > 2.5) {
    // Composite elevator frame: two slender jambs and a continuous head.
    uv = WorldCm.z < 420 ? p.zy : p.yz;
    module.x=HeightCm; enabled.y=0;
}
float2 q = (frac(uv/module+0.5)-0.5)*module;
float2 footprint=max(abs(ddx(uv))+abs(ddy(uv)),0.0001);
float halfWidth=JointWidthCm*0.5;
float2 lo=q-footprint*0.5, hi=q+footprint*0.5;
float2 coverage=saturate((min(hi,halfWidth)-max(lo,-halfWidth))/footprint)*enabled;
// When many joints enter one footprint, converge to physical area coverage.
coverage=lerp(coverage,JointWidthCm/module*enabled,saturate((footprint-module*0.5)/(module*0.5)));
float mask=1-(1-coverage.x)*(1-coverage.y);
float bevel=max(min(JointWidthCm*0.25,0.15),0.02);
float2 edgeT=saturate((abs(q)-(halfWidth-bevel))/bevel);
float2 slope=sign(q)*JointDepthCm/bevel*6*edgeT*(1-edgeT)*enabled;
slope*=saturate(1-footprint/(JointWidthCm*2));
return float3(mask,slope.x,slope.y);
'''
NORMAL_CODE='''
float3 a=abs(GeometryNormal);
int plane=a.x>=a.y && a.x>=a.z?0:(a.y>=a.z?1:2);
float3 U=plane==0?float3(0,1,0):float3(1,0,0);
float3 V=plane==2?float3(0,1,0):float3(0,0,1);
if(plane==2 && ExtentCm.x<ExtentCm.y){U=float3(0,1,0);V=float3(1,0,0);}
if(LayoutMode>0.5 && LayoutMode<1.5){U=float3(1,0,0);V=float3(0,0,1);}
if(LayoutMode>1.5 && LayoutMode<2.5){U=float3(0,1,0);V=float3(0,0,1);}
if(LayoutMode>2.5){U=WorldCm.z<420?float3(0,0,1):float3(0,1,0);V=float3(0,0,0);}
float3 gradient=U*Layout.g+V*Layout.b;
gradient-=GeometryNormal*dot(gradient,GeometryNormal);
return normalize(FaceNormal-gradient);
'''
def build():
    guard(True,True);path=ASSETS+'/M_Slabs01'
    assert not u.EditorAssetLibrary.does_asset_exist(path)
    m=u.EditorAssetLibrary.duplicate_asset(STONE,path);assert m
    def node(cls,**kwargs):
        n=LIB.create_material_expression(m,cls)
        for k,v in kwargs.items():n.set_editor_property(k,v)
        return n
    def wire(a,b,pin='',out=''):assert LIB.connect_material_expressions(a,out,b,pin)
    def output(a,key):assert LIB.connect_material_property(a,'',getattr(u.MaterialProperty,'MP_'+key))
    def scalar(name,value):return node(u.MaterialExpressionScalarParameter,parameter_name=name,default_value=value)
    def vector(name,value):return node(u.MaterialExpressionVectorParameter,parameter_name=name,default_value=u.LinearColor(*value,1))
    def custom(code,inputs):
        ii=[]
        for name in inputs:
            i=u.CustomInput();i.set_editor_property('input_name',name);ii.append(i)
        n=node(u.MaterialExpressionCustom,code=code,inputs=ii,output_type=u.CustomMaterialOutputType.CMOT_FLOAT3)
        for name,src in inputs.items():wire(src,n,name)
        return n
    old={k:LIB.get_material_property_input_node(m,getattr(u.MaterialProperty,'MP_'+k)) for k in ['BASE_COLOR','ROUGHNESS','NORMAL','SPECULAR']}
    assert abs(old['SPECULAR'].get_editor_property('default_value')-.4)<1e-6
    nodes=LIB.get_material_expressions(m)
    world=next(n for n in nodes if isinstance(n,u.MaterialExpressionWorldPosition))
    normal=next(n for n in nodes if isinstance(n,u.MaterialExpressionVertexNormalWS))
    origin=vector('OriginCm',[0,0,0]);extent=vector('ExtentCm',[240,240,840]);mode=scalar('LayoutMode',0)
    layout=custom(LAYOUT_CODE,dict(WorldCm=world,GeometryNormal=normal,OriginCm=origin,ExtentCm=extent,
        WidthCm=scalar('WidthCm',120),HeightCm=scalar('HeightCm',240),JointWidthCm=scalar('JointWidthCm',.5),JointDepthCm=scalar('JointDepthCm',.075),LayoutMode=mode))
    mask=node(u.MaterialExpressionComponentMask,r=True,g=False,b=False,a=False);wire(layout,mask)
    factor=node(u.MaterialExpressionLinearInterpolate,const_a=1);wire(scalar('GroutFaceMultiplier',.32),factor,'B');wire(mask,factor,'Alpha')
    color=node(u.MaterialExpressionMultiply);wire(old['BASE_COLOR'],color,'A');wire(factor,color,'B');output(color,'BASE_COLOR')
    rough=node(u.MaterialExpressionLinearInterpolate);wire(old['ROUGHNESS'],rough,'A');wire(scalar('GroutRoughness',.65),rough,'B');wire(mask,rough,'Alpha');output(rough,'ROUGHNESS')
    finalnormal=custom(NORMAL_CODE,dict(GeometryNormal=normal,FaceNormal=old['NORMAL'],Layout=layout,ExtentCm=extent,LayoutMode=mode,WorldCm=world));output(finalnormal,'NORMAL')
    LIB.layout_material_expressions(m);LIB.recompile_material(m);assert u.EditorAssetLibrary.save_loaded_asset(m)
    return finish_instances(m)
def finish_instances(m):
    rows=json.loads((OUT/'plan.json').read_text())['rows'];instances=[]
    for r in rows:
        name=r['new'].split('/')[-1].split('.')[0]
        a=u.load_asset(ASSETS+'/'+name) if u.EditorAssetLibrary.does_asset_exist(ASSETS+'/'+name) else u.AssetToolsHelpers.get_asset_tools().create_asset(name,ASSETS,u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
        assert a
        LIB.set_material_instance_parent(a,m)
        for k,v in {'OriginCm':r['origin_cm'],'ExtentCm':[b-a for a,b in zip(r['bounds_min_cm'],r['bounds_max_cm'])]}.items():
            LIB.set_material_instance_vector_parameter_value(a,k,u.LinearColor(*v,1))
            actual=LIB.get_material_instance_vector_parameter_value(a,k)
            assert max(abs(getattr(actual,c)-x) for c,x in zip(['r','g','b'],v))<.001
        LIB.set_material_instance_scalar_parameter_value(a,'LayoutMode',r['mode'])
        assert LIB.get_material_instance_scalar_parameter_value(a,'LayoutMode')==r['mode']
        LIB.update_material_instance(a);assert u.EditorAssetLibrary.save_loaded_asset(a)
        instances.append(a.get_path_name())
    recipe=dict(candidate='LobbyMaterials-Complete01/SlabLayout01',master=m.get_path_name(),accepted_face_graph=STONE,
        physical_source_coverage_cm=240,face_roughness='Accepted ORM.G directly, except fractional joint coverage blends grout roughness',
        specular=.4,F0=.032,metallic='Unchanged accepted ORM.B = 0',coat=False,
        basecolor='Unchanged accepted Correction01 triangular phase sampling; no brightness checker or new pixels',
        layout_code=LAYOUT_CODE,normal_code=NORMAL_CODE,rows=rows,instances=instances,
        material_only=True,axes='Identity orthonormal building frame in centimetres, excludes actor scale and import orientation',
        glazing='DEFERRED_BY_OWNER',source_helper='Scripts/OpeningLobby/materialscomplete01_slabs_material.py')
    source=ROOT/'Assets/Source/OpeningLobby/MaterialsComplete01/SlabLayout01';source.mkdir(parents=True,exist_ok=True)
    (source/'recipe.json').write_text(json.dumps(recipe,indent=2));(source/'SlabLayout.hlsl').write_text(LAYOUT_CODE);(source/'SlabNormal.hlsl').write_text(NORMAL_CODE)
    return write('authorship',dict(master=m.get_path_name(),instances=len(instances),source=source.relative_to(ROOT).as_posix()))
