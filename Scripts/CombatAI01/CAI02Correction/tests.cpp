int Checks=0,Failures=0;
void Check(bool Pass,const char* Name){++Checks;if(!Pass){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
CombatAI::Stimulus Step(uint64 Id,double Now,double X){
    CombatAI::StimulusData S;S.Id=Id;S.Generation=9;S.Kind=CombatAI::Sense::Step;
    S.Category=CombatAI::SourceTeam::Player;S.OccurredWorld=S.ReceivedWorld=Now;
    S.Region={X,500,0};S.Confidence=.65;S.Uncertainty=200;return CombatAI::Stimulus(S);
}
void SearchTick(UEnemyCombatComponent& C,double Now){
    C.World.Now=Now;C.ApplyEvidenceIntent(Now);C.AdvanceSearch(Now);
}
void RepeatedSounds(int Hz){
    UEnemyCombatComponent C;C.Pawn.ActualCrouch=true;
    int Events=0,Completions=0,AssignmentChanges=0,MaxEvaluated=0;
    double FirstCompletion=-1,FirstScan=-1;
    CombatAI::ActionToken Assignment;
    for(int I=0;I<8*Hz;++I){
        const double Now=1+double(I)/Hz;C.World.Now=Now;
        if(I%(Hz*2/5)==0){
            const int Phase=Events%16;const double X=-800+200*(Phase<=8?Phase:16-Phase);
            C.ReceiveStimulus(Step(static_cast<uint64>(++Events),Now,X));
        }
        const bool Scanning=C.bTacticalScan;
        SearchTick(C,Now);
        if(C.Assignment.Token!=Assignment){++AssignmentChanges;Assignment=C.Assignment.Token;}
        if(FirstScan<0&&C.bTacticalScan)FirstScan=C.ScanStartedAt;
        if(Scanning&&!C.bTacticalScan){++Completions;if(FirstCompletion<0)FirstCompletion=Now;}
        MaxEvaluated=std::max(MaxEvaluated,C.CandidateIndex);
    }
    Check(Events==20&&C.Knowledge.Revision==20,"R1 accepts the review's 20 fresh steps over eight world seconds");
    Check(Completions>0&&MaxEvaluated>8,"R1 selects during the sound stream without waiting for silence");
    Check(FirstCompletion-FirstScan<=4+1.0/Hz+.0001,"R1 finite original scan deadline plus one decision tick");
    Check(AssignmentChanges==1,"R1 compatible updates preserve the investigation token");
    Check(C.Assignment.EvidenceId==20&&C.IntentEvidenceId==20,"R1 assignment retains latest permitted evidence identity");
    Check(C.Pawn.AimCalls>=20,"R1 fresh regional evidence retains prompt attention");
    std::cout<<"repeated_sound hz="<<Hz<<" events="<<Events<<" selections="<<Completions
        <<" evaluated="<<MaxEvaluated<<" first_decision_world_seconds="<<FirstCompletion-FirstScan
        <<" assignment_changes="<<AssignmentChanges<<'\n';
}
void PrepareProposal(UEnemyCombatComponent& C){
    C.Pawn.ActualCrouch=true;C.World.ProtectDestination=true;
    C.ReceiveStimulus(Step(1,1,500));C.ApplyEvidenceIntent(1);
    C.Transfers.Refresh(1);C.ScanOrigin=C.Feet();C.ScanRequest=C.Assignment.Token;
    C.TacticalCandidates.Add(C.AssessTacticalPosition({300,0,0},C.Feet(),true,true));C.CandidateIndex=1;
}
void SelectMove(UEnemyCombatComponent& C){
    PrepareProposal(C);C.ChooseTacticalPosition(1);
    Check(C.bSelectedPosition&&C.Action.Kind==CombatAI::ActionKind::Move&&!C.Path.IsEmpty(),"fixture selects a genuinely safer checked destination");
}
void MovementAndCancellation(){
    UEnemyCombatComponent C;SelectMove(C);
    const auto Token=C.Action.Token,Assignment=C.Assignment.Token;
    const auto Path=C.Path;const double Started=C.TacticalMoveStartedAt;
    C.World.Now=1.4;C.ReceiveStimulus(Step(2,1.4,700));C.ApplyEvidenceIntent(1.4);
    Check(C.Action.Token==Token&&C.Assignment.Token==Assignment&&C.Path==Path,"R1 moving sound update preserves action and route");
    Check(C.SearchAnchor.X==700&&C.Pawn.Aim==C.LastKnownAim&&C.NextSight<=1.45,"R1 moving attention uses the fresh captured region");
    C.AdvanceSearch(1.4);
    Check(C.bSelectedPosition&&C.SelectedPosition.EvidenceId==2&&C.FollowCalls==1,"R1 safe destination revalidated before continuing movement");
    Check(C.Pawn.Follow&&C.Pawn.Aim==C.LastKnownAim,"R1 movement keeps the short sound attention window");
    Check(C.Transfers.Attempts==1&&C.TacticalMoveStartedAt==Started,"R1 retarget does not renew transfer or travel deadline");
    C.World.Now=1.8;C.ReceiveStimulus(Step(3,1.8,900));C.ApplyEvidenceIntent(1.8);C.World.FailDestination=true;
    C.AdvanceSearch(1.8);
    Check(!C.bSelectedPosition&&C.Path.IsEmpty()&&C.FollowCalls==1,"R1 unsafe updated destination cancels before movement");
    Check(C.RejectedPositions.Contains(300,0,1.8)&&C.Transfers.Attempts==1,"R1 safety cancellation retains rejection and transfer history");
    Check(!C.Action.Accepts(Token),"R1 rejected movement token cannot complete");

    UEnemyCombatComponent Stale;PrepareProposal(Stale);
    Stale.World.Now=1.4;Stale.ReceiveStimulus(Step(2,1.4,-700));Stale.ApplyEvidenceIntent(1.4);
    Stale.World.FailDestination=true;Stale.ChooseTacticalPosition(1.4);
    Check(!Stale.bSelectedPosition&&Stale.Path.IsEmpty()&&Stale.Transfers.Attempts==0,"R1 cached scan winner cannot authorize stale unsafe travel");

    UEnemyCombatComponent P;SelectMove(P);const auto OldToken=P.Action.Token,OldAssignment=P.Assignment.Token;
    P.Pawn.Authority=EGASPEnemyAuthority::Physics;P.World.Now=2;P.AdvanceCombat(.1f);
    Check(P.State==EEnemyCombatState::Recovery&&!P.bTacticalScan&&!P.bSelectedPosition&&P.Path.IsEmpty(),"R1 physical authority cancels scan and movement");
    Check(!P.Action.Accepts(OldToken)&&!P.Assignment.Accepts(OldAssignment)&&P.Knowledge.Revision==1,"R1 physical cancellation rejects old work but retains living evidence");
    P.World.Now=2.4;P.ReceiveStimulus(Step(2,2.4,-600));P.AdvanceCombat(.1f);
    Check(P.Knowledge.Revision==2&&P.bEvidencePending&&P.FollowCalls==0,"R1 recovery can receive memory without movement");
    P.ActualFeet={-80,50,0};P.Pawn.Authority=EGASPEnemyAuthority::Locomotion;P.World.Now=2.5;P.AdvanceCombat(.1f);
    Check(P.State==EEnemyCombatState::Search&&P.ScanOrigin==P.ActualFeet&&!P.Action.Accepts(OldToken),"R1 recovery replans at actual feet with a fresh action");
    P.SetEnabled(false);
    Check(P.Path.IsEmpty()&&!P.bTacticalScan&&!P.bSelectedPosition&&P.Knowledge.Revision==0,"affected reset clears correction state and evidence");

    UEnemyCombatComponent D;D.ReceiveStimulus(Step(1,1,200));D.State=EEnemyCombatState::Reload;
    D.Gates.ReloadUntil=5;D.ApplyEvidenceIntent(1);
    Check(D.bEvidencePending&&D.Gates.ReloadUntil==5&&D.IntentEvidenceId==0,"R1 sound cannot cancel an unpaid reload deadline");
    D.State=EEnemyCombatState::Search;D.bTargetVisible=true;D.ApplyEvidenceIntent(1);
    Check(D.bEvidencePending&&D.IntentEvidenceId==0,"R1 current sight retains precedence over sound");
}
void StanceGeometry(){
    UEnemyCombatComponent S,C;S.SearchAnchor=C.SearchAnchor={600,0,0};S.SearchForward=C.SearchForward={1,0,0};
    C.Pawn.ActualCrouch=true;S.World.MidHeightLedge=C.World.MidHeightLedge=true;
    auto Stand=S.AssessTacticalPosition({}, {},false,false);
    auto Crouch=C.AssessTacticalPosition({}, {},false,true);
    Check(S.World.Queries!=C.World.Queries,"R2 standing and crouching no longer query identical segments");
    Check(!(Stand.Features.WeaponMask&1)&&(Crouch.Features.WeaponMask&1),"R2 review 120-140 cm ledge blocks standing weapon but clears crouch");
    std::cout<<"review_ledge standing_front_clear="<<bool(Stand.Features.WeaponMask&1)
        <<" crouched_front_clear="<<bool(Crouch.Features.WeaponMask&1)<<'\n';
    S.World.MidHeightLedge=C.World.MidHeightLedge=false;
    S.World.LowWeaponLedge=C.World.LowWeaponLedge=true;
    Stand=S.AssessTacticalPosition({}, {},false,false);Crouch=C.AssessTacticalPosition({}, {},false,true);
    Check((Stand.Features.WeaponMask&1)&&!(Crouch.Features.WeaponMask&1),"R2 reverse low obstacle cannot borrow standing weapon clearance");
    S.World.LowWeaponLedge=C.World.LowWeaponLedge=false;S.World.LowScreen=C.World.LowScreen=true;
    S.World.ScreenTop=C.World.ScreenTop=80;
    Stand=S.AssessTacticalPosition({}, {},false,false);Crouch=C.AssessTacticalPosition({}, {},false,true);
    Check(Stand.Features.OpenDistance[0]>=220&&Crouch.Features.OpenDistance[0]<220,"R2 body and eye samples use a compatible lower profile");
    S.World.ScreenTop=C.World.ScreenTop=110;
    Stand=S.AssessTacticalPosition({}, {},false,false);Crouch=C.AssessTacticalPosition({}, {},false,true);
    Check((Stand.Features.RegionVisibleMask&2)&&!(Crouch.Features.RegionVisibleMask&2),"R2 exposure origin respects low occlusion without lowering the threat region");
    Check(Crouch.Rating.Exposure<Stand.Rating.Exposure,"R2 height-sensitive exposure changes the assessment");
    bool LowerOrigin=false,ThreatStillAt130=false;
    for(const auto& Q:C.World.Queries)if(Q.From.Z==90&&Q.To.X==600&&Q.To.Y==0){LowerOrigin=true;ThreatStillAt130=Q.To.Z==130;}
    Check(LowerOrigin&&ThreatStillAt130,"R2 own stance does not invent a crouched hidden target");
}
void StanceTransitions(){
    UEnemyCombatComponent C;C.Memory.Alert=C.Memory.HasObservation=true;
    C.SearchAnchor={600,0,0};C.SearchForward={1,0,0};C.World.MidHeightLedge=true;
    C.HoldTacticalPosition(1);Check(!C.HeldPosition.bCrouched&&!(C.HeldPosition.Features.WeaponMask&1),"R2 standing hold uses achieved standing stance");
    C.NextHoldValidation=50;C.NextLookAt=50;C.Pawn.ActualCrouch=true;
    C.HoldTacticalPosition(1.01);
    Check(C.HeldPosition.bCrouched&&(C.HeldPosition.Features.WeaponMask&1)&&C.NextHoldValidation<3,"R2 achieved crouch reassesses the hold before its periodic timer");
    Check(C.SearchLook.Z==100,"R2 observation facing follows achieved crouched eye height");
    C.NextHoldValidation=50;C.Pawn.ActualCrouch=false;C.HoldTacticalPosition(1.02);
    Check(!C.HeldPosition.bCrouched&&!(C.HeldPosition.Features.WeaponMask&1)&&C.SearchLook.Z==150,"R2 returning to standing refreshes hold and facing immediately");

    UEnemyCombatComponent Unachieved;PrepareProposal(Unachieved);Unachieved.Pawn.ActualCrouch=false;
    Unachieved.ChooseTacticalPosition(1);
    Check(!Unachieved.bSelectedPosition&&Unachieved.Path.IsEmpty()&&Unachieved.Transfers.Attempts==0,"R2 unachieved crouch cannot authorize movement");
    Unachieved.AdvanceSearch(1.1);
    Check(Unachieved.Pawn.RequestedCrouch&&!Unachieved.HeldPosition.bCrouched&&Unachieved.FollowCalls==0,"R2 refused crouch retains honestly assessed standing observation");

    UEnemyCombatComponent A;SelectMove(A);A.ActualFeet=A.SearchGoal;A.World.Now=2;A.AdvanceSearch(2);
    Check(!A.bSelectedPosition&&A.bHeldPosition&&A.HeldPosition.bCrouched&&A.TacticalPhase==CombatAI::TacticalPhase::Holding,"R2 arrival accepts actual feet with achieved crouch");
    UEnemyCombatComponent Wrong;SelectMove(Wrong);Wrong.ActualFeet=Wrong.SearchGoal;Wrong.Pawn.ActualCrouch=false;Wrong.World.Now=2;Wrong.AdvanceSearch(2);
    Check(!Wrong.bSelectedPosition&&!Wrong.bHeldPosition&&Wrong.Path.IsEmpty()&&Wrong.FollowCalls==0,"R2 arrival cannot inherit unachieved crouch protection");
    UEnemyCombatComponent Changed;SelectMove(Changed);Changed.Pawn.ActualCrouch=false;Changed.World.Now=1.1;Changed.AdvanceSearch(1.1);
    Check(!Changed.bSelectedPosition&&Changed.FollowCalls==0&&Changed.Path.IsEmpty(),"R2 mid-route stance change cancels before moving");

    for(bool Backoff:{false,true}){
        UEnemyCombatComponent V;SelectMove(V);const auto OldAssignment=V.Assignment.Token;
        V.Pawn.RequestedCrouch=true;V.FreshSight=true;V.World.Now=1.1;
        V.Gates.ContactUntil=9;V.Gates.AimUntil=8;V.Gates.PauseUntil=7;V.NextShot=6;
        if(Backoff)V.WeaponBackoff.Set(V.LastKnownGround.X,V.LastKnownGround.Y,9);
        V.AdvanceCombat(.1f);
        Check(!V.Pawn.RequestedCrouch&&V.Pawn.ActualCrouch,"R2 visible contact requests stand without pretending Mover achieved it");
        Check(!V.bSelectedPosition&&!V.bHeldPosition&&!V.bTacticalScan&&!V.Assignment.Accepts(OldAssignment),"R2 visible contact discards old crouched tactical authorization");
        Check(V.Gates.AimUntil==8&&V.Gates.PauseUntil==7&&V.NextShot==6&&V.FireCalls==0,"R2 standing contact and backoff retain unpaid weapon gates");
        V.Pawn.ActualCrouch=false;V.World.Now=1.2;V.AdvanceCombat(.1f);
        Check(!V.Pawn.RequestedCrouch&&!V.Pawn.ActualCrouch&&V.FireCalls==0,"R2 achieved standing transition respects readiness");
    }
}
int main(){
    RepeatedSounds(120);RepeatedSounds(5);
    MovementAndCancellation();StanceGeometry();StanceTransitions();
    std::cout<<"checks="<<Checks<<" failures="<<Failures<<'\n';return Failures?1:0;
}
