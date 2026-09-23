// Extends the primary review's deterministic adapters; previous files stay frozen.
// No gameplay is simulated: geometry, clock, movement and weapon boundaries are fakes.
#include "CombatAIObservation.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using int32=int; using uint64=std::uint64_t; using TCHAR=char;
constexpr int INDEX_NONE=-1, ForceInit=0;
constexpr float TacticalAcceptance=25.f;
#define TEXT(X) X
#define SCENE_QUERY_STAT(X) 0
template<class T> struct TNumericLimits { static T Max(){return std::numeric_limits<T>::max();} };
template<class F> struct ScopeExit {F Function; ~ScopeExit(){Function();}};
struct ScopeExitFactory {template<class F> auto operator+(F Fcn){return ScopeExit<F>{Fcn};}};
#define ON_SCOPE_EXIT auto ScopeGuard=ScopeExitFactory{} + [&]()
struct FVector {
    double X=0,Y=0,Z=0;
    FVector()=default;
    FVector(double A,double B,double C):X(A),Y(B),Z(C){}
    static const FVector UpVector,ForwardVector,ZeroVector;
    FVector operator+(FVector B)const{return {X+B.X,Y+B.Y,Z+B.Z};}
    FVector operator-(FVector B)const{return {X-B.X,Y-B.Y,Z-B.Z};}
    FVector operator*(double S)const{return {X*S,Y*S,Z*S};}
    FVector operator-()const{return {-X,-Y,-Z};}
    bool operator==(const FVector&)const=default;
    static double Dist2D(FVector A,FVector B){return std::hypot(A.X-B.X,A.Y-B.Y);}
    FVector GetSafeNormal2D()const{double L=std::hypot(X,Y);return L>.001?FVector(X/L,Y/L,0):FVector();}
    bool IsNearlyZero()const{return std::abs(X)+std::abs(Y)+std::abs(Z)<.001;}
    bool ContainsNaN()const{return !std::isfinite(X)||!std::isfinite(Y)||!std::isfinite(Z);}
    FVector RotateAngleAxis(double Angle,FVector)const{
        Angle*=3.141592653589793/180;return {X*std::cos(Angle)-Y*std::sin(Angle),X*std::sin(Angle)+Y*std::cos(Angle),Z};
    }
    static FVector CrossProduct(FVector A,FVector B){return {A.Y*B.Z-A.Z*B.Y,A.Z*B.X-A.X*B.Z,A.X*B.Y-A.Y*B.X};}
};
const FVector FVector::UpVector{0,0,1},FVector::ForwardVector{1,0,0},FVector::ZeroVector{};
struct FBox {
    FVector Min,Max;bool IsValid=false;
    FBox()=default;explicit FBox(int){}
    FBox(FVector A,FVector B):Min(A),Max(B),IsValid(true){}
    FVector GetCenter()const{return (Min+Max)*.5;}
    FVector GetExtent()const{return (Max-Min)*.5;}
    FBox ExpandBy(double N)const{return {Min-FVector(N,N,N),Max+FVector(N,N,N)};}
};
struct FMath {
    template<class T>static T Clamp(T V,T A,T B){return std::clamp(V,A,B);}
    template<class T>static T Min(T A,T B){return std::min(A,B);}
    template<class T>static T Max(T A,T B){return std::max(A,B);}
    static double Abs(double V){return std::abs(V);}
};
template<class T>struct TArray:std::vector<T>{
    using std::vector<T>::operator=;
    int Num()const{return static_cast<int>(this->size());}
    bool IsValidIndex(int I)const{return I>=0&&I<Num();}
    bool IsEmpty()const{return this->empty();}
    void Reset(int N=0){this->clear();this->reserve(N);}
    void Add(const T& V){this->push_back(V);}
};
struct FString:std::string {using std::string::operator=;void Reset(){clear();}const char* operator*()const{return c_str();}};
enum ECollisionChannel {ECC_Visibility,ECC_Pawn,ECC_WorldStatic};
constexpr int ECR_Block=2;
struct Primitive {
    struct {FBox Box{{100,-100,0},{300,100,300}};FBox GetBox()const{return Box;}} Bounds;
    int GetCollisionResponseToChannel(ECollisionChannel)const{return ECR_Block;}
};
struct FHitResult {
    FVector ImpactPoint,ImpactNormal;double Distance=0;Primitive* Component=nullptr;
    Primitive* GetComponent()const{return Component;}
};
struct FCollisionQueryParams {FCollisionQueryParams(int,bool){}};
struct FCollisionObjectQueryParams {explicit FCollisionObjectQueryParams(ECollisionChannel){}};
struct FCollisionShape {double Radius;static FCollisionShape MakeSphere(double R){return {R};}};
struct FQuat {static constexpr int Identity=0;};
struct QueryRecord {FVector From,To;double Radius;bool operator==(const QueryRecord&)const=default;};
struct WorldAdapter {
    double Now=1,ScreenTop=110;std::vector<QueryRecord> Queries;
    bool MidHeightLedge=false,LowWeaponLedge=false,LowScreen=false,ProtectDestination=false,FailDestination=false;
    double GetTimeSeconds()const{return Now;}
    static bool IntersectsSlab(FVector From,FVector To,double Radius,double Bottom,double Top){
        if(std::abs(To.X-From.X)<.001)return false;
        const double T=(100-From.X)/(To.X-From.X);
        if(T<0||T>1)return false;
        const FVector P=From+(To-From)*T;
        return std::abs(P.Y)<20+Radius&&P.Z+Radius>=Bottom&&P.Z-Radius<=Top;
    }
    bool SweepSingleByObjectType(FHitResult&,FVector From,FVector To,int,FCollisionObjectQueryParams,FCollisionShape Shape,FCollisionQueryParams){
        Queries.push_back({From,To,Shape.Radius});
        return (MidHeightLedge&&IntersectsSlab(From,To,Shape.Radius,120,140)) ||
            (LowWeaponLedge&&IntersectsSlab(From,To,Shape.Radius,75,95));
    }
};
enum class EGASPEnemyAuthority {Locomotion,Physics};
enum class EGASPALSRifleStance {Ready,Aim};
struct EnemyAdapter {
    bool Dead=false,Ready=true,Held=true,ActualCrouch=false,RequestedCrouch=false,bRightHandOccupied=true,Follow=false;
    int Foundation=1,AimCalls=0,Stops=0;
    FVector Aim;EGASPEnemyAuthority Authority=EGASPEnemyAuthority::Locomotion;
    EGASPALSRifleStance Stance=EGASPALSRifleStance::Ready;
    bool IsDead()const{return Dead;}
    bool IsReady()const{return Ready;}
    bool IsRifleHeld()const{return Held;}
    bool IsMovementCrouched()const{return ActualCrouch;}
    void SetRifleAimTarget(FVector P){Aim=P;Follow=true;++AimCalls;}
    void SetCrouchCommand(bool B){RequestedCrouch=B;}
    void SetRifleFollowPlayer(bool B){Follow=B;}
    void SetRifleStance(EGASPALSRifleStance S){Stance=S;}
    void StopMovementCommand(){++Stops;}
};
bool IsValid(int P){return P!=0;}
struct FColor {static constexpr int Yellow=0,Orange=1;};
template<class... A>void DrawDebugSphere(A...){ }
template<class... A>void DrawDebugDirectionalArrow(A...){ }
struct {int GetValueOnGameThread()const{return 0;}} SensesDebug;
FVector Vector(CombatAI::Position P){return {P.X,P.Y,P.Z};}
enum class EEnemyCombatState {Disabled,Idle,Acquire,Pursue,Aim,Burst,Reload,Search,Return,Blocked,Recovery,Dead};
struct UEnemyCombatComponent {
    struct FTacticalPosition {
        FVector Ground,FacingBasis;CombatAI::PositionFeatures Features;CombatAI::PositionRating Rating;
        TArray<FVector> Route;FBox Obstacle;bool bCrouched=false;uint64 EvidenceId=0;
    };
    WorldAdapter World;EnemyAdapter Pawn;Primitive Column;
    bool bEnabled=true,bTargetVisible=false,bEvidencePending=false,bReposition=false,bRequestedWalk=true;
    bool bTacticalScan=false,bHeldPosition=false,bSelectedPosition=false,bPlanning=false,bPlanFailed=false;
    bool FreshSight=false,FollowSucceeds=true;
    EEnemyCombatState State=EEnemyCombatState::Idle;
    CombatAI::Knowledge Knowledge;CombatAI::EncounterMemory Memory;
    CombatAI::TacticalAssignment Assignment;CombatAI::ActionToken ScanRequest,PathRequest,ReloadRequest;
    CombatAI::ActionRuntime Action;CombatAI::ResponseGates Gates;
    CombatAI::DestinationBackoff MoveBackoff,WeaponBackoff;
    CombatAI::PositionHistory RejectedPositions,VisitedPositions;CombatAI::TransferBudget Transfers;
    CombatAI::TacticalPhase TacticalPhase=CombatAI::TacticalPhase::None;
    CombatAI::PathOutcome LastPathOutcome=CombatAI::PathOutcome::None;
    CombatAI::ContactKind Contact=CombatAI::ContactKind::None;
    TArray<FTacticalPosition> TacticalCandidates;FTacticalPosition HeldPosition,SelectedPosition;
    TArray<FVector> Path;TArray<int> Nodes,OpenNodes,CellNodes;
    std::array<int,static_cast<size_t>(CombatAI::PositionRejection::Count)> RejectionCounts{};
    uint64 EncounterGeneration=9,IntentEvidenceId=0,SightEventId=0;std::uint32_t StableSpawnIndex=0;
    double NextEvidenceResponse=0,NextSight=0,NextTacticalScan=0,NextLookAt=0,NextRepath=0;
    double NextTacticalWork=0,NextHoldValidation=0,HoldStartedAt=0,ScanStartedAt=0,TacticalMoveStartedAt=0;
    double LastProgress=0,StateStarted=0,CaptureDeltaSeconds=0,ContactAt=0,ContactDecisionAt=0,NextShot=0,ObstructedSince=-1;
    int FailedAttempts=0,SurfaceIndex=0,CandidateIndex=0,TacticalRejected=0,TacticalQueryCount=0,TacticalPeakQueries=0;
    int LookSector=-1,PathIndex=0,BurstRemaining=0,Magazine=12,Reloads=0,Acquisitions=0,ObstructionAttempts=0;
    unsigned ViewedSectors=0;FString TacticalReason,Reason;
    int SearchRestarts=0,FollowCalls=0,FireCalls=0,SightCalls=0;
    FVector Home,LastKnownGround,LastKnownAim,SearchAnchor,SearchForward,SearchLook,ScanOrigin,ActualFeet,SearchGoal,PathGoal,ProgressPosition;
    struct {void Reset(){}} Target;
    struct {FVector Vector()const{return {1,0,0};}} HomeFacing;
    // Tuning definitions are extracted from the production reflected struct.
    struct {
        // @PRODUCTION_TUNING@
    } Tuning;
    UEnemyCombatComponent(){Knowledge.Reset(EncounterGeneration);}
    EnemyAdapter* Enemy(){return &Pawn;}
    WorldAdapter* GetWorld(){return &World;}
    FVector Feet()const{return ActualFeet;}
    void RecordTrace(CombatAI::Event,const char*){}
    void RecordPath(CombatAI::PathOutcome O,const char*){LastPathOutcome=O;}
    void CapsuleSize(float& R,float& H)const{R=34;H=Pawn.ActualCrouch?55.f:86.f;}
    bool TacticalGround(FVector Ref,FVector& Ground,CombatAI::PositionRejection& Failure){
        Ground=Ref;Failure=CombatAI::PositionRejection::Support;
        if(World.FailDestination&&Ref.X>=100)return false;
        Failure=CombatAI::PositionRejection::None;return true;
    }
    bool TacticalRoute(FVector From,FVector To,const FBox&,TArray<FVector>& Route,double& Length){Route.Add(To);Length=FVector::Dist2D(From,To);return true;}
    bool TacticalWalk(FVector,FVector){return true;}
    bool TacticalTrace(FVector From,FVector To,FHitResult& Hit,ECollisionChannel Channel=ECC_Visibility){
        World.Queries.push_back({From,To,0});
        const bool Blocked=Channel==ECC_Pawn ||
            (World.LowScreen&&WorldAdapter::IntersectsSlab(From,To,0,40,World.ScreenTop)) ||
            (World.ProtectDestination&&From.X>=100&&std::abs(From.Z-90)<.01);
        if(!Blocked)return false;
        const auto Direction=(To-From).GetSafeNormal2D();
        Hit.Component=&Column;Hit.ImpactPoint=From+Direction*150;Hit.ImpactNormal=-Direction;Hit.Distance=150;return true;
    }
    bool FollowPath(FVector,float,double,CombatAI::MovePurpose){++FollowCalls;return FollowSucceeds;}
    bool ObservePlayer(){++SightCalls;bTargetVisible=FreshSight;return FreshSight;}
    bool CanShoot(FVector&,FVector&,bool& Blocked)const{Blocked=false;return false;}
    bool Fire(double,CombatAI::ActionToken){++FireCalls;return false;}
    void ClearIntent(CombatAI::ActionFailure Why=CombatAI::ActionFailure::Replaced);
    CombatAI::ActionToken EnsureAction(CombatAI::ActionKind,double);
    bool FinishAction(CombatAI::ActionToken,CombatAI::ActionStatus,CombatAI::ActionFailure);
    void ChangeState(EEnemyCombatState,const TCHAR*);
    void SuspendForPhysics(bool);
    void SetEnabled(bool);
    void ReceiveStimulus(const CombatAI::Stimulus&);
    void ApplyEvidenceIntent(double);
    void BeginSearch(const TCHAR*,bool bRestart=true);
    void AdvanceCombat(float);
    void FailTactic(const TCHAR*,CombatAI::ActionFailure,bool);
    void ResetTactics(bool bClearHistory=true);
    FVector TacticalDirection(int32)const;
    FTacticalPosition AssessTacticalPosition(FVector,FVector,bool,bool,FBox Obstacle=FBox(ForceInit));
    void AddTacticalCandidate(FVector,FBox Obstacle=FBox(ForceInit));
    void BeginTacticalScan(double);
    void AdvanceTacticalScan(double);
    void ChooseTacticalPosition(double);
    void RejectTacticalPosition(const FVector&,CombatAI::PositionRejection,double);
    void SetObservationFacing(double);
    void HoldTacticalPosition(double);
    void AdvanceSearch(double);
};
