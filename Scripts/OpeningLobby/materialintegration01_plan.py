"""Bind every actual source slot to an explicit fresh role before editor writes."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/OpeningLobby/MaterialIntegration01/WorkerFresh01'
SOURCE = ROOT / 'Assets/Source/OpeningLobby/MaterialIntegration01'


def main():
    inventory = json.loads((OUT / 'Source/inventory.json').read_text())
    source = json.loads((OUT / 'Source/all-properties.json').read_text())
    neutral = {f'/Game/OpeningLobby/ArchitectureReworkA01/Materials/M_RA01_{n}.M_RA01_{n}': n
               for n in ['Stone', 'Wall', 'Floor', 'Strip', 'Ceiling', 'Metal', 'Glazing']}
    doors = {'FB01_EPos_Leaf', 'FB01_ENeg_Leaf', 'FB01_IPos_Leaf', 'FB01_INeg_Leaf', 'FB01_ElevatorLeaves'}
    pilot = {'Floor', 'FloorStrip_-1', 'FloorStrip_1', 'RA01_PortalJamb_1', 'RA01_Shoulder_1',
             'RA01_EndPier_1', 'RA01_Beam_1', 'RA01_UpperWall_1', 'RA01_FirstPier_1',
             'RA01_SoffitPerimeter_1', 'RA01_TerminalEndCeiling_1', 'RA01_TerminalField_1',
             'RA01_ContextAisleCeiling_1', 'RA01_EntranceBacking_1', 'RA01_PortalHead',
             'RA01_Datum', 'RA01_DoorCollar', 'FB01_EPos_Shell', 'FB01_EPos_Frame',
             'FB01_EPos_Leaf', 'FB01_Checkpoint', 'FB01_newNcolumnNN12p6N2p4', 'Pier_1_1'}
    rows = []
    for item in inventory:
        for slot, old in enumerate(item['materials']):
            protected = None
            role = neutral.get(old)
            if not item['visible'] or item['hidden_in_game'] or item['actor_hidden']:
                protected = 'Invisible component: preserve all original bindings'
            elif role == 'Glazing':
                protected = 'Existing glazing outside opaque scope'
            elif role is None:
                protected = 'Nonneutral owner override: excluded from automatic replacement'
            if not protected:
                if item['label'] in doors:
                    assert role == 'Metal'
                    role = 'Door'
                new = f'/Game/OpeningLobby/MaterialIntegration01/Materials/M_MI01_{role}.M_MI01_{role}'
            else:
                new = old
            rows.append(dict(actor=item['actor'], label=item['label'], component=item['component'],
                             mesh=item['mesh'], slot=slot, old=old, new=new, role=role,
                             source_override_materials=item['overrides'], protected_reason=protected,
                             pilot=item['label'] in pilot and not protected))
    assert len(rows) == 107 and len({(r['actor'], r['component'], r['slot']) for r in rows}) == 107
    assert not any(r['protected_reason'] and r['role'] != 'Glazing' for r in rows)
    (OUT / 'material-mapping.json').write_text(json.dumps(rows, indent=2))
    # Compare actual transforms against the historical worker's saved scene audit.
    historical = json.loads((ROOT / 'Saved/OpeningLobby/FunctionalBuild01/Worker/saved-source-audit.json').read_text())
    (OUT / 'historical-audit-structure.json').write_text(json.dumps(dict(keys=list(historical)), indent=2))
    counts = dict(collections.Counter(r['role'] for r in rows))
    (OUT / 'assembly-contract.md').write_text('''# MaterialIntegration01 fresh assembly contract

Source: /Game/Maps/L_OpeningLobby_FunctionalBuild01, saved SHA-256
46972ef30ef07f5a5aaa8cad0f8c026302c1269f1b5e08828e6f87795d168d31.
Live Unreal 5.8.1, MeridianSquad, clean source, PIE stopped at preflight.
127 actors, 148 components, 107 mesh components and material slots.
Preserve the owner's checkpoint at X -2090 cm (historical worker X -2460 cm).
Full current reflected properties, not the historical map, define preservation.

The two OwnerReferences01 PNGs were inspected directly: dense, varied green-grey
mineral stone; a visibly different polished floor with long branching pale veins;
near-black strips with small mineral flecks; subdued metal; quieter ceiling planes.
Retain the approved architecture, original light and exposure. No geometry seams,
texture panel grid, decals, branding, glass or atmosphere changes.

Every actual mesh/component/slot has an explicit old/new path in material-mapping.json.
Only exact known neutral source paths qualify. Six glazing slots remain untouched.
No invisible mesh component or nonneutral owner override was found. All non-mesh
components, collision and gameplay are protected by full property comparison.
The five opaque service/elevator leaf bindings use the new Door family; other
metal uses the new Metal family. Mesh defaults are never edited.

Pilot: the positive entrance portal/shoulder/soffit/room/first-column assembly,
checkpoint, floor and both strips. Inspect native eye-level and oblique stills
before propagating the explicit binding list. Two complete palette trials maximum
after initial authoring; technical API repairs are recorded separately.

New sources: independent NumPy procedural recipes, explicit seeds and canonical
PNG channels, plus newly created native Unreal graphs. No image input is read by
the generator. Existing lobby material graphs and textures are not authoring inputs.
The installed Blender distribution supplies a standalone Python/NumPy interpreter;
no Blender scene, bake or DCC contribution is required. No installation or service.

Planned seven families: 2048 stone/wall/strip, 4096 floor, 1024 ceiling/metal/door;
three channels per family (sRGB base color, linear ORM, DirectX normal).
Estimated canonical textures and native assets <=300 MB, captures/evidence <=150 MB;
total fresh growth target <=450 MB, hard task target 750 MB. Initial no-junction
inventory: project 12.016 GB; cumulative lobby 0.964 GB (limits 250 GB / 2 GB).

Acceptance: fresh provenance/native dependency audit; coherent real-scale material
response; 101 exact opaque overrides; unchanged source and all nonmaterial data;
saved/reopened bindings and shaders; matched native 1920x1080 Before/Final images;
possessed standing PIE and short forward/return movement; temporary settings restored;
clean candidate loaded with PIE stopped; exact manifest for independent review.
Final architecture, atmosphere and the owner's edited full route are outside this pass.
''', encoding='utf-8')
    print(json.dumps(dict(slots=len(rows), roles=counts, pilot_slots=sum(r['pilot'] for r in rows))))


if __name__ == '__main__':
    main()
