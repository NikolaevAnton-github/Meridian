// One static, smooth 3D absorption field. World units are centimeters.
// Three oblique low-frequency components have wavelengths 4m, 3m and 5m.
// Their weighted sum lies in [-1,1]; onset therefore remains within 13.7-15.1m.
float3 ray = WorldCm-CameraCm;
float distanceCm = length(ray);
float dz = ray.z;
float t0 = 0.0;
float t1 = 1.0;
if (abs(dz)>0.001) {
    float cross = (1370.0-CameraCm.z)/dz;
    if (dz>0.0) t0=max(t0,cross); else t1=min(t1,cross);
} else if (CameraCm.z<=1370.0) { return 1.0; }
t0=saturate(t0); t1=saturate(t1);
float opticalDepth = 0.0;
[unroll] for (int i=0;i<16;i++) {
    float t=lerp(t0,t1,(i+0.5)/16.0);
    float3 p=CameraCm+ray*t;
    float field=0.55*sin(dot(p,float3(0.72,0.60,0.35))*0.0157079633+0.9)
               +0.30*sin(dot(p,float3(-0.38,0.86,0.34))*0.0209439510+2.1)
               +0.15*sin(dot(p,float3(0.25,-0.43,0.867))*0.0125663706-0.7);
    float onset=1440.0+70.0*field;
    float h=max(p.z-onset,0.0)/max(1780.0-onset,1.0);
    float sigma=0.034*(1.0+0.30*field)*h*h;
    opticalDepth+=sigma;
}
opticalDepth*=distanceCm*max(t1-t0,0.0)/16.0;
// Exact roof concealment at 17.9m, independent of spatial modulation.
float roof=saturate((WorldCm.z-1760.0)/30.0);
return exp(-opticalDepth)*(1.0-roof*roof*(3.0-2.0*roof));