// Minimal deterministic adapters; runner appends verbatim production methods.
// These test the policy/producers' boundary calls, not Unreal runtime behavior.
#include "CombatAIObservation.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>

using uint64=std::uint64_t;
using int64=std::int64_t;
using TCHAR=char;
#define TEXT(X) X
struct FVector
{
    double X=0,Y=0,Z=0;
    FVector()=default;
    explicit FVector(double S):X(S),Y(S),Z(S){}
    FVector(double A,double B,double C):X(A),Y(B),Z(C){}
    FVector operator+(FVector B)const{return {X+B.X,Y+B.Y,Z+B.Z};}
    FVector operator-(FVector B)const{return {X-B.X,Y-B.Y,Z-B.Z};}
    FVector operator*(double S)const{return {X*S,Y*S,Z*S};}
    static double Dist2D(FVector A,FVector B){return std::hypot(A.X-B.X,A.Y-B.Y);}
    FVector GetSafeNormal2D()const {const double L=std::hypot(X,Y);return L>.001?FVector(X/L,Y/L,0):FVector();}
    bool IsNearlyZero()const{return std::abs(X)+std::abs(Y)+std::abs(Z)<.001;}
    FVector Rotation()const{return {};}
};
struct FMath
{
    template<class T> static T Clamp(T X,T A,T B){return std::clamp(X,A,B);}
    template<class T> static T Min(T A,T B){return std::min(A,B);}
    template<class T> static T Max(T A,T B){return std::max(A,B);}
    static float DegreesToRadians(float X){return X*.0174532925f;}
};
struct FColor {static constexpr int Yellow=0,Orange=1;};
template<class... Args>void DrawDebugSphere(Args...){ }
template<class... Args>void DrawDebugDirectionalArrow(Args...){ }
struct Debug { int GetValueOnGameThread()const{return 0;} } SensesDebug;
FVector Vector(CombatAI::Position P){return {P.X,P.Y,P.Z};}
enum class EEnemyCombatState{Disabled,Idle,Search,Reload,Recovery};
struct EnemyFixture
{
    bool Dead=false; FVector Aim; int AimCalls=0;
    bool IsDead()const{return Dead;}
    void SetRifleAimTarget(FVector P){Aim=P;++AimCalls;}
};
struct ACombatProjectileWorld
{
    double Time=1; int Launches=0; bool AcceptLaunch=true;
    double GetTimeSeconds()const{return Time;}
    static ACombatProjectileWorld* Find(ACombatProjectileWorld* W){return W;}
    int64 Launch(EnemyFixture*,FVector,FVector,float){return AcceptLaunch?++Launches:0;}
};
struct USoundBase{}; struct UNiagaraSystem{};
template<class T>T* LoadObject(void*,const char*){return nullptr;}
struct UGameplayStatics
{
    template<class T>static float GetGlobalTimeDilation(T*){return .25f;}
    template<class... T>static void PlaySoundAtLocation(T...){ }
};
enum class ENCPoolMethod{AutoRelease};
struct UNiagaraFunctionLibrary{template<class... T>static void SpawnSystemAtLocation(T...){ }};
struct UEnemyCombatComponent
{
    bool bEnabled=true,bTargetVisible=false,bEvidencePending=false,bReposition=false;
    bool FreshSight=false,MuzzleClear=true;
    EEnemyCombatState State=EEnemyCombatState::Idle;
    CombatAI::Knowledge Knowledge;
    CombatAI::EncounterMemory Memory;
    CombatAI::TacticalAssignment Assignment;
    CombatAI::ActionRuntime Action;
    CombatAI::ResponseGates Gates;
    std::uint32_t StableSpawnIndex=0;
    uint64 IntentEvidenceId=0,EncounterGeneration=9;
    double NextEvidenceResponse=0,NextSight=0,NextTacticalScan=0,NextLookAt=0,NextRepath=0,HoldStartedAt=0;
    double NextShot=0,ObstructedSince=-1,FlashUntil=0;
    int FailedAttempts=0,TraceCalls=0,SearchCalls=0,ClearCalls=0;
    int Magazine=5,Shots=0,BurstRemaining=3,ObstructionAttempts=0;
    int64 LastShotId=0;
    FVector Home,LastKnownGround,LastKnownAim,SearchAnchor,SearchForward,SearchLook,LastMuzzle,LastBarrel;
    struct {FVector Vector()const{return {1,0,0};}} HomeFacing;
    struct {float SpreadDegrees=.6f,BulletSpeed=14000,BulletDamage=10,ShotInterval=.18f;} Tuning;
    struct {FVector VRandCone(FVector D,float){return D;}} Spread;
    USoundBase* ShotSound=nullptr; UNiagaraSystem* MuzzleEffect=nullptr;
    EnemyFixture Fixture; ACombatProjectileWorld Clock;
    UEnemyCombatComponent(){Knowledge.Reset(9);}
    EnemyFixture* Enemy(){return &Fixture;}
    ACombatProjectileWorld* GetWorld(){return &Clock;}
    FVector Feet()const{return {};}
    void RecordTrace(CombatAI::Event,const char*){++TraceCalls;}
    void ClearIntent(){++ClearCalls;}
    void ResetTactics(bool){ }
    void ChangeState(EEnemyCombatState S,const char*){State=S;++SearchCalls;}
    bool ObservePlayer(){return FreshSight;}
    bool CanShoot(FVector& M,FVector& D,bool& Blocked)const{M={0,0,140};D={1,0,0};Blocked=!MuzzleClear;return MuzzleClear;}
    void ReceiveStimulus(const CombatAI::Stimulus& Record);
    void ApplyEvidenceIntent(double Now);
    void BeginSearch(const TCHAR* Why,bool bRestart=true);
    bool Fire(double Now,CombatAI::ActionToken Request);
};
