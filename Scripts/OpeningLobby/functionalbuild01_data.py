"""Production modules from the exact approved drawing solids; metres throughout."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/OpeningLobby/FunctionalBuild01/Worker'
SRC=ROOT/'Assets/Source/OpeningLobby/FunctionalBuild01'
MAP='/Game/Maps/L_OpeningLobby_FunctionalBuild01'
BASE='/Game/Maps/L_OpeningLobby_ArchitectureReworkA01'
ASSETS='/Game/OpeningLobby/FunctionalBuild01'
DESIGN=ROOT/'Assets/Concepts/OpeningLobby/FunctionalRevision02'
D=json.loads((DESIGN/'design.json').read_text())

def replaced(name):
    return name.startswith(('Detector','Station','InnerDoor','InnerHighWindow','InnerWindow')) or name=='InnerBoundary'

def prepare():
    # Execute only the two frozen pure geometry functions; retained scene is reused.
    script="const fs=require('fs');const dir="+json.dumps(str(DESIGN))+";const D=JSON.parse(fs.readFileSync(dir+'/design.json'));const S=D.shared;function retainedSolids(){return [];}\n"
    script+=(DESIGN/'geometry.mjs.txt').read_text()+(DESIGN/'retained-functions.mjs.txt').read_text()
    script+='\nconsole.log(JSON.stringify(solids(D.retained_A)));'
    rows=json.loads(subprocess.check_output(['node','-e',script],text=True))
    (SRC/'approved-solids.json').write_text(json.dumps(rows,indent=2))
    return rows

def geometry():
    rows=json.loads((SRC/'approved-solids.json').read_text())
    groups={}
    for row in rows:
        name,b,kind=row['id'],row['b'],row['kind']
        if name.startswith('retained-inner-band'):continue
        if name.endswith('roof-band'):
            # Piers/end masses already supply these regions. Trim buried coplanar
            # roof faces at the retained masses without changing closure coverage.
            b=list(b);b[:2]=[-28.8,-22.2] if name.startswith('E') else [22.2,29.97]
        if name.startswith('I') and kind=='infill':
            b=list(b);b[1]=min(b[1],29.97)
        if name[:2] in ['E+','E-','I+','I-']:
            suffix='Shell' if kind=='infill' else ('Leaf' if 'closed-leaf' in name else 'Frame')
            group=name[:2].replace('+','Pos').replace('-','Neg')+'_'+suffix
        elif name.startswith('new-column'):group=name.replace('-','N').replace('.','p')
        elif name.startswith(('joined','lane')):group='Checkpoint'
        elif name.startswith('elevator-closed-leaf'):group='ElevatorLeaves'
        else:group='ElevatorFrame'
        material='Wall' if kind=='infill' else ('Metal' if kind in ['metal','checkpoint'] else 'Stone')
        groups.setdefault(group,{'boxes':[],'material':material,'source_ids':[]})
        groups[group]['boxes'].append(b);groups[group]['source_ids'].append(name)
    # Opaque wall retains the original X30 plane, with a true opening to the
    # back of the new 0.06 m closed leaves. No overlay sign or high-window patch.
    e=D['elevator'];w=e['opening_width']/2;h=e['opening_height']
    groups['InnerOpaqueWall']={'boxes':[[30,30.4,-8,-w,0,18],[30,30.4,w,8,0,18],[30,30.4,-w,w,h,18],[30.06,30.4,-w,w,0,h]],'material':'Wall','source_ids':['InnerBoundary replacement with scheduled leaf backing']}
    modules={};instances={}
    for name,item in groups.items():
        boxes=item['boxes'];bounds=[f(b[i] for b in boxes) for i,f in enumerate([min,max,min,max,min,max])]
        center=[(bounds[i*2]+bounds[i*2+1])/2 for i in range(3)]
        size=[bounds[i*2+1]-bounds[i*2] for i in range(3)]
        local=[[round(v-center[i//2],7) for i,v in enumerate(b)] for b in boxes]
        # Reuse identical column module; room shells retain their proper handedness.
        module='TallColumn' if name.startswith('newNcolumn') else name
        modules[module]={'size_m':size,'boxes_m':local,'material':item['material']}
        instances[name]={'module':module,'center_m':center,'size_m':size,'bounds_m':bounds,'source_ids':item['source_ids'],'blocking':True}
    return {'modules':modules,'instances':instances,'design_sha256':hashlib.sha256((DESIGN/'design.json').read_bytes()).hexdigest()}

if __name__=='__main__':
    SRC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    prepare();data=geometry();(OUT/'geometry-contract.json').write_text(json.dumps(data,indent=2))
    print(json.dumps({'modules':len(data['modules']),'instances':len(data['instances'])}))
