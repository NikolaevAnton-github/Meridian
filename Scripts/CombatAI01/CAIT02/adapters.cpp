// Engine boundaries for source fixtures. Collision is conservative AABB geometry,
// not a claim about Chaos, animation, navigation or actual game motion.
#include "CombatAIObservation.h"
#include <cmath>
#include <cstdint>
#include <iostream>
#include <limits>
#include <memory>
#include <string>
#include <type_traits>
#include <vector>
using int32=int; using uint32=std::uint32_t; using uint64=std::uint64_t; using int64=std::int64_t; using TCHAR=char;
constexpr int INDEX_NONE=-1,ForceInit=0; constexpr float TacticalAcceptance=25.f,MaxCandidateTravel=900.f;
#define TEXT(X) X
#define SCENE_QUERY_STAT(X) 0
template<class T> struct TNumericLimits {static T Max(){return std::numeric_limits<T>::max();}};
struct FMath {
    template<class T>static T Clamp(T V,T A,T B){return std::clamp(V,A,B);}
    template<class T>static T Min(T A,T B){return std::min(A,B);}
    template<class T>static T Max(T A,T B){return std::max(A,B);}
    static double Abs(double V){return std::abs(V);} static double Cos(double V){return std::cos(V);}
    static double DegreesToRadians(double V){return V*3.141592653589793/180;}
    static bool IsFinite(double V){return std::isfinite(V);} static int CeilToInt(double V){return static_cast<int>(std::ceil(V));}
    template<class T>static T Lerp(T A,T B,double Tm){return A+(B-A)*Tm;}
};
struct FRotator;
struct FVector {
    double X=0,Y=0,Z=0;
    FVector()=default;FVector(double A,double B,double C):X(A),Y(B),Z(C){} explicit FVector(double A):X(A),Y(A),Z(A){}
    static const FVector UpVector,ForwardVector,ZeroVector;
    FVector operator+(FVector B)const{return {X+B.X,Y+B.Y,Z+B.Z};}
    FVector operator-(FVector B)const{return {X-B.X,Y-B.Y,Z-B.Z};}
    FVector operator*(double B)const{return {X*B,Y*B,Z*B};} FVector operator-()const{return {-X,-Y,-Z};}
    bool operator==(const FVector&)const=default;
    bool Equals(FVector B,double Tolerance)const{return std::abs(X-B.X)<=Tolerance&&std::abs(Y-B.Y)<=Tolerance&&std::abs(Z-B.Z)<=Tolerance;}
    static double Dist2D(FVector A,FVector B){return std::hypot(A.X-B.X,A.Y-B.Y);}
    static double DotProduct(FVector A,FVector B){return A.X*B.X+A.Y*B.Y+A.Z*B.Z;}
    static FVector CrossProduct(FVector A,FVector B){return {A.Y*B.Z-A.Z*B.Y,A.Z*B.X-A.X*B.Z,A.X*B.Y-A.Y*B.X};}
    double SizeSquared()const{return X*X+Y*Y+Z*Z;}
    FVector GetSafeNormal()const{double L=std::sqrt(SizeSquared());return L>.001?*this*(1/L):FVector();}
    FVector GetSafeNormal2D()const{double L=std::hypot(X,Y);return L>.001?FVector(X/L,Y/L,0):FVector();}
    bool IsNearlyZero()const{return SizeSquared()<.00001;}
    bool ContainsNaN()const{return !std::isfinite(X)||!std::isfinite(Y)||!std::isfinite(Z);}
    FVector RotateAngleAxis(double A,FVector)const{A=FMath::DegreesToRadians(A);return {X*std::cos(A)-Y*std::sin(A),X*std::sin(A)+Y*std::cos(A),Z};}
    FRotator Rotation()const;
};
const FVector FVector::UpVector{0,0,1},FVector::ForwardVector{1,0,0},FVector::ZeroVector{};
struct FRotator {static const FRotator ZeroRotator; FVector Vector()const{return {1,0,0};}};
const FRotator FRotator::ZeroRotator{}; FRotator FVector::Rotation()const{return {};}
struct FBox {
    FVector Min,Max;bool IsValid=false;FBox()=default;explicit FBox(int){}
    FBox(FVector A,FVector B):Min(A),Max(B),IsValid(true){}
    FVector GetCenter()const{return (Min+Max)*.5;} FVector GetExtent()const{return (Max-Min)*.5;}
    FBox ExpandBy(double X)const{return {Min-FVector(X),Max+FVector(X)};}
};
template<class T>struct TArray:std::vector<T>{using std::vector<T>::operator=;
    int Num()const{return static_cast<int>(this->size());} bool IsValidIndex(int I)const{return I>=0&&I<Num();}
    bool IsEmpty()const{return this->empty();} void Reset(int N=0){this->clear();this->reserve(N);} void Add(const T& V){this->push_back(V);}};
template<class A,class B>struct TMap{void Reset(){}};
struct FIntPoint{};
struct FString:std::string{using std::string::operator=;void Reset(){clear();}const char* operator*()const{return c_str();}};
template<class T>using TObjectPtr=T*;
template<class T>using TUniquePtr=std::unique_ptr<T>;
template<class T>using TSharedRef=std::shared_ptr<T>;
template<class T>struct TWeakObjectPtr {T* Ptr=nullptr;void Reset(){Ptr=nullptr;}bool IsValid()const{return Ptr!=nullptr;}void operator=(T* P){Ptr=P;}};
template<class T>bool IsValid(T* P){return P!=nullptr;}
template<class T,class U>T* Cast(U* P){return reinterpret_cast<T*>(P);}
template<class F>struct ScopeExit{F Function;~ScopeExit(){Function();}};
struct ScopeExitFactory{template<class F>auto operator+(F Fn){return ScopeExit<F>{Fn};}};
#define ON_SCOPE_EXIT auto ScopeGuard=ScopeExitFactory{} + [&]()
enum ECollisionChannel {ECC_Visibility,ECC_Pawn,ECC_WorldStatic};
constexpr int ECR_Block=2,ECR_Ignore=0;
struct FCollisionQueryParams{bool bTraceComplex=false;FCollisionQueryParams(int,bool){}template<class T>void AddIgnoredActor(T*){}};
struct FCollisionResponseParams{struct{void SetResponse(ECollisionChannel,int){}}CollisionResponse;explicit FCollisionResponseParams(int){}};
struct FCollisionObjectQueryParams{explicit FCollisionObjectQueryParams(ECollisionChannel){}};
struct FCollisionShape{double Radius=0,Height=0;static FCollisionShape MakeSphere(double R){return {R,R};}static FCollisionShape MakeCapsule(double R,double H){return {R,H};}};
struct FQuat{static constexpr int Identity=0;};
struct Primitive{struct{FBox Box;FBox GetBox()const{return Box;}}Bounds;bool Static=true;int PawnResponse=ECR_Block,VisResponse=ECR_Block;
    int GetCollisionResponseToChannel(ECollisionChannel C)const{return C==ECC_Pawn?PawnResponse:VisResponse;}};
struct FHitResult{FVector ImpactPoint,ImpactNormal;double Distance=0;Primitive* Component=nullptr;Primitive* GetComponent()const{return Component;}};
struct AGASPEnemyFixture; struct UEnemyCombatComponent;
struct WorldAdapter{
    double Now=1;bool HasManager=true,Floor=true;int Launches=0;std::vector<Primitive> Boxes;std::vector<AGASPEnemyFixture*> Roster;
    std::vector<std::pair<FVector,FVector>> Queries;Primitive FloorPart;
    double GetTimeSeconds()const{return Now;}
    void Box(FVector A,FVector B){Primitive P;P.Bounds.Box={A,B};Boxes.push_back(P);}
    static bool Intersect(FVector A,FVector B,FBox Box,double& Time,FVector& Normal){
        double Low=0,High=1;const auto D=B-A; const double Starts[]={A.X,A.Y,A.Z},Deltas[]={D.X,D.Y,D.Z};
        const double Lo[]={Box.Min.X,Box.Min.Y,Box.Min.Z},Hi[]={Box.Max.X,Box.Max.Y,Box.Max.Z};
        for(int I=0;I<3;++I){
            if(std::abs(Deltas[I])<1e-8){if(Starts[I]<Lo[I]||Starts[I]>Hi[I])return false;continue;}
            double T1=(Lo[I]-Starts[I])/Deltas[I],T2=(Hi[I]-Starts[I])/Deltas[I];double Sign=-1;
            if(T1>T2){std::swap(T1,T2);Sign=1;}
            if(T1>Low){Low=T1;Normal={};if(I==0)Normal.X=Sign;else if(I==1)Normal.Y=Sign;else Normal.Z=Sign;}
            High=std::min(High,T2);if(Low>High)return false;
        }
        Time=Low;return High>=0&&Low<=1;
    }
    bool Trace(FHitResult& Hit,FVector A,FVector B,ECollisionChannel Channel,FVector Expand={},bool StaticOnly=true){
        Queries.emplace_back(A,B);double Best=2;Primitive* Part=nullptr;FVector Normal;
        if(Floor&&A.Z>0&&B.Z<=0){Best=A.Z/(A.Z-B.Z);Part=&FloorPart;Normal={0,0,1};}
        for(auto& P:Boxes){if((StaticOnly&&!P.Static)||P.GetCollisionResponseToChannel(Channel)!=ECR_Block)continue;
            double T=0;FVector N;FBox Box{P.Bounds.Box.Min-Expand,P.Bounds.Box.Max+Expand};
            if(Intersect(A,B,Box,T,N)&&T<Best){Best=T;Part=&P;Normal=N;}}
        if(!Part)return false;
        Hit={A+(B-A)*Best,Normal,std::sqrt((B-A).SizeSquared())*Best,Part};return true;
    }
    bool LineTraceSingleByChannel(FHitResult& H,FVector A,FVector B,ECollisionChannel C,FCollisionQueryParams,FCollisionResponseParams){return Trace(H,A,B,C);}
    bool SweepSingleByChannel(FHitResult& H,FVector A,FVector B,int,ECollisionChannel C,FCollisionShape S,FCollisionQueryParams){return Trace(H,A,B,C,{S.Radius,S.Radius,S.Height},false);}
    bool SweepSingleByChannel(FHitResult& H,FVector A,FVector B,int,ECollisionChannel C,FCollisionShape S,FCollisionQueryParams,FCollisionResponseParams){return Trace(H,A,B,C,{S.Radius,S.Radius,S.Height});}
    bool SweepSingleByObjectType(FHitResult& H,FVector A,FVector B,int,FCollisionObjectQueryParams,FCollisionShape S,FCollisionQueryParams){return Trace(H,A,B,ECC_Pawn,{S.Radius,S.Radius,S.Height});}
    bool OverlapAnyTestByObjectType(FVector A,int,FCollisionObjectQueryParams,FCollisionShape S,FCollisionQueryParams){FHitResult H;return Trace(H,A,A,ECC_Pawn,{S.Radius,S.Radius,S.Height});}
};
struct UCapsuleComponent{float Radius=34,HalfHeight=86;float GetScaledCapsuleRadius()const{return Radius;}float GetScaledCapsuleHalfHeight()const{return HalfHeight;}};
struct UStanceSettings{float CrouchHalfHeight=55;};
struct UCharacterMoverComponent{UStanceSettings Settings;template<class T>const T* FindSharedSettings()const{return &Settings;}};
struct APawn{UCapsuleComponent Capsule,Original;UCharacterMoverComponent Mover;
    template<class T>const T* FindComponentByClass()const{if constexpr(std::is_same_v<T,UCapsuleComponent>)return &Capsule;else return &Mover;}};
struct UMovementUtils{template<class T>static const T* GetOriginalComponentType(APawn* P){return &P->Original;}};
struct UGASPALSRifleAnimInstance{float RifleAlpha=1,RifleAimAlpha=1;};
struct FTransform{FVector Origin;FVector TransformPosition(FVector)const{return Origin;}};
struct MeshAdapter{FVector Location{0,0,130},Right{1,0,0};UGASPALSRifleAnimInstance Anim;
    FVector GetSocketLocation(const char*)const{return Location;}bool DoesSocketExist(const char*)const{return true;}
    FTransform GetComponentTransform()const{return {Location};}FVector GetRightVector()const{return Right;}
    UGASPALSRifleAnimInstance* GetAnimInstance(){return &Anim;}};
enum class EGASPEnemyAuthority{Locomotion,Recovery,Dead};
enum class EGASPALSRifleStance{Ready,Aim};
enum class EEnemyCombatState{Disabled,Idle,Acquire,Pursue,Aim,Burst,Reload,Search,Return,Blocked,Recovery,Dead};
struct AGASPEnemyFixture{
    bool Dead=false,Ready=true,Held=true,ActualCrouch=false,bCrouchCommand=false,bRightHandOccupied=true,Follow=false;
    float Health=100,MaxHealth=100,MovementAlpha=0;int Stops=0;FVector Aim;
    APawn Data;APawn* Foundation=&Data;MeshAdapter BodyData,RifleData;MeshAdapter* Body=&BodyData;MeshAdapter* Rifle=&RifleData;
    UEnemyCombatComponent* Combat=nullptr;EGASPEnemyAuthority Authority=EGASPEnemyAuthority::Locomotion;
    EGASPALSRifleStance Stance=EGASPALSRifleStance::Ready;
    bool IsDead()const{return Dead;}bool IsReady()const{return Ready;}bool IsRifleHeld()const{return Held&&Rifle;}
    bool IsMovementCrouched()const{return ActualCrouch;}float GetRifleMovementAlpha()const{return MovementAlpha;}
    void SetCrouchCommand(bool B){bCrouchCommand=B;}void SetRifleAimTarget(FVector P){Aim=P;Follow=true;}
    void SetRifleFollowPlayer(bool B){Follow=B;}void SetRifleStance(EGASPALSRifleStance S){Stance=S;}
    void StopMovementCommand(){++Stops;}
};
template<class T>struct TActorIterator{WorldAdapter* W;size_t I=0;explicit TActorIterator(WorldAdapter* P):W(P){}
    explicit operator bool()const{return I<W->Roster.size();}void operator++(){++I;}T* operator*()const{return W->Roster[I];}};
struct ACombatProjectileWorld{
    WorldAdapter* World=nullptr;
    static ACombatProjectileWorld* Find(WorldAdapter* W){static ACombatProjectileWorld M;M.World=W;return W->HasManager?&M:nullptr;}
    void BuildQuery(FCollisionQueryParams&,const AGASPEnemyFixture*){}
    int64 Launch(AGASPEnemyFixture*,FVector,FVector,float){return ++World->Launches;}
};
struct FRandomStream{FVector VRandCone(FVector V,double){return V;}};
struct USoundBase{};struct UNiagaraSystem{};struct FJsonObject{};
template<class T>T* LoadObject(void*,const char*){return nullptr;}
struct UGameplayStatics{static float GetGlobalTimeDilation(void*){return 1;}template<class... A>static void PlaySoundAtLocation(A...){}};
enum class ENCPoolMethod{AutoRelease};
struct UNiagaraFunctionLibrary{template<class... A>static void SpawnSystemAtLocation(A...){}};
struct FColor{static constexpr int Yellow=0,Orange=1;};
template<class... A>void DrawDebugSphere(A...){}template<class... A>void DrawDebugDirectionalArrow(A...){}
struct{int GetValueOnGameThread()const{return 0;}} SensesDebug;
FVector Vector(CombatAI::Position P){return {P.X,P.Y,P.Z};}
