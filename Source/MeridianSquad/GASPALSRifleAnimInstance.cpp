#include "GASPALSRifleAnimInstance.h"
#include "GASPEnemyFixture.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "GameFramework/Pawn.h"
#include "Serialization/JsonSerializer.h"
#if WITH_EDITOR
#include "Serialization/ArchiveReplaceObjectRef.h"
#endif

bool UGASPALSAnimationLibrary::RemapImportedReferences(const TArray<UObject*>& Sources, const TArray<UObject*>& Derivatives)
{
#if WITH_EDITOR
    if (Sources.Num() != Derivatives.Num()) return false;
    TMap<UObject*,UObject*> Replacements;
    for (int32 I=0; I<Sources.Num(); ++I)
    {
        if (!Sources[I] || !Derivatives[I] || !Derivatives[I]->GetPathName().StartsWith(TEXT("/GASPALSEnemy01/"))) return false;
        Replacements.Add(Sources[I],Derivatives[I]);
    }
    for (UObject* Asset : Derivatives)
    {
        Asset->Modify();
        FArchiveReplaceObjectRef<UObject> Replace(Asset,Replacements,
            EArchiveReplaceObjectFlags::IgnoreOuterRef | EArchiveReplaceObjectFlags::IgnoreArchetypeRef);
        Asset->PostEditChange();
    }
    return true;
#else
    return false;
#endif
}

FString UGASPALSAnimationLibrary::CompareSkeletons(USkeleton* SourceSkeleton, USkeleton* TargetSkeleton)
{
    if (!SourceSkeleton || !TargetSkeleton) return TEXT("{}");
    const auto& Source = SourceSkeleton->GetReferenceSkeleton();
    const auto& Target = TargetSkeleton->GetReferenceSkeleton();
    auto Result = MakeShared<FJsonObject>();
    Result->SetNumberField(TEXT("source_raw_bones"),Source.GetRawBoneNum());
    Result->SetNumberField(TEXT("target_raw_bones"),Target.GetRawBoneNum());
    TArray<TSharedPtr<FJsonValue>> Rows;
    for (int32 T = 0; T < Target.GetRawBoneNum(); ++T)
    {
        const FName Name = Target.GetBoneName(T);
        const int32 S = Source.FindBoneIndex(Name);
        auto Row = MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("bone"),Name.ToString());
        Row->SetNumberField(TEXT("source_index"),S);
        Row->SetNumberField(TEXT("target_index"),T);
        if (S != INDEX_NONE)
        {
            const int32 SP = Source.GetParentIndex(S), TP = Target.GetParentIndex(T);
            Row->SetBoolField(TEXT("parent_matches"),(SP == INDEX_NONE && TP == INDEX_NONE) ||
                (SP != INDEX_NONE && TP != INDEX_NONE && Source.GetBoneName(SP) == Target.GetBoneName(TP)));
            const FTransform A = Source.GetRefBonePose()[S], B = Target.GetRefBonePose()[T];
            Row->SetNumberField(TEXT("translation_delta"),(A.GetTranslation()-B.GetTranslation()).Size());
            Row->SetNumberField(TEXT("rotation_delta_degrees"),FMath::RadiansToDegrees(A.GetRotation().AngularDistance(B.GetRotation())));
            Row->SetStringField(TEXT("source_ref"),A.ToString());
            Row->SetStringField(TEXT("target_ref"),B.ToString());
        }
        Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Result->SetArrayField(TEXT("bones"),Rows);
    FString Text;
    FJsonSerializer::Serialize(Result,TJsonWriterFactory<>::Create(&Text));
    return Text;
}

void UGASPALSRifleAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    const auto* Enemy = AGASPEnemyFixture::FromFoundation(TryGetPawnOwner());
    if (!Enemy) { RifleAlpha = RifleLeanDegrees = 0; return; }
    const bool bRifleOwnsPose = Enemy->Authority == EGASPEnemyAuthority::Locomotion && !Enemy->IsDead() && Enemy->IsRifleHeld();
    // Physical snapshots, ragdoll and get-up own the arms immediately. The return
    // is gradual and participates in the existing physical-target handoff blend.
    RifleAlpha = bRifleOwnsPose ? FMath::FInterpTo(RifleAlpha, 1.f, DeltaSeconds, 5.f) : 0.f;
    const auto Motion = Enemy->GetFireMotion();
    const bool CanLean = bRifleOwnsPose && Motion.Gate() == CombatAI::MotionGate::Ready &&
        Motion.Speed <= 15 && !Enemy->IsMovementCrouched() && !Enemy->bCrouchCommand;
    // About .27 world seconds to full 32-degree exposure, symmetric blend back.
    // Physical authority/weapon loss clears the offset immediately.
    RifleLeanDegrees = bRifleOwnsPose ? FMath::FInterpConstantTo(RifleLeanDegrees,
        CanLean ? Enemy->RifleLeanTarget : 0.f, DeltaSeconds, 120.f) : 0.f;
    const float Ready = Enemy->RifleStance == EGASPALSRifleStance::Relax ? 0.f : 1.f;
    const float Aim = Enemy->RifleStance == EGASPALSRifleStance::Aim ? 1.f : 0.f;
    RifleReadyAlpha = FMath::FInterpTo(RifleReadyAlpha, Ready, DeltaSeconds, 8.f);
    RifleAimAlpha = FMath::FInterpTo(RifleAimAlpha, Aim, DeltaSeconds, 8.f);
    RifleMoveAlpha = FMath::FInterpTo(RifleMoveAlpha, Enemy->GetRifleMovementAlpha(), DeltaSeconds, 8.f);
    RifleCrouchAlpha = FMath::FInterpTo(RifleCrouchAlpha, Enemy->IsMovementCrouched() ? 1.f : 0.f, DeltaSeconds, 10.f);
    const float Pitch = FMath::Clamp(Enemy->GetRifleAimDirection().Rotation().Pitch, -70.f, 70.f);
    RiflePitchTime = FMath::FInterpTo(RiflePitchTime, .5f - Pitch / 180.f, DeltaSeconds, 12.f);
}

FRotator UGASPALSRifleAnimInstance::GetRifleAimCorrection(FVector2D RootRelativeAim) const
{
    // The retained downstream OffsetRootBone can keep a heading different from
    // the capsule. AO.X is GASP's desired yaw relative to that retained root.
    // The imported pitch sweep rotates around component X. Its reference rifle
    // barrel (+Y on M4A1) also has an authored yaw bias: calibrate that
    // vector from hand_r plus the source attachment, rather than moving the gun
    // in the wrist. Both hands and the chest turn together before the grip IK.
    const FVector SourceBarrel(.22681, .97307, .041112);
    const float Pitch = 90.f - 180.f * RiflePitchTime;
    const FVector SweptBarrel = FQuat(FVector::ForwardVector, FMath::DegreesToRadians(Pitch))
        .RotateVector(SourceBarrel.GetSafeNormal());
    const float Yaw = FMath::FindDeltaAngleDegrees(SweptBarrel.Rotation().Yaw, 90.f + RootRelativeAim.X);
    // Preserve the imported pitch sweep; this seam compensates only heading.
    // A rear target belongs to the source turn-in-place. Fade before its 110
    // degree idle AO limit so crossing +/-180 cannot twist the physical spine.
    const float TurnBlend = 1.f - FMath::SmoothStep(60.f, 110.f, float(FMath::Abs(RootRelativeAim.X)));
    const FQuat Heading = FRotator(0.f, Yaw * RifleAimAlpha * TurnBlend, 0.f).Quaternion();
    // The existing component-space spine_01 control is upstream of grip IK and
    // downstream of the leg-preserving rifle layer. Roll about the corrected
    // barrel vector so pitch/yaw survive; positive lean exposes the right side.
    const FVector Axis = Heading.RotateVector(SweptBarrel.GetSafeNormal());
    const FQuat Lean(Axis, FMath::DegreesToRadians(-RifleLeanDegrees * RifleAimAlpha * TurnBlend));
    return (Lean * Heading).Rotator();
}

bool UGASPALSAnimationLibrary::AssignSkeleton(UAnimSequence* Sequence, USkeleton* Skeleton)
{
#if WITH_EDITOR
    if (!Sequence || !Skeleton || !Sequence->GetSkeleton() ||
        !Sequence->GetPathName().StartsWith(TEXT("/GASPALSEnemy01/"))) return false;
    const auto& Source = Sequence->GetSkeleton()->GetReferenceSkeleton();
    const auto& Target = Skeleton->GetReferenceSkeleton();
    // The adopted GASP skeleton appends props_root/prop_01/poi. All 88 source
    // bones keep their exact indices, parents and reference transforms; these
    // unanimated target-only helpers retain their target reference pose.
    if (Source.GetRawBoneNum() > Target.GetRawBoneNum()) return false;
    for (int32 Index = 0; Index < Source.GetRawBoneNum(); ++Index)
        if (Source.GetBoneName(Index) != Target.GetBoneName(Index) ||
            Source.GetParentIndex(Index) != Target.GetParentIndex(Index) ||
            !Source.GetRefBonePose()[Index].Equals(Target.GetRefBonePose()[Index], .01f)) return false;
    Sequence->Modify();
    Sequence->SetSkeleton(Skeleton);
    Sequence->PostEditChange();
    return true;
#else
    return false;
#endif
}
