#include "GASPALSLocomotionFixture.h"
#include "CombatProjectileWorld.h"
#include "PhysicsControlComponent.h"
#include "Animation/AnimMontage.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "UObject/UnrealType.h"

namespace
{
bool SourceBool(const UObject* Object,FName Name)
{
    const auto* P=Object ? FindFProperty<FBoolProperty>(Object->GetClass(),Name) : nullptr;
    return P && P->GetPropertyValue_InContainer(Object);
}
constexpr float LocalHitDuration=.55f;
}

UGASPALSPostSourceTick::UGASPALSPostSourceTick()
{
    PrimaryComponentTick.bCanEverTick=true;
    PrimaryComponentTick.TickGroup=TG_PrePhysics;
}
void UGASPALSPostSourceTick::TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(DeltaTime,TickType,TickFunction);
    const auto* Enemy=Cast<AGASPALSLocomotionFixture>(AGASPEnemyFixture::FromFoundation(GetOwner()));
    if (Enemy && Enemy->IsDead() && Enemy->Body)
        Enemy->Body->SetAllMotorsAngularDriveParams(0,0,0);
}

void AGASPALSLocomotionFixture::ConfigureHitControls()
{
    auto* PostSource=NewObject<UGASPALSPostSourceTick>(Character,TEXT("MSQ121PassiveCorpse"),RF_Transient);
    Character->AddInstanceComponent(PostSource);
    PostSource->RegisterComponent();
    PostSource->AddTickPrerequisiteActor(Character);
    PostSource->AddTickPrerequisiteComponent(Body);
    PhysicsControl=NewObject<UPhysicsControlComponent>(Character,TEXT("MSQ121LocalizedHits"),RF_Transient);
    Character->AddInstanceComponent(PhysicsControl);
    PhysicsControl->RegisterComponent();
    PhysicsControl->AddTickPrerequisiteActor(this);
    PhysicsControl->AddTickPrerequisiteComponent(Body);
    PhysicsControl->AddTickPrerequisiteComponent(CharacterMovement);
    const auto* Asset=Body->GetPhysicsAsset();
    for (const auto& Setup:Asset->SkeletalBodySetups)
    {
        const FName Bone=Setup->BoneName;
        if (Bone==TEXT("root") || Bone==TEXT("pelvis")) continue;
        FName Parent=Body->GetParentBone(Bone);
        while (!Parent.IsNone() && Asset->FindBodyIndex(Parent)==INDEX_NONE) Parent=Body->GetParentBone(Parent);
        auto* BI=Body->GetBodyInstance(Bone);
        if (Parent.IsNone() || !BI) continue;
        FPhysicsControlData Data;
        Data.bEnabled=false;
        Data.bUseSkeletalAnimation=true;
        Data.bOnlyControlChildObject=true;
        Data.bDisableCollision=false;
        Data.LinearStrength=6.f; Data.AngularStrength=12.f;
        Data.MaxForce=FMath::Max(1.f,BI->GetBodyMass())*3500.f;
        Data.MaxTorque=FMath::Max(1.f,BI->GetBodyMass())*180000.f;
        const FName Control=PhysicsControl->CreateControl(Body,Parent,Body,Bone,Data,
            FPhysicsControlTarget(),TEXT("LocalizedHits"),TEXT("MSQ121_"));
        if (!Control.IsNone()) LocalHitControls.Add(Bone,Control);
    }
    Body->SetAllBodiesSimulatePhysics(false);
    Body->SetAllBodiesPhysicsBlendWeight(0.f);
    Body->bBlendPhysics=false;
}

FName AGASPALSLocomotionFixture::StartLocalHit(FName HitBone)
{
    // CMC keeps the pelvis/feet support frame. Pelvic hits act on the adjacent
    // lower spine; only a strong hit releases the entire body to source ragdoll.
    FName Root=HitBone;
    const FString Name=HitBone.ToString();
    if (HitBone==TEXT("pelvis") || HitBone==TEXT("root") || Name.StartsWith(TEXT("spine"))) Root=TEXT("spine_01");
    else if (Name.Contains(TEXT("arm")) || Name.StartsWith(TEXT("hand")) || Name.StartsWith(TEXT("clavicle")))
        Root=Name.EndsWith(TEXT("_l")) ? FName("clavicle_l") : FName("clavicle_r");
    else if (Name.StartsWith(TEXT("thigh")) || Name.StartsWith(TEXT("calf")) || Name.StartsWith(TEXT("foot")))
        Root=Name.EndsWith(TEXT("_l")) ? FName("thigh_l") : FName("thigh_r");
    FName ImpulseBone=LocalHitControls.Contains(HitBone) ? HitBone : NAME_None;
    double NearestDistance=TNumericLimits<double>::Max();
    const FVector HitBoneLocation=Body->GetSocketLocation(HitBone);
    for (const auto& Pair:LocalHitControls)
    {
        if (Pair.Key!=Root && !Body->BoneIsChildOf(Pair.Key,Root)) continue;
        if (auto* BI=Body->GetBodyInstance(Pair.Key))
        {
            BI->SetInstanceSimulatePhysics(true,true,true);
            BI->PhysicsBlendWeight=1.f;
            LocalHitRemaining.Add(Pair.Key,LocalHitDuration);
            PhysicsControl->SetControlEnabled(Pair.Value,true);
            FPhysicsControlMultiplier Soft;
            Soft.LinearStrengthMultiplier=FVector(.08f);
            Soft.AngularStrengthMultiplier=.08f;
            PhysicsControl->SetControlMultiplier(Pair.Value,Soft);
            if (!LocalHitControls.Contains(HitBone))
            {
                const double Distance=FVector::DistSquared(HitBoneLocation,Body->GetSocketLocation(Pair.Key));
                if (Distance<NearestDistance) { ImpulseBone=Pair.Key; NearestDistance=Distance; }
            }
        }
    }
    // Per-body weights must govern local hits. The component-wide flag would
    // force every simulated body's blend to 1 and bypass the fade-out.
    Body->bBlendPhysics=false;
    return ImpulseBone;
}

void AGASPALSLocomotionFixture::UpdateLocalHits(float DeltaSeconds)
{
    for (auto It=LocalHitRemaining.CreateIterator();It;++It)
    {
        It.Value()=FMath::Max(0.f,It.Value()-DeltaSeconds);
        const float Alpha=It.Value()/LocalHitDuration;
        FPhysicsControlMultiplier Strength;
        const float Drive=FMath::Lerp(1.f,.08f,Alpha*Alpha);
        Strength.LinearStrengthMultiplier=FVector(Drive); Strength.AngularStrengthMultiplier=Drive;
        const FName Control=LocalHitControls.FindRef(It.Key());
        PhysicsControl->SetControlMultiplier(Control,Strength);
        if (auto* BI=Body->GetBodyInstance(It.Key()))
        {
            BI->PhysicsBlendWeight=FMath::Clamp(Alpha*3.f,0.f,1.f);
            if (It.Value()==0)
            {
                BI->SetInstanceSimulatePhysics(false,true,true);
                PhysicsControl->SetControlEnabled(Control,false);
            }
        }
        if (It.Value()==0) It.RemoveCurrent();
    }
    if (Authority==EGASPEnemyAuthority::Locomotion) Body->bBlendPhysics=false;
}
void AGASPALSLocomotionFixture::ClearLocalHits()
{
    for (const auto& Pair:LocalHitControls) PhysicsControl->SetControlEnabled(Pair.Value,false);
    LocalHitRemaining.Reset();
}

void AGASPALSLocomotionFixture::StartSourceRagdoll(bool bDeath)
{
    ClearLocalHits();
    const bool WasRagdoll=SourceBool(Character,TEXT("bIsRagdolling"));
    ChangeSourceAuthority(bDeath ? EGASPEnemyAuthority::Dead : EGASPEnemyAuthority::Falling);
    BalanceState=bDeath ? EDummyBalanceState::Dead : EDummyBalanceState::Falling;
    Character->ConsumeMovementInputVector();
    // The source owns capsule disabling, montage interruption and simulation.
    // Calling StartRagdoll again would destroy an existing corpse's momentum.
    if (!WasRagdoll) CallFoundation(TEXT("StartRagdoll"));
    Body->SetAllBodiesPhysicsBlendWeight(1.f);
    Body->bBlendPhysics=true;
    Body->bPauseAnims=false;
    RagdollSeconds=SettledSeconds=GettingUpSeconds=0;
    bHadSourceGetUp=false;
    if (bDeath)
    {
        // Source UpdateRagdoll normally adds velocity-scaled angular motors.
        // A corpse must stay passive; its update remains responsible for location.
        Body->SetAllMotorsAngularDriveParams(0,0,0);
    }
}

bool AGASPALSLocomotionFixture::CanSourceGetUp() const
{
    if (!SourceBool(Character,TEXT("RagdollOnGround"))) return false;
    const auto* Pelvis=Body->GetBodyInstance(TEXT("pelvis"));
    if (!Pelvis || Pelvis->GetUnrealWorldVelocity().Size()>45.f ||
        Pelvis->GetUnrealWorldAngularVelocityInRadians().Size()>1.5f) return false;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(GASPALSGetUpClearance),false);
    Query.AddIgnoredActor(this); Query.AddIgnoredActor(Character);
    FHitResult Floor;
    const FVector P=Pelvis->GetUnrealWorldTransform().GetLocation();
    if (!GetWorld()->LineTraceSingleByChannel(Floor,P+FVector(0,0,20),P-FVector(0,0,150),ECC_WorldStatic,Query) ||
        Floor.ImpactNormal.Z<CharacterMovement->GetWalkableFloorZ()) return false;
    const auto* Defaults=CastChecked<ACharacter>(Character->GetClass()->GetDefaultObject());
    const float HalfHeight=Defaults->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    const float Radius=Capsule->GetScaledCapsuleRadius();
    const FVector Center=Floor.ImpactPoint+FVector(0,0,HalfHeight+2.f);
    return !GetWorld()->OverlapBlockingTestByChannel(Center,FQuat::Identity,ECC_Pawn,
        FCollisionShape::MakeCapsule(Radius,HalfHeight-.5f),Query);
}

void AGASPALSLocomotionFixture::UpdateSourceRecovery(float DeltaSeconds)
{
    if (IsDead()) return;
    if (Authority==EGASPEnemyAuthority::Falling || Authority==EGASPEnemyAuthority::Down)
    {
        RagdollSeconds+=DeltaSeconds;
        if (CanSourceGetUp())
        {
            SettledSeconds+=DeltaSeconds;
            ChangeSourceAuthority(EGASPEnemyAuthority::Down);
            BalanceState=EDummyBalanceState::Down;
        }
        else SettledSeconds=0;
        if (RagdollSeconds>=1.1f && SettledSeconds>=.65f)
        {
            // Original source snapshot, face-up selection and montage playback.
            ChangeSourceAuthority(EGASPEnemyAuthority::GettingUp);
            BalanceState=EDummyBalanceState::GettingUp;
            CallFoundation(TEXT("StopRagdoll"));
            Body->SetAllBodiesPhysicsBlendWeight(0.f); Body->bBlendPhysics=false;
            Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
            GettingUpSeconds=0;
            bHadSourceGetUp=FoundationAnimation->GetCurrentActiveMontage()!=nullptr;
        }
    }
    else if (Authority==EGASPEnemyAuthority::GettingUp)
    {
        GettingUpSeconds+=DeltaSeconds;
        UAnimMontage* Montage=FoundationAnimation->GetCurrentActiveMontage();
        if (Montage) bHadSourceGetUp=true;
        if (!CharacterMovement->IsMovingOnGround() && GettingUpSeconds>.2f)
        { StartSourceRagdoll(false); return; }
        if (bHadSourceGetUp && !Montage)
        {
            ++SourceGetUps;
            ChangeSourceAuthority(EGASPEnemyAuthority::Locomotion);
            BalanceState=EDummyBalanceState::Standing;
        }
        else if (GettingUpSeconds>8.f || (!bHadSourceGetUp && GettingUpSeconds>1.f))
            StartSourceRagdoll(false);
    }
}

float AGASPALSLocomotionFixture::ReceiveBullet(int64 ShotId,float Damage,const FVector& Direction,const FHitResult& Hit,
    double ContactTime,double BirthTime,uint64 CombatFrame,float FallImpulseMultiplier,float DeathImpulseMultiplier)
{
    auto* BI=Body ? Body->GetBodyInstance(Hit.BoneName) : nullptr;
    if (!bReady || !BI || !FMath::IsFinite(Damage) || Damage<=0 || Direction.ContainsNaN()) return 0;
    const bool WasDead=IsDead();
    const auto* World=ACombatProjectileWorld::Find(GetWorld());
    const float Applied=WasDead || (World && World->bImmortalDummies) ? 0.f : FMath::Min(Health,Damage);
    Health=FMath::Max(0.f,Health-Applied);
    if (!WasDead && Health==0)
    { ++Deaths; DeathTime=ContactTime; DeathFrame=CombatFrame; StartSourceRagdoll(true); }
    RecentImpact=ImpactAge<=.65f ? RecentImpact+Damage : Damage;
    ImpactAge=0;
    // Ordinary rifle contacts keep combat authority. Large or clustered contacts
    // release the entire body, without entering the old recovery/stepping loop.
    const bool Strong=!IsDead() && (Damage>=40.f || RecentImpact>=60.f || Authority==EGASPEnemyAuthority::GettingUp);
    if (Strong) StartSourceRagdoll(false);
    FName ImpulseBone=Hit.BoneName;
    if (!IsDead() && Authority==EGASPEnemyAuthority::Locomotion) ImpulseBone=StartLocalHit(Hit.BoneName);
    auto* ImpactBody=Body->GetBodyInstance(ImpulseBone);
    const float Base=FMath::Min(FMath::Clamp(BulletImpulse,0.f,5000.f),BI->GetBodyMass()*FMath::Clamp(MaxImpulseVelocity,0.f,450.f));
    float Scale=1.f;
    if (!WasDead && IsDead() && FMath::IsFinite(DeathImpulseMultiplier)) Scale=FMath::Clamp(DeathImpulseMultiplier,1.f,6.f);
    else if (Strong && FMath::IsFinite(FallImpulseMultiplier)) Scale=FMath::Clamp(FallImpulseMultiplier,1.f,6.f);
    if (ImpactBody && !ImpulseBone.IsNone())
    {
        Body->WakeRigidBody(ImpulseBone);
        Body->AddImpulseAtLocation(Direction.GetSafeNormal()*Base*Scale,Hit.ImpactPoint,ImpulseBone);
        ++PhysicalHits;
    }
    auto Row=MakeShared<FJsonObject>();
    Row->SetNumberField(TEXT("shot"),ShotId); Row->SetNumberField(TEXT("birth_time"),BirthTime);
    Row->SetNumberField(TEXT("contact_time"),ContactTime); Row->SetNumberField(TEXT("combat_frame"),CombatFrame);
    Row->SetStringField(TEXT("bone"),Hit.BoneName.ToString()); Row->SetStringField(TEXT("impulse_bone"),ImpulseBone.ToString());
    Row->SetNumberField(TEXT("damage"),Applied); Row->SetBoolField(TEXT("was_dead"),WasDead);
    Row->SetNumberField(TEXT("impulse_magnitude"),Base*Scale); Row->SetNumberField(TEXT("impulse_count"),ImpactBody ? 1 : 0);
    Row->SetBoolField(TEXT("strong"),Strong); Row->SetBoolField(TEXT("custom_balance"),false);
    Contacts.Add(MakeShared<FJsonValueObject>(Row));
    if (Contacts.Num()>128) Contacts.RemoveAt(0,Contacts.Num()-128);
    return Applied;
}

void AGASPALSLocomotionFixture::ApplyExternalDisturbance(FVector Impulse,FVector WorldPoint,FName Bone)
{
    auto* BI=Body ? Body->GetBodyInstance(Bone) : nullptr;
    if (!bReady || !BI || Impulse.ContainsNaN() || WorldPoint.ContainsNaN() || Impulse.IsNearlyZero()) return;
    const bool Strong=Impulse.Size()/FMath::Max(1.f,BI->GetBodyMass())>=320.f;
    if (!IsDead() && (Strong || Authority==EGASPEnemyAuthority::GettingUp)) StartSourceRagdoll(false);
    const FName ImpulseBone=Authority==EGASPEnemyAuthority::Locomotion ? StartLocalHit(Bone) : Bone;
    if (!ImpulseBone.IsNone()) Body->AddImpulseAtLocation(Impulse,WorldPoint,ImpulseBone);
}
