#include "DestructibleCladding.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/DamageEvents.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Serialization/JsonSerializer.h"

ADestructibleCladding::ADestructibleCladding()
{
    PrimaryActorTick.bCanEverTick = false;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("CladdingRoot")));
}

bool ADestructibleCladding::BuildSpecimen()
{
    // Runtime rebuilding would invalidate projectile component identities and is not permitted.
    if (!GetWorld() || GetWorld()->IsGameWorld() || PieceMeshes.IsEmpty() || PieceMeshes.Num() > 64 ||
        PieceTransforms.Num() != PieceMeshes.Num() || PieceMassKg.Num() != PieceMeshes.Num()) return false;
    for (int32 I = 0; I < PieceMeshes.Num(); ++I)
        if (!PieceMeshes[I] || !FMath::IsFinite(PieceMassKg[I]) || PieceMassKg[I] <= 0 ||
            PieceTransforms[I].ContainsNaN()) return false;
    for (UStaticMeshComponent* Piece : Pieces)
        if (Piece) { RemoveInstanceComponent(Piece); Piece->DestroyComponent(); }
    Pieces.Empty();
    Broken.Init(false, PieceMeshes.Num());
    for (int32 I = 0; I < PieceMeshes.Num(); ++I)
    {
        auto* Piece = NewObject<UStaticMeshComponent>(this);
        Piece->SetMobility(EComponentMobility::Movable);
        Piece->SetStaticMesh(PieceMeshes[I]);
        Piece->SetupAttachment(GetRootComponent());
        Piece->SetRelativeTransform(PieceTransforms[I]);
        Piece->SetCollisionProfileName(TEXT("BlockAll"));
        Piece->SetGenerateOverlapEvents(false);
        Piece->SetCanEverAffectNavigation(false);
        Piece->SetLinearDamping(0.5f);
        Piece->SetAngularDamping(1.5f);
        Piece->BodyInstance.bUseCCD = true;
        AddInstanceComponent(Piece);
        Piece->RegisterComponent();
        Piece->SetMassOverrideInKg(NAME_None, PieceMassKg[I]);
        Pieces.Add(Piece);
    }
    return true;
}

void ADestructibleCladding::BeginPlay()
{
    Super::BeginPlay();
    Broken.Init(false, Pieces.Num());
    for (int32 I = 0; I < Pieces.Num(); ++I) RestorePiece(I);
    if (auto* PC = UGameplayStatics::GetPlayerController(this, 0))
    {
        EnableInput(PC);
        InputComponent->BindKey(EKeys::F7, IE_Pressed, this, &ADestructibleCladding::ResetSpecimen);
    }
}

void ADestructibleCladding::RestorePiece(int32 Index)
{
    auto* Piece = Pieces[Index].Get();
    if (!Piece || !PieceTransforms.IsValidIndex(Index)) return;
    if (Piece->IsSimulatingPhysics())
    {
        Piece->SetPhysicsLinearVelocity(FVector::ZeroVector);
        Piece->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
    }
    Piece->SetSimulatePhysics(false);
    Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Piece->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepWorldTransform);
    Piece->SetRelativeTransform(PieceTransforms[Index], false, nullptr, ETeleportType::TeleportPhysics);
    Piece->SetCollisionProfileName(TEXT("BlockAll"));
    Piece->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Piece->SetMassOverrideInKg(NAME_None, PieceMassKg.IsValidIndex(Index) ? PieceMassKg[Index] : 1.f);
    Piece->SetVisibility(true);
    Broken[Index] = false;
}

void ADestructibleCladding::ResetSpecimen()
{
    if (bChanging || !GetWorld() || !GetWorld()->IsGameWorld()) return;
    TGuardValue<bool> Guard(bChanging, true);
    ++ResetGeneration;
    ++CollisionRevision;
    OnCladdingChanged.Broadcast(INDEX_NONE, GetComponentsBoundingBox(), CollisionRevision, ResetGeneration, true);
    for (int32 I = 0; I < Pieces.Num(); ++I) RestorePiece(I);
    LastPiece = INDEX_NONE;
    LastDamage = 0;
    UE_LOG(LogTemp, Display, TEXT("ED01 reset generation=%d components=%d revision=%d"), ResetGeneration, Pieces.Num(), CollisionRevision);
}

float ADestructibleCladding::TakeDamage(float Damage, const FDamageEvent& Event,
    AController* EventInstigator, AActor* Causer)
{
    if (bChanging || !FMath::IsFinite(Damage) || Damage <= 0 || !Event.IsOfType(FPointDamageEvent::ClassID)) return 0;
    const auto& Point = static_cast<const FPointDamageEvent&>(Event);
    const int32 Index = Pieces.IndexOfByPredicate([&Point](const auto& Piece) { return Piece.Get() == Point.HitInfo.GetComponent(); });
    if (!Broken.IsValidIndex(Index) || Broken[Index]) return 0;
    LastHit = Point.HitInfo.ImpactPoint;
    LastDamage = Damage;
    LastPiece = Index;
    if (!FMath::IsFinite(BreakThreshold) || Damage < FMath::Max(1.f, BreakThreshold)) return 0;
    const double Start = FPlatformTime::Seconds();
    TGuardValue<bool> Guard(bChanging, true);
    auto* Piece = Pieces[Index].Get();
    ++CollisionRevision;
    OnCladdingChanged.Broadcast(Index, Piece->Bounds.GetBox(), CollisionRevision, ResetGeneration, false);
    Broken[Index] = true;
    // The same visible convex body is released. No hidden surface proxy or replacement is left behind.
    // Bonded-to-core support is local: one projectile releases exactly its contacted piece.
    const FVector Normal = GetActorTransform().TransformVectorNoScale(LocalOutwardNormal).GetSafeNormal(UE_SMALL_NUMBER, FVector::YAxisVector);
    // A 4 cm panel needs to clear its bonded neighbours before rigid simulation.
    // The bounded outward release avoids friction-locking flush convex seams;
    // the visible body and its collider move together, without an invisible proxy.
    const float Clearance = FMath::IsFinite(ReleaseClearanceCm) ? FMath::Clamp(ReleaseClearanceCm, 0.f, 8.f) : 4.5f;
    Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Piece->AddWorldOffset(Normal * Clearance, false, nullptr, ETeleportType::TeleportPhysics);
    Piece->SetCollisionObjectType(ECC_PhysicsBody);
    Piece->SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore); // Rubble traversal is later scope.
    Piece->SetCollisionResponseToChannel(ECC_PhysicsBody, ECR_Ignore);
    // ED-01 debris is not cover. Moving generic Visibility blockers invalidate the
    // finite-projectile coordinator's history and cancel firing globally. Match
    // existing physical weapon props instead of weakening that launch/history guard.
    // Bonded panels and the solid backing remain Visibility blockers; reset restores it.
    Piece->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
    Piece->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Piece->SetSimulatePhysics(true);
    const float Speed = FMath::IsFinite(ReleaseSpeedCmS) ? FMath::Clamp(ReleaseSpeedCmS, 0.f, 150.f) : 80.f;
    Piece->AddImpulse(Normal * Speed * Piece->GetMass());
    Piece->SetPhysicsAngularVelocityInDegrees(FVector(25, 0, Index % 2 ? 15 : -15));
    LastBreakMs = (FPlatformTime::Seconds() - Start) * 1000.;
    UE_LOG(LogTemp, Display, TEXT("ED01 point break piece=%d hit=%s damage=%.1f mass=%.2f revision=%d generation=%d ms=%.3f causer=%s"),
        Index, *LastHit.ToString(), Damage, Piece->GetMass(), CollisionRevision, ResetGeneration, LastBreakMs, *GetNameSafe(Causer));
    return Damage;
}

FString ADestructibleCladding::GetCladdingState() const
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("actor"), GetPathName());
    Root->SetNumberField(TEXT("revision"), CollisionRevision);
    Root->SetNumberField(TEXT("generation"), ResetGeneration);
    Root->SetNumberField(TEXT("last_piece"), LastPiece);
    Root->SetNumberField(TEXT("last_damage"), LastDamage);
    Root->SetStringField(TEXT("last_hit"), LastHit.ToString());
    Root->SetNumberField(TEXT("last_break_ms"), LastBreakMs);
    TArray<TSharedPtr<FJsonValue>> Rows;
    int32 Detached = 0, Simulating = 0, Awake = 0;
    for (int32 I = 0; I < Pieces.Num(); ++I)
    {
        auto* Piece = Pieces[I].Get();
        if (!Piece) continue;
        const bool bBroken = Broken.IsValidIndex(I) && Broken[I];
        Detached += bBroken;
        Simulating += Piece->IsSimulatingPhysics();
        Awake += Piece->IsAnyRigidBodyAwake();
        auto Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("id"), I);
        Row->SetStringField(TEXT("component"), Piece->GetName());
        Row->SetBoolField(TEXT("broken"), bBroken);
        Row->SetBoolField(TEXT("simulating"), Piece->IsSimulatingPhysics());
        Row->SetBoolField(TEXT("awake"), Piece->IsAnyRigidBodyAwake());
        Row->SetNumberField(TEXT("mass_kg"), Piece->IsSimulatingPhysics() ? Piece->GetMass() : PieceMassKg[I]);
        Row->SetStringField(TEXT("position"), Piece->GetComponentLocation().ToString());
        Row->SetStringField(TEXT("velocity"), Piece->GetPhysicsLinearVelocity().ToString());
        Row->SetNumberField(TEXT("collision"), static_cast<int32>(Piece->GetCollisionEnabled()));
        if (PieceTransforms.IsValidIndex(I))
            Row->SetNumberField(TEXT("rest_position_error_cm"), FVector::Distance(Piece->GetComponentLocation(), (PieceTransforms[I] * GetActorTransform()).GetLocation()));
        Rows.Add(MakeShared<FJsonValueObject>(Row));
    }
    Root->SetNumberField(TEXT("components"), Pieces.Num());
    Root->SetNumberField(TEXT("broken"), Detached);
    Root->SetNumberField(TEXT("simulating"), Simulating);
    Root->SetNumberField(TEXT("awake"), Awake);
    Root->SetArrayField(TEXT("pieces"), Rows);
    FString Result;
    FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result));
    return Result;
}
