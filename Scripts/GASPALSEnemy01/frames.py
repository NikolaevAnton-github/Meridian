"""Extract actual, unmodified frames from the retained WGC recordings."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Saved/PurchasedArms04/Worker/PythonPackages'))
import av
name=sys.argv[1]
out=ROOT/'Saved/CombatSlice01/GASPALSEnemy01/Video'
dest=out/(name+'-Frames');dest.mkdir(exist_ok=True)
times=[float(t) for t in sys.argv[2:]]
with av.open(str(out/(name+'.mp4'))) as video:
    for frame in video.decode(video=0):
        if times and frame.time>=times[0]:
            stamp=times.pop(0)
            frame.to_image().save(dest/f'{stamp:06.2f}.png')
        if not times: break
print(dest)
