"""Exercise existing identity cases and revision-scoped held-key refresh locally."""
import ast
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'Saved/OpeningLobby/Layout03'
sys.modules['unreal'] = SimpleNamespace(Paths=SimpleNamespace(convert_relative_path_to_full=lambda p:str(Path(p).resolve())))
from layout02_verification import require_project

tree = ast.parse((ROOT/'Scripts/OpeningLobby/verify_lobby.py').read_text())
cls = next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='WalkCheck')
ns = dict(re=re,require_project=require_project)
for name in ['validate_identity','keys']:
    node = next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual shared verifier>', 'exec'),ns)
cases_tree = ast.parse((ROOT/'Saved/OpeningLobby/Layout02/check_verifier_identity.py').read_text())
node = next(n for n in cases_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cases' for t in n.targets))
exec(compile(ast.Module(body=[node],type_ignores=[]),'<existing identity cases>', 'exec'),ns)
initial = json.loads((ROOT/'Saved/OpeningLobby/Layout02/runtime-verification.json').read_text())['initial']
initial['project'] = str(ROOT/'MeridianSquad.uproject')
results = []
target = SimpleNamespace(target_map='/Game/Maps/L_OpeningLobby_Layout02')
for name,changes,expected in ns['cases']:
    try:
        ns['validate_identity'](target,dict(initial,**changes))
        accepted = True
    except AssertionError:
        accepted = False
    assert accepted == expected,name
    results.append(dict(case=name,passed=True))
for revision,config,expected_presses in [('Stage1',None,1),('Layout02',{},1),('Layout03',{'refresh_held_input':True},2)]:
    pawn = SimpleNamespace(probe_key=Mock())
    target = SimpleNamespace(config=config,held=set(),pawn=pawn)
    ns['keys'](target,['W'])
    ns['keys'](target,['W'])
    ns['keys'](target,[])
    calls = [tuple(c.args) for c in pawn.probe_key.call_args_list]
    assert calls == [('W',1.,True)]*expected_presses+[('W',0.,False)],calls
    assert not target.held
    results.append(dict(case=revision+' held-key and release behavior',passed=True))
(OUT/'verifier-regression.json').write_text(json.dumps(results,indent=2))
print(f'{len(results)} identity and key-input regression cases passed')
