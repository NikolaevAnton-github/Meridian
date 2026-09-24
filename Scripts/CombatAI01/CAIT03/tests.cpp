int Checks=0,Failures=0;
void Check(bool Pass,const char* Name){++Checks;if(!Pass){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
void Tick(UEnemyCombatComponent& C,double Now){C.TestWorld.Now=Now;C.AdvanceCombat(.01f);}
void Contact(UEnemyCombatComponent& C){
    C.FreshSight=true;C.RefreshTacticalContext(1);C.ObservePlayer();C.Gates={};C.NextSight=100;
    C.NextCoverScan=100;C.State=EEnemyCombatState::Aim;C.Shots=1;
    C.Assignment.Assign(9,CombatAI::TacticalObjective::Engage,1,1);
}
void Tall(UEnemyCombatComponent& C){
    C.ActualFeet={40,0,0};C.Home=C.ActualFeet;C.ScanOrigin=C.ActualFeet;
    C.TestWorld.Box({100,-70,0},{140,70,300});
    C.CoverThreatGround=C.LastKnownGround=C.FreshGround={1000,0,0};
    C.CoverThreatAim=C.LastKnownAim={1000,0,165};C.Memory.Observe(1);C.RefreshTacticalContext(1);
    C.Assignment.Assign(9,CombatAI::TacticalObjective::Engage,1,1);
}
void InstallLean(UEnemyCombatComponent& C,CombatAI::CoverSide Side){
    Tall(C);auto P=C.AssessTacticalPosition(C.Feet(),C.Feet(),false,true);C.AssessCoverOptions(P);
    C.CoverPlan=P.CoverOptions[Side==CombatAI::CoverSide::Left?0:1];
    C.ActualFeet=C.CoverPlan.Anchor;C.CoverStarted=1;
    C.Assignment.Assign(9,CombatAI::TacticalObjective::CoverEngagement,1,1);C.CoverOwner=C.Assignment.Token;
    C.SetCoverPhase(CombatAI::CoverPhase::Protected,1,"source fixture protected anchor");
    auto& B=C.Pawn.BodyData;B.Named=true;B.Pivot=C.Feet()+FVector(0,0,95);B.Head=C.Feet()+FVector(0,0,170);
    B.Torso=C.Feet()+FVector(0,0,140);B.Hand=C.Feet()+FVector(15,12,145);
    C.Pawn.RifleData.Location=C.Feet()+FVector(75,12,145);C.Pawn.RifleData.Right={1,0,0};
}
void AcknowledgeLean(UEnemyCombatComponent& C){
    // Explicit socket boundary, not an engine pose simulation. These positions
    // stand for a completed evaluation; graph/native math are verified separately.
    auto& B=C.Pawn.BodyData;const FQuat Q(C.LeanAxis,FMath::DegreesToRadians(-C.LeanSign()*C.Tuning.CoverLeanDegrees));
    B.Head=C.LeanPivot+Q.RotateVector(C.LeanNeutral[0]-C.LeanPivot);
    B.Torso=C.LeanPivot+Q.RotateVector(C.LeanNeutral[1]-C.LeanPivot);
    B.Hand=C.LeanPivot+Q.RotateVector(C.LeanNeutral[2]-C.LeanPivot);
    C.Pawn.RifleData.Location=C.LeanPivot+Q.RotateVector(C.LeanNeutral[3]-C.LeanPivot);
    B.Anim.RifleLeanDegrees=C.LeanSign()*C.Tuning.CoverLeanDegrees;
}
void MobileTests(){
    UEnemyCombatComponent C;Contact(C);Tick(C,1.1);
    Check(C.MobilePhase==CombatAI::MobilePhase::Strafe&&!C.Pawn.MovementCommand.IsNearlyZero(),"production engagement starts deliberate strafe through real route consumer");
    Check(C.State==EEnemyCombatState::Burst&&C.TestWorld.Launches==1,"aim and launch coexist with production movement");
    const auto Move=C.PathRequest;const auto Burst=C.Action.Token;
    C.Pawn.Data.Mover.Velocity={0,-175,0};Tick(C,1.29);
    Check(C.MoveAction.Accepts(Move)&&C.PathRequest==Move&&C.Action.Token==Burst&&C.TestWorld.Launches==2,"moving second shot retains both request owners");
    Check(!C.Pawn.MovementCommand.IsNearlyZero()&&C.Spread.LastCone>FMath::DegreesToRadians(1.8),"achieved walking adds accuracy cost without stopping movement");
    Tick(C,1.48);Check(C.TestWorld.Launches==3&&C.State==EEnemyCombatState::Aim&&C.MoveAction.Accepts(Move),"burst completion cannot cancel movement");
    Tick(C,1.6);Check(C.TestWorld.Launches==3&&!C.Pawn.MovementCommand.IsNearlyZero(),"finite burst rest leaves moving aim active");
    C.ActualFeet=C.MobileGoal;Tick(C,1.7);
    Check(C.MobilePhase==CombatAI::MobilePhase::Cooldown&&C.NextMobileAt>4.8&&C.Pawn.MovementCommand.IsNearlyZero(),"arrival ends one step and imposes world-time movement rest");
    Tick(C,1.94);Check(C.TestWorld.Launches==4&&C.MobilePhase==CombatAI::MobilePhase::Cooldown,"stationary cooldown still permits next finite burst");
    UEnemyCombatComponent Approach;Contact(Approach);Approach.FreshGround={5600,0,0};Approach.ObservePlayer();Tick(Approach,1.1);
    Check(Approach.MobilePhase==CombatAI::MobilePhase::Approach&&Approach.MobileGoal.X==450&&Approach.TestWorld.Launches==0,"out-of-range policy requests bounded 450cm approach");
    Approach.ActualFeet={200,0,0};Approach.Pawn.Data.Mover.Velocity={175,0,0};Tick(Approach,1.3);
    Check(Approach.TestWorld.Launches==1&&Approach.MoveAction.Accepts(Approach.PathRequest)&&!Approach.Pawn.MovementCommand.IsNearlyZero(),"approach fires upon entering range without compulsory stop");
    UEnemyCombatComponent Block;Contact(Block);Block.TestWorld.Box({-100,-300,0},{100,-70,300});Block.TestWorld.Box({-100,70,0},{100,300,300});Tick(Block,1.1);
    Check(Block.MobilePhase==CombatAI::MobilePhase::Cooldown&&Block.TestWorld.Launches==1,"blocked strafe routes choose bounded hold and preserve direct fire");
    UEnemyCombatComponent Stale;Contact(Stale);Tick(Stale,1.1);auto Old=Stale.PathRequest;Stale.MoveAction.Reset(9);Tick(Stale,1.2);
    Check(!Stale.MoveAction.Accepts(Old)&&Stale.Pawn.MovementCommand.IsNearlyZero(),"obsolete movement request cannot keep submitting locomotion");
    UEnemyCombatComponent Tight;Contact(Tight);Tight.ActualFeet={0,0,0};Tight.Path={{16,0,0}};Tight.PathGoal={16,0,0};Tight.PathRequest=Tight.EnsureMoveAction(1);Tight.LastProgress=1;
    Tight.FollowPath({16,0,0},12,1.1,CombatAI::MovePurpose::Cover);
    Check(!Tight.Pawn.MovementCommand.IsNearlyZero(),"lean 12cm acceptance is not stranded by 18cm waypoint skip");
}
void FireTests(){
    UEnemyCombatComponent C;Contact(C);C.BurstRemaining=3;auto Token=C.EnsureAction(CombatAI::ActionKind::Burst,1);
    C.Pawn.Data.Mover.Velocity={220,0,0};Check(C.Fire(1.1,Token),"220cm/s achieved grounded walking launches");
    C.Pawn.Data.Mover.Velocity={220.01,0,0};Check(!C.Fire(1.4,Token),"above speed envelope rejects birth");
    C.Pawn.Data.Mover.Velocity={175,0,0};C.Pawn.bWalkCommand=false;Check(!C.Fire(1.4,Token),"running command outside supported gait rejects moving birth");
    C.Pawn.bWalkCommand=true;C.Pawn.Data.Mover.Grounded=false;Check(!C.Fire(1.4,Token),"airborne achieved motion rejects birth");
    C.Pawn.Data.Mover.Grounded=true;C.Pawn.Data.Mover.Velocity.Z=46;Check(!C.Fire(1.4,Token),"unsupported vertical speed rejects birth");
    C.Pawn.Data.Mover.Velocity.Z=0;C.Pawn.bCrouchCommand=true;Check(!C.Fire(1.4,Token),"stance transition safety survives mobile fire");
    C.Pawn.bCrouchCommand=false;C.FreshSight=false;Check(!C.Fire(1.4,Token)&&C.Magazine==11,"fresh sight veto preserves ammunition");
    C.FreshSight=true;C.Pawn.BodyData.Location={0,0,140};C.Pawn.RifleData.Location={80,0,140};C.TestWorld.Box({30,-20,110},{40,20,165});
    Check(!C.Fire(1.4,Token),"near cover between torso and barrel rejects clipped origin");
    C.TestWorld.Boxes.clear();C.Pawn.RifleData.Right={0,1,0};Check(!C.Fire(1.4,Token),"actual barrel alignment retained");
    C.Pawn.RifleData.Right={1,0,0};C.Gates.ReloadUntil=2;Check(!C.Fire(1.4,Token),"reload deadline gates every mobile launch");
    C.Gates={};C.ClearIntent(CombatAI::ActionFailure::Authority);Check(!C.Fire(1.5,Token),"physical cancellation rejects stale burst");
}
void LeanTests(){
    using Side=CombatAI::CoverSide;using Phase=CombatAI::CoverPhase;
    UEnemyCombatComponent G;Tall(G);auto P=G.AssessTacticalPosition(G.Feet(),G.Feet(),false,true);G.AssessCoverOptions(P);
    Check(P.CoverOptions[0].Score>-1e9&&P.CoverOptions[1].Score>-1e9,"static geometry yields independent left and right torso-lean anchors");
    Check(P.CoverOptions[0].Anchor==P.CoverOptions[0].Pose&&P.CoverOptions[1].Anchor==P.CoverOptions[1].Pose,"lean exposure keeps the same feet on both sides");
    G.TestWorld.Box({0,-650,0},{90,-80,300});G.AssessCoverOptions(P);
    Check(P.CoverOptions[0].Score<=-1e9&&P.CoverOptions[1].Score>-1e9,"blocked left body space preserves independently clear right");
    UEnemyCombatComponent R;Tall(R);R.TestWorld.Box({0,80,0},{90,650,300});auto RP=R.AssessTacticalPosition(R.Feet(),R.Feet(),false,true);R.AssessCoverOptions(RP);
    Check(RP.CoverOptions[0].Score>-1e9&&RP.CoverOptions[1].Score<=-1e9,"blocked right body space preserves independently clear left");
    for(auto SideValue:{Side::Left,Side::Right}){
        UEnemyCombatComponent C;InstallLean(C,SideValue);C.TestWorld.Now=1.2;C.AdvanceCover(1.2);
        Check(C.CoverPhase==Phase::Exposing&&C.bLeanPoseCaptured&&C.Pawn.RifleLeanTarget*C.LeanSign()>0,"achieved neutral pose requests signed lean after arc validation");
        Check(!C.AchievedLeanClear(),"requested lean alone cannot authorize exposure");
        C.Pawn.BodyData.Anim.RifleLeanDegrees=C.Pawn.RifleLeanTarget;
        Check(!C.AchievedLeanClear(),"float without actual socket displacement is refused");
        AcknowledgeLean(C);Check(C.AchievedLeanClear(),"signed achieved head and chest plus actual rifle clearance accepted");
        C.TestWorld.Now=1.4;C.AdvanceCover(1.4);Check(C.CoverPhase==Phase::Aiming&&C.TestWorld.Launches==0,"achieved lean without fresh contact does not fire");
        C.TestWorld.Now=1.9;C.AdvanceCover(1.9);Check(C.CoverPhase==Phase::Returning&&C.BurstRemaining==0&&C.Pawn.RifleLeanTarget==0,"no-contact exposure returns within bounded deadline");
        C.TestWorld.Now=2;C.AdvanceCover(2);Check(C.CoverPhase==Phase::Returning&&C.Pawn.MovementCommand.IsNearlyZero(),"return blend owns feet until completed");
        C.Pawn.BodyData.Anim.RifleLeanDegrees=0;C.TestWorld.Now=2.2;C.AdvanceCover(2.2);
        Check(C.CoverPhase==Phase::Returning,"zero float without returned head/chest keeps return ownership");
        C.Pawn.BodyData.Head=C.LeanNeutral[0];C.Pawn.BodyData.Torso=C.LeanNeutral[1];C.Pawn.BodyData.Hand=C.LeanNeutral[2];C.Pawn.RifleData.Location=C.LeanNeutral[3];
        C.TestWorld.Now=2.3;C.AdvanceCover(2.3);
        Check(C.CoverPhase==Phase::None&&!C.bLeanPoseCaptured,"completed failed exposure clears lean owner and captured pose");
    }
    UEnemyCombatComponent Refuse;InstallLean(Refuse,Side::Right);Refuse.TestWorld.Now=1.2;Refuse.AdvanceCover(1.2);Refuse.TestWorld.Now=3.3;Refuse.AdvanceCover(3.3);
    Check(Refuse.CoverPhase==Phase::Returning&&Refuse.bEndCoverAfterReturn,"unachieved lean terminates under deadline");
    UEnemyCombatComponent Shot;InstallLean(Shot,Side::Right);Shot.TestWorld.Now=1.2;Shot.AdvanceCover(1.2);AcknowledgeLean(Shot);Shot.FreshSight=true;
    Shot.Pawn.RifleData.Right=(Shot.FreshGround+FVector(0,0,130)-Shot.Pawn.RifleData.Location).GetSafeNormal();
    Shot.TestWorld.Now=1.4;Shot.AdvanceCover(1.4);Shot.TestWorld.Now=1.6;Shot.AdvanceCover(1.6);
    Check(Shot.TestWorld.Launches==2&&Shot.CoverPhase==Phase::Firing,"actual lean/current sight producer reaches real launch consumer");
    const auto* Manager=ACombatProjectileWorld::Find(Shot.GetWorld());Check(Manager->LastPosition==Shot.Pawn.RifleData.Location,"projectile birth uses achieved visible muzzle");
    Shot.TestWorld.Box(Shot.Pawn.BodyData.Head-FVector(5),Shot.Pawn.BodyData.Head+FVector(5));Shot.TestWorld.Now=1.8;Shot.AdvanceCover(1.8);
    Check(Shot.TestWorld.Launches==2&&Shot.CoverPhase==Phase::Returning,"new actual head obstruction cancels firing and returns");
    UEnemyCombatComponent Low;Tall(Low);Low.TestWorld.Boxes[0].Bounds.Box.Max.Z=112;
    auto Up=Low.AssessCoverOption(Low.Feet(),Low.Feet(),Side::Up);Check(Up.Score>-1e9,"existing low-cover stand lane remains selectable");
    Low.CoverPlan=Up;Low.CoverStarted=1;Low.CoverOwner=Low.Assignment.Token;Low.Pawn.ActualCrouch=true;Low.SetCoverPhase(Phase::ToAnchor,1,"low-cover fixture");Low.AdvanceCover(1);
    Low.TestWorld.Now=1.2;Low.AdvanceCover(1.2);Check(Low.CoverPhase==Phase::Exposing&&!Low.Pawn.bCrouchCommand&&Low.Pawn.RifleLeanTarget==0,"low cover requests stand without lean ownership");
}
void CancelTests(){
    using Side=CombatAI::CoverSide;
    for(int Kind=0;Kind<5;++Kind){
        UEnemyCombatComponent C;InstallLean(C,Side::Right);C.TestWorld.Now=1.2;C.AdvanceCover(1.2);AcknowledgeLean(C);
        C.PathRequest=C.EnsureMoveAction(1.2);C.BurstRemaining=3;const auto Burst=C.EnsureAction(CombatAI::ActionKind::Burst,1.2);const auto Owner=C.CoverOwner;
        if(Kind==0)C.SuspendForPhysics(false);if(Kind==1)C.SuspendForPhysics(true);if(Kind==2)C.SetEnabled(false);
        if(Kind==3){C.Pawn.Held=false;Tick(C,1.3);}if(Kind==4)C.ResetCombat(C.Feet(),FRotator::ZeroRotator);
        Check(!C.Action.Accepts(Burst)&&!C.MoveAction.Accepts(C.PathRequest)&&!C.Assignment.Accepts(Owner)&&C.CoverPhase==CombatAI::CoverPhase::None&&C.BurstRemaining==0&&C.Pawn.RifleLeanTarget==0&&C.Pawn.BodyData.Anim.RifleLeanDegrees==0,"interrupt/death/disable/loss/reset clears both action lanes and stale lean offsets");
    }
    UEnemyCombatComponent C;Contact(C);Tick(C,1.1);C.SuspendForPhysics(false);C.ActualFeet={-250,300,0};C.FreshSight=false;Tick(C,1.5);
    Check(C.State==EEnemyCombatState::Search&&C.Path.IsEmpty()&&C.ScanOrigin==C.Feet(),"recovery replans from actual feet instead of old mobile goal");
}
void BlendTests(){
    AGASPEnemyFixture E;
    for(float Sign:{-1.f,1.f}){
        E.RifleLeanTarget=32*Sign;
        const float First=UpdateLean(0,&E,.05f),Slow=UpdateLean(0,&E,.0125f);
        Check(std::abs(First-6*Sign)<.001&&std::abs(Slow-1.5*Sign)<.001,"native lean consumer and installed interpolator use signed world-delta blend");
        Check(UpdateLean(First,&E,1)==32*Sign,"bounded lean blend reaches target without overshoot");
        E.RifleLeanTarget=0;Check(std::abs(UpdateLean(32*Sign,&E,.05f)-26*Sign)<.001,"native return blend is gradual and symmetric");
    }
    E.RifleLeanTarget=32;E.Data.Mover.Grounded=false;Check(UpdateLean(12,&E,.05f)==6,"ground loss blends voluntary lean out");
    E.Data.Mover.Grounded=true;E.Authority=EGASPEnemyAuthority::Recovery;Check(UpdateLean(32,&E,.001f)==0,"physical authority clears animation offset immediately");
    E.Authority=EGASPEnemyAuthority::Locomotion;E.Held=false;Check(UpdateLean(-32,&E,.001f)==0,"weapon loss clears animation offset immediately");
}
int main(){MobileTests();FireTests();LeanTests();CancelTests();BlendTests();std::cout<<Checks<<" checks, "<<Failures<<" failures\n";return Failures?1:0;}
