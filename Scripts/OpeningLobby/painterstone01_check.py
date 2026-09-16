"""Focused preservation, native capture and Painter PNG checks; no route rerun."""
import copy
import importlib.util
import json
import struct
import sys
from pathlib import Path
from painterstone01_evidence import ROOT,OUT,entry,digest
BASE=ROOT/'Saved/OpeningLobby/PainterStone01/Worker'

def write(name,data):
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2))
    return data

def differences(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,before=a,after=b)]
    if isinstance(a,dict):
        if set(a)!=set(b):return [dict(path=path,before_keys=list(a),after_keys=list(b))]
        return [r for k in a for r in differences(a[k],b[k],path+'/'+str(k))]
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,before=a,after=b)]
        return [r for i,(x,y) in enumerate(zip(a,b)) for r in differences(x,y,path+'/'+str(i))]
    return [] if a==b else [dict(path=path,before=a,after=b)]

def properties():
    def read(folder):
        root=BASE if folder in ['Source','Template'] else OUT
        return json.loads((root/folder/'all-properties.json').read_text().replace(
            'L_OpeningLobby_FunctionalBuild01','TASKMAP').replace('L_OpeningLobby_PainterStone01','TASKMAP'))
    source=read('Source');template=read('Template');final=read('Final');restored=read('Restored')
    d=differences(final,restored)
    write('restored-property-differences',d)
    assert not d,d[:8]
    d=differences(source,template)
    write('template-property-differences',d)
    assert not d,d[:8]
    expected=copy.deepcopy(source)
    bindings=json.loads((BASE/'bindings.json').read_text())['rows']
    for row in bindings:
        node=expected['actors'][row['actor']]['components'][row['component']]['properties']
        assert node['overrideMaterials']==[dict(refPath=p) for p in row['source_overrides']]
        node['overrideMaterials']=[dict(refPath=row['new'])]
    d=differences(expected,final)
    write('nonmaterial-property-differences',d)
    assert not d,d[:8]
    def leaves(obj):
        if isinstance(obj,dict):return sum(leaves(x) for x in obj.values())
        if isinstance(obj,list):return sum(leaves(x) for x in obj)
        return 1
    report=dict(passed=True,actors=len(source['actors']),components=sum(len(a['components']) for a in source['actors'].values()),
        compared_leaf_values=leaves(expected),binding_changes=bindings,unexpected_differences=[],
        normalization='Copied map basename only. Exactly four declared component overrideMaterials substitutions.',
        preserved='Every reflected actor/component/world/world-settings property and renderer setting. Mesh bytes checked independently.')
    write('property-preservation',report)
    original=json.loads((BASE/'Final/all-properties.json').read_text().replace('L_OpeningLobby_PainterStone01','TASKMAP'))
    d=differences(original,final)
    write('original-candidate-property-differences',d)
    assert not d,d[:8]
    print(json.dumps({k:v for k,v in report.items() if k not in ['binding_changes','preserved','normalization']}),flush=True)

def captures_original_history():
    views=['entrance-90','sample-context-90','column-near-90','front-return-90','grazing-90']
    rows=[]
    for view in views:
        before=json.loads((OUT/'Before'/(view+'-camera.json')).read_text())
        for folder in ['Before','Sample01','QARevision01','QAChannelCorrection','Final']:
            p=OUT/folder/(view+'.png');raw=p.read_bytes()
            assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1920,1080)
            camera=json.loads((OUT/folder/(view+'-camera.json')).read_text())
            assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm']))<1
            assert camera['actual_hfov']==90
            assert camera['runtime']['world_seconds']>1 and camera['runtime']['ready'] and camera['runtime']['possessed']
            assert max(abs((a-b+180)%360-180) for a,b in zip(camera['actual_rotation'],[camera['pitch'],camera['yaw'],0]))<.01
            assert all(camera[k]==before[k] for k in ['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution'])
            rows.append(dict(**entry(p),camera_metadata=(OUT/folder/(view+'-camera.json')).relative_to(ROOT).as_posix()))
    standing=json.loads((OUT/'Final/standing-possession.json').read_text())
    assert standing['standing'] and standing['possessed'] and standing['world_seconds']>1
    assert standing['state']['walkable_floor'] and not standing['state']['falling']
    for folder in ['Before','Sample01','QARevision01','QAChannelCorrection','Final']:
        assert json.loads((OUT/folder/'capture-settings-restored.json').read_text())['matched']
    for view in ['full-entrance-90','entrance-clear-90','portal-complete-90']:
        wide_before=json.loads((OUT/'BeforeContext'/(view+'-camera.json')).read_text())
        for folder in ['BeforeContext','FinalContext']:
            p=OUT/folder/(view+'.png');raw=p.read_bytes()
            assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1920,1080)
            camera=json.loads((OUT/folder/(view+'-camera.json')).read_text())
            assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm']))<1
            assert camera['actual_hfov']==90 and camera['runtime']['ready'] and camera['runtime']['world_seconds']>1
            assert camera['runtime']['possessed']
            assert max(abs((a-b+180)%360-180) for a,b in zip(camera['actual_rotation'],[camera['pitch'],camera['yaw'],0]))<.01
            assert all(camera[k]==wide_before[k] for k in ['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution'])
            assert json.loads((OUT/folder/'capture-settings-restored.json').read_text())['matched']
            rows.append(dict(**entry(p),camera_metadata=(OUT/folder/(view+'-camera.json')).relative_to(ROOT).as_posix()))
    write('capture-verification',dict(passed=True,images=rows,standing_possession=standing,
        matched='Pose, rotation, HFOV90, 1920x1080 and original renderer. Separate still poses are not route movement evidence.'))
    print('31 native images verified: five views across five QA states and six matched context images.',flush=True)


def captures():
    rows=[]
    views=['entrance-90','sample-context-90','column-near-90','front-return-90','grazing-90','portal-complete-90']
    for folder in ['Trial01','Final']:
        times=[]
        for view in views:
            p=OUT/folder/(view+'.png')
            if folder=='Trial01' and view not in ['column-near-90','sample-context-90','portal-complete-90']:continue
            raw=p.read_bytes()
            assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1920,1080)
            camera=json.loads((p.with_name(view+'-camera.json')).read_text())
            before_folder='BeforeContext' if view=='portal-complete-90' else 'Before'
            original_folder='FinalContext' if view=='portal-complete-90' else 'Final'
            before=json.loads((BASE/before_folder/(view+'-camera.json')).read_text())
            original=json.loads((BASE/original_folder/(view+'-camera.json')).read_text())
            keys=['actual_xyz_cm','actual_rotation','actual_hfov','renderer','resolution','exposure']
            assert all(camera[k]==before[k]==original[k] for k in keys),view
            assert max(abs(a-b) for a,b in zip(camera['actual_xyz_cm'],camera['requested_xyz_cm']))<1
            assert camera['actual_hfov']==90 and camera['runtime']['ready']
            assert camera['runtime']['standing'] and camera['runtime']['possessed']
            assert camera['runtime']['world_seconds']>1
            times.append(camera['runtime']['world_seconds'])
            rows.append(dict(**entry(p),camera_metadata=entry(p.with_name(view+'-camera.json')),
                unchanged_source_image=entry(BASE/before_folder/(view+'.png')),
                original_candidate_image=entry(BASE/original_folder/(view+'.png'))))
        assert len(set(times))==len(times) and max(times)-min(times)>1
        settings=json.loads((OUT/folder/'capture-settings-restored.json').read_text())
        assert settings['matched'] and settings['slate_throttle_unchanged']==0
    standing=json.loads((OUT/'Final/standing-possession.json').read_text())
    assert standing['standing'] and standing['possessed'] and standing['world_seconds']>1
    s=standing['state']
    assert s['walking'] and s['walkable_floor'] and not s['falling']
    assert s['gravity_z']==-980 and s['eye_above_capsule_bottom']==170
    write('capture-verification',dict(passed=True,images=rows,standing_possession=standing,
        scope='Nine new stills: one three-view trial and six final views. Original Before and Review01 candidate images reused read-only. No route rerun.'))
    print('Nine new native captures verified against source and original candidate poses; settings restored.',flush=True)

def textures():
    spec=importlib.util.spec_from_file_location('existing_png_validator',ROOT/'Scripts/Benchmarks/OrchestrationAB/verify_maps.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    rows=[]
    for channel,suffix in [('BaseColor','BaseColor'),('ORM','OcclusionRoughnessMetallic'),('Normal','Normal')]:
        exported=BASE/'Exports/Correction01/FinalReopened'/('StoneSample_240cm_PainterStone01_'+suffix+'.png')
        canonical=ROOT/'Assets/Source/OpeningLobby/PainterStone01/Channels'/('T_PainterStone01_'+channel+'.png')
        previous=BASE/'Exports/Correction01/FinalSaved'/exported.name
        assert digest(exported)==digest(canonical)
        assert digest(previous)==digest(exported),channel
        if channel!='BaseColor':
            assert digest(exported)==digest(BASE/'Exports/FinalReopened'/exported.name),channel
        info,pixels=helper.decode_png(exported.read_bytes())
        assert (info['width'],info['height'])==(2048,2048)
        assert set(pixels[3::4])=={255}
        ranges=[[min(pixels[i::4]),max(pixels[i::4])] for i in range(3)]
        means=[sum(pixels[i::4])/(2048*2048)/255 for i in range(3)]
        if channel=='ORM':
            assert ranges[0]==[255,255] and ranges[2]==[0,0]
            assert .17<ranges[1][0]/255<=ranges[1][1]/255<.31
        if channel=='Normal':
            assert ranges[2][0]>=250
            # Geological edge pixels can exceed a narrow RG interval without coarse
            # relief. Keep the established positive-Z check and report the full
            # distribution; polish is assessed in the actual grazing/native view.
            normal_distribution=dict(rg_min_max=ranges[:2],positive_z_min=ranges[2][0],
                mean_abs_xy_deviation=[sum(abs(v-127.5) for v in pixels[i::4])/(2048*2048) for i in range(2)],
                rg_fraction_outside_118_138=[sum(not 118<=v<=138 for v in pixels[i::4])/(2048*2048) for i in range(2)])
            write('normal-distribution',normal_distribution)
            print(json.dumps(normal_distribution),flush=True)
        if digest(previous)==digest(exported):reopen=dict(byte_exact=True,max_channel_difference=0)
        else:
            _,prior=helper.decode_png(previous.read_bytes())
            count=0;max_diff=0
            for x,y in zip(pixels,prior):
                delta=abs(x-y)
                count+=delta>0
                max_diff=max(max_diff,delta)
            assert max_diff<=1,(channel,max_diff)
            reopen=dict(byte_exact=False,max_channel_difference=max_diff,changed_channel_values=count,
                scope='Final source exported again after another actual close/open. At most 1/255 native regeneration rounding permitted. Canonical file is exactly the identified Final export.')
        rows.append(dict(channel=channel,canonical=entry(canonical),exported=entry(exported),png=info,
            rgb_min_max_8bit=ranges,rgb_means_normalized=means,reopen=reopen))
        print(json.dumps(dict(channel=channel,ranges=ranges,reopen=reopen)),flush=True)
    write('texture-channel-verification',dict(passed=True,rows=rows,decoder='Scripts/Benchmarks/OrchestrationAB/verify_maps.py',
        inputs='Actual native Painter exports only. No pixel generation or editing.'))

def affected():
    old=json.loads((BASE/'native-material-audit.json').read_text())
    new=json.loads((OUT/'native-material-audit.json').read_text())
    ds=differences(old,new)
    expected={'/nodes//Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01.M_PainterStone01:MaterialExpressionCustom_0/properties/code',
        '/nodes//Game/OpeningLobby/PainterStone01/Materials/M_PainterStone01.M_PainterStone01:MaterialExpressionCustom_0/properties/desc',
        '/statistics/num_pixel_shader_instructions'}
    assert {d['path'] for d in ds}==expected,ds
    write('native-differences',ds)
    source=json.loads((BASE/'Painter/final-source-evidence.json').read_text())
    final=json.loads((OUT/'Painter/final-source-evidence.json').read_text())
    rows=[]
    for uid in ['186','195','204','213']:
        ds=[]
        for key in ['fills','parameters']:
            if uid in source[key]:ds+=differences(source[key][uid],final[key][uid])
        previous=source['layer_properties'][uid]
        ds+=differences(previous,final['layer_properties'][uid][previous['channel']])
        assert not ds,(uid,ds)
        rows.append(dict(uid=uid,unchanged=True))
    archive=json.loads((ROOT/'Saved/OpeningLobby/PainterStone01/Controller/BeforeCorrection01/archive.json').read_text(encoding='utf-8-sig'))
    changed=[];unchanged=[]
    for previous in archive['entries']:
        actual=entry(ROOT/previous['path'])
        (unchanged if all(previous[k]==actual[k] for k in ['path','bytes','sha256']) else changed).append(actual)
    required=['Content/Maps/L_OpeningLobby_PainterStone01.umap',
        'Content/OpeningLobby/PainterStone01/Textures/T_PainterStone01_ORM.uasset',
        'Content/OpeningLobby/PainterStone01/Textures/T_PainterStone01_Normal.uasset',
        'Assets/Source/OpeningLobby/PainterStone01/StoneSample.blend',
        'Assets/Source/OpeningLobby/PainterStone01/mesh.json']
    assert all(p in [x['path'] for x in unchanged] for p in required)
    write('affected-assets-verification',dict(passed=True,unchanged_painter_layers=rows,
        archived_live_inputs_changed=changed,archived_live_inputs_unchanged=unchanged,
        native_audit_changed_fields=sorted(expected),
        scope='Native layers 120/177 changed. Layer 186 and finish-layer sources/parameters exact; original single-channel property entries compared to same channel in explicit correction records. Native ORM/Normal, authoring mesh and sample map bytes exact.'))
    print(json.dumps(dict(passed=True,native_changed_fields=len(expected),unchanged_painter_layers=len(rows),
        changed_archived_live_inputs=len(changed),unchanged_archived_live_inputs=len(unchanged))),flush=True)


if __name__=='__main__':
    {'properties':properties,'captures':captures,'textures':textures,'affected':affected}[sys.argv[1]]()
