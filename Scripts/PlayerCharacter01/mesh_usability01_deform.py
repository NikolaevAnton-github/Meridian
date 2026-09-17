"""Reuse the keyed, evaluated Deformation03 probes on the actual original garment."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
variant=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'Bind01'
assert variant in ('Bind01','Bind02','Bind03','Bind04','Bind05')
path=ROOT/'Scripts/PlayerCharacter01/metahuman_trial01_deform.py'
code=path.read_text(encoding='utf-8')
code=code.replace("ROOT/'Assets/Source/PlayerCharacter01/MetaHumanTrial01'","ROOT/'Assets/Source/PlayerCharacter01/MeshUsability01'")
code=code.replace("ROOT/'Saved/PlayerCharacter01/MetaHumanTrial01/Worker/Deformation03'",f"ROOT/'Saved/PlayerCharacter01/MeshUsability01/Worker/Deformation{variant}'")
code=code.replace("BASE/'Solve02/Datum16_APose02_Inspection.blend'",f"BASE/'Datum16_{variant}.blend'")
code=code.replace("o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)",f"o.name=='Datum16_ExistingTopology_{variant}'")
code=code.replace("BASE/'Solve02/Datum16_APose03_Deformation.blend'",f"BASE/'Datum16_{variant}_Deformation.blend'")
code=code.replace("'MHTrial01_StaticSkinningProbes'",f"'MeshUsability01_{variant}_StaticSkinningProbes'")
code=code.replace("input='Solve02/APose/MH_Datum16_Trial01_Body.fbx'",f"input='Datum16_{variant}.fbx'")
code=code.replace("'deep_crouch','ankle_flex'","'deep_crouch','ankle_flex','wrist_flex'")
code=code.replace("elif name=='deep_crouch':", "elif name=='wrist_flex':\n        for side in ('l','r'):rotate('hand_'+side,(1,0,0),50)\n    elif name=='deep_crouch':")
if '--final' in sys.argv:
    code=code.replace('Deformation'+variant,"Deformation"+variant+'Final')
    code=code.replace(variant+'_Deformation.blend',variant+'_DeformationFinal.blend')
    code=code.replace("'wrist_flex']","'wrist_flex','cross_body_right','elbow_twist_right']")
    code=code.replace("elif name=='deep_crouch':", "elif name=='cross_body_right':\n        aim('upperarm_r','lowerarm_r',(.5,-1,.1));aim('lowerarm_r','hand_r',(.9,-.1,.2))\n    elif name=='elbow_twist_right':\n        aim('lowerarm_r','hand_r',(0,-1,.2));rotate('lowerarm_r',rig.pose.bones['hand_r'].head-rig.pose.bones['lowerarm_r'].head,-80)\n    elif name=='deep_crouch':")
exec(compile(code,str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
