
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
