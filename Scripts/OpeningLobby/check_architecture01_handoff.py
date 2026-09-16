"""Read-only final evidence checks; reports stay in the dedicated candidate root."""
import json
from architecture01_inventory import ROOT, OUT, digest


def main():
    previous=json.loads((ROOT/'Saved/OpeningLobby/Layout03/Review/evidence-audit.json').read_text())
    historical={name:sha for name,sha in previous['input_hashes'].items()
                if name.startswith('Saved/OpeningLobby/Layout03/')}
    mismatches=[name for name,sha in historical.items() if digest(ROOT/name)!=sha]
    approval=json.loads((ROOT/'Docs/Approvals/LobbyLayout03-Scale01.json').read_text())
    map_matches=digest(ROOT/approval['map_file'])==approval['map_sha256']
    preservation=dict(historical_files_checked=len(historical),mismatches=mismatches,
                      accepted_map_matches=map_matches,passed=not mismatches and map_matches)
    (OUT/'historical-evidence-check.json').write_text(json.dumps(preservation,indent=2))
    assert preservation['passed'],preservation

    stats=json.loads((OUT/'shader-audit.json').read_text())
    assert len(stats)==9 and all(row['num_pixel_shader_instructions']>0 for row in stats.values())
    lines=(ROOT/'Saved/Logs/MeridianSquad_2.log').read_text(errors='replace').splitlines()
    failures=[i for i,line in enumerate(lines) if 'Failed to compile Material' in line]
    strip_saves=[i for i,line in enumerate(lines) if 'Saving Package: /Game/OpeningLobby/Architecture01/Materials/M_A01_Strip' in line]
    assert strip_saves and (not failures or max(failures)<max(strip_saves))
    shader=dict(materials=len(stats),all_compiled_statistics_nonzero=True,
                last_transient_failure=lines[max(failures)] if failures else None,
                final_strip_save=lines[max(strip_saves)],
                compile_failures_after_final_strip_save=0,
                method='UE 5.8 MaterialEditingLibrary.GetStatistics finishes compilation on each actual material resource; checked local engine implementation.',
                transient_warning='Missing ComponentMask input while rebuilding existing graphs; completed graphs have valid compiled statistics.',passed=True)
    (OUT/'shader-final-check.json').write_text(json.dumps(shader,indent=2))
    print(json.dumps(dict(historical=preservation,compiled_materials=9)))


if __name__=='__main__':main()
