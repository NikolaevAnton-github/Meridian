"""Isolate inspected adapters; never change predecessor evidence."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'Scripts/OpeningLobby'
for suffix in ['unreal','tools','client','capture','runtime']:
    s=(S/('uppervoid01_soft_'+suffix+'.py')).read_text()
    s=s.replace('uppervoid01_soft_','uppervoid01_volume_').replace('OpeningLobbyUpperVoid01SoftTools','OpeningLobbyUpperVoid01VolumeTools').replace('UpperVoid01/HeightCorrection02','UpperVoid01/HeightCorrection03')
    if suffix=='capture':
        s=s.replace("['Before','Trial01','Trial02','Trial03','Final']","['Before','IsolatePP','IsolateLF','Trial01','Trial02','Final']")
    if suffix=='runtime':
        s=s.replace('age-self.last_frame>=3','age-self.last_frame>=6')
    target=S/('uppervoid01_volume_'+suffix+'.py');assert not target.exists();target.write_text(s,encoding='utf-8')
print('New output adapters ready')
