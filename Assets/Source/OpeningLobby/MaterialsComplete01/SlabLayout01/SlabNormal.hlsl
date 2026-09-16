
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
