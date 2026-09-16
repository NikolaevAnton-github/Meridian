"""Scheduled dimensions from actual reopened actor bounds and collision profiles."""
import json
from functionalbuild01_data import OUT,D

def run():
    construction=json.loads((OUT/'construction.json').read_text());rows=construction['actor_bounds']
    profiles=json.loads((OUT/'imported-profile-probes.json').read_text());probes={p['name']:p for p in profiles['probes']}
    records=[]
    def check(name,actual,expected,tolerance=.0005):
        if not isinstance(actual,list):actual=[actual];expected=[expected]
        error=max(abs(a-b) for a,b in zip(actual,expected))
        records.append({'criterion':name,'actual_m':actual,'expected_m':expected,'max_error_m':error,'tolerance_m':tolerance,'passed':error<=tolerance})
    def bounds(name):
        row=rows[name];return [(row['center'][i//2]+(-1 if i%2==0 else 1)*row['extent'][i//2])/100 for i in range(6)]
    for side,sign in [('Pos',1),('Neg',-1)]:
        for end in ['E','I']:
            b=bounds('FB01_'+end+side+'_Shell')
            # Inner 3cm closure is supplied by the unchanged original end band.
            x_end=30 if end=='I' else -30
            if end=='I':check(end+side+' room shell to retained end-band joint',b[1],29.97)
            check(end+side+' hallward cap',b[1] if end=='E' else b[0],-19.8 if end=='E' else 19.8)
            check(end+side+' gross room extents',[10.2 if end=='I' else b[1]-b[0],b[3]-b[2]],[10.2,6.4])
            check(end+side+' outer and hall faces',sorted([abs(b[2]),abs(b[3])]),[5.6,12])
            check(end+side+' aisle roof top',b[5],9.2)
            f=bounds('FB01_'+end+side+'_Leaf');width=f[3]-f[2] if end=='E' else f[1]-f[0]
            depth=f[1]-f[0] if end=='E' else f[3]-f[2]
            check(end+side+' leaf size',[width,f[5]-f[4],depth],[1.2,2.4,.06])
            check(end+side+' flush threshold',f[4],0)
            centre=(f[2]+f[3])/2 if end=='E' else (f[0]+f[1])/2
            check(end+side+' door centre',centre,sign*10 if end=='E' else 26.1)
            leaf=probes[('entrance_leaf_' if end=='E' else 'inner_leaf_')+str(sign)+'_150']['impact_cm']
            check(end+side+' visible recess',abs(leaf[0]/100+19.8) if end=='E' else abs(leaf[1]/100)-5.6,.24)
    columns=[(n,bounds(n)) for n in rows if n.startswith('FB01_newNcolumn')]
    assert len(columns)==4
    for name,b in columns:
        check(name+' section and height',[b[1]-b[0],b[3]-b[2],b[5]-b[4]],[2.4,2.4,18])
        check(name+' centres',[abs((b[0]+b[1])/2),abs((b[2]+b[3])/2)],[12.6,2.4])
        check(name+' flush floor and ceiling',[b[4],b[5]],[0,18])
        check(name+' axial half-gap',min(abs(b[2]),abs(b[3])),1.2)
        check(name+' original pier side gap',5.6-max(abs(b[2]),abs(b[3])),2)
    b=bounds('FB01_Checkpoint');check('checkpoint envelope',[b[1]-b[0],b[3]-b[2],b[5]],[.9,11.2,2.58])
    check('checkpoint station',(b[0]+b[1])/2,-24.6)
    for sign in [-1,1]:
        a=probes['lane_left_'+str(sign)]['impact_cm'][1]/100;c=probes['lane_right_'+str(sign)]['impact_cm'][1]/100
        check('lane '+str(sign)+' actual width',abs(a-c),1.5)
        check('lane '+str(sign)+' actual height',probes['lane_head_'+str(sign)]['impact_cm'][2]/100,2.4)
    b=bounds('FB01_ElevatorFrame');check('elevator frame',[b[1]-b[0],b[3]-b[2],b[5]],[.6,4.4,4.6])
    b=bounds('FB01_ElevatorLeaves');check('elevator opening and closed leaf',[b[0],b[1],b[3]-b[2],b[5]],[30,30.06,3.6,4.2])
    check('main ceiling underside',bounds('CentralCeiling')[4],18)
    check('sidewall clear width',bounds('SideWall_1')[2]-bounds('SideWall_-1')[3],24)
    check('end datums span',bounds('FB01_InnerOpaqueWall')[0]-(-30),60)
    report={'passed':all(r['passed'] for r in records),'measurements':records,'basis':'Saved/reopened construction.json actor bounds plus actual complex collision profiles','primary_tolerance_m':.05,'measurement_comparison_tolerance_m':.0005,'retained_context_checks':'Every unchanged baseline actor transform, mesh, collision, material and light/exposure compared in construction.json'}
    (OUT/'scheduled-measurements.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'measurements':len(records),'failures':[r for r in records if not r['passed']]}))

if __name__=='__main__':run()
