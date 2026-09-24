int main(){
    int Checks=0;auto Check=[&](bool Pass,const char* Name){++Checks;if(!Pass){std::cerr<<Name<<'\n';std::exit(1);}};
    ACombatProjectileWorld W;AGASPEnemyFixture Wrapper,Other;ACharacter Source,Player,Unrelated;AEnemyPrototypeCharacter Prototype;
    Source.Owner=&Wrapper;Wrapper.Foundation=&Source;Unrelated.Owner=&Wrapper;
    Player.Capsule.Center={8,0,0};Unrelated.Capsule.Center={100,0,0};Prototype.Capsule.Center={100,0,0};
    Source.Capsule.Radius=50;Source.Capsule.HalfHeight=86;
    W.Data.Actors={&Wrapper,&Source,&Player,&Prototype,&Unrelated};W.Cache();
    Check(W.PreviousCapsules.Num()==3,"ordinary/player/prototype capsules retained");
    Check(!W.PreviousCapsules.Find(&Source),"owned source capsule excluded from history");
    Check(W.PreviousDummies.Num()==1,"one skeletal representation");
    Check(PhysicalProjectileOwner(&Source)==&Wrapper&&PhysicalProjectileOwner(&Wrapper)==&Wrapper,"source/wrapper canonical body");
    Check(!PhysicalProjectileOwner(&Unrelated),"ownership alone does not alias another actor");
    Check(!SameProjectileBody(nullptr,nullptr)&&!SameProjectileBody(&Source,&Player),"null/unrelated identities distinct");
    // Inject a pre-adoption/stale capsule; arbitration must reject it too.
    W.CachedCapsules.Add(&Source,{{0,0,0},50,86,{}});
    BulletData B;B.Shooter=&Player;B.BirthCapsules=W.PreviousCapsules;B.BirthDummies=W.PreviousDummies;
    FHitResult Hit;
    Check(Arbitrate(W,B,{0,0,0},{10,0,0},Hit)&&Hit.GetActor()==&Wrapper,"capsule entry cannot consume later bone contact");
    Check(Hit.BoneName=="spine_03"&&Hit.ImpactPoint==FVector(4,0,0),"actual bone and impact are preserved");
    Check(Dispatch(B,Hit)==25&&Wrapper.DamageCalls==1&&UGameplayStatics::GenericCalls==0,"one skeletal dispatch, no generic duplicate");
    Check(Wrapper.LastBone==Hit.BoneName&&Wrapper.LastPoint==Hit.ImpactPoint,"receiver observes exact contact");
    Other.Pose.Time=.2;Other.Pose.Bone="calf_l";Other.Pose.Point={2,0,0};W.Data.Actors.push_back(&Other);W.Cache();
    Check(Arbitrate(W,B,{0,0,0},{10,0,0},Hit)&&Hit.GetActor()==&Other&&Hit.BoneName=="calf_l","nearest skeletal contact wins");
    AActor Surface;Hit=FHitResult(&Surface,nullptr,{1,0,0},{-1,0,0});Hit.Time=.1;
    Check(Arbitrate(W,B,{0,0,0},{10,0,0},Hit,true)&&Hit.GetActor()==&Surface,"earlier finite-flight surface wins");
    W.Data.Actors={&Wrapper,&Source};W.Cache();
    for(AActor* Shooter:{static_cast<AActor*>(&Wrapper),static_cast<AActor*>(&Source)}){
        BulletData Shot;Shot.Shooter=Shooter;Shot.BirthDummies=W.PreviousDummies;Shot.BirthDummies.Find(&Wrapper)->Inside=true;
        LaunchClearance(Shooter,{0,0,0},Shot);Check(!Shot.bLaunchClear,"inside launch body activates immunity for both identities");
        W.CachedDummies.Find(&Wrapper)->Inside=true;
        Check(!Arbitrate(W,Shot,{0,0,0},{1,0,0},Hit)&&!Shot.bLaunchClear,"own body cannot intercept uncleared launch");
        W.CachedDummies.Find(&Wrapper)->Inside=false;
        Check(!Arbitrate(W,Shot,{0,0,0},{10,0,0},Hit)&&Shot.bLaunchClear,"exit clears immunity after that segment");
        Check(Arbitrate(W,Shot,{10,0,0},{0,0,0},Hit)&&SameProjectileBody(Hit.GetActor(),Shooter),"after-clear self contact uses the same body identity");
    }
    Wrapper.Dead=true;Source.Capsule.Query=false;W.Cache();
    Check(!W.PreviousCapsules.Find(&Source)&&W.PreviousDummies.Find(&Wrapper),"corpse bodies remain eligible without capsule");
    B.Shooter=&Player;Check(Arbitrate(W,B,{0,0,0},{10,0,0},Hit),"corpse bone contact is considered");
    Check(Dispatch(B,Hit)==0&&Wrapper.DamageCalls==2,"corpse still receives its single physical receiver call");
    ACharacter Replacement;Replacement.Owner=&Wrapper;Wrapper.Foundation=&Replacement;Source.Valid=false;Wrapper.Pose.Epoch=2;
    W.Data.Actors={&Wrapper,&Source,&Replacement,&Player};W.Cache();
    Check(!W.PreviousCapsules.Find(&Source)&&!W.PreviousCapsules.Find(&Replacement),"reset records neither destroyed nor replacement movement capsule");
    Check(W.PreviousDummies.Find(&Wrapper)->Epoch==2,"reset refreshes physical pose epoch");
    Wrapper.Ready=false;W.Cache();Check(W.PreviousDummies.Num()==0&&!W.PreviousCapsules.Find(&Replacement),"unready body does not fall back to capsule damage");
    W.Data.Actors={&Player};Player.Capsule.Center={5,0,0};W.Cache();B.Shooter=nullptr;B.bFirstAdvance=false;
    Check(Arbitrate(W,B,{0,0,0},{10,0,0},Hit)&&Hit.GetActor()==&Player,"ordinary character still uses capsule contact");
    Check(Dispatch(B,Hit)==25&&UGameplayStatics::GenericCalls==1,"ordinary generic damage remains");
    TArray<FPendingHit> Pending;BulletData A,C,D;A.Id=3;C.Id=2;D.Id=1;
    Pending.Add({A,{},.5});Pending.Add({C,{},.2});Pending.Add({D,{},.5});Order(Pending);
    Check(Pending[0].Bullet.Id==2&&Pending[1].Bullet.Id==1&&Pending[2].Bullet.Id==3,"contact time then shot id ordering retained");
    std::cout<<Checks<<" extracted production routing/arbitration assertions passed\n";
}
