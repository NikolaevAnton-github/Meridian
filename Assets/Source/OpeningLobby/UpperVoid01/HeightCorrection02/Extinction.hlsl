float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Early visible decay with a long dark tail, anchored exclusively to world height.
float tail = (1.0-h)*(1.0-h)*(1.0+2.0*h);
return exp(-8.0*h*h)*tail;