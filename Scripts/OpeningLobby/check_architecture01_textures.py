"""Reuse established PNG/UV channel checks without invoking benchmark execution."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/Stage2/Architecture01'
spec=importlib.util.spec_from_file_location('channel_helpers',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
triangles=json.loads((OUT/'checkpoint-uv.json').read_text())
positions=helpers.sample_positions(triangles,1024,1024)
assert len(positions)>=10
reports=[]
for p in sorted((OUT/'PainterTextures').glob('*.png')):
    info,pixels=helpers.decode_png(p.read_bytes())
    assert (info['width'],info['height'])==(1024,1024)
    wanted=[48.45,58.65,53.55] if 'BaseColor' in p.name else ([255,86.7,63.75] if 'Occlusion' in p.name else [128,128,255])
    maximum=0
    for position in positions:
        offset=(position['y']*1024+position['x'])*4
        maximum=max(maximum,max(abs(pixels[offset+i]-wanted[i]) for i in range(3)))
    row=dict(file=p.name,png=info,covered_uv_samples=len(positions),expected_rgb=wanted,max_channel_error=maximum,passed=maximum<=2)
    reports.append(row)
for p in sorted((ROOT/'Assets/Source/OpeningLobby/Architecture01/Textures').glob('*.png')):
    info,pixels=helpers.decode_png(p.read_bytes())
    assert (info['width'],info['height'])==(1024,1024)
    row=dict(file=p.name,png=info,passed=True)
    if '_ORM' in p.name:
        assert all(pixels[i]==255 and pixels[i+2]==0 for i in range(0,len(pixels),4))
        row['roughness_range']=[min(pixels[1::4])/255,max(pixels[1::4])/255]
    elif '_Normal' in p.name:
        row['xy_range']=[min(min(pixels[0::4]),min(pixels[1::4])),max(max(pixels[0::4]),max(pixels[1::4]))]
        assert min(pixels[2::4])>=250
    reports.append(row)
(OUT/'texture-channel-check.json').write_text(json.dumps(dict(passed=all(r['passed'] for r in reports),reports=reports),indent=2))
assert all(r['passed'] for r in reports),reports
print(f'Validated {len(reports)} PNG maps; Painter channel values pass at {len(positions)} covered UV pixels.')
