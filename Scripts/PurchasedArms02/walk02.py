"""MSQ-62 configuration of the existing input/collision verifier, without captures."""
import types
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MODULE = None

def configuration(root):
    out = ROOT/'Saved/PurchasedArms02/Worker/Walk02'
    out.mkdir(parents=True,exist_ok=True)
    plan = [('wait','spawn',1),('mouse','mouse_yaw',30,0),('mouse','mouse_pitch',0,20),
        ('look','restore_look',0,0),('move','clear_entrance',-2700,-105),('move','wall_approach',-2700,0),
        ('hold','entrance_wall_collision','D',2.2),('move','lane_align',-2700,465),
        ('move','lane_inbound',-1900,465),('move','axis_align',-1900,0),
        ('move','elevator_approach',2850,0),('move','walk_back',0,0)]
    return dict(map='/Game/Maps/L_OpeningLobby_PainterStone01',out=out,plan=plan,view_plan=plan,
        refresh_held_input=True,collision_surfaces={'entrance_wall_collision':560},contact_tolerance_cm=3)

def start():
    global MODULE
    path = ROOT/'Scripts/OpeningLobby/verify_lobby.py'
    source = path.read_text()
    source = source.replace("'layout03_verification' if revision == 'Layout03' else 'layout02_verification'", "'walk02'")
    source = source.replace("'/Script/MeridianSquad.OpeningLobbyCharacter'", "'/Game/InfimaGames/TacticalFPSAnimations/Common/Core/Characters/BP_TFA_BaseCharacter.BP_TFA_BaseCharacter_C'")
    module = types.ModuleType('purchased_arms02_existing_verifier')
    exec(compile(source,str(path),'exec'),module.__dict__)
    result = module.start(revision='Layout03')
    MODULE = module
    return result

def status():
    result = MODULE.status() if MODULE else {'done':True,'error':'not started'}
    return {k:v for k,v in result.items() if k not in ['initial','events']}
