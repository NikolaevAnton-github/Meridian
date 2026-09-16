// Analytic Beer-Lambert absorption through a world-anchored upper half-space.
// Density begins with zero slope at 13.7m: sigma(z)=0.034*(height/410)^2 per cm.
float span = max(FadeEndCm-FadeStartCm,1.0);
float a = max(CameraCm.z-FadeStartCm,0.0);
float b = max(WorldCm.z-FadeStartCm,0.0);
float dz = WorldCm.z-CameraCm.z;
float distanceCm = length(WorldCm-CameraCm);
float integral = abs(dz)>0.01 ? abs(b*b*b-a*a*a)*distanceCm/(3.0*abs(dz)*span*span) : distanceCm*a*a/(span*span);
float transmittance = exp(-0.034*integral);
// Exact terminal suppression is confined to the roof margin, above useful volume.
float roof = saturate((WorldCm.z-FadeEndCm)/20.0);
return transmittance*(1.0-roof*roof*(3.0-2.0*roof));