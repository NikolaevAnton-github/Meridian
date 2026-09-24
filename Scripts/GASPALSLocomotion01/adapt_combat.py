"""Replace old animation-class casts with the observed adapter state contract."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'Source/MeridianSquad'
patches={
 'EnemyCombatComponent.cpp':[
  ('const auto* Anim = Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance());\n    if (!Anim || Anim->RifleAlpha < .9f || Anim->RifleAimAlpha < .9f)',
   'const auto Pose = E->GetRiflePose();\n    if (!Pose.bValid || Pose.Layer < .9f || Pose.Aim < .9f)')],
 'EnemyCombatMobile.cpp':[
  ('const auto* Anim=E->Body ? Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance()) : nullptr;\n    if (!Anim || FMath::Abs(Anim->RifleLeanDegrees)>.5f)',
   'const auto Pose=E->GetRiflePose();\n    if (!Pose.bValid || FMath::Abs(Pose.Lean)>.5f)')],
 'EnemyCombatObservation.cpp':[
  ('if (const auto* Anim=E->Body ? Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance()) : nullptr)\n            S.LeanAnimated=Anim->RifleLeanDegrees;',
   'S.LeanAnimated=E->GetRiflePose().Lean;')],
 'EnemyCombatLean.cpp':[
  ('const auto* Anim=E && E->Body ? Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance()) : nullptr;',
   'const auto Pose=E ? E->GetRiflePose() : FEnemyRiflePose{};'),
  ('const auto* Anim=E->Body ? Cast<UGASPALSRifleAnimInstance>(E->Body->GetAnimInstance()) : nullptr;\n    const float Actual=Anim ? Anim->RifleLeanDegrees : 0;',
   'const auto Pose=E->GetRiflePose();\n    const float Actual=Pose.Lean;'),
  ('!Anim || Anim->RifleAlpha<.99f || Anim->RifleAimAlpha<.99f || FMath::Abs(Anim->RifleLeanDegrees)',
   '!Pose.bValid || Pose.Layer<.99f || Pose.Aim<.99f || FMath::Abs(Pose.Lean)'),
  ('|| !Anim || LeanSign()', '|| !Pose.bValid || LeanSign()'),
  ('Anim->RifleLeanDegrees-LeanSign()', 'Pose.Lean-LeanSign()')]
}
for name,edits in patches.items():
    p=ROOT/name
    raw=p.read_bytes()
    nl=b'\r\n' if b'\r\n' in raw else b'\n'
    text=raw.decode().replace('\r\n','\n')
    for before,after in edits:
        assert before in text,(name,before)
        text=text.replace(before,after)
    text=text.replace('#include "GASPALSRifleAnimInstance.h"\n','')
    p.write_bytes(text.replace('\n',nl.decode()).encode())
print('Updated four combat consumers without changing tactical policy.')
