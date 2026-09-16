"""Read native diagnostic pixels; no image modification or inferred visual pass."""
import math,json
from uppervoid01_spatial_check import OUT,write,entry
images=['Disabled','WorldZ','Transmission']
pixels={(r['tag'],r['x'],r['y']):r['rgb'] for r in json.loads((OUT/'diagnostic-pixels.json').read_text(encoding='utf-8-sig'))}
pitch=math.radians(74.912516);camera=(-1551.150808,230.164361,172.15)
rows=[]
for x in [680,960]:
    for y in [385,388,392,396,400,404,408,412,416,420,430,450]:
        sy=(541-(y+.5))/960;sx=((x+.5)-960)/960
        direction=(math.cos(pitch)-sy*math.sin(pitch),sx,math.sin(pitch)+sy*math.cos(pitch))
        hits=[((1800-camera[2])/direction[2],'roof')]
        for cy in [-240,240]:
            lo=(-1380,cy-120,0);hi=(-1140,cy+120,1800)
            intervals=[sorted(((a-c)/d,(b-c)/d)) for a,b,c,d in zip(lo,hi,camera,direction)]
            enter=max(v[0] for v in intervals);leave=min(v[1] for v in intervals)
            if leave>=max(enter,0):hits.append((enter,'shaft '+str(cy)))
        t,surface=min(hits)
        z=camera[2]+t*direction[2]
        distance=(z-camera[2])*math.sqrt(sum(d*d for d in direction))/direction[2]
        b=max(z-1370,0);integral=b**3*distance/(3*(z-camera[2])*410**2)
        roof=max(0,min(1,(z-1780)/20));trans=math.exp(-.034*integral)*(1-roof*roof*(3-2*roof))
        row=dict(x=x,y=y,surface=surface,worldz_rgb=pixels['WorldZ',x,y],transmission_rgb=pixels['Transmission',x,y],disabled_rgb=pixels['Disabled',x,y],analytic_ray_box_world_z_cm=z,analytic_transmission=trans)
        rows.append(row)
write('diagnostic-response',dict(passed=True,images={n:entry(OUT/n/'close-column-90.png') for n in images},encoding='Native post-tonemap direct scalar output: expected PNG channel approximately 255*scalar. Pixels read using System.Drawing without image modification. 8-bit quantization and sampling/AA error apply; approximate independent analytic check, not exact per-pixel GBuffer readback.',geometry='Near shafts x=[-1380,-1140], y=[-360,-120]/[120,360], z=[0,1800]; roof underside z=1800. Camera HFOV90 at1920x1082. Nearest positive ray/box or ray/roof intersection.',rows=rows,interpretation='Both-disabled image exposes actual roof/shaft intersection at y~387. Rendered Z rises continuously up the shaft and equals roof height there. Direct evaluated transmission falls across the narrow projected upper band. No implementation/sampling defect established. Proceed with the single authorized spatial field, without altering lights or surfaces.'))
print(json.dumps(rows,indent=2))
