"""Revision data for the existing real-input verifier; centimeters and degrees."""
from pathlib import Path
import json
import os

MAP = '/Game/Maps/L_OpeningLobby_Layout02'
ROOT = Path(__file__).resolve().parents[2]

def require_project(project):
    """Compare the editor path with this script workspace, not the editor root."""
    import unreal
    actual = os.path.normcase(os.path.realpath(unreal.Paths.convert_relative_path_to_full(project)))
    expected = os.path.normcase(os.path.realpath(ROOT/'MeridianSquad.uproject'))
    if actual != expected:
        raise AssertionError(dict(actual_project=actual, expected_project=expected))

def configuration(root):
    out = Path(root)/'Saved/OpeningLobby/Layout02'
    bounds = json.loads((out/'construction.json').read_text())['blocking_bounds']
    # Contact center = nearest measured blocking face minus the live capsule radius.
    surfaces = {name: bounds[actor]['center'][1]-bounds[actor]['extent'][1]
                for name,actor in [('wall_collision','SideWall_620'),('column_collision','Pier_210_340')]}
    plan = [
        ('wait','spawn',1),
        ('mouse','mouse_yaw',30,0),('mouse','mouse_pitch',0,20),('look','restore_look',0,0),
        ('move','checkpoint_inbound',-1110,-105),
        ('move','entrance_view_position',-1100,0),('capture','entrance-to-inner',2),
        ('move','center',0,0),('capture','center',2),
        ('move','inner_door',1380,0),('look','reverse_view',180,0),
        ('capture','inner-to-entrance',2),('look','restore_look',0,0),
        ('move','west_side',1380,-500),('move','west_return',-1400,-500),
        ('move','checkpoint_return_approach',-1400,-105),('move','checkpoint_second_inbound',-1100,-105),
        ('move','security_oblique_position',-850,180),('look','security_oblique_look',200,0),
        ('capture','security-oblique',2),('look','restore_look',0,0),
        ('move','east_aisle_entry',-850,500),('move','east_route',1380,500),
        ('hold','wall_collision','D',2.0),('move','leave_wall',1380,0),
        ('move','column_approach',210,0),('hold','column_collision','D',2.0),
        ('move','leave_column',210,0),('jump','gravity_jump',1.8),
        ('move','east_return_approach',1380,0),('move','east_return_entry',1380,500),
        ('move','east_return',-1400,500),('move','entrance_cross',-1400,-105),
        ('move','checkpoint_outbound_approach',-1100,-105),('move','checkpoint_outbound',-1400,-105),
    ]
    view_plan = [('look','initial_look',0,0),('move','checkpoint_inbound',-1110,-105),
                 ('move','entrance_view_position',-1100,0),('capture','entrance-to-inner',2),
                 ('move','center',0,0),('capture','center',2),
                 ('move','inner_door',1380,0),('look','reverse_view',180,0),
                 ('capture','inner-to-entrance',2),('look','restore_look',0,0),
                 ('move','security_approach',-850,0),('move','security_oblique_position',-850,180),
                 ('look','security_oblique_look',200,0),('capture','security-oblique',2),
                 ('look','restore_look',0,0),('move','checkpoint_return',-1100,-105),
                 ('move','return_to_entrance',-1400,-105)]
    return dict(map=MAP,out=out,plan=plan,view_plan=view_plan,collision_surfaces=surfaces,contact_tolerance_cm=3.)
