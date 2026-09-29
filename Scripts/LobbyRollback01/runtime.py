"""Reuse MSQ-152 input recording, with isolated PIE-only test preparation."""
import importlib.util
import json
import sys
from pathlib import Path
import unreal as u

ROOT = Path('D:/devgames/MeridianSquad')
OUT = ROOT / 'Saved/LobbyRollback01'
sys.path.insert(0, str(ROOT / 'Scripts/LobbyPlaytestFix01'))
import scene
scene.OUT = OUT
spec = importlib.util.spec_from_file_location('rollback_input_recorder', ROOT / 'Scripts/LobbyPlaytestFix01/runtime.py')
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


def prepare():
    world, pawn, rifle, sim = recorder.objects()
    # This setting is discarded when PIE stops. It prevents unrelated enemy hits.
    fixtures = u.GameplayStatics.get_all_actors_of_class(world, u.GASPEnemyFixture)
    sim.set_enemy_combat_mode(False)
    assert rifle.probe_ammo(30, 90)
    for actor in u.GameplayStatics.get_all_actors_of_class(world, u.Actor):
        name = actor.get_class().get_name()
        assert not any(s in name for s in ['DemoColumn', 'LobbyFacing', 'DestructionFragment'])
        for component in actor.get_components_by_class(u.ActorComponent):
            assert not any(s in component.get_class().get_name() for s in ['DemoColumn', 'LobbyFacing', 'DestructionFragment'])
    initial = recorder.state()
    assert len(initial['props']) == 14
    scene.write('runtime-initial.json', {'method': 'Fresh full-build PIE; only enemy combat disabled and finite ammo prepared.',
                'enemy_fixtures': len(fixtures), 'state': initial})
    print(json.dumps({'props': len(initial['props']), 'rifle_mode': initial['rifle']['automatic'], 'fixtures': len(fixtures)}))


def concrete():
    recorder.run('rifle-concrete', [[.05, 'position', [-840,380,100]], [.1,'key','V',True],
                 [.2,'key','V',False], [.3,'aim',[-840,700,100]], [.8,'fire',True], [3.8,'fire',False]], 4.5)


def reset(name):
    recorder.run(name, [[.1,'key','F6',True], [.2,'key','F6',False]], 2.0)


def glass():
    recorder.run('rifle-glass', [[.1,'position',[1680,-648,92]], [.25,'ammo',10,20],
                 [.35,'key','V',True], [.45,'key','V',False], [.7,'aim',[1680,-700,172]],
                 [1.2,'fire',True], [1.35,'fire',False], [2.,'aim',[1680,-700,172]],
                 [2.3,'fire',True], [2.45,'fire',False]], 3.3)
