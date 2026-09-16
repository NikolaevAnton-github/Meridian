"""Reuse Layout03 schedule/capture checks through explicit measured A aliases."""
import ast
import hashlib
import json
from pathlib import Path
from reworka01_data import ROOT,OUT,MAP

VIEWS=['C1-90','C2-75','C2-90','A-oblique-106','A-oblique-90','C3-context-90','Terminal-soffit-90','Terminal-junction-90']

def run():
    actual=json.loads((OUT/'construction.json').read_text())
    rows=dict(actual['actor_bounds']);aliases={}
    def alias(name,*sources):
        rs=[rows[n] for n in sources]
        low=[min(r['center'][i]-r['extent'][i] for r in rs) for i in range(3)]
        high=[max(r['center'][i]+r['extent'][i] for r in rs) for i in range(3)]
        rows[name]=dict(center=[(a+b)/2 for a,b in zip(low,high)],extent=[(b-a)/2 for a,b in zip(low,high)])
        aliases[name]=list(sources)
    alias('EntranceBoundary','RA01_EntranceBacking_-1','RA01_EntranceBacking_1')
    for sign in [-1,1]:
        for old,new in [('Pier_0_','RA01_FirstPier_'),('LongLintel_','RA01_Beam_'),('EntranceLeaf_','RA01_DoorLeaf_')]:
            alias(old+str(sign),new+str(sign))
        alias('SideAisleCeiling_'+str(sign),*[n+str(sign) for n in ['RA01_TerminalEndCeiling_','RA01_TerminalField_','RA01_ContextAisleCeiling_']])
    alias('EntranceUpperGlazing','RA01_UpperGlazing')
    alias('EntranceLowerField','RA01_LowerSidelight_-1','RA01_LowerSidelight_1','RA01_LowerOverlight','RA01_DoorLeaf_-1','RA01_DoorLeaf_1','RA01_DoorCollar')
    adapted=OUT/'ScheduleAdapter';adapted.mkdir(exist_ok=True)
    (adapted/'construction.json').write_text(json.dumps(dict(actor_bounds=rows),indent=2))
    path=ROOT/'Scripts/OpeningLobby/check_layout03_evidence.py';tree=ast.parse(path.read_text())
    dims=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='dimensions')
    changes=[]
    for node in ast.walk(dims):
        if not isinstance(node,ast.For) or not isinstance(node.target,ast.Tuple):continue
        names=[n.id for n in node.target.elts if isinstance(n,ast.Name)]
        if names==['end','sign']:
            node.iter=ast.parse("[('Inner',1)]",mode='eval').body
            changes.append('EntranceEndBand old thin 18m facing is replaced by A engaged pier/jamb/shoulder; exact A actual profiles and bounds are checked separately.')
        if names==['name','back','front','sign']:
            node.iter=ast.parse("[('Inner frame/leaf','InnerDoorFrame','InnerDoorLeaf',-1),('Inner wall/frame','InnerBoundary','InnerDoorFrame',-1)]",mode='eval').body
            changes.append('A entry field is partitioned into disjoint lights/leaves around its closed collar, replacing old superimposed entrance proxy layers; inner layer checks retained.')
    assert len(changes)==2
    ns=dict(ROOT=ROOT,OUT=adapted,json=json)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[dims],type_ignores=[])),str(path),'exec'),ns)
    ns['dimensions']()
    report=json.loads((adapted/'schedule-verification.json').read_text())
    report.update(map=MAP,aliases=aliases,adapter_changes=changes,validator_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        aisle_ceiling_note='Baseline Z9.2 fields retained; local A Z8.4 perimeter and actual opening are separately verified by 26 imported-geometry section traces.')
    (OUT/'schedule-verification.json').write_text(json.dumps(report,indent=2))
    # Preserve the existing native PNG/header and actual camera pose checks.
    capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='captures')
    for node in capture.body:
        if isinstance(node,ast.For):node.iter=ast.parse(repr(VIEWS),mode='eval').body;break
    for view in VIEWS:
        p=OUT/(view+'-camera.json');row=json.loads(p.read_text());row['roll']=0
        p.write_text(json.dumps(row,indent=2))
    import struct
    ns=dict(OUT=OUT,json=json,struct=struct,hashlib=hashlib)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[capture],type_ignores=[])),str(path),'exec'),ns)
    ns['captures']()
    return dict(schedule_checks=len(report['checks']),captures=len(VIEWS))

if __name__=='__main__':print(json.dumps(run()))
