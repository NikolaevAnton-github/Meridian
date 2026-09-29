#include "DestructionCollisionPolicy.h"

#include "Dom/JsonObject.h"
#include "Engine/Blueprint.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "HAL/FileManager.h"
#include "GeometryCollection/GeometryCollectionComponent.h"
#include "GeometryCollection/GeometryCollectionObject.h"
#include "GeometryCollection/GeometryCollection.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Parse.h"
#include "Misc/SecureHash.h"
#include "ProfilingDebugging/CpuProfilerTrace.h"
#include "UObject/Package.h"
#include "UObject/UnrealType.h"

namespace
{
constexpr TCHAR VendorClassPath[] = TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_BreakableObject.BP_BreakableObject_C");
constexpr TCHAR VendorPackage[] = TEXT("/Game/NextGenDestruction/Blueprints/Actors/BP_BreakableObject");
// DP-02's immutable graph export SHA256 is 9854e465...43da. This SHA1 identifies
// the same on-disk asset; it is a compatibility gate, not a security boundary.
constexpr TCHAR VerifiedAssetSHA1[] = TEXT("EA97E1F45BDC1803A049AA38C5EA4EB3E8E6E4E8");
const FName DesiredProfile(TEXT("IgnoreCharChaos"));

// Form a pointer to the actual base member from its legal protected-access
// context. Applying that base-member pointer to a base object needs no downcast,
// layout offset, aliasing trick or replacement component. Read only: every
// mutation still uses the supported engine setter and its GT/PT filter updates.
class FCollisionProfileReadAccess : public UGeometryCollectionComponent
{
public:
    static const TArray<FName>& Read(const UGeometryCollectionComponent& Component)
    {
        return Component.*(&FCollisionProfileReadAccess::CollisionProfilePerParticle);
    }
};

int32 TransformCount(const UGeometryCollectionComponent* Component)
{
    const UGeometryCollection* Rest = Component ? Component->GetRestCollection() : nullptr;
    return Rest && Rest->GetGeometryCollection() ? Rest->GetGeometryCollection()->Transform.Num() : INDEX_NONE;
}

bool IdenticalProfile(const UGeometryCollectionComponent& Component)
{
    const TArray<FName>& Profiles = FCollisionProfileReadAccess::Read(Component);
    const int32 Num = TransformCount(&Component);
    return Num > 0 && Profiles.Num() == Num && Profiles[0] == DesiredProfile;
}

FProperty* FindNormalizedProperty(UClass* Class, const TCHAR* Name)
{
    for (TFieldIterator<FProperty> It(Class); It; ++It)
        if (It->GetName().Replace(TEXT(" "), TEXT("")) == Name) return *It;
    return nullptr;
}

bool CollisionSignature(UFunction* Function)
{
    if (!Function || Function->Script.IsEmpty()) return false;
    TArray<FProperty*> Parameters;
    for (TFieldIterator<FProperty> It(Function); It; ++It)
        if (It->HasAnyPropertyFlags(CPF_Parm)) Parameters.Add(*It);
    const FStructProperty* Info = Parameters.Num() == 1 ? CastField<FStructProperty>(Parameters[0]) : nullptr;
    return Info && Info->Struct == FChaosPhysicsCollisionInfo::StaticStruct()
        && !Info->HasAnyPropertyFlags(CPF_ReturnParm);
}

bool VerifyAsset(UClass* Class, FString& Reason)
{
#if WITH_EDITOR
    const UBlueprint* Blueprint = Cast<UBlueprint>(Class->ClassGeneratedBy);
    if (!Blueprint || Blueprint->GetOutermost()->IsDirty()
        || (Blueprint->Status != BS_UpToDate && Blueprint->Status != BS_UpToDateWithWarnings))
    {
        Reason = TEXT("loaded vendor Blueprint is dirty or not compiled successfully");
        return false;
    }
    const FString Filename = FPackageName::LongPackageNameToFilename(VendorPackage, FPackageName::GetAssetPackageExtension());
    const FDateTime Timestamp = IFileManager::Get().GetTimeStamp(*Filename);
    const int64 FileSize = IFileManager::Get().FileSize(*Filename);
    static FDateTime CheckedTimestamp;
    static int64 CheckedSize = -2;
    static bool bHashMatches = false;
    // Hash once per process while the source file is unchanged. Each install
    // still checks its loaded Blueprint and file stamp. No I/O in callbacks.
    if (CheckedTimestamp != Timestamp || CheckedSize != FileSize)
    {
        TArray<uint8> Bytes;
        bHashMatches = FFileHelper::LoadFileToArray(Bytes, *Filename)
            && FSHA1::HashBuffer(Bytes.GetData(), Bytes.Num()).ToString().Equals(VerifiedAssetSHA1, ESearchCase::IgnoreCase);
        CheckedTimestamp = Timestamp;
        CheckedSize = FileSize;
    }
    if (!bHashMatches)
    {
        Reason = TEXT("vendor source asset differs from verified DP-02 graph");
        return false;
    }
    return true;
#else
    Reason = TEXT("cooked vendor graph has no validated artifact fingerprint");
    return false;
#endif
}

}

UDestructionCollisionPolicy::UDestructionCollisionPolicy()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UDestructionCollisionPolicy::Initialize(UGeometryCollectionComponent* InCollection)
{
    check(IsInGameThread());
    if (bInitialized) return bInstalled || Mode == TEXT("vendor");
    bInitialized = true;
    Collection = InCollection;
    FParse::Value(FCommandLine::Get(), TEXT("DestructionCollisionMode="), Mode);
    Mode.ToLowerInline();
    if (Mode == TEXT("vendor"))
    {
        ValidationReason = TEXT("unmodified vendor control; no policy instrumentation");
        return true;
    }
    auto Fail = [this](const FString& Reason)
    {
        ValidationReason = Reason;
        UE_LOG(LogTemp, Warning, TEXT("DP03 collision policy keeps vendor callback: %s (%s)"),
            *Reason, *GetPathNameSafe(Collection));
        return false;
    };
    if (Mode != TEXT("observe") && Mode != TEXT("native")) return Fail(TEXT("unknown collision mode"));
    if (!IsValid(Collection) || !IsValid(Collection->GetOwner()) || GetOwner() != Collection->GetOwner()
        || !GetWorld() || !GetWorld()->IsGameWorld()) return Fail(TEXT("invalid game-world owner/component"));
    AActor* Owner = GetOwner();
    BoundClass = Owner->GetClass();
    if (BoundClass->GetPathName() != VendorClassPath) return Fail(TEXT("unsupported owner class"));
    FString AssetReason;
    if (!VerifyAsset(BoundClass, AssetReason)) return Fail(AssetReason);
    TArray<FName> Bindings;
    for (TFieldIterator<UFunction> It(BoundClass); It; ++It)
        if (Collection->OnChaosPhysicsCollision.Contains(Owner, It->GetFName())) Bindings.Add(It->GetFName());
    const TArray<UObject*> Targets = Collection->OnChaosPhysicsCollision.GetAllObjects();
    if (Bindings.Num() != 1 || Targets.Num() != 1 || Targets[0] != Owner
        || !CollisionSignature(Owner->FindFunction(Bindings[0])))
        return Fail(TEXT("unsupported collision binding topology or signature"));

    CollisionInfoProperty = CastField<FStructProperty>(FindNormalizedProperty(BoundClass, TEXT("CollisionInfo")));
    if (!CollisionInfoProperty || CollisionInfoProperty->Struct != FChaosPhysicsCollisionInfo::StaticStruct()
        || CollisionInfoProperty->HasAnyPropertyFlags(CPF_RepNotify))
        return Fail(TEXT("unsupported collision property schema"));

    OriginalBinding.BindUFunction(Owner, Bindings[0]);
    OriginalDelegates = Collection->OnChaosPhysicsCollision;
    Collection->OnChaosPhysicsCollision.Remove(OriginalBinding);
    Collection->OnChaosPhysicsCollision.AddUniqueDynamic(this, &UDestructionCollisionPolicy::ReceiveCollision);
    bInstalled = bValidated = true;
    ValidationReason = TEXT("verified source graph, single binding and native property schema");
    return true;
}

void UDestructionCollisionPolicy::ReceiveCollision(const FChaosPhysicsCollisionInfo& CollisionInfo)
{
    check(IsInGameThread());
    if (!bInstalled) return;
    TRACE_CPUPROFILER_EVENT_SCOPE(DP03_CollisionPolicy);
    ++RawCallbacks;
    AActor* Owner = GetOwner();
    if (!IsValid(Collection) || !IsValid(Owner) || Owner->GetClass() != BoundClass
        || CollisionInfo.Component != Collection)
    {
        ++FallbackCallbacks;
        bValidated = false;
        ValidationReason = TEXT("runtime owner/component identity changed");
        OriginalDelegates.Broadcast(CollisionInfo);
        ++ForwardedCallbacks;
        return;
    }

    const double Speed = CollisionInfo.Velocity.Size();
    const bool bProfileRequest = Speed > .5;
    const bool bIdentical = bProfileRequest && IdenticalProfile(*Collection);
    if (bProfileRequest) ++ProfileRequested;
    // Every event that can touch the vendor's sleep or sound branches keeps the
    // exact original synchronous callback, latent owner, random calls and gate.
    // Only its straight-line, low-speed profile branch has a native equivalent.
    if (Mode == TEXT("observe") || Speed > 200.)
    {
        if (Speed > 200.) ++SleepRetriggers;
        OriginalDelegates.Broadcast(CollisionInfo);
        ++ForwardedCallbacks;
        if (bProfileRequest)
        {
            ++ProfileNativeCalls;
            if (bIdentical) ++ProfileSkippedIdentical;
            else if (IdenticalProfile(*Collection)) ++ProfileApplied;
            else ++ProfileUnapplied;
        }
        return;
    }

    ++NativeCallbacks;
    // At this speed both vendor sleep and sound branches are false. The graph's
    // other observable state is its persistent Collision Info value and the
    // profile request, which still takes effect before this callback returns.
    CollisionInfoProperty->CopyCompleteValue(CollisionInfoProperty->ContainerPtrToValuePtr<void>(Owner), &CollisionInfo);

    if (bProfileRequest)
    {
        // This exactly matches the engine's authoritative array-size/FName
        // early-out. It never uses the previous event, actor ObjectId, or a cache
        // of desired requests. Changed values still reach the engine immediately.
        if (bIdentical)
        {
            ++ProfileSkippedIdentical;
            ++ProfileSkippedSetter;
        }
        else
        {
            ++ProfileNativeCalls;
            Collection->SetPerParticleCollisionProfileName(TArray<int32>{0}, DesiredProfile);
            if (IdenticalProfile(*Collection)) ++ProfileApplied;
            else ++ProfileUnapplied;
        }
    }
}

void UDestructionCollisionPolicy::Restore()
{
    check(IsInGameThread());
    if (!bInstalled) return;
    bInstalled = false;
    ++ResetInvalidations;
    if (IsValid(Collection))
    {
        Collection->OnChaosPhysicsCollision.RemoveDynamic(this, &UDestructionCollisionPolicy::ReceiveCollision);
        Collection->OnChaosPhysicsCollision.AddUnique(OriginalBinding);
    }
    OriginalDelegates.Clear();
    OriginalBinding.Unbind();
}

void UDestructionCollisionPolicy::EndPlay(const EEndPlayReason::Type Reason)
{
    Restore();
    Super::EndPlay(Reason);
}

TSharedRef<FJsonObject> UDestructionCollisionPolicy::Snapshot() const
{
    auto Result = MakeShared<FJsonObject>();
    Result->SetStringField(TEXT("mode"), Mode);
    Result->SetBoolField(TEXT("installed"), bInstalled);
    Result->SetBoolField(TEXT("validated"), bValidated);
    Result->SetBoolField(TEXT("counters_available"), bValidated);
    Result->SetStringField(TEXT("validation_reason"), ValidationReason);
    Result->SetStringField(TEXT("actor"), GetPathNameSafe(GetOwner()));
    Result->SetStringField(TEXT("component"), GetPathNameSafe(Collection));
    Result->SetNumberField(TEXT("actor_unique_id"), GetOwner() ? GetOwner()->GetUniqueID() : 0);
    Result->SetNumberField(TEXT("component_unique_id"), Collection ? Collection->GetUniqueID() : 0);
    Result->SetNumberField(TEXT("policy_unique_id"), GetUniqueID());
    Result->SetStringField(TEXT("asset_sha1"), VerifiedAssetSHA1);
    Result->SetStringField(TEXT("profile_counter_scope"), TEXT("collision bone 0 override names; not filter submissions or break writes"));
    Result->SetNumberField(TEXT("raw_callbacks"), double(RawCallbacks));
    Result->SetNumberField(TEXT("forwarded_callbacks"), double(ForwardedCallbacks));
    Result->SetNumberField(TEXT("native_callbacks"), double(NativeCallbacks));
    Result->SetNumberField(TEXT("fast_handled_callbacks"), double(NativeCallbacks));
    Result->SetNumberField(TEXT("fallback_callbacks"), double(FallbackCallbacks));
    Result->SetNumberField(TEXT("profile_requested"), double(ProfileRequested));
    Result->SetNumberField(TEXT("profile_applied"), double(ProfileApplied));
    Result->SetNumberField(TEXT("profile_skipped_identical"), double(ProfileSkippedIdentical));
    Result->SetNumberField(TEXT("profile_skipped_setter"), double(ProfileSkippedSetter));
    Result->SetNumberField(TEXT("profile_unapplied"), double(ProfileUnapplied));
    Result->SetNumberField(TEXT("profile_native_calls"), double(ProfileNativeCalls));
    Result->SetNumberField(TEXT("sleep_retriggers"), double(SleepRetriggers));
    Result->SetNumberField(TEXT("reset_invalidations"), double(ResetInvalidations));
    Result->SetBoolField(TEXT("presentation_completion_counters_available"), false);
    Result->SetStringField(TEXT("latent_policy"), TEXT("all speed>200 events synchronously execute original vendor callback and original actor-owned latent actions"));
    if (IsValid(Collection))
    {
        const TArray<FName>& Profiles = FCollisionProfileReadAccess::Read(*Collection);
        Result->SetNumberField(TEXT("profile_array_size"), Profiles.Num());
        Result->SetNumberField(TEXT("rest_transform_count"), TransformCount(Collection));
        Result->SetStringField(TEXT("authoritative_profile0"), Profiles.IsEmpty() ? TEXT("") : Profiles[0].ToString());
    }
    return Result;
}
