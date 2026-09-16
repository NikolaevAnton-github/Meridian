"""Task-scoped fingerprints using the existing no-junction storage walker."""
import json
import sys
from pathlib import Path
from functionalbuild01_preflight import walk, digest

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Saved/OpeningLobby/PainterStone01/Worker'
OUT = BASE / 'Correction01'

def allowed(path):
    return path.startswith(('Saved/OpeningLobby/PainterStone01/Worker/Correction01/',
        'Saved/OpeningLobby/PainterStone01/Worker/Exports/Correction01/',
        'Content/OpeningLobby/PainterStone01/', 'Assets/Source/OpeningLobby/PainterStone01/',
        'Scripts/OpeningLobby/painterstone01_')) or path in (
        'Docs/OpeningLobbyPainterStone01.md', 'Content/Maps/L_OpeningLobby_PainterStone01.umap')

def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p))

def usage():
    return dict(project_bytes=sum(p.stat().st_size for p in walk(ROOT)),
        lobby_bytes=sum(p.stat().st_size for f in ['Saved/OpeningLobby', 'Assets/Concepts/OpeningLobby',
            'Assets/Source/OpeningLobby', 'Content/OpeningLobby'] for p in walk(ROOT/f)))

def scan():
    OUT.mkdir(parents=True, exist_ok=True)
    target=OUT/'protected-before.json'
    assert not target.exists()
    paths=[ROOT/f for f in ['AGENTS.md','.codex/config.toml','MeridianSquad.uproject','.gitattributes']]
    for f in ['Assets','Content','Config','Scripts','Docs','.agents','Source','Saved/OpeningLobby/MaterialIntegration01']:
        paths.extend(p for p in walk(ROOT/f) if '__pycache__' not in str(p)
                     and not allowed(p.relative_to(ROOT).as_posix()))
    data=dict(entries=[entry(p) for p in paths], **usage())
    target.write_text(json.dumps(data,indent=2))
    print(json.dumps(dict(protected=len(paths),project_GB=data['project_bytes']/1e9,lobby_GB=data['lobby_bytes']/1e9)))

def protected():
    before=json.loads((OUT/'preservation-before.json').read_text())
    rows=[];differences=[]
    for old in before['entries']:
        p=ROOT/old['path']
        current=entry(p) if p.is_file() else dict(path=old['path'],missing=True)
        rows.append(current)
        if current!=old:differences.append(dict(before=old,after=current))
    report=dict(passed=not differences,checked_files=len(rows),
        differences=differences,entries=rows,
        scope='Exact correction-start baseline: protected source/native/config/code/doc files and rejected history, all original Worker and Review01 records, and controller BeforeCorrection01 archive. Mutable live task sources are excluded.')
    (OUT/'protected-after.json').write_text(json.dumps(report,indent=2))
    assert report['passed'],dict(changed=differences)
    print(json.dumps(dict(protected_unchanged=len(rows))),flush=True)

def task_files():
    paths=[]
    for f in [OUT,BASE/'Exports/Correction01',ROOT/'Content/OpeningLobby/PainterStone01',ROOT/'Assets/Source/OpeningLobby/PainterStone01']:
        paths.extend(p for p in walk(f) if '__pycache__' not in str(p) and not p.name.endswith(('.lock','.painter_lock')))
    for folder in ['Before','Source','Template']:
        paths.extend(walk(BASE/folder))
    paths.extend(BASE/'BeforeContext'/name for name in ['portal-complete-90.png','portal-complete-90-camera.json','capture-settings-before.json','capture-settings-restored.json'])
    paths.extend(BASE/name for name in ['bindings.json','Exports/StoneSample_240cm.fbx','Painter/creation-completed.json'])
    paths.extend(ROOT/'Assets/Concepts/OpeningLobby/OwnerReferences01'/name for name in ['01-InnerEnd.png','02-EntranceSecurity.png'])
    paths.append(ROOT/'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap')
    # Bind historical comparison evidence and unchanged helper dependencies explicitly.
    for view in ['entrance-90','sample-context-90','column-near-90','front-return-90','grazing-90','portal-complete-90']:
        folder=BASE/('FinalContext' if view=='portal-complete-90' else 'Final')
        paths.extend([folder/(view+'.png'),folder/(view+'-camera.json')])
    paths.extend(BASE/'Painter'/name for name in ['final-source-evidence.json'])
    paths.extend(ROOT/'Saved/OpeningLobby/PainterStone01/Review01'/name for name in ['report.md','verdict.json'])
    paths.extend(ROOT/name for name in ['Docs/Tasks/OpeningLobbyPainterStone01.md',
        'Docs/Tasks/OpeningLobbyPainterStone01Correction01.md','Scripts/OpeningLobby/reworka01_capture.py',
        'Scripts/OpeningLobby/functionalbuild01_preflight.py','Scripts/OpeningLobby/functionalbuild01_client.py',
        'Scripts/OpeningLobby/materialintegration01_unreal.py','Scripts/OpeningLobby/architecture01_lightstudy.py',
        'Scripts/OpeningLobby/architecture01_reflection.py','Scripts/OpeningLobby/stage1_tools.py',
        'Scripts/Benchmarks/OrchestrationAB/verify_maps.py'])
    paths.extend((ROOT/'Scripts/OpeningLobby').glob('painterstone01_*.py'))
    paths.extend(ROOT/f for f in ['Docs/OpeningLobbyPainterStone01.md','Content/Maps/L_OpeningLobby_PainterStone01.umap'] if (ROOT/f).is_file())
    return sorted(set(paths))

def storage():
    before=json.loads((OUT/'storage-before.json').read_text())
    current=usage();current['task_artifact_bytes']=sum(p.stat().st_size for p in task_files())
    current.update(project_growth_bytes=current['project_bytes']-before['project_bytes'],
        cumulative_lobby_growth_bytes=current['lobby_bytes']-before['lobby_bytes'],
        project_limit_bytes=250_000_000_000,lobby_limit_bytes=2_000_000_000,fresh_growth_aim_bytes=300_000_000,
        method='Existing no-junction walker; apparent file bytes, decimal GB. Project includes project-local generated caches and history. Lobby aggregate matches preflight roots; map also counted in task/project.',
        task_files=len(task_files()))
    current['within_hard_limits']=current['project_bytes']<current['project_limit_bytes'] and current['lobby_bytes']<current['lobby_limit_bytes']
    current['controller_archive_bytes']=sum(p.stat().st_size for p in walk(ROOT/'Saved/OpeningLobby/PainterStone01/Controller/BeforeCorrection01'))
    current['new_correction_evidence_and_export_bytes']=sum(p.stat().st_size for f in [OUT,BASE/'Exports/Correction01'] for p in walk(f))
    current['within_fresh_growth_aim']=None
    current['aim_scope']='300 MB was the first-pass aim; this is a bounded correction with retained first-pass history and controller archive.'
    (OUT/'storage.json').write_text(json.dumps(current,indent=2))
    assert current['within_hard_limits'],current
    print(json.dumps(current),flush=True)

def provenance():
    src=ROOT/'Assets/Source/OpeningLobby/PainterStone01'
    recipe=json.loads((src/'layer-recipe.json').read_text())
    native=json.loads((OUT/'native-material-audit.json').read_text())
    channels=json.loads((OUT/'texture-channel-verification.json').read_text())
    layer_sources=[]
    resource_urls=set()
    for layer in recipe['tree']['layers']:
        uid=str(layer['uid']);fill=recipe['fills'][uid]
        sources=fill['sources']
        for s in [sources.get('material')]+list(sources.get('channels',{}).values()):
            if not s:continue
            assert s['type'] in ['SourceSubstance','SourceUniformColor'],s
            if s.get('resource_url'):
                assert s['resource_url'].startswith('resource://starter_assets/'),s
                resource_urls.add(s['resource_url'])
        layer_sources.append(dict(uid=layer['uid'],name=layer['name'],active_channels=layer['active_channels'],
            sources=sources,projection=fill['projection'],blend=recipe['layer_properties'][uid]))
    assert len(layer_sources)==6 and len(resource_urls)==3
    assert len(native['import_sources'])==3
    rows=[]
    for channel in channels['rows']:
        stem=Path(channel['canonical']['path']).stem
        asset='/Game/OpeningLobby/PainterStone01/Textures/'+stem+'.'+stem
        assert [Path(p).resolve() for p in native['import_sources'][asset]]==[(ROOT/channel['canonical']['path']).resolve()]
        rows.append(dict(channel=channel['channel'],canonical=channel['canonical'],exported=channel['exported'],
            source_regeneration=channel['reopen'],native_asset=asset,
            native_file=entry(ROOT/'Content/OpeningLobby/PainterStone01/Textures'/(stem+'.uasset'))))
    reference_root=ROOT/'Assets/Concepts/OpeningLobby/OwnerReferences01'
    report=dict(candidate=recipe['candidate'],source_project=entry(src/'PainterStone01.spp'),
        native_authoring_mesh=entry(src/'StoneSample.blend'),mesh_metadata=entry(src/'mesh.json'),
        imported_mesh=entry(BASE/'Exports/StoneSample_240cm.fbx'),physical_coverage_cm=[240,240],
        visual_references=[entry(reference_root/(name+'.png')) for name in ['01-InnerEnd','02-EntranceSecurity']],
        visual_reference_use='Viewed only, including foreground faces at original image resolution. No reference or rejected pixel input to Painter.',
        authored_pixel_inputs=[],stock_procedural_resources=sorted(resource_urls),viewer_resources=[r for r in recipe['resources']['resources'] if r['context']=='viewer'],
        layers=layer_sources,complete_parameter_metadata=entry(src/'layer-recipe.json'),
        export_preset=recipe['export_preset'],channels=rows,normal_format='DirectX',
        native_material=entry(ROOT/'Content/OpeningLobby/PainterStone01/Materials/M_PainterStone01.uasset'),
        native_dependency_graph=native['dependencies'],bindings=json.loads((BASE/'bindings.json').read_text())['rows'],
        material_map=entry(ROOT/'Content/Maps/L_OpeningLobby_PainterStone01.umap'),
        owner_source_map=entry(ROOT/'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap'),
        no_old_material_or_texture_inputs=True,provenance_scope='Authored stone only. Untouched areas intentionally retain original owner-map material dependencies.',
        evidence=[entry(BASE/'Painter/creation-completed.json'),entry(OUT/'Painter/final-source-evidence.json'),
            entry(OUT/'Painter/save-reopen-export-calls.json'),entry(OUT/'texture-channel-verification.json'),
            entry(OUT/'native-material-audit.json'),entry(OUT/'protected-after.json')],
        sampling_change=entry(OUT/'native-sampling-change.json'))
    (OUT/'provenance.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(native_layers=len(layer_sources),procedural_inputs=len(resource_urls),imported_texture_inputs=0,verified_export_chains=len(rows))),flush=True)

def manifest():
    assert json.loads((OUT/'protected-after.json').read_text())['passed']
    assert json.loads((OUT/'property-preservation.json').read_text())['passed']
    assert json.loads((OUT/'texture-channel-verification.json').read_text())['passed']
    assert json.loads((OUT/'capture-verification.json').read_text())['passed']
    state=json.loads((OUT/'final-state.json').read_text())['state']
    assert not state['pie'] and not state['dirty_content'] and not state['dirty_maps']
    excluded={OUT/x for x in ['manifest.json','identity.json','manifest-verification.json']}
    rows=[entry(p) for p in task_files() if p not in excluded]
    assert rows and len(rows)==len({row['path'] for row in rows}) and all(row['bytes']>0 for row in rows)
    record=dict(candidate='LobbyPainter-Stone01/Correction01',status='pending_focused_independent_recheck_and_owner_material_direction',
        entries=rows,excluded_self_references=[p.relative_to(ROOT).as_posix() for p in sorted(excluded)],
        scope='All current task source/native assets and helpers, correction evidence/exports, unchanged source/reference evidence, initial candidate comparisons and Review01 findings used for this correction. Historical comparison images/readbacks are evidence only. Controller archive is excluded; it remains preservation history, not current material input.')
    target=OUT/'manifest.json';assert not target.exists()
    target.write_text(json.dumps(record,indent=2))
    lookup={r['path']:r for r in rows}
    identity=dict(candidate=record['candidate'],status=record['status'],manifest=entry(target),
        map=lookup['Content/Maps/L_OpeningLobby_PainterStone01.umap'],
        painter_project=lookup['Assets/Source/OpeningLobby/PainterStone01/PainterStone01.spp'],
        source_map=entry(ROOT/'Content/Maps/L_OpeningLobby_FunctionalBuild01.umap'),entries=len(rows))
    (OUT/'identity.json').write_text(json.dumps(identity,indent=2))
    failures=[r['path'] for r in rows if entry(ROOT/r['path'])!=r]
    assert not failures,failures
    assert entry(target)==identity['manifest']
    (OUT/'manifest-verification.json').write_text(json.dumps(dict(passed=True,entries_checked=len(rows),
        manifest_sha256=identity['manifest']['sha256'],failures=[]),indent=2))
    print(json.dumps(identity,indent=2),flush=True)

if __name__ == '__main__':
    {'scan':scan,'protected':protected,'storage':storage,'provenance':provenance,'manifest':manifest}[sys.argv[1]]()
