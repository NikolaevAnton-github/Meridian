"""Create isolated height-correction adapters from immutable task primitives."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'Scripts/OpeningLobby'
for suffix in ['unreal','tools','client','capture','runtime']:
    source=(S/('uppervoid01_'+suffix+'.py')).read_text()
    source=source.replace('uppervoid01_', 'uppervoid01_height_')
    source=source.replace('OpeningLobbyUpperVoid01Tools','OpeningLobbyUpperVoid01HeightTools')
    source=source.replace('Saved/OpeningLobby/UpperVoid01/Worker','Saved/OpeningLobby/UpperVoid01/HeightCorrection01/Worker')
    if suffix=='capture':
        source=source.replace("'east-aisle-90':(-1150,980,0,12),'west-aisle-90':(1150,-980,180,12)","'east-aisle-90':(-1150,980,0,55),'west-aisle-90':(1150,-980,180,55)")
    if suffix=='unreal':
        source=source.replace("guard(True,True,pie=True);return write('initial-live-state',s)","guard(True,True,pie=state()['pie']);return write('initial-live-state',s)")
    if suffix=='runtime':
        source=source.replace("OUT/'Movement02'","OUT/'Movement'")
        source=source.replace("('move','west_return',-1680,-980)","('look','west_aisle_up',0,65),('capture','west_aisle_up_hold',6),('look','restore_west',0,0),('move','west_return',-1680,-980)")
        source=source.replace('age-self.last_frame>=8','age-self.last_frame>=6')
    target=S/('uppervoid01_height_'+suffix+'.py')
    assert not target.exists(),target
    target.write_text(source,encoding='utf-8')
print('Created five isolated adapters; original helpers unchanged.')
