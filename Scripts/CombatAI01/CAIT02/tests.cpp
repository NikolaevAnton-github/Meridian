int Checks=0,Failures=0;
void StartPlan(UEnemyCombatComponent& C,CombatAI::CoverSide Side=CombatAI::CoverSide::Up);
void Check(bool Pass,const char* Name){++Checks;if(!Pass){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
void Tick(UEnemyCombatComponent& C,double Now){C.TestWorld.Now=Now;C.AdvanceCombat(.01f);}
void SeedSight(UEnemyCombatComponent& C){C.FreshSight=true;C.RefreshTacticalContext(C.TestWorld.Now);C.ObservePlayer();C.NextSight=0;}
void Fixture(UEnemyCombatComponent& C,bool Low=true){
    C.ActualFeet={40,0,0};C.Home={40,0,0};C.TestWorld.Box({100,-70,0},{140,70,Low?112.0:300.0});
    C.CoverThreatGround={1000,0,0};C.CoverThreatAim={1000,0,130};C.ScanOrigin=C.ActualFeet;
    C.LastKnownGround=C.CoverThreatGround;C.LastKnownAim=C.CoverThreatAim;
    C.Memory.Observe(1);C.RefreshTacticalContext(1);C.Assignment.Assign(9,CombatAI::TacticalObjective::Engage,1,1);
}
void ContextTests(){
    UEnemyCombatComponent C;C.RefreshTacticalContext(1);
    Check(C.Context.SelfHealthKnown&&C.Context.SelfHealth==1&&!C.Context.TargetHealth.Known,"producer uses actual self health and unknown target");
    Check(C.Context.Allies.Known&&C.Context.Allies.Available==0,"one fixture excludes itself and its foundation");
    const auto Healthy=C.Context;C.Pawn.Health=20;C.RefreshTacticalContext(1);
    Check(CombatAI::EvaluateRisk(C.Context).Protection>CombatAI::EvaluateRisk(Healthy).Protection,"damage changes protection preference through producer");
    Check(CombatAI::SelectRangeIntent(C.Context,6500,false)==CombatAI::RangeIntent::FavorProtection,"low health refuses exposed out-of-range advance");
    Check(!CombatAI::CoverTransferEligible(Healthy,650,true,false)&&CombatAI::CoverTransferEligible(C.Context,650,true,false),"actual low health makes farther protective transfer eligible");
    C.Pawn.Health=100;CombatAI::HealthKnowledge K{true,.2,1,5,9,22,1};C.ReceiveTargetHealth(K);C.RefreshTacticalContext(1);
    Check(C.Context.TargetHealth.Known&&CombatAI::EvaluateRisk(C.Context).CautiousAttack>0,"injected evidence-backed health advantage affects policy");
    Check(CombatAI::CoverTransferEligible(Healthy,430,true,false)&&!CombatAI::CoverTransferEligible(C.Context,430,true,false),"known advantage favors retaining useful range over distant transfer");
    C.RefreshTacticalContext(6);Check(!C.Context.TargetHealth.Known,"expired target health becomes unknown");
    K.Generation=8;C.ReceiveTargetHealth(K);C.RefreshTacticalContext(6);Check(!C.Context.TargetHealth.Known,"stale generation cannot manufacture target health");
    UEnemyCombatComponent Ally;C.TestWorld.Roster.push_back(&Ally.Pawn);C.NextAllyRefresh=0;C.RefreshTacticalContext(6);
    Check(C.Context.Allies.Available==1&&C.Context.Allies.Capable==std::array<int,3>{1,1,1},"available roster summarizes actual weapon capabilities once");
    Check(CombatAI::EvaluateRisk(C.Context).CautiousAttack>CombatAI::EvaluateRisk(Healthy).CautiousAttack,"produced support capabilities affect cautious attack preference");
    Ally.Pawn.Held=false;C.NextAllyRefresh=0;C.RefreshTacticalContext(6);
    Check(C.Context.Allies.Available==1&&C.Context.Allies.Capable[0]==0,"weaponless ally is available but supplies no rifle capability");
    C.TestWorld.HasManager=false;C.NextAllyRefresh=0;C.RefreshTacticalContext(6);Check(!C.Context.Allies.Known,"missing roster explicitly unknown");
    Check(CombatAI::SelectRangeIntent(Healthy,4000,false)==CombatAI::RangeIntent::HoldRange,"rifle uses existing forty-meter range");
    Check(CombatAI::SelectRangeIntent(Healthy,6500,true)==CombatAI::RangeIntent::SeekLane,"obstruction never licenses a rush");
    auto Short=Healthy;Short.Weapon.EffectiveRange=800;Short.Weapon.PreferredRange=600;
    Check(CombatAI::CautiousStep(Short,1000)==400&&CombatAI::CautiousStep(Healthy,7000)==450,"profiles produce bounded range-dependent steps");
    Short.Weapon.Capabilities=CombatAI::CoverFire;Check(CombatAI::SelectRangeIntent(Short,1000,false)==CombatAI::RangeIntent::NoWeapon,"cover capability cannot bypass direct-fire capability");
}
void GeometryTests(){
    UEnemyCombatComponent C;Fixture(C,false);
    auto P=C.AssessTacticalPosition(C.Feet(),C.Feet(),false,true);C.AssessCoverOptions(P);
    Check(P.CoverOptions[0].Score>-1e9&&P.CoverOptions[1].Score>-1e9,"real static column produces independent left and right lanes");
    Check(P.CoverOptions[2].Score<=-1e9,"tall cover rejects standing shot through cover");
    C.TestWorld.Box({0,-640,0},{90,-90,300});C.AssessCoverOptions(P);
    Check(P.CoverOptions[0].Score<=-1e9&&P.CoverOptions[1].Score>-1e9,"blocked left route does not disable right");
    UEnemyCombatComponent R;Fixture(R,false);R.TestWorld.Box({0,90,0},{90,640,300});
    auto RP=R.AssessTacticalPosition(R.Feet(),R.Feet(),false,true);R.AssessCoverOptions(RP);
    Check(RP.CoverOptions[0].Score>-1e9&&RP.CoverOptions[1].Score<=-1e9,"blocked right route independently preserves left");
    UEnemyCombatComponent L;Fixture(L);auto Up=L.AssessCoverOption(L.Feet(),L.Feet(),CombatAI::CoverSide::Up);
    Check(Up.Score>-1e9&&Up.Features.Return&&Up.Features.Outbound,"low cover requires crouched protection and standing lane");
    L.TestWorld.Box({0,-50,120},{90,50,180});Up=L.AssessCoverOption(L.Feet(),L.Feet(),CombatAI::CoverSide::Up);
    Check(Up.Score<=-1e9&&!Up.Features.PoseClear,"standing capsule rejects ceiling while crouch volume fits");
    UEnemyCombatComponent No;Fixture(No);No.TestWorld.Boxes.clear();
    Check(No.AssessCoverOption(No.Feet(),No.Feet(),CombatAI::CoverSide::Up).Score<=-1e9,"coordinate offsets alone do not provide protection");
    No.TestWorld.Floor=false;Check(!No.CoverCapsule(No.Feet(),true),"unsupported anchor rejected");
    UEnemyCombatComponent Dynamic;Fixture(Dynamic);Dynamic.TestWorld.Boxes[0].Static=false;
    Check(!Dynamic.CoverProtected(Dynamic.Feet()),"concealed dynamic actor cannot produce static cover");
}
void SelectionAndGateTests(){
    using P=CombatAI::CoverPhase;
    UEnemyCombatComponent C;Fixture(C,false);C.TestWorld.Box({0,-640,0},{90,-90,300});
    C.SearchAnchor=C.CoverThreatGround;C.SearchForward={1,0,0};C.bCoverScan=true;C.BeginTacticalScan(1);
    for(int I=0;I<180&&C.bTacticalScan;++I){C.TestWorld.Now=1+I*.03;C.AdvanceTacticalScan(C.TestWorld.Now);}
    Check(C.bCoverScanReady&&C.CandidateIndex>0&&C.TestWorld.Now<5.1,"production bounded geometry producer completes cover proposals");
    C.ChooseCover(C.TestWorld.Now);
    Check(C.CoverPhase==P::ToAnchor&&C.CoverPlan.Features.Side==CombatAI::CoverSide::Right&&C.Assignment.Accepts(C.CoverOwner),"real scan/selector commits valid alternate side and ownership");
    UEnemyCombatComponent N;N.RefreshTacticalContext(1);N.Memory.Observe(1);N.Assignment.Assign(9,CombatAI::TacticalObjective::Engage,1,1);
    N.CoverThreatGround={1000,0,0};N.CoverThreatAim={1000,0,130};N.bCoverScan=true;N.BeginTacticalScan(1);
    for(int I=0;I<180&&N.bTacticalScan;++I){N.TestWorld.Now=1+I*.03;N.AdvanceTacticalScan(N.TestWorld.Now);}
    N.ChooseCover(N.TestWorld.Now);Check(N.CoverPhase==P::None&&N.CoverGate==CombatAI::CoverGate::NoOption&&N.NextCoverScan>N.TestWorld.Now,"no-cover finite scan supplies diagnostic retry");
    UEnemyCombatComponent Reload;StartPlan(Reload);Reload.Magazine=0;Tick(Reload,1);const auto ReloadToken=Reload.ReloadRequest;
    Check(Reload.State==EEnemyCombatState::Reload&&Reload.CoverPhase==P::Protected&&Reload.Pawn.bCrouchCommand,"empty magazine reloads in protected achieved stance");
    Tick(Reload,2);Check(Reload.Magazine==0&&Reload.ReloadRequest==ReloadToken,"concealment retains one reload request without premature refill");
    Tick(Reload,3.7);Check(Reload.Reloads==1&&Reload.Magazine==12,"protected reload commits once on its world deadline");
    Tick(Reload,3.8);Check(Reload.Reloads==1,"subsequent cover phase cannot duplicate ammo commit");
    UEnemyCombatComponent Die;StartPlan(Die);auto Owner=Die.CoverOwner;Die.Pawn.Dead=true;Tick(Die,1.1);
    Check(Die.State==EEnemyCombatState::Dead&&Die.CoverPhase==P::None&&!Die.Assignment.Accepts(Owner)&&!Die.Memory.Alert,"death invalidates cover and personal evidence");
    UEnemyCombatComponent Launch;SeedSight(Launch);Launch.BurstRemaining=3;auto Token=Launch.EnsureAction(CombatAI::ActionKind::Burst,1);
    Launch.Gates.ReloadUntil=2;Check(!Launch.Fire(1,Token)&&Launch.TestWorld.Launches==0,"direct launch enforces reload deadline itself");
    Launch.Gates={};Launch.FreshSight=false;Check(!Launch.Fire(1.2,Token)&&Launch.TestWorld.Launches==0,"cached visible contact cannot authorize birth after failed fresh sight");
    Launch.FreshSight=true;Launch.Pawn.bCrouchCommand=true;Launch.Pawn.ActualCrouch=false;
    Check(!Launch.Fire(1.3,Token),"achieved stance mismatch vetoes launch");
    Launch.Pawn.bCrouchCommand=false;Launch.Pawn.MovementAlpha=.5;
    Check(!Launch.Fire(1.4,Token),"achieved locomotion vetoes launch");
    Launch.Pawn.MovementAlpha=0;Launch.Pawn.RifleData.Right={0,1,0};Check(!Launch.Fire(1.5,Token),"barrel alignment veto retained");
    Launch.Pawn.RifleData.Right={1,0,0};Launch.ClearIntent();Check(!Launch.Fire(1.6,Token),"canceled action token cannot launch");
    UEnemyCombatComponent Hearing;StartPlan(Hearing);CombatAI::StimulusData Sound;
    Sound.Id=20;Sound.Generation=9;Sound.Kind=CombatAI::Sense::Step;Sound.Category=CombatAI::SourceTeam::Player;
    Sound.OccurredWorld=Sound.ReceivedWorld=1;Sound.Confidence=.65;Sound.Uncertainty=200;Sound.Region={-800,500,0};
    Hearing.ReceiveStimulus(CombatAI::Stimulus(Sound));const auto Known=Hearing.LastKnownGround;Hearing.ApplyEvidenceIntent(1);
    Check(Hearing.bEvidencePending&&Hearing.LastKnownGround==Known&&Hearing.CoverPhase==P::ToAnchor,"new sound is retained without destroying cover ownership");
}
void StartPlan(UEnemyCombatComponent& C,CombatAI::CoverSide Side){
    Fixture(C,Side==CombatAI::CoverSide::Up);C.Pawn.ActualCrouch=true;
    C.CoverPlan=C.AssessCoverOption(C.Feet(),C.Feet()+FVector(0,Side==CombatAI::CoverSide::Left?-160:Side==CombatAI::CoverSide::Right?160:0,0),Side);
    C.Assignment.Assign(9,CombatAI::TacticalObjective::CoverEngagement,1,1);C.CoverOwner=C.Assignment.Token;
    C.CoverStarted=1;C.SetCoverPhase(CombatAI::CoverPhase::ToAnchor,1,"fixture selected valid plan");
}
void LifecycleTests(){
    using P=CombatAI::CoverPhase;
    UEnemyCombatComponent C;StartPlan(C);const auto Owner=C.CoverOwner;
    Tick(C,1);Check(C.CoverPhase==P::Protected&&C.Pawn.bCrouchCommand,"actual crouched anchor enters protection");
    Tick(C,1.2);Check(C.CoverPhase==P::Exposing&&!C.Pawn.bCrouchCommand&&C.CoverOwner==Owner,"own occlusion preserves cover ownership and requests real stand");
    Tick(C,1.4);Check(C.TestWorld.Launches==0&&C.CoverPhase==P::Exposing,"unachieved stand cannot fire");
    C.Pawn.ActualCrouch=false;C.FreshSight=true;C.Pawn.Body->Location=C.Feet()+FVector(0,0,130);C.Pawn.Rifle->Location=C.Pawn.Body->Location;
    Tick(C,1.5);Check(C.TestWorld.Launches==1&&C.CoverPhase==P::Firing,"achieved stand and fresh sight launches first eligible fixture request");
    Tick(C,1.6);Check(C.TestWorld.Launches==1,"cadence retained during exposure");
    Tick(C,1.7);Tick(C,1.9);Check(C.TestWorld.Launches==3&&C.CoverPhase==P::Returning&&C.Pawn.bCrouchCommand,"finite burst commands crouched return");
    C.Pawn.ActualCrouch=true;C.FreshSight=false;Tick(C,2.0);
    Check(C.CoverPhase==P::Protected&&C.CoverOwner==Owner&&C.TestWorld.Launches==3,"duck sight loss retains completed cover cycle");
    Tick(C,2.1);Check(C.CoverPhase==P::Protected,"burst rest is not removed by hidden reacquisition");
    Tick(C,2.4);Check(C.CoverPhase==P::Exposing,"repeat exposure after world-clock pause");
    C.Pawn.ActualCrouch=false;Tick(C,2.5);Tick(C,3.1);
    Check(C.CoverPhase==P::Returning&&C.TestWorld.Launches==3,"no fresh contact causes bounded return without blind shot");
    UEnemyCombatComponent Refused;StartPlan(Refused);Tick(Refused,1);Tick(Refused,1.2);Tick(Refused,4.3);
    Check(Refused.CoverPhase==P::Returning&&Refused.TestWorld.Launches==0,"stand refusal has finite deadline");
    UEnemyCombatComponent Move;StartPlan(Move,CombatAI::CoverSide::Right);Tick(Move,1);Tick(Move,1.2);
    Check(Move.FollowCalls>0&&Move.MovementPurpose==CombatAI::MovePurpose::Cover&&Move.Pawn.bCrouchCommand,"lateral exposure submits crouched movement through existing navigator");
    Move.ActualFeet=Move.CoverPlan.Pose;Tick(Move,1.3);Check(!Move.Pawn.bCrouchCommand&&Move.TestWorld.Launches==0,"arrived lateral pose still requires achieved stand");
    Move.FreshSight=false;Move.Pawn.ActualCrouch=false;Tick(Move,1.4);Tick(Move,2);
    Move.FollowSucceeds=false;Move.Pawn.ActualCrouch=true;Tick(Move,2.1);
    Check(Move.CoverPhase==P::None&&Move.Path.IsEmpty(),"invalid return stops at actual feet and discards plan");
    UEnemyCombatComponent Physics;StartPlan(Physics);Physics.ObstructedSince=.5;auto Token=Physics.CoverOwner;Physics.Pawn.Authority=EGASPEnemyAuthority::Recovery;Tick(Physics,1.2);
    Check(Physics.CoverPhase==P::None&&!Physics.Assignment.Accepts(Token)&&!Physics.Pawn.bCrouchCommand,"physical interruption clears ownership burst and pose requests");
    Physics.ActualFeet={-200,50,0};Physics.Pawn.Authority=EGASPEnemyAuthority::Locomotion;Tick(Physics,1.5);
    Check(Physics.ScanOrigin==Physics.Feet()&&!Physics.Assignment.Accepts(Token)&&Physics.ObstructedSince<0,"recovery rebuilds from actual displaced feet without obsolete obstruction");
    UEnemyCombatComponent Lost;StartPlan(Lost);Lost.Pawn.Held=false;Tick(Lost,1.2);
    Check(Lost.CoverPhase==P::None&&Lost.BurstRemaining==0&&!Lost.Pawn.bCrouchCommand,"weapon loss clears cover requests before any movement");
    UEnemyCombatComponent Reset;StartPlan(Reset);auto Old=Reset.CoverOwner;Reset.SetEnabled(false);
    Check(Reset.CoverPhase==P::None&&!Reset.Assignment.Accepts(Old)&&!Reset.Pawn.bCrouchCommand,"disable invalidates same-generation cover ownership");
}
void PolicyTests(){
    UEnemyCombatComponent C;C.FreshGround={4000,0,0};SeedSight(C);C.NextCoverScan=100;
    Tick(C,1);Tick(C,1.11);
    Check(C.TestWorld.Launches==1&&C.FollowCalls==0,"visible in-range rifle fires by .11 world seconds without advance");
    C.Pawn.RifleData.Anim.RifleAlpha=0; // Body animation is the actual producer.
    C.Pawn.BodyData.Anim.RifleAimAlpha=0;Tick(C,1.4);Check(C.TestWorld.Launches==1,"animation readiness remains a launch veto");
    for(int I=0;I<100;++I)Tick(C,1.4);
    Check(C.TestWorld.Launches==1,"no wall-clock or frame-count repayment while world clock is unchanged");
    UEnemyCombatComponent Blocked;SeedSight(Blocked);Blocked.NextCoverScan=100;
    Blocked.TestWorld.Box({100,-50,0},{140,50,300});Tick(Blocked,1);Tick(Blocked,1.11);
    Check(Blocked.RangeIntent==CombatAI::RangeIntent::SeekLane&&Blocked.FollowCalls==0&&Blocked.TestWorld.Launches==0,"blocked muzzle does not request pursuit to target feet");
    UEnemyCombatComponent Far;Far.FreshGround={6500,0,0};SeedSight(Far);Far.NextCoverScan=100;Tick(Far,1);Tick(Far,1.11);
    Check(Far.SearchGoal.X==450&&Far.MovementPurpose==CombatAI::MovePurpose::Cautious&&Far.bRequestedWalk,"out-of-range engagement requests one bounded walking step");
    UEnemyCombatComponent Hidden;StartPlan(Hidden);Hidden.FreshSight=false;Hidden.FreshGround={-9000,2000,0};const auto Threat=Hidden.CoverThreatGround;
    Tick(Hidden,1);Tick(Hidden,1.2);Check(Hidden.CoverThreatGround==Threat&&Hidden.LastKnownGround==Threat,"hidden target relocation cannot alter proposal or aim evidence");
    Hidden.Memory.LastSeen=-10;Tick(Hidden,1.3);Check(Hidden.CoverPhase==CombatAI::CoverPhase::None,"stale plan expires at already achieved protected feet");
    UEnemyCombatComponent Shift;StartPlan(Shift);Shift.FreshSight=true;Shift.FreshGround={1000,600,0};Tick(Shift,1.2);
    Check(Shift.CoverPhase==CombatAI::CoverPhase::None,"new observed threat displacement invalidates plan at protected feet");
    UEnemyCombatComponent Small;StartPlan(Small);Small.bTargetVisible=true;Small.LastKnownGround={1000,100,0};Small.LastKnownAim={1000,100,130};Small.CoverValidateAt=5;
    Check(Small.RefreshCoverThreat(1.1)&&Small.CoverThreatGround==Small.LastKnownGround&&Small.CoverValidateAt==0,"small observed movement refreshes threat geometry and forces revalidation");
    Small.bTargetVisible=false;Small.LastKnownGround={1000,120,0};Small.RefreshCoverThreat(1.2);
    Check(Small.CoverThreatGround.Y==100,"failed sight cannot refine active cover geometry");
}
void SearchRegression(){
    UEnemyCombatComponent C;C.Pawn.ActualCrouch=true;C.TestWorld.Box({100,-70,0},{140,70,300});
    CombatAI::ActionToken Assignment;int AssignmentChanges=0,Completed=0,Events=0;
    for(int I=0;I<400;++I){
        double Now=1+I*.02;C.TestWorld.Now=Now;
        if(I%20==0){CombatAI::StimulusData S;S.Id=static_cast<uint64>(++Events);S.Generation=9;S.Kind=CombatAI::Sense::Step;
            S.Category=CombatAI::SourceTeam::Player;S.OccurredWorld=S.ReceivedWorld=Now;S.Confidence=.65;S.Uncertainty=200;S.Region={800.0+(I%4)*20,500,0};C.ReceiveStimulus(CombatAI::Stimulus(S));}
        bool WasScanning=C.bTacticalScan;Tick(C,Now);
        if(WasScanning&&!C.bTacticalScan)++Completed;
        if(Assignment!=C.Assignment.Token){Assignment=C.Assignment.Token;++AssignmentChanges;}
    }
    Check(Events==20&&C.Knowledge.Revision==20&&Completed>0,"affected geometry scan still completes during repeated sound evidence");
    Check(AssignmentChanges==1&&C.IntentEvidenceId==20,"repeated sound updates preserve search assignment and progress");
}
int main(){ContextTests();GeometryTests();LifecycleTests();PolicyTests();SelectionAndGateTests();SearchRegression();std::cout<<"assertions="<<Checks<<" failures="<<Failures<<'\n';return Failures?1:0;}
