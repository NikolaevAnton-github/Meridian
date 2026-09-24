#include "GASPALSLocomotionFixture.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"

void AGASPALSLocomotionFixture::UpdateCoverAnatomy()
{
    if (!IsReady() || IsDead() || Authority!=EGASPEnemyAuthority::Locomotion ||
        !LocalHitRemaining.IsEmpty() || !CharacterMovement->IsMovingOnGround()) return;
    const auto Pose=GetRiflePose();
    const bool Crouched=IsMovementCrouched();
    // Crouched protection lowers the rifle; standing exposure aims it. Record
    // each consumer's actual achieved weapon pose, including locomotion samples.
    if (!Pose.bValid || (Crouched ? Pose.Aim>.01f : Pose.Aim<.99f) ||
        FMath::Abs(Pose.Lean)>.25f || FMath::Abs(RifleLeanTarget)>.25f) return;
    const FVector Muzzle=Rifle->DoesSocketExist(TEXT("Muzzle")) ? Rifle->GetSocketLocation(TEXT("Muzzle")) :
        Rifle->GetComponentTransform().TransformPosition(FVector(0,62,9));
    if (!Crouched && (!bHasRifleAimTarget || FVector::DotProduct(Rifle->GetRightVector(),(RifleAimTarget-Muzzle).GetSafeNormal())<
        FMath::Cos(FMath::DegreesToRadians(6.f)))) return;
    const FVector Feet=Character->GetActorLocation()-FVector(0,0,Capsule->GetScaledCapsuleHalfHeight());
    const FRotator Heading(0,(Crouched ? GetRifleAimDirection() : Rifle->GetRightVector()).Rotation().Yaw,0);
    FEnemyCoverAnatomy Measured;
    Measured.bRequired=true;
    for (const FVector& P:TArray<FVector>{Body->GetSocketLocation(TEXT("head")),Body->GetSocketLocation(TEXT("spine_05")),
        Body->GetSocketLocation(TEXT("hand_r")),Muzzle})
    {
        if (P.ContainsNaN()) return;
        Measured.Points.Add(Heading.UnrotateVector(P-Feet));
    }
    Measured.Pivot=Heading.UnrotateVector(Body->GetSocketLocation(TEXT("spine_01"))-Feet);
    if (Measured.Pivot.ContainsNaN()) return;
    CoverAnatomy[Crouched ? 1 : 0]=MoveTemp(Measured);
}

FEnemyCoverAnatomy AGASPALSLocomotionFixture::GetCoverAnatomy(bool bCrouched) const
{
    auto Result=CoverAnatomy[bCrouched ? 1 : 0];
    Result.bRequired=true;
    if (Result.IsValid() || !Character || !CharacterMovement || !Capsule) return Result;
    Result=CoverAnatomy[bCrouched ? 0 : 1]; Result.bRequired=true;
    if (!Result.IsValid()) return Result;
    // Candidate01 Masculine/Rifle calibration: paired standing aim and crouched
    // ready poses; tracked provenance: Scripts/CombatAI01/GASPALSFix01/source-anatomy-calibration.json.
    // CMC shrinks its capsule by only 26 cm, while this graph lowers the head
    // about 43 cm. Use the measured per-point change until the stance is observed.
    // These are proposal offsets for this source asset, never launch authority.
    const FVector CrouchDelta[]={FVector(-3.7595,-9.3866,-43.3461),FVector(-5.7002,-2.4666,-44.1514),
        FVector(-6.2943,-1.2147,-45.5226),FVector(-47.7292,-64.9061,-74.6304)};
    const float Scale=Body->GetComponentScale().Z*(bCrouched ? 1.f : -1.f);
    for (int32 I=0; I<4; ++I) Result.Points[I]+=CrouchDelta[I]*Scale;
    Result.Pivot+=FVector(-9.4090,2.9773,-43.6486)*Scale;
    return Result;
}
