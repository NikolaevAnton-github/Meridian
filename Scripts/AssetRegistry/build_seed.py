"""Build reviewable seed manifests from saved acceptance evidence, without DCC calls."""
import json
from pathlib import Path

from registry import ROOT, fingerprint

OUT = Path(__file__).parent / 'manifests'


def evidence(source, note):
    return {'source': source, 'note': note}


def build(name):
    probe = name == 'PipelineProbe'
    report = 'Saved/AgentSetup/PainterProbe/verification.json' if probe else 'Docs/Benchmarks/OrchestrationABResults.json'
    data = json.loads((ROOT / report).read_text())
    files = data['files'] if probe else data['runs'][name]['files']
    expected = {f['path']: f for f in files}
    if probe:
        hashes = json.loads((ROOT / 'Saved/AgentSetup/BlenderProbe/asset-hashes.json').read_text(encoding='utf-8-sig'))
        for f in hashes:
            path = Path(f['Path']).relative_to(ROOT).as_posix()
            if path not in expected:
                expected[path] = {'path': path, 'sha256': f['Hash'].lower()}
        expected['Saved/Exports/SmokeTest/SM_PipelineProbe.fbx'] = {'path': 'Saved/Exports/SmokeTest/SM_PipelineProbe.fbx'}
    artifacts = []
    for path, accepted in expected.items():
        p = ROOT / path
        observed = fingerprint(p)
        note = 'Saved acceptance manifest; current bytes match its SHA-256.'
        source = report
        if path.endswith('.blend') and probe:
            source = 'Saved/AgentSetup/BlenderProbe/asset-hashes.json'
        if probe and path.endswith('M_PipelineProbe_Green.uasset'):
            source = 'Saved/AgentSetup/BlenderProbe/asset-hashes.json'
        if accepted.get('sha256') and accepted['sha256'] != observed['sha256']:
            if not (probe and path.endswith('SM_PipelineProbe.uasset')):
                raise ValueError('Accepted hash mismatch: ' + path)
            source = 'Saved/AgentSetup/PainterProbe/unreal-material.json'
            note = 'Later Painter report explicitly saves/rebinds this mesh; old Blender hash is superseded. Current fingerprint is an inventory baseline, not historical byte verification.'
        elif not accepted.get('sha256'):
            source = 'Saved/AgentSetup/BlenderProbe/export.json'
            note = 'Export report identifies this file but has no accepted hash; current fingerprint is an inventory baseline only.'
        role = {'.blend': 'blender_source', '.spp': 'painter_source', '.fbx': 'mesh_export', '.png': 'texture_export'}.get(p.suffix)
        if p.suffix == '.uasset':
            role = 'unreal_mesh' if p.stem.startswith('SM_') else 'unreal_texture' if p.stem.startswith('T_') else 'unreal_material'
        if not role:
            raise ValueError('Unsupported seed file: ' + path)
        artifacts.append({'path': path, 'role': role, **observed,
                          'unreal_package': '/Game/' + path[8:-7] if path.startswith('Content/') else None,
                          'evidence': [evidence(source, note)]})
    by_role = {}
    for item in artifacts:
        by_role.setdefault(item['role'], []).append(item['path'])
    edges = []

    def edge(up, down, kind, source, note, status='declared'):
        edges.append({'upstream': up, 'downstream': down, 'kind': kind, 'status': status,
                      'evidence': [evidence(source, note)]})

    workflow = 'Docs/PainterWorkflow.md' if probe else 'Docs/Benchmarks/OrchestrationABComparison.md'
    blend = by_role['blender_source'][0]
    spp = by_role['painter_source'][0]
    mesh = by_role['unreal_mesh'][0]
    fbx = by_role['mesh_export'][0]
    edge(blend, fbx, 'export', 'Saved/AgentSetup/BlenderProbe/export.json' if probe else workflow,
         'Report explicitly records Blender source and FBX export.' if probe else 'Accepted workflow describes source/export parity; exact derivation is declared.',
         'verified' if probe else 'declared')
    edge(fbx, spp, 'project_input', workflow, 'Documented pipeline input; saved SPP provenance was not independently parsed.')
    edge(fbx, mesh, 'import', workflow, 'Documented FBX import; exact import-source metadata has not been independently read.')
    for png in by_role['texture_export']:
        edge(spp, png, 'export', workflow, 'Documented Painter export; saved SPP-to-file derivation is declared.')
        # Filename mapping is useful for discovery, but never counts as verification.
        channel = Path(png).stem.rsplit('_', 1)[1].replace('OcclusionRoughnessMetallic', 'ORM')
        part = None if probe else ('Body' if '_Body_' in png else 'Metal')
        textures = [p for p in by_role['unreal_texture'] if p.endswith('_' + channel + '.uasset') and (part is None or '_' + part + '_' in p)]
        for texture in textures:
            edge(png, texture, 'import', workflow, 'Filename/channel mapping consistent with workflow; not verified import metadata.', 'unverified')
            for material in by_role['unreal_material']:
                if ('Painter' in Path(material).stem if probe else material.endswith('_' + part + '.uasset')):
                    edge(texture, material, 'texture_input', workflow, 'Expected texture/material mapping; report does not independently identify the texture object in each sample.', 'declared')
    for material in by_role['unreal_material']:
        if probe and material.endswith('M_PipelineProbe_Green.uasset'):
            # The old material remains inventory; the later Painter assignment supersedes it.
            continue
        source = 'Saved/AgentSetup/PainterProbe/unreal-material.json' if probe else f'Saved/AgentSetup/OrchestrationAB/Independent/{name}/unreal-verification.json'
        edge(material, mesh, 'material_assignment', source,
             'Saved material assignment verified in the existing Unreal acceptance report.', 'verified')
    return {'asset': name, 'artifacts': artifacts, 'dependencies': edges}


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for name in ('PipelineProbe', 'BenchA', 'BenchB'):
        manifest = build(name)
        (OUT / (name + '.json')).write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'asset': name, 'artifacts': len(manifest['artifacts']), 'dependencies': len(manifest['dependencies'])}))
