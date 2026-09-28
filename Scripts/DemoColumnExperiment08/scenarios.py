"""Real-input scenarios; execute after play_probe.py in the same Unreal globals."""
def normal_events():
    return [[0,'position',[750,0,90.15]],
            [1,'aim',[119.1,-23.6814,208.8754]],[1.3,'fire',True],[1.8,'fire',False],
            [5,'sample','independent-facing-landed'],
            [7,'aim',[119.1,0,440]],[7.3,'fire',True],[7.8,'fire',False],
            [9,'aim',[119.1,0,440]],[9.3,'fire',True],[9.8,'fire',False],
            [11,'aim',[119.1,0,440]],[11.3,'fire',True],[11.8,'fire',False],
            [14,'sample','concrete-landed'],[15,'aim',[260,0,20]],
            [16,'capture','normal-ground'],[21,'sample','settled']]


def stress_events():
    events=[[0,'key','F6',True],[.8,'key','F6',False],[1.5,'sample','fresh-reset'],[2,'reload']]
    positions=[[750,0,90.15],[0,750,90.15],[-750,0,90.15]]
    for face in range(3):
        base=8+45*face
        events.append([base-1,'position',positions[face]])
        for i in range(30):
            row=i//3
            offset=[-60,0,60][row%3]
            z=110+165*row
            target=[119.1,offset,z] if face==0 else [offset,119.1,z] if face==1 else [-119.1,offset,z]
            t=round(base+i*1.2,2)
            events.extend([[t,'aim',target],[t+.2,'fire',True],[t+.6,'fire',False]])
        events.extend([[base+36,'sample','face-'+str(face)],[base+36.5,'reload']])
    events.extend([[150,'position',[850,400,90.15]],[151,'aim',[220,0,35]],
                   [152,'sample','settled-cap'],[153,'capture','stacked-ground'],
                   [157,'key','F6',True],[157.5,'key','F6',False],[159,'sample','final-fresh']])
    return sorted(events,key=lambda e:e[0])
