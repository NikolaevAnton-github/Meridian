"""Create isolated adapters from inspected, immutable task primitives."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'Scripts/OpeningLobby'
for suffix in ['unreal','tools','client','capture','runtime']:
    s=(S/('uppervoid01_height_'+suffix+'.py')).read_text()
    s=s.replace('uppervoid01_height_','uppervoid01_soft_').replace('OpeningLobbyUpperVoid01HeightTools','OpeningLobbyUpperVoid01SoftTools').replace('UpperVoid01/HeightCorrection01','UpperVoid01/HeightCorrection02')
    if suffix=='unreal':
        s=s.replace("exec(compile(p.read_text(),str(p),'exec'),legacy.__dict__)","source=p.read_text().replace(\"(folder / 'property-schemas.json').write_text(json.dumps(schemas, separators=(',', ':')))\",\"pass # Immutable schema reference retained in predecessor\")\nsource=source.replace(\"(folder / 'all-properties.json').write_text(json.dumps(data, separators=(',', ':')))\",\"__import__('gzip').open(folder / 'all-properties.json.gz','wt',encoding='utf-8').write(json.dumps(data,separators=(',', ':')))\")\nexec(compile(source,str(p),'exec'),legacy.__dict__)")
    if suffix=='capture':
        s=s.replace("def run(operation,argument):", "base.cap.VIEWS['close-column-90']=(-1551.150808,230.164361,0,74.912516)\n_original_shoot=base.cap.shoot\ndef compact_shoot(view):\n    # Reuse native shoot primitive with an explicit per-view capture size.\n    import unreal as u\n    source=(ROOT/'Scripts/OpeningLobby/reworka01_capture.py').read_text()\n    ns={}\n    exec(compile(source,str(ROOT/'Scripts/OpeningLobby/reworka01_capture.py'),'exec'),ns)\n    ns.update(OUT=base.cap.OUT,VIEWS=base.cap.VIEWS,MAP=MAP)\n    if view!='close-column-90':\n        source=source.replace('HighResShot 1920x1080','HighResShot 960x540')\n        exec(compile(source,str(ROOT/'Scripts/OpeningLobby/reworka01_capture.py'),'exec'),ns)\n        ns.update(OUT=base.cap.OUT,VIEWS=base.cap.VIEWS,MAP=MAP)\n    record=ns['shoot'](view)\n    record['resolution']=[1920,1080] if view=='close-column-90' else [960,540]\n    return record\nbase.cap.shoot=compact_shoot\n\ndef run(operation,argument):")
        s=s.replace("r['exposure']=", "r['edits']='None. Native HighResShot PNG at recorded resolution.'\n        r['exposure']=")
    if suffix=='runtime':
        start=s.index('        self.plan=[');end=s.index('\n    def tick',start)
        s=s[:start]+"        self.plan=[('wait','spawn',2),('move','entrance_clear',-2700,-105),('move','lane_align',-2700,465),('move','lane_inbound',-1900,465),('move','axis_align',-1900,0),('move','column_approach',-1560,0),('move','near_column',-1560,240),('look','near_column_up',0,75),('capture','close_column_up',7),('look','nearby_turn',22,68),('wait','turned_up',3),('look','restore_column',0,0)]"+s[end:]
        s=s.replace('age-self.last_frame>=6','age-self.last_frame>=3')
    target=S/('uppervoid01_soft_'+suffix+'.py');assert not target.exists();target.write_text(s,encoding='utf-8')
print('Isolated adapters created')
