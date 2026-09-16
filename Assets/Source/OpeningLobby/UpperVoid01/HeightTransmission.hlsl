float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Quintic extinction: zero derivatives at both endpoints, fixed world height.
float extinction = h*h*h*(h*(h*6.0-15.0)+10.0);
return 1.0-extinction;