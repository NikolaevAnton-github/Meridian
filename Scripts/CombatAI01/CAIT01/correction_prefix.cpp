// Deterministic unit adapters adapted from the preserved primary-review gap probe.
// The runner appends unchanged production methods and the installed UE channel filter.
#include "CombatAIObservation.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <string>
#include <vector>

using int32 = int;
using uint64 = std::uint64_t;
using TCHAR = char;
constexpr int INDEX_NONE = -1;
constexpr float TacticalAcceptance = 45.f;
#define TEXT(Value) Value
#define SCENE_QUERY_STAT(Value) 0
template<class T> struct TNumericLimits { static constexpr T Max() { return std::numeric_limits<T>::max(); } };
struct FVector {
    float X=0, Y=0, Z=0;
    FVector() = default;
    FVector(float A, float B, float C) : X(A), Y(B), Z(C) {}
    static float Dist2D(FVector A, FVector B) { return std::hypot(A.X-B.X, A.Y-B.Y); }
    FVector operator+(FVector B) const { return {X+B.X,Y+B.Y,Z+B.Z}; }
    FVector operator*(double Scale) const { return {float(X*Scale),float(Y*Scale),float(Z*Scale)}; }
    bool operator==(const FVector&) const = default;
};
struct FIntPoint {
    int X, Y;
    bool operator<(const FIntPoint& B) const { return X==B.X ? Y<B.Y : X<B.X; }
    FIntPoint operator+(FIntPoint B) const { return {X+B.X,Y+B.Y}; }
};
struct FMath {
    template<class T> static T Clamp(T V, T L, T H) { return std::clamp(V,L,H); }
    template<class T> static T Max(T A, T B) { return std::max(A,B); }
    template<class T> static T Min(T A, T B) { return std::min(A,B); }
    static float Abs(float V) { return std::abs(V); }
    static int RoundToInt(float V) { return static_cast<int>(std::round(V)); }
};
template<class T> struct TArray : std::vector<T> {
    int Num() const { return static_cast<int>(this->size()); }
    bool IsEmpty() const { return this->empty(); }
    void Reset() { this->clear(); }
    int Add(const T& V) { this->push_back(V); return Num()-1; }
    void AddUnique(const T& V) { if (std::find(this->begin(),this->end(),V)==this->end()) Add(V); }
    void RemoveAtSwap(int I) { (*this)[I]=this->back(); this->pop_back(); }
};
template<class K,class V> struct TMap : std::map<K,V> {
    void Reset() { this->clear(); }
    void Add(K Key,V Value) { (*this)[Key]=Value; }
    const V* Find(K Key) const { auto I=this->find(Key); return I==this->end()?nullptr:&I->second; }
};
namespace Algo { template<class T> void Reverse(T& V) { std::reverse(V.begin(),V.end()); } }
struct FPlatformTime { static double Seconds() { return 0; } };
struct FString : std::string {
    using std::string::operator=;
    const char* operator*() const { return c_str(); }
};
enum ECollisionChannel { ECC_WorldStatic, ECC_WorldDynamic, ECC_Visibility, ECC_Pawn, ChannelCount };
enum ECollisionResponse { ECR_Ignore, ECR_Overlap, ECR_Block };
struct FCollisionQueryParams { FCollisionQueryParams(int,bool) {} };
struct FCollisionResponseContainer {
    std::array<ECollisionResponse,ChannelCount> Channels{};
    void SetResponse(ECollisionChannel C,ECollisionResponse R) { Channels[C]=R; }
};
struct FCollisionResponseParams {
    FCollisionResponseContainer CollisionResponse;
    explicit FCollisionResponseParams(ECollisionResponse R) { CollisionResponse.Channels.fill(R); }
};
enum class ENarrowFilterResult { None, Overlap, Block };
struct FShapeFilterData {
    uint64 Channel, Blocks, Overlaps;
    uint64 GetCollisionChannelMask() const { return Channel; }
    uint64 GetBlockChannels() const { return Blocks; }
    uint64 GetOverlapChannels() const { return Overlaps; }
};
struct FQueryFilterData : FShapeFilterData {
    ENarrowFilterResult ChannelTypeNarrowFilter(const FShapeFilterData&) const;
};
struct Primitive {
    ECollisionChannel ObjectType=ECC_WorldStatic;
    std::array<ECollisionResponse,ChannelCount> Responses{};
    Primitive(ECollisionChannel Object,ECollisionResponse Visibility,ECollisionResponse Pawn)
        : ObjectType(Object) { Responses[ECC_Visibility]=Visibility; Responses[ECC_Pawn]=Pawn; }
    FShapeFilterData Filter() const {
        FShapeFilterData F{uint64(1)<<ObjectType,0,0};
        for (int I=0; I<ChannelCount; ++I) {
            if (Responses[I]==ECR_Block) F.Blocks |= uint64(1)<<I;
            if (Responses[I]==ECR_Overlap) F.Overlaps |= uint64(1)<<I;
        }
        return F;
    }
};
struct FHitResult {
    Primitive* Component=nullptr;
    float Distance=0;
    Primitive* GetComponent() const { return Component; }
};
struct WorldAdapter {
    std::vector<FHitResult> Hits;
    int RayCalls=0;
    double Now=0;
    double GetTimeSeconds() const { return Now; }
    // The actual installed ChannelTypeNarrowFilter body below decides eligibility.
    // The adapter models a single ray returning its nearest eligible blocking hit.
    bool LineTraceSingleByChannel(FHitResult& Hit,FVector From,FVector To,ECollisionChannel Channel,
        const FCollisionQueryParams&,const FCollisionResponseParams& Response) {
        ++RayCalls;
        FQueryFilterData Filter{{uint64(1)<<Channel,0,0}};
        for (int I=0; I<ChannelCount; ++I) {
            if (Response.CollisionResponse.Channels[I]==ECR_Block) Filter.Blocks |= uint64(1)<<I;
            if (Response.CollisionResponse.Channels[I]==ECR_Overlap) Filter.Overlaps |= uint64(1)<<I;
        }
        Hit={};
        const float Length=std::sqrt(std::pow(To.X-From.X,2.f)+std::pow(To.Y-From.Y,2.f)+std::pow(To.Z-From.Z,2.f));
        for (const auto& Candidate:Hits) {
            if (!Candidate.Component || Candidate.Distance>Length ||
                Filter.ChannelTypeNarrowFilter(Candidate.Component->Filter())!=ENarrowFilterResult::Block) continue;
            if (!Hit.Component || Candidate.Distance<Hit.Distance) Hit=Candidate;
        }
        return Hit.Component!=nullptr;
    }
};
enum class EGASPALSRifleStance { Ready, Aim };
struct EnemyAdapter {
    bool Stopped=false, FollowPlayer=false, Crouching=false;
    FVector Aim;
    EGASPALSRifleStance Stance=EGASPALSRifleStance::Ready;
    void StopMovementCommand() { Stopped=true; }
    void SetCrouchCommand(bool V) { Crouching=V; }
    void SetRifleStance(EGASPALSRifleStance V) { Stance=V; }
    void SetRifleFollowPlayer(bool V) { FollowPlayer=V; }
    void SetRifleAimTarget(FVector V) { Aim=V; }
};
class UEnemyCombatComponent {
public:
    struct TuningValues {
        float NavigationCell=80,NavigationRadius=2800,SearchSeconds=2,TacticalReassessSeconds=2.5;
        int MaxPathExpansions=1200;
    } Tuning;
    struct FPathNode {
        FIntPoint Cell{0,0}; FVector Ground;
        float Cost=std::numeric_limits<float>::max();
        int Parent=INDEX_NONE; bool bClosed=false,bWalkable=false;
    };
    struct FTacticalPosition {
        FVector Ground;
        CombatAI::PositionFeatures Features;
        CombatAI::PositionRating Rating;
    };
    WorldAdapter World;
    EnemyAdapter Pawn;
    FVector Home,FixtureFeet,PathGoal,ProgressPosition,SearchGoal,SearchLook,AssessedReference,AssessedFrom;
    TArray<FVector> Path;
    TArray<FPathNode> Nodes;
    TArray<int> OpenNodes;
    TMap<FIntPoint,int> CellNodes;
    CombatAI::ActionRuntime Action;
    CombatAI::ActionToken PathRequest;
    CombatAI::EncounterMemory Memory;
    CombatAI::MovePurpose MovementPurpose=CombatAI::MovePurpose::Search;
    CombatAI::TacticalAssignment Assignment;
    CombatAI::TacticalPhase TacticalPhase=CombatAI::TacticalPhase::None;
    CombatAI::PositionHistory RejectedPositions,VisitedPositions;
    CombatAI::TransferBudget Transfers;
    FTacticalPosition SelectedPosition,HeldPosition;
    CombatAI::PositionFeatures FixtureFeatures;
    std::uint64_t EncounterGeneration=1;
    int PathIndex=0,LastPathExpanded=0,PathPlans=0,TacticalQueryCount=0,TacticalPeakQueries=0,TacticalRejected=0;
    int LookSector=-1,CandidateIndex=0,ConnectorChecks=0,ConnectorRejected=0,FollowCalls=0;
    unsigned ViewedSectors=0;
    std::array<int,static_cast<size_t>(CombatAI::PositionRejection::Count)> RejectionCounts{};
    float PathAcceptance=80,PathCell=80,MaxConnectorLength=0,LastFollowAcceptance=0;
    bool bPlanning=false,bPlanFailed=false,bHeldPosition=false,bSelectedPosition=false,bTacticalScan=false;
    bool BlockFirstConnector=false,BlockAllConnectors=false,UnsupportedGoal=false,FollowResult=true,TraceFacing=false;
    bool AssessedRoute=false;
    double PlanStarted=0,LastProgress=0,NextHoldValidation=0,NextTacticalScan=0,NextLookAt=0;
    double HoldStartedAt=0,TacticalMoveStartedAt=0;
    FString TacticalReason;
    FVector Feet() const { return FixtureFeet; }
    WorldAdapter* GetWorld() { return &World; }
    EnemyAdapter* Enemy() { return &Pawn; }
    void NavigationQuery(FCollisionQueryParams&) const {}
    bool GroundPoint(FVector Reference,FVector& Ground,const FCollisionQueryParams&) const {
        Ground=Reference; return !(UnsupportedGoal && Reference==PathGoal);
    }
    bool WalkSegment(FVector From,FVector To,const FCollisionQueryParams&) {
        if (To==PathGoal) {
            ++ConnectorChecks; MaxConnectorLength=std::max(MaxConnectorLength,FVector::Dist2D(From,To));
            if (BlockAllConnectors || (BlockFirstConnector && From==FixtureFeet)) { ++ConnectorRejected; return false; }
        }
        return true;
    }
    bool FinishAction(CombatAI::ActionToken Request,CombatAI::ActionStatus Status,CombatAI::ActionFailure Failure)
        { return Action.Finish(Request,Status,Failure,World.Now); }
    CombatAI::ActionToken EnsureAction(CombatAI::ActionKind Kind,double Now) {
        return Action.Kind==Kind && Action.Status==CombatAI::ActionStatus::Running ? Action.Token : Action.Start(EncounterGeneration,Kind,Now);
    }
    void RecordPath(CombatAI::PathOutcome,const TCHAR*) {}
    void RecordTrace(CombatAI::Event,const TCHAR*) {}
    void ClearIntent(CombatAI::ActionFailure Why=CombatAI::ActionFailure::Replaced) {
        FinishAction(Action.Token,CombatAI::ActionStatus::Canceled,Why); Path.Reset(); bPlanning=bPlanFailed=false;
    }
    FTacticalPosition AssessTacticalPosition(FVector Reference,FVector From,bool Route) {
        AssessedReference=Reference; AssessedFrom=From; AssessedRoute=Route;
        FTacticalPosition P; P.Ground=Reference; P.Features=FixtureFeatures;
        if (TraceFacing) {
            FHitResult Hit;
            P.Features.OpenDistance[0]=TacticalTrace(Reference,Reference+FVector(600,0,0),Hit) ? Hit.Distance : 600;
        }
        P.Rating=CombatAI::RatePosition(P.Features); return P;
    }
    FVector TacticalDirection(int Sector) const {
        const double Angle=Sector*3.141592653589793/4;
        return {float(std::cos(Angle)),float(std::sin(Angle)),0};
    }
    bool FollowPath(FVector,float Acceptance,double,CombatAI::MovePurpose) {
        ++FollowCalls; LastFollowAcceptance=Acceptance; return FollowResult;
    }
    void BeginTacticalScan(double) { bTacticalScan=true; }
    void AdvanceTacticalScan(double) {}
    bool PlanPath(FVector Goal,float Acceptance);
    void ContinuePath();
    bool TacticalTrace(FVector From,FVector To,FHitResult& Hit,ECollisionChannel Response=ECC_Visibility);
    void RejectTacticalPosition(const FVector&,CombatAI::PositionRejection,double);
    void SetObservationFacing(double);
    void HoldTacticalPosition(double);
    void AdvanceSearch(double);
};
