"""Use the existing project's installed MSVC harness convention for one changed header."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Saved/GASPALSLocomotion01/Worker'
VC=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
SDK=Path('C:/Program Files (x86)/Windows Kits/10')
CPP=Path(__file__).with_name('motion_gate_check.cpp')
EXE=OUT/'motion-gate.exe'
args=[str(VC/'bin/Hostx64/x64/cl.exe'),'/nologo','/std:c++20','/EHsc','/W4','/WX',
    '/I'+str(ROOT/'Source/MeridianSquad'),'/I'+str(VC/'include'),'/I'+str(SDK/'Include/10.0.22621.0/ucrt'),
    str(CPP),'/Fe:'+str(EXE),'/Fo:'+str(OUT/'motion-gate.obj'),'/link',
    '/LIBPATH:'+str(VC/'lib/x64'),'/LIBPATH:'+str(SDK/'Lib/10.0.22621.0/ucrt/x64'),
    '/LIBPATH:'+str(SDK/'Lib/10.0.22621.0/um/x64')]
build=subprocess.run(args,cwd=OUT,capture_output=True,text=True)
(OUT/'motion-gate-build.log').write_text(build.stdout+build.stderr)
assert build.returncode==0,build.stdout+build.stderr
run=subprocess.run([str(EXE)],cwd=OUT,capture_output=True,text=True)
result=dict(build_exit=build.returncode,run_exit=run.returncode,output=run.stdout+run.stderr,
    production_header='Source/MeridianSquad/CombatAIMobile.h',
    header_sha256=hashlib.sha256((ROOT/'Source/MeridianSquad/CombatAIMobile.h').read_bytes()).hexdigest(),
    scope='Real production FireMotion header. No engine world, gameplay or firing.')
with (OUT/'motion-gate-check.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
raise SystemExit(run.returncode)
