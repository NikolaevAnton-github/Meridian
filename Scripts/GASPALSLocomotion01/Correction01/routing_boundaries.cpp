// Plain identity/history/contact data only. No actor lifecycle or engine world.
#include <algorithm>
#include <cstdlib>
#include <utility>
constexpr double BulletRadius=.5;
template<class T>struct TWeakObjectPtr {T* Ptr=nullptr;TWeakObjectPtr()=default;TWeakObjectPtr(T* P):Ptr(P){}T* Get()const{return Ptr;}bool operator==(const TWeakObjectPtr&)const=default;};
template<class K,class V>struct TMap {
    struct Entry {K Key;V Value;}; std::vector<Entry> Rows;
    void Add(K Key,V Value){for(auto& E:Rows)if(E.Key==Key){E.Value=Value;return;}Rows.push_back({Key,Value});}
    const V* Find(K Key)const{for(const auto& E:Rows)if(E.Key==Key)return &E.Value;return nullptr;}
    V* Find(K Key){return const_cast<V*>(std::as_const(*this).Find(Key));}
    auto begin()const{return Rows.begin();}auto end()const{return Rows.end();}int Num()const{return int(Rows.size());}
};
template<class T>T&& MoveTemp(T& X){return std::move(X);}
struct UPrimitiveComponent{virtual ~UPrimitiveComponent()=default;};
struct UCapsuleComponent:UPrimitiveComponent {FVector Center;float Radius=1,HalfHeight=1;bool Query=true;
    bool IsQueryCollisionEnabled()const{return Query;}FVector GetComponentLocation()const{return Center;}
    float GetScaledCapsuleRadius()const{return Radius;}float GetScaledCapsuleHalfHeight()const{return HalfHeight;}};
struct AActor {virtual ~AActor()=default;AActor* Owner=nullptr;bool Valid=true;
    AActor* GetOwner()const{return Owner;}template<class T>bool IsA()const{return dynamic_cast<const T*>(this)!=nullptr;}};
template<class T>bool IsValid(const T* P){return P&&P->Valid;}
template<class T,class U>auto Cast(U* P){using R=std::conditional_t<std::is_const_v<U>,const T*,T*>;return dynamic_cast<R>(P);}
struct ACharacter:AActor {UCapsuleComponent Capsule;UPrimitiveComponent Mesh;
    UCapsuleComponent* GetCapsuleComponent()const{return const_cast<UCapsuleComponent*>(&Capsule);}
    UPrimitiveComponent* GetMesh(){return &Mesh;}};
struct FEnemyHitSphere {FVector Center;double Radius=1;std::string Bone;};
struct AEnemyPrototypeCharacter:ACharacter {TArray<FEnemyHitSphere> Regions;auto SampleHitSpheres()const{return Regions;}};
struct FHitResult {
    AActor* Actor=nullptr;UPrimitiveComponent* Component=nullptr;FVector ImpactPoint,ImpactNormal;std::string BoneName;
    double Time=0,Distance=0;bool bBlockingHit=false;
    FHitResult()=default;FHitResult(AActor* A,UPrimitiveComponent* C,FVector P,FVector N):Actor(A),Component(C),ImpactPoint(P),ImpactNormal(N){}
    AActor* GetActor()const{return Actor;}
};
struct FDummyPose {int Epoch=1;bool Contact=true,Inside=false;double Time=.4;std::string Bone="spine_03";FVector Point{4,0,0};};
struct APhysicsControlDummy:AActor {bool Ready=true,Dead=false;FDummyPose Pose;UPrimitiveComponent Mesh;
    int DamageCalls=0;std::string LastBone;FVector LastPoint;mutable int LastBeforeEpoch=0;
    bool IsReady()const{return Ready;}FDummyPose SamplePhysicalPose()const{return Pose;}
    // The unchanged skeletal tracer supplies this hit. Test only its consumers.
    bool TracePhysicalPose(const FDummyPose& Before,const FDummyPose& After,FVector Start,FVector End,double,FHitResult& Hit)const{
        LastBeforeEpoch=Before.Epoch;
        if(Start==End)return After.Inside;
        if(!After.Contact)return false;
        Hit=FHitResult(const_cast<APhysicsControlDummy*>(this),const_cast<UPrimitiveComponent*>(&Mesh),After.Point,{1,0,0});
        Hit.Time=After.Time;Hit.BoneName=After.Bone;Hit.bBlockingHit=true;return true;
    }
    float ReceiveBullet(int64,float Damage,FVector,const FHitResult& Hit,double,double,uint64,float,float){
        ++DamageCalls;LastBone=Hit.BoneName;LastPoint=Hit.ImpactPoint;return Dead?0:Damage;}
};
struct AGASPEnemyFixture:APhysicsControlDummy {AActor* Foundation=nullptr;
    static AGASPEnemyFixture* FromFoundation(const AActor* Actor){return Actor?Cast<AGASPEnemyFixture>(Actor->GetOwner()):nullptr;}};
struct DataSet {std::vector<AActor*> Actors;};
template<class T>struct TActorIterator {DataSet* Data;size_t Index=0;explicit TActorIterator(DataSet* D):Data(D){Skip();}
    void Skip(){while(Index<Data->Actors.size()&&(!Data->Actors[Index]->Valid||!Cast<T>(Data->Actors[Index])))++Index;}
    explicit operator bool()const{return Index<Data->Actors.size();}void operator++(){++Index;Skip();}
    T* operator*()const{return Cast<T>(Data->Actors[Index]);}T* operator->()const{return operator*();}};
struct ACombatProjectileWorld {
    struct FCapsuleSample{FVector Center;float Radius,HalfHeight;TArray<FEnemyHitSphere> Regions;};
    DataSet Data;DataSet* GetWorld()const{return const_cast<DataSet*>(&Data);}
    TMap<TWeakObjectPtr<ACharacter>,FCapsuleSample> PreviousCapsules,CachedCapsules;
    TMap<TWeakObjectPtr<APhysicsControlDummy>,FDummyPose> PreviousDummies,CachedDummies;
    TMap<TWeakObjectPtr<ACharacter>,FCapsuleSample> SampleCapsules()const;
    TMap<TWeakObjectPtr<APhysicsControlDummy>,FDummyPose> SampleDummies()const;
    void RecordCapsules();void Cache(){RecordCapsules();CachedCapsules=PreviousCapsules;CachedDummies=PreviousDummies;}
};
struct BulletData {TWeakObjectPtr<AActor> Shooter;TWeakObjectPtr<AActor> Instigator;bool bLaunchClear=true,bFirstAdvance=true;
    int64 Id=1;float Damage=25,FallImpulseMultiplier=4,DeathImpulseMultiplier=6;double BirthTime=0;FVector Velocity{10,0,0};
    TMap<TWeakObjectPtr<ACharacter>,ACombatProjectileWorld::FCapsuleSample> BirthCapsules;
    TMap<TWeakObjectPtr<APhysicsControlDummy>,FDummyPose> BirthDummies;
};
struct UGameplayStatics {inline static int GenericCalls=0;template<class... T>static float ApplyPointDamage(T...){++GenericCalls;return 25;}};
