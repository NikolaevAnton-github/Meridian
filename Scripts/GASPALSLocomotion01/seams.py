"""Read-only source physics/held-object and command-consumer evidence."""
import json
import unreal as u
from Scripts.GASPALSLocomotion01.editor import OUT,state,defaults

def run():
    before=state()
    assert not before['pie'] and not before['dirty'],before
    pa=u.load_asset('/GASPALS/Characters/UEFN_Mannequin/Rigs/PA_UEFN_Mannequin')
    rows=json.loads(u.GASPALSLocomotionLibrary.inspect_physics_asset(pa))
    unsupported=[bone for bone,row in rows.items() if row['unsupported']]
    assert not unsupported,unsupported
    rifle=u.load_asset('/GASPALS/OverlaySystem/Props/Meshes/M4A1')
    old=u.load_asset('/GASPALSEnemy01/OverlaySystem/Props/Meshes/M4A1')
    result=dict(before=before,physics_bodies=rows,unsupported_bullet_shapes=unsupported,
        rifle=defaults(rifle),old_rifle=defaults(old),after=state())
    (OUT/'source-seams.json').write_text(json.dumps(result,indent=2))
    return dict(physics_bodies=len(rows),shapes=sum(r['sphere']+r['box']+r['capsule'] for r in rows.values()),
        unsupported=unsupported,after=result['after'])
