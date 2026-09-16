"""Diagnose the unexpected Painter export channel before making a correction."""
import sys
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Scripts/Benchmarks/OrchestrationAB'))
from verify_maps import decode_png
info,pixels=decode_png((ROOT/'Assets/Source/OpeningLobby/PainterStone01/Channels/T_PainterStone01_ORM.png').read_bytes())
result=dict(channels={name:dict(min=min(pixels[i::4]),max=max(pixels[i::4]),mean=sum(pixels[i::4])/len(pixels[i::4])/255)
    for i,name in enumerate(['AO','Roughness','Metallic'])},png=info)
(ROOT/'Saved/OpeningLobby/PainterStone01/Worker/orm-diagnostic.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
