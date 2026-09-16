float h = saturate((WorldCm.z - FadeStartCm) / max(FadeEndCm - FadeStartCm, 1.0));
// Broad cubic light transmission avoids duplicating the sharper extinction curve.
return (1.0-h)*(1.0-h)*(1.0+2.0*h);