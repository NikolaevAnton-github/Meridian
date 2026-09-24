UEnemyCombatComponent::UEnemyCombatComponent(){EncounterGeneration=9;Knowledge.Reset(9);bEnabled=true;State=EEnemyCombatState::Idle;Pawn.Combat=this;TestWorld.Roster={&Pawn};}
AGASPEnemyFixture* UEnemyCombatComponent::Enemy()const{return const_cast<AGASPEnemyFixture*>(&Pawn);}
FVector UEnemyCombatComponent::Feet()const{return ActualFeet;}
void UEnemyCombatComponent::CapsuleSize(float& R,float& H)const{R=34;H=Pawn.ActualCrouch?55.f:86.f;}
void UEnemyCombatComponent::RecordTrace(CombatAI::Event,const char*){}
void UEnemyCombatComponent::RecordPath(CombatAI::PathOutcome O,const char*){LastPathOutcome=O;}
bool UEnemyCombatComponent::FollowPath(FVector,float,double,CombatAI::MovePurpose P){++FollowCalls;MovementPurpose=P;bRequestedWalk=CombatAI::WantsWalk(P,500,1);return FollowSucceeds;}
bool UEnemyCombatComponent::TryObservePlayer(){
    if(!FreshSight)return false;
    LastKnownGround=FreshGround;LastKnownAim=FreshGround+FVector(0,0,130);Target=Pawn.Foundation;
    Memory.Observe(TestWorld.Now);++SightEventId;IntentEvidenceId=SightEventId;return true;
}
