"""Narrow in-memory adapter to the existing real-input verifier; historical files stay intact."""
import importlib.util
import types
from pathlib import Path
from architecture01_unreal import ROOT,OUT,MAP

_module=None

def start():
    global _module
    assert _module is None or _module._run is None or _module._run.done
    source=(ROOT/'Scripts/OpeningLobby/verify_lobby.py').read_text()
    # Inject a dedicated revision/configuration without modifying historical defaults/guards.
    source=source.replace("assert revision in ('Stage1','Layout02','Layout03'), revision", "assert revision in ('Stage1','Layout02','Layout03','Architecture01'), revision")
    source=source.replace("if revision in ('Layout02','Layout03'):","if revision in ('Layout02','Layout03','Architecture01'):")
    source=source.replace("self.config = importlib.reload(module).configuration(ROOT)","self.config = importlib.reload(module).configuration(ROOT)\n            if revision == 'Architecture01':\n                self.config.update(map='/Game/Maps/L_OpeningLobby_Architecture01', out=ROOT/'Saved/OpeningLobby/Stage2/Architecture01')")
    source=source.replace("'layout03_verification' if revision == 'Layout03' else 'layout02_verification'","'layout03_verification' if revision in ('Layout03','Architecture01') else 'layout02_verification'")
    _module=types.ModuleType('architecture01_existing_verifier')
    exec(compile(source,str(ROOT/'Scripts/OpeningLobby/verify_lobby.py'),'exec'),_module.__dict__)
    assert "Architecture01" in source and source.count("self.config.update(map=")==1
    return _module.start(revision='Architecture01')

def status():
    report=_module.status() if _module else dict(done=True,passed=False,error='Not started')
    return {k:v for k,v in report.items() if k not in ('initial','events')}
