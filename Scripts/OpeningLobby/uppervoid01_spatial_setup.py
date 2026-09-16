"""Isolate the inspected HC03 adapters for the bounded HC04 diagnostic."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'Scripts/OpeningLobby'
for suffix in ['unreal','tools','client','capture','runtime']:
    source=(S/('uppervoid01_volume_'+suffix+'.py')).read_text()
    source=source.replace('uppervoid01_volume_','uppervoid01_spatial_').replace('OpeningLobbyUpperVoid01VolumeTools','OpeningLobbyUpperVoid01SpatialTools').replace('UpperVoid01/HeightCorrection03','UpperVoid01/HeightCorrection04')
    if suffix=='capture':
        source=source.replace("['Before','IsolatePP','IsolateLF','Trial01','Trial02','Final']","['Before','Disabled','WorldZ','Transmission','Trial01','Final']")
        source=source.replace("_original_shoot=", "base.cap.VIEWS['lateral-column-90']=(-1551.150808,330.164361,0,74.912516)\n_original_shoot=")
        source=source.replace("view=='close-column-90'", "view in ['close-column-90','lateral-column-90']")
        source=source.replace("lighting='Baseline lighting' if folder=='Before' else 'UpperVoid01 scheduled lighting and postprocess; intentionally different from baseline'", "lighting='All scene lights fixed; dedicated atmosphere diagnostic/correction only'")
    target=S/('uppervoid01_spatial_'+suffix+'.py')
    assert not target.exists(),target
    target.write_text(source,encoding='utf-8')
print('HC04 adapters ready')
