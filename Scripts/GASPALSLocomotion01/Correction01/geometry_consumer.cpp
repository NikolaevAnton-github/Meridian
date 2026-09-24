struct UEnemyCombatComponent {
    AGASPEnemyFixture Fixture;WorldAdapter World;FVector Home;int TacticalQueryCount=0;
    struct {float NavigationRadius=5000,MaxStepHeight=35,MaxSlopeDegrees=45;} Tuning;
    const AGASPEnemyFixture* Enemy()const{return &Fixture;}
    WorldAdapter* GetWorld()const{return const_cast<WorldAdapter*>(&World);}
    bool PoseCapsuleSize(bool,float&,float&)const;void CapsuleSize(float&,float&)const;
    bool CoverCapsule(FVector,bool);bool CoverWalk(FVector,FVector);
    bool TacticalTrace(FVector,FVector,FHitResult&,ECollisionChannel=ECC_Visibility);
    bool TacticalGround(FVector,FVector&,CombatAI::PositionRejection&,int32=-1);
    bool TacticalWalk(FVector,FVector,int32=-1);
};
