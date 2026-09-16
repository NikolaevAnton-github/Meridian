"""Reuse reviewed triplanar graph and import checks for one new coated metal."""
import types
from paintermetal01_unreal import ROOT,OUT,ASSETS
def adapter():
    p=ROOT/'Scripts/OpeningLobby/painterstone01_material.py'
    source=p.read_text().replace('from painterstone01_unreal import','from paintermetal01_unreal import')
    source=source.replace("for channel in (['BaseColor'] if existed else ['BaseColor','ORM','Normal']):","for channel in ['BaseColor','ORM','Normal']:")
    source=source.replace('PainterStone01','PainterMetal01').replace('default_value=240','default_value=120').replace('physical_coverage_cm=240','physical_coverage_cm=120')
    source=source.replace('240 cm matches the native Painter authoring plane','120 cm physical export coverage; native fine satin coating')
    source=source.replace("parameter_name='DielectricSpecular',default_value=.4","parameter_name='DielectricSpecular',default_value=.5")
    source=source.replace('Polished dielectric with 3.2 percent normal-incidence reflectance; no coat','Opaque satin coating over metal; dielectric F0 4 percent; metallic zero')
    source=source.replace("source='Scripts/OpeningLobby/painterstone01_material.py'","source='Scripts/OpeningLobby/paintermetal01_material.py'")
    module=types.ModuleType('metal_graph');module.__file__=str(p)
    exec(compile(source,str(p),'exec'),module.__dict__)
    return module
