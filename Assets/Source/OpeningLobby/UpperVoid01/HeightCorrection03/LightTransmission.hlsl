// Reserve direct-light attenuation for the roof; the visible shaft ramp belongs to PP.
float h = saturate((WorldCm.z - 1750.0) / 40.0);
return 1.0-h*h*(3.0-2.0*h);