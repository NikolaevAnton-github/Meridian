#include "GASPALSLocomotionFixture.h"
#include "EnemyCombatComponent.h"
#include "CombatProjectileWorld.h"
#include "PhysicsControlComponent.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimStateMachineTypes.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"

namespace
{
const TCHAR* CharacterPath = TEXT("/Game/Development/GASPALSLocomotion01/Candidate01/BP_GASPALSEnemy_Candidate01.BP_GASPALSEnemy_Candidate01_C");
const TCHAR* RifleLayerPath = TEXT("/GASPALS/OverlaySystem/Overlays/Poses/Rifle/ABP_Overlay_Rifle.ABP_Overlay_Rifle_C");
// The source project uses 30. Keep this scoped to the migrated graph: the older
// sample uses the same DDC cvar name with a different default in the owner config.
TAutoConsoleVariable<float> SourceRootRadius(TEXT("msq.GASPALS.OffsetRootTranslationRadius"),30.f,
    TEXT("Source GASPALS root translation radius, cm. Used only by the MSQ-121 graph."));
TAutoConsoleVariable<bool> SourceThreadSafe(TEXT("msq.GASPALS.ThreadSafeAnimationUpdate"),true,
    TEXT("Source GASPALS thread-safe animation update default."));
TAutoConsoleVariable<bool> SourceExperimental(TEXT("msq.GASPALS.ExperimentalStateMachine"),false,
    TEXT("Source GASPALS experimental state machine default."));
TAutoConsoleVariable<bool> SourceExperimentalDebug(TEXT("msq.GASPALS.ExperimentalStateMachineDebug"),false,
    TEXT("Source GASPALS experimental state machine debug default."));

int64 ReadEnum(const UObject* Object, FName Name)
{
    if (!Object) return INDEX_NONE;
    const auto* P = FindFProperty<FProperty>(Object->GetClass(),Name);
    if (const auto* E = CastField<FEnumProperty>(P))
        return E->GetUnderlyingProperty()->GetSignedIntPropertyValue(E->ContainerPtrToValuePtr<void>(Object));
    if (const auto* E = CastField<FByteProperty>(P)) return E->GetPropertyValue_InContainer(Object);
    return INDEX_NONE;
}
void WriteBool(UObject* Object, FName Name, bool Value)
{
    if (auto* P = Object ? FindFProperty<FBoolProperty>(Object->GetClass(),Name) : nullptr)
        P->SetPropertyValue_InContainer(Object,Value);
}
UObject* ReadObject(const UObject* Object, FName Name)
{
    const auto* P = Object ? FindFProperty<FObjectPropertyBase>(Object->GetClass(),Name) : nullptr;
    return P ? P->GetObjectPropertyValue_InContainer(Object) : nullptr;
}
TSharedPtr<FJsonValue> JsonVector(FVector V)
{
    return MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{
        MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)});
}
FString JsonString(const TSharedRef<FJsonObject>& Object)
{
    FString Result;
    FJsonSerializer::Serialize(Object,TJsonWriterFactory<>::Create(&Result));
    return Result;
}
}

void UGASPALSLocomotionAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    const auto* Enemy = Cast<AGASPALSLocomotionFixture>(AGASPEnemyFixture::FromFoundation(TryGetPawnOwner()));
    if (!Enemy || !Enemy->IsReady() || Enemy->IsDead() || Enemy->Authority != EGASPEnemyAuthority::Locomotion)
    {
        MSQLeanDegrees = 0;
        MSQLeanRotation = FRotator::ZeroRotator;
        return;
    }
    MSQLeanDegrees = FMath::FInterpConstantTo(MSQLeanDegrees,Enemy->RifleLeanTarget,
        FMath::Clamp(DeltaSeconds,0.f,.2f),120.f);
    // Rotate the upper-body subtree about the actual source rifle barrel axis.
    // This preserves source aim/IK and the barrel direction during tactical lean.
    const FVector Axis = GetOwningComponent()->GetComponentTransform().InverseTransformVectorNoScale(
        Enemy->Rifle ? Enemy->Rifle->GetRightVector() : Enemy->GetRifleAimDirection()).GetSafeNormal();
    MSQLeanRotation = FQuat(Axis,FMath::DegreesToRadians(-MSQLeanDegrees)).Rotator();
}

AGASPALSLocomotionFixture::AGASPALSLocomotionFixture()
{
    // Historical objects remain constructible for archived fixtures, but no tick,
    // source Mover input producer or balance/recovery drive belongs to this path.
    FoundationPhysicsTick->PrimaryComponentTick.bStartWithTickEnabled = false;
    FoundationPhysicsTick->SetComponentTickEnabled(false);
    UnusedLegacyBody->SetVisibility(false,true);
    UnusedLegacyBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    UnusedLegacyBody->SetComponentTickEnabled(false);
    UnusedLegacyControls->SetComponentTickEnabled(false);
}

void AGASPALSLocomotionFixture::DestroySourcePawn()
{
    bReady = false;
    if (IsValid(PhysicsControl) && PhysicsControl != UnusedLegacyControls)
        PhysicsControl->DestroyControls(PhysicsControl->GetAllControlNames());
    LocalHitControls.Reset(); LocalHitRemaining.Reset();
    if (IsValid(Foundation))
    {
        // The sample creates optional mesh-display actors on possession. They
        // belong to this pawn, so reset removes them as well as the held component.
        TArray<AActor*> AttachedChildren;
        Foundation->GetAttachedActors(AttachedChildren,true,true);
        for (AActor* Child : AttachedChildren)
            if (IsValid(Child) && Child->GetOwner()==Foundation) Child->Destroy();
        for (FName Name : {FName("SpawnedStaticMeshes"),FName("SpawnedSkeletalMeshes")})
            if (const auto* P=FindFProperty<FArrayProperty>(Foundation->GetClass(),Name))
                if (const auto* Inner=CastField<FObjectPropertyBase>(P->Inner))
                {
                    FScriptArrayHelper Values(P,P->ContainerPtrToValuePtr<void>(Foundation));
                    for (int32 I=0;I<Values.Num();++I)
                        if (auto* Actor=Cast<AActor>(Inner->GetObjectPropertyValue(Values.GetRawPtr(I))))
                            if (IsValid(Actor) && Actor->GetOwner()==Foundation) Actor->Destroy();
                }
        Foundation->Destroy();
    }
    if (IsValid(CommandController)) CommandController->Destroy();
    Foundation=nullptr; Character=nullptr; CharacterMovement=nullptr;
    CommandController=nullptr; Capsule=nullptr; FoundationAnimation=nullptr; Rifle=nullptr;
    Body=UnusedLegacyBody; PhysicsControl=UnusedLegacyControls;
}

void AGASPALSLocomotionFixture::ResetDummy()
{
    if (Combat) Combat->StopCombat();
    DestroySourcePawn();
    SetActorTransform(Home,false,nullptr,ETeleportType::TeleportPhysics);
    Health=FMath::IsFinite(MaxHealth) ? FMath::Clamp(MaxHealth,1.f,100000.f) : 100.f;
    Deaths=PhysicalHits=SourceGetUps=0; DeathFrame=0; DeathTime=-1;
    ++PoseEpoch;
    Contacts.Reset(); SourceFailure.Reset();
    StopMovementCommand();
    RifleStance=EGASPALSRifleStance::Ready;
    RifleLeanTarget=0;
    bCrouchCommand=bRifleFollowPlayer=bHasRifleAimTarget=false;
    bRifleHeld=true;
    Authority=EGASPEnemyAuthority::Locomotion; BalanceState=EDummyBalanceState::Standing;
    RecentImpact=RagdollSeconds=SettledSeconds=GettingUpSeconds=0; ImpactAge=10;
    bHadSourceGetUp=false;
    if (Combat) Combat->ResetCombat(Home.GetLocation(),Home.Rotator());
    UClass* Class=LoadClass<ACharacter>(nullptr,CharacterPath);
    RifleLayerClass=LoadClass<UAnimInstance>(nullptr,RifleLayerPath);
    if (!Class || !RifleLayerClass) { SourceFailure=TEXT("MSQ-121 source class/layer is unavailable"); return; }
    const auto* Defaults=CastChecked<ACharacter>(Class->GetDefaultObject());
    FTransform Placement=Home;
    Placement.AddToTranslation(FVector(0,0,Defaults->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()+2.f));
    FActorSpawnParameters Spawn;
    Spawn.Owner=this; Spawn.ObjectFlags|=RF_Transient; Spawn.bDeferConstruction=true;
    Spawn.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    Character=GetWorld()->SpawnActor<ACharacter>(Class,Placement,Spawn);
    Foundation=Character;
    if (!Character) { SourceFailure=TEXT("MSQ-121 source character spawn failed"); return; }
    Character->AutoPossessAI=EAutoPossessAI::Disabled;
    Character->AutoPossessPlayer=EAutoReceiveInput::Disabled;
    Character->FinishSpawning(Placement);
    Body=Character->GetMesh(); CharacterMovement=Character->GetCharacterMovement();
    Capsule=Character->GetCapsuleComponent(); FoundationAnimation=Body->GetAnimInstance();
    FActorSpawnParameters ControllerSpawn;
    ControllerSpawn.Owner=this; ControllerSpawn.ObjectFlags|=RF_Transient;
    CommandController=GetWorld()->SpawnActor<AGASPEnemyCommandController>(ControllerSpawn);
    if (!CommandController || !FoundationAnimation || !Body->GetPhysicsAsset())
    { SourceFailure=TEXT("MSQ-121 source components are unavailable"); return; }
    CommandController->Possess(Character);
    Character->SetOwner(this);
    // Source possession initializes CharactersSkeletalMeshes after its overlay
    // event. Reapply the original functions once that array is complete.
    CallFoundation(TEXT("UpdateOverlayBase"));
    CallFoundation(TEXT("UpdateOverlayPose"));
    Rifle=Cast<USkeletalMeshComponent>(ReadObject(Character,TEXT("OverlaySkeletalMesh")));
    Body->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Body->SetCollisionResponseToChannel(ECC_Pawn,ECR_Ignore);
    Body->SetCollisionResponseToChannel(ECC_Camera,ECR_Ignore);
    Body->SetGenerateOverlapEvents(false);
    if (Rifle)
    {
        Rifle->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Rifle->SetGenerateOverlapEvents(false);
        Rifle->SetCanEverAffectNavigation(false);
    }
    Foundation->AddTickPrerequisiteActor(this);
    TInlineComponentArray<UActorComponent*> SourceComponents(Foundation);
    for (UActorComponent* Component:SourceComponents)
        if (Component->GetName().Contains(TEXT("PreCMCTick"))) Component->AddTickPrerequisiteActor(this);
    CharacterMovement->AddTickPrerequisiteActor(this);
    ConfigureHitControls();
    bReady=Rifle && Rifle->GetSkeletalMeshAsset() && !LocalHitControls.IsEmpty();
    if (!bReady) SourceFailure=TEXT("MSQ-121 source rifle or local hit controls are unavailable");
    ApplySourceCommands();
    UpdateLabel();
}

void AGASPALSLocomotionFixture::ApplySourceCommands()
{
    if (!Character || !CharacterMovement || !CommandController) return;
    if (bRifleFollowPlayer)
        if (auto* Player=GetWorld()->GetFirstPlayerController())
        {
            FRotator Rotation;
            Player->GetPlayerViewPoint(RifleAimTarget,Rotation);
            bHasRifleAimTarget=true;
        }
    const bool Active=bReady && !IsDead() && Authority==EGASPEnemyAuthority::Locomotion;
    const bool Aim=Active && RifleStance==EGASPALSRifleStance::Aim;
    const bool Strafe=Active && (bHasRifleAimTarget || RifleStance!=EGASPALSRifleStance::Relax);
    const FVector Facing=bHasRifleAimTarget ? GetRifleAimDirection() :
        (!MovementCommand.IsNearlyZero() ? MovementCommand : Character->GetActorForwardVector());
    CommandController->SetControlRotation(Facing.Rotation());
    if (auto* Input=FindFProperty<FStructProperty>(Character->GetClass(),TEXT("CharacterInputState")))
    {
        void* Data=Input->ContainerPtrToValuePtr<void>(Character);
        for (TFieldIterator<FBoolProperty> It(Input->Struct);It;++It)
        {
            const FString Name=It->GetName();
            if (Name.StartsWith(TEXT("WantsToWalk_"))) It->SetPropertyValue_InContainer(Data,bWalkCommand);
            else if (Name.StartsWith(TEXT("WantsToSprint_"))) It->SetPropertyValue_InContainer(Data,false);
            else if (Name.StartsWith(TEXT("WantsToStrafe_"))) It->SetPropertyValue_InContainer(Data,Strafe);
            else if (Name.StartsWith(TEXT("WantsToAim_"))) It->SetPropertyValue_InContainer(Data,Aim);
        }
    }
    WriteBool(Character,TEXT("bIsAimInputDown"),Aim);
    if (Active && bCrouchCommand) Character->Crouch(); else Character->UnCrouch();
    Character->AddMovementInput(Active ? MovementCommand : FVector::ZeroVector,1.f);
    // Source PreCMCTick consumes these inputs and computes gait, directional speed,
    // acceleration, friction, braking and rotation. No native MaxWalkSpeed override.
    SetHandOccupancy(Active && IsRifleHeld(),IsRifleHeld());
}

bool AGASPALSLocomotionFixture::IsMovementCrouched() const
{ return Character && Character->bIsCrouched; }
float AGASPALSLocomotionFixture::GetRifleMovementAlpha() const
{ return CharacterMovement ? FMath::Clamp(CharacterMovement->Velocity.Size2D()/100.f,0.f,1.f) : 0.f; }
CombatAI::FireMotion AGASPALSLocomotionFixture::GetFireMotion() const
{
    const FVector V=CharacterMovement ? CharacterMovement->Velocity : FVector::ZeroVector;
    CombatAI::FireMotion Result{V.Size2D(),V.Z,
        IsReady() && !IsDead() && Authority==EGASPEnemyAuthority::Locomotion,
        CharacterMovement && CharacterMovement->IsMovingOnGround(),ReadEnum(Character,TEXT("Gait"))==0};
    Result.SpeedLimit=CharacterMovement ? CharacterMovement->GetMaxSpeed() : 0;
    return Result;
}
FEnemyRiflePose AGASPALSLocomotionFixture::GetRiflePose() const
{
    FEnemyRiflePose Result;
    auto* Main=Body ? Body->GetAnimInstance() : nullptr;
    auto* Layer=Main && RifleLayerClass ? Main->GetLinkedAnimLayerInstanceByClass(RifleLayerClass) : nullptr;
    if (!Layer || !IsRifleHeld()) return Result;
    int32 Machine=INDEX_NONE; const FBakedAnimationStateMachine* Description=nullptr;
    Layer->GetStateMachineIndexAndDescription(TEXT("SM_OverlayPose"),Machine,&Description);
    const int32 AimState=Description ? Description->FindStateIndex(TEXT("Aiming")) : INDEX_NONE;
    if (Machine==INDEX_NONE || AimState==INDEX_NONE) return Result;
    Result.bValid=true;
    Result.Layer=Authority==EGASPEnemyAuthority::Locomotion && !IsDead() ? 1.f : 0.f;
    Result.Aim=Layer->GetInstanceStateWeight(Machine,AimState);
    if (const auto* Anim=Cast<UGASPALSLocomotionAnimInstance>(Main)) Result.Lean=Anim->MSQLeanDegrees;
    return Result;
}
void AGASPALSLocomotionFixture::SetRifleLean(float Degrees,bool bImmediate)
{
    RifleLeanTarget=FMath::IsFinite(Degrees) ? FMath::Clamp(Degrees,-35.f,35.f) : 0.f;
    if (bImmediate && Body)
        if (auto* Anim=Cast<UGASPALSLocomotionAnimInstance>(Body->GetAnimInstance()))
        { Anim->MSQLeanDegrees=0; Anim->MSQLeanRotation=FRotator::ZeroRotator; }
}

void AGASPALSLocomotionFixture::Tick(float DeltaSeconds)
{
    // Deliberately call AActor, never AGASPEnemyFixture/APhysicsControlDummy::Tick.
    AActor::Tick(DeltaSeconds);
    if (!bReady || !IsValid(Character)) return;
    SetActorTransform(Character->GetActorTransform());
    ImpactAge+=DeltaSeconds;
    if (ImpactAge>.65f) RecentImpact=0;
    UpdateLocalHits(DeltaSeconds);
    UpdateSourceRecovery(DeltaSeconds);
    if (Combat) Combat->AdvanceCombat(DeltaSeconds);
    ApplySourceCommands();
    UpdateLabel();
}
void AGASPALSLocomotionFixture::ChangeSourceAuthority(EGASPEnemyAuthority NewAuthority)
{
    if (Authority==NewAuthority) return;
    Authority=NewAuthority;
    if (Authority!=EGASPEnemyAuthority::Locomotion)
    {
        SetRifleLean(0,true);
        if (Combat) Combat->SuspendForPhysics(IsDead());
    }
}
void AGASPALSLocomotionFixture::EndPlay(const EEndPlayReason::Type Reason)
{
    if (Combat) Combat->StopCombat();
    DestroySourcePawn();
    APhysicsControlDummy::EndPlay(Reason);
}

FString AGASPALSLocomotionFixture::GetDummyState(bool IncludeContacts) const
{
    auto Root=MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("name"),GetName());
    Root->SetBoolField(TEXT("ready"),bReady);
    Root->SetNumberField(TEXT("health"),Health);
    Root->SetNumberField(TEXT("deaths"),Deaths);
    Root->SetNumberField(TEXT("physical_hits"),PhysicalHits);
    Root->SetNumberField(TEXT("epoch"),PoseEpoch);
    Root->SetStringField(TEXT("failure"),SourceFailure);
    auto Data=MakeShared<FJsonObject>();
    Data->SetStringField(TEXT("authority"),StaticEnum<EGASPEnemyAuthority>()->GetNameStringByValue(static_cast<int64>(Authority)));
    Data->SetStringField(TEXT("foundation"),Character ? Character->GetClass()->GetPathName() : TEXT(""));
    Data->SetStringField(TEXT("movement_stack"),TEXT("GASPALS CharacterMovement"));
    Data->SetBoolField(TEXT("custom_balance_active"),false);
    Data->SetField(TEXT("movement_command"),JsonVector(MovementCommand));
    Data->SetField(TEXT("capsule_velocity"),JsonVector(CharacterMovement ? CharacterMovement->Velocity : FVector::ZeroVector));
    Data->SetBoolField(TEXT("crouched"),IsMovementCrouched());
    Data->SetNumberField(TEXT("source_speed_limit"),CharacterMovement ? CharacterMovement->GetMaxSpeed() : 0);
    Data->SetNumberField(TEXT("source_gait"),ReadEnum(Character,TEXT("Gait")));
    Data->SetNumberField(TEXT("local_physical_regions"),LocalHitRemaining.Num());
    Data->SetNumberField(TEXT("source_getups"),SourceGetUps);
    const auto Pose=GetRiflePose();
    Data->SetNumberField(TEXT("source_aim_weight"),Pose.Aim);
    Data->SetNumberField(TEXT("lean_degrees"),Pose.Lean);
    Root->SetObjectField(TEXT("gasp"),Data);
    if (IncludeContacts) Root->SetArrayField(TEXT("contacts"),Contacts);
    if (Combat)
    {
        TSharedPtr<FJsonObject> State;
        if (FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Combat->GetCombatState()),State))
            Root->SetObjectField(TEXT("enemy_combat"),State);
    }
    return JsonString(Root);
}

FString UGASPALSLocomotionLibrary::InspectProperties(UObject* Object)
{
    auto Result=MakeShared<FJsonObject>();
    if (!Object) return TEXT("{}");
    for (TFieldIterator<FProperty> It(Object->GetClass());It;++It)
    {
        FString Value;
        It->ExportText_InContainer(0,Value,Object,nullptr,Object,PPF_None);
        Result->SetStringField(It->GetName(),Value);
    }
    return JsonString(Result);
}
FString UGASPALSLocomotionLibrary::InspectAnimationStates(UAnimInstance* Animation)
{
    auto Result=MakeShared<FJsonObject>();
    int32 Index=INDEX_NONE; const FBakedAnimationStateMachine* Desc=nullptr;
    if (Animation) Animation->GetStateMachineIndexAndDescription(TEXT("SM_OverlayPose"),Index,&Desc);
    Result->SetNumberField(TEXT("machine_index"),Index);
    if (Desc)
        for (const auto& State:Desc->States)
            Result->SetNumberField(State.StateName.ToString(),Desc->FindStateIndex(State.StateName));
    return JsonString(Result);
}
FString UGASPALSLocomotionLibrary::InspectPhysicsAsset(UPhysicsAsset* Asset)
{
    auto Result=MakeShared<FJsonObject>();
    if (Asset)
        for (const USkeletalBodySetup* Setup:Asset->SkeletalBodySetups)
        {
            const auto& Geometry=Setup->AggGeom;
            auto Row=MakeShared<FJsonObject>();
            const int32 Supported=Geometry.SphereElems.Num()+Geometry.BoxElems.Num()+Geometry.SphylElems.Num();
            Row->SetNumberField(TEXT("sphere"),Geometry.SphereElems.Num());
            Row->SetNumberField(TEXT("box"),Geometry.BoxElems.Num());
            Row->SetNumberField(TEXT("capsule"),Geometry.SphylElems.Num());
            Row->SetNumberField(TEXT("unsupported"),Geometry.GetElementCount()-Supported);
            Row->SetNumberField(TEXT("collision_enabled"),static_cast<int32>(Setup->DefaultInstance.GetCollisionEnabled()));
            Result->SetObjectField(Setup->BoneName.ToString(),Row);
        }
    return JsonString(Result);
}
