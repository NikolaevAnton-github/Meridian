"""Reuse accepted rifle probes, selecting one architectural instance explicitly."""
import json
from pathlib import Path
import unreal as u

ROOT=Path('D:/devgames/MeridianSquad')
OUT=ROOT/'Saved/LobbyColumns01'
probe={}
exec((ROOT/'Scripts/DemoColumnExperiment09/play_probe.py').read_text(),probe)
probe['OUT']=OUT

def objects_for(object_id):
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world
    pawn=u.GameplayStatics.get_player_pawn(world,0)
    actors=u.GameplayStatics.get_all_actors_of_class(world,u.Actor)
    actor=next(a for a in actors if a.actor_has_tag('LobbyColumns01') and str(a.get_component_by_class(u.NGDPropComponent).object_id)==object_id)
    return world,pawn,actor

def run(name,object_id,position,targets):
    probe['objects']=lambda: objects_for(object_id)
    world,pawn,actor=probe['objects']()
    # Leave one input frame for any previous release before changing the loadout.
    events=[[0,'fire',False],[.5,'ammo',30,90],[.6,'position',position]]
    clock=3
    for target in targets:
        events += [[clock,'aim',target],[clock+.5,'sample','before-'+str(target[2])]]
        for shot in range(5):
            t=clock+1+shot*1.1
            events += [[t,'fire',True],[t+.4,'fire',False]]
        clock+=9
        events += [[clock-.2,'sample','after-'+str(target[2])]]
    events += [[clock+2,'capture','damage'],[clock+3,'key','F6',True],[clock+3.5,'key','F6',False],[clock+6,'sample','reset']]
    return probe['run'](name,events,clock+8)

def all_state(name):
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    actors=u.GameplayStatics.get_all_actors_of_class(world,u.Actor)
    rows=[]
    for a in actors:
        if not a.actor_has_tag('DemoColumnStacking08'): continue
        prop=a.get_component_by_class(u.NGDPropComponent)
        clad=a.get_component_by_class(u.DemoColumnCladding)
        rebar=next(m for m in a.get_components_by_class(u.StaticMeshComponent) if m.static_mesh and m.static_mesh.get_name()=='SM_ConcretePillar_Square_5m_REBAR')
        c,e,_=u.SystemLibrary.get_component_bounds(rebar)
        rows.append(dict(label=a.get_actor_label(),prop=json.loads(prop.get_state()),cladding=json.loads(clad.get_state()),rebar_z=[c.z-e.z,c.z+e.z]))
    (OUT/(name+'.json')).write_text(json.dumps(rows,indent=2))
    print(json.dumps(dict(instances=len(rows),ready=sum(r['prop']['ready'] for r in rows))))
