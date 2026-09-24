#include "GASPEnemyFixture.h"
#include "CombatMovement.h"
#include "GASPALSRifleAnimInstance.h"
#include "EnemyCombatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "DefaultMovementSet/CharacterMoverComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "HAL/IConsoleManager.h"
#include "MovementMode.h"
#include "UObject/UnrealType.h"

void AGASPEnemyFixture::SetRifleStance(EGASPALSRifleStance NewStance) { RifleStance = NewStance; }
void AGASPEnemyFixture::SetRifleHeld(bool bHeld)
{
    bRifleHeld = bHeld;
    SetHandOccupancy(bHeld && Authority == EGASPEnemyAuthority::Locomotion, bHeld);
    if (!bHeld && Combat) Combat->SuspendForPhysics(false);
}
void AGASPEnemyFixture::SetRifleAimTarget(FVector WorldTarget)
{
    if (WorldTarget.ContainsNaN()) return;
    RifleAimTarget = WorldTarget;
    bHasRifleAimTarget = true;
    bRifleFollowPlayer = false;
}
void AGASPEnemyFixture::SetRifleFollowPlayer(bool bFollow)
{
    bRifleFollowPlayer = bFollow;
    if (!bFollow) bHasRifleAimTarget = false;
}
void AGASPEnemyFixture::SetCrouchCommand(bool bCrouch) { bCrouchCommand = bCrouch; }
bool AGASPEnemyFixture::IsMovementCrouched() const
{
    const auto* CharacterMover = Cast<UCharacterMoverComponent>(Mover);
    return CharacterMover && CharacterMover->IsCrouching();
}
float AGASPEnemyFixture::GetRifleMovementAlpha() const
{
    return Mover ? FMath::Clamp(Mover->GetVelocity().Size2D() / 100.f, 0.f, 1.f) : 0.f;
}
CombatAI::FireMotion AGASPEnemyFixture::GetFireMotion() const
{
    const auto* CharacterMover = Cast<UCharacterMoverComponent>(Mover);
    const FVector Velocity = Mover ? Mover->GetVelocity() : FVector::ZeroVector;
    return {Velocity.Size2D(), Velocity.Z,
        IsReady() && !IsDead() && Authority == EGASPEnemyAuthority::Locomotion,
        CharacterMover && CharacterMover->IsOnGround(), bWalkCommand};
}
void AGASPEnemyFixture::SetRifleLean(float Degrees, bool bImmediate)
{
    RifleLeanTarget = FMath::IsFinite(Degrees) ? FMath::Clamp(Degrees, -35.f, 35.f) : 0.f;
    if (bImmediate && Body)
        if (auto* Anim = Cast<UGASPALSRifleAnimInstance>(Body->GetAnimInstance())) Anim->RifleLeanDegrees = 0;
}
FVector AGASPEnemyFixture::GetRifleAimDirection() const
{
    const FVector Forward = Foundation ? Foundation->GetActorForwardVector() : GetActorForwardVector();
    if (!bHasRifleAimTarget || !Body) return Forward;
    const FVector Delta = RifleAimTarget - Body->GetSocketLocation(TEXT("spine_05"));
    return Delta.SizeSquared() > 1.f ? Delta.GetSafeNormal() : Forward;
}
void AGASPEnemyFixture::UpdateRifleInput()
{
    if (!Foundation) return;
    // Set the instance value consumed by GASP's gait selector before input/simulation.
    // Manual fixtures retain their authored speed when combat is disabled.
    if (auto* Walking = Mover ? Mover->FindMovementModeByName(TEXT("Walking")) : nullptr)
        if (auto* Speed = FindFProperty<FNumericProperty>(Walking->GetClass(), TEXT("WalkSpeed"));
            Speed && Speed->IsFloatingPoint())
        {
            const double Value = Combat && Combat->bEnabled ? CombatMovement::BaseSpeed :
                Speed->GetFloatingPointPropertyValue(Speed->ContainerPtrToValuePtr<void>(Walking->GetClass()->GetDefaultObject()));
            Speed->SetFloatingPointPropertyValue(Speed->ContainerPtrToValuePtr<void>(Walking), Value);
        }
    if (bRifleFollowPlayer)
        if (auto* Player = GetWorld()->GetFirstPlayerController())
        {
            FRotator Rotation;
            Player->GetPlayerViewPoint(RifleAimTarget, Rotation);
            bHasRifleAimTarget = true;
        }
    const bool bLocomotion = Authority == EGASPEnemyAuthority::Locomotion && !IsDead();
    if (!CommandController)
    {
        FActorSpawnParameters Spawn;
        Spawn.Owner = this;
        Spawn.ObjectFlags |= RF_Transient;
        CommandController = GetWorld()->SpawnActor<AGASPEnemyCommandController>(Spawn);
        if (CommandController)
        {
            CommandController->Possess(Foundation);
            // The fixture remains the combat/physics owner used by the bridge.
            Foundation->SetOwner(this);
        }
    }
    const FVector Aim = GetRifleAimDirection();
    if (CommandController)
        CommandController->SetControlRotation((bLocomotion && bHasRifleAimTarget ? Aim : Foundation->GetActorForwardVector()).Rotation());
    if (bLocomotion && bHasRifleAimTarget)
        if (auto* Cached = FindFProperty<FStructProperty>(Foundation->GetClass(), TEXT("MoverDefaultInputs_PreSim")))
            if (Cached->Struct == FCharacterDefaultInputs::StaticStruct())
            {
                auto* Inputs = Cached->ContainerPtrToValuePtr<FCharacterDefaultInputs>(Foundation);
                Inputs->ControlRotation = Aim.Rotation();
                Inputs->OrientationIntent = Aim.GetSafeNormal2D();
            }
    if (auto* State = FindFProperty<FStructProperty>(Foundation->GetClass(), TEXT("PlayerInputState")))
    {
        void* Data = State->ContainerPtrToValuePtr<void>(Foundation);
        for (TFieldIterator<FBoolProperty> It(State->Struct); It; ++It)
        {
            const FString Name = It->GetName();
            if (Name.StartsWith(TEXT("WantsToAim_"))) It->SetPropertyValue_InContainer(Data, bLocomotion && RifleStance == EGASPALSRifleStance::Aim);
            if (Name.StartsWith(TEXT("WantsToStrafe_"))) It->SetPropertyValue_InContainer(Data, bLocomotion && bHasRifleAimTarget);
            if (Name.StartsWith(TEXT("WantsToCrouch_"))) It->SetPropertyValue_InContainer(Data, bLocomotion && bCrouchCommand);
        }
    }
    if (auto* CharacterMover = Cast<UCharacterMoverComponent>(Mover))
    {
        if (bLocomotion && bCrouchCommand) CharacterMover->Crouch();
        else CharacterMover->UnCrouch();
    }
    SetHandOccupancy(bLocomotion && IsRifleHeld(), IsRifleHeld());
}
void AGASPEnemyFixture::CreateRifle()
{
    if (!Body || Rifle) return;
    auto* Mesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/GASPALSEnemy01/OverlaySystem/Props/Meshes/M4A1.M4A1"));
    if (!Mesh) return;
    Rifle = NewObject<USkeletalMeshComponent>(Foundation, TEXT("GASPALSRifle"), RF_Transient);
    Foundation->AddInstanceComponent(Rifle);
    Rifle->SetSkeletalMeshAsset(Mesh);
    Rifle->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Rifle->SetGenerateOverlapEvents(false);
    Rifle->SetCanEverAffectNavigation(false);
    Rifle->SetupAttachment(Body, TEXT("hand_r"));
    // Source overlay_rifle socket, copied as a component offset so the accepted
    // GASP skeleton remains immutable. The source prop has a static reference pose.
    Rifle->SetRelativeTransform(FTransform(FRotator(0,75,0), FVector(-7.60517584,1.43000278,-.04438320)));
    Rifle->RegisterComponent();
    Rifle->SetComponentTickEnabled(false);
    SetHandOccupancy(true, true);
}

namespace
{
void RifleCommand(const TArray<FString>& Args, UWorld* World)
{
    if (!World || !World->IsGameWorld() || Args.IsEmpty()) return;
    for (TActorIterator<AGASPEnemyFixture> It(World); It; ++It)
    {
        auto* Enemy = *It;
        // Explicit manual commands take control until resume/reset; AI cannot
        // overwrite an owner's pose or movement command on the following tick.
        if (Enemy->Combat && Enemy->Combat->bEnabled) Enemy->Combat->SetEnabled(false);
        const FString Operation = Args[0].ToLower();
        if (Operation == TEXT("relax")) Enemy->SetRifleStance(EGASPALSRifleStance::Relax);
        else if (Operation == TEXT("ready")) Enemy->SetRifleStance(EGASPALSRifleStance::Ready);
        else if (Operation == TEXT("aim")) { Enemy->SetRifleStance(EGASPALSRifleStance::Aim); Enemy->SetRifleFollowPlayer(true); }
        else if (Operation == TEXT("crouch")) Enemy->SetCrouchCommand(Args.Num() < 2 || Args[1].ToBool());
        else if (Operation == TEXT("stand")) Enemy->SetCrouchCommand(false);
        else if (Operation == TEXT("follow")) Enemy->SetRifleFollowPlayer(Args.Num() < 2 || Args[1].ToBool());
        else if (Operation == TEXT("target") && Args.Num() == 4)
            Enemy->SetRifleAimTarget(FVector(FCString::Atof(*Args[1]), FCString::Atof(*Args[2]), FCString::Atof(*Args[3])));
        else if (Operation == TEXT("move") && Args.Num() >= 3)
            Enemy->SetMovementCommand(FVector(FCString::Atof(*Args[1]), FCString::Atof(*Args[2]), 0), Args.Num() < 4 || Args[3] != TEXT("run"));
        else if (Operation == TEXT("stop")) Enemy->StopMovementCommand();
    }
}
FAutoConsoleCommandWithWorldAndArgs RifleConsole(
    TEXT("msq.EnemyRifle"),
    TEXT("Enemy test: relax | ready | aim (tracks player) | crouch [0/1] | stand | follow [0/1] | target X Y Z | move X Y [walk/run] | stop. Applies to all fixtures; F6 resets."),
    FConsoleCommandWithWorldAndArgsDelegate::CreateStatic(&RifleCommand));
}
