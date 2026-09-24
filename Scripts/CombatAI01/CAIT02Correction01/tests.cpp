// Bounded corrections to the review reproductions; no engine/game execution.
void ConsumeStance(UEnemyCombatComponent& C,bool CanExpand=true,bool CanEnter=true)
{
    C.Pawn.ConsumeRifleStance();
    C.Pawn.Data.Mover.Acknowledge(CanExpand,CanEnter);
}
void SelectSearchRoute(UEnemyCombatComponent& C)
{
    C.ActualFeet={-400,0,0}; C.Home=C.ActualFeet;
    C.TestWorld.Box({100,-70,0},{140,70,300});
    C.LastKnownGround={1000,0,0}; C.LastKnownAim={1000,0,130};
    C.Memory.Observe(1); C.RefreshTacticalContext(1);
    C.BeginSearch("R1: remembered sight and reachable protected column");
    for(int I=0;I<180&&!C.bSelectedPosition;++I)
    {
        C.TestWorld.Now=1+I*.03;
        C.AdvanceSearch(C.TestWorld.Now);
        ConsumeStance(C);
    }
    Check(C.bSelectedPosition&&C.SelectedPosition.bCrouched,"R1 real scan selects crouched transfer");
}
void SearchHandoffs()
{
    UEnemyCombatComponent C; SelectSearchRoute(C);
    Check(C.Pawn.bCrouchCommand&&C.Pawn.Data.Mover.bWantsToCrouch&&C.Pawn.IsMovementCrouched(),
          "R1 selected request survives real stance consumer and clear standing space");
    const auto Rejected=C.TacticalRejected;
    C.TestWorld.Now+=.05; C.AdvanceSearch(C.TestWorld.Now); ConsumeStance(C);
    Check(C.bSelectedPosition&&C.TacticalRejected==Rejected&&C.FollowCalls==1,
          "R1 next decision follows selected route without rejecting its own stance");
    // The retained FollowPath adapter does not consume the crouch-to-walk term;
    // verify the actual command and purpose delivered to that unchanged boundary.
    Check(C.Pawn.bCrouchCommand&&C.MovementPurpose==CombatAI::MovePurpose::Search,"R1 route submits crouched search movement");
    C.ActualFeet=C.SearchGoal; // Explicit achieved-feet boundary, not simulated travel.
    C.TestWorld.Now+=.05; C.AdvanceSearch(C.TestWorld.Now);
    Check(C.bHeldPosition&&!C.bSelectedPosition&&C.HeldPosition.bCrouched&&C.Path.IsEmpty(),
          "R1 actual arrival accepts protected crouched hold and ends route");
    ConsumeStance(C);
    Check(C.Pawn.bCrouchCommand&&C.Pawn.Data.Mover.bWantsToCrouch&&C.Pawn.IsMovementCrouched(),
          "R1 arrival ownership handoff preserves achieved/requested crouch");
    C.TestWorld.Now+=.05; C.AdvanceSearch(C.TestWorld.Now); ConsumeStance(C);
    Check(C.bHeldPosition&&C.TacticalPhase==CombatAI::TacticalPhase::Holding&&C.TacticalRejected==Rejected,
          "R1 following hold decision retains validated protection");
    C.TestWorld.Now+=1.05; C.AdvanceSearch(C.TestWorld.Now); ConsumeStance(C);
    Check(C.bHeldPosition&&C.HeldPosition.bCrouched&&C.Pawn.IsMovementCrouched(),"R1 timed hold revalidation uses achieved crouch");
    std::cout<<"R1 held="<<C.bHeldPosition<<" crouch="<<C.Pawn.IsMovementCrouched()
             <<" requested="<<C.Pawn.bCrouchCommand<<" goal="<<C.SearchGoal.X<<','<<C.SearchGoal.Y<<'\n';

    UEnemyCombatComponent Refused; SelectSearchRoute(Refused);
    Refused.Pawn.ActualCrouch=false; // Engine may refuse/lose achieved stance.
    Refused.TestWorld.Now+=.05; Refused.AdvanceSearch(Refused.TestWorld.Now);
    Check(!Refused.bSelectedPosition&&Refused.Path.IsEmpty()&&!Refused.Pawn.bCrouchCommand,
          "R1 real achieved-stance loss still rejects and cancels the route");
    UEnemyCombatComponent Route; SelectSearchRoute(Route); Route.FollowSucceeds=false;
    Route.TestWorld.Now+=.05; Route.AdvanceSearch(Route.TestWorld.Now); ConsumeStance(Route);
    Check(!Route.bSelectedPosition&&!Route.Pawn.bCrouchCommand&&!Route.Pawn.IsMovementCrouched(),
          "R1 failed route retains cancellation pose cleanup");
}
void CancellationConsumers()
{
    for(int Mode=0;Mode<5;++Mode)
    {
        UEnemyCombatComponent C;
        C.Pawn.bCrouchCommand=true; ConsumeStance(C);
        C.Path={{40,0,0}}; C.BurstRemaining=3;
        C.PathRequest=C.EnsureAction(CombatAI::ActionKind::Move,1);
        const auto Token=C.PathRequest;
        if(Mode==0) C.SetEnabled(false);
        if(Mode==1) C.SetEnabled(true); // ResetCombat's actual reset/enable consumer.
        if(Mode==2) {C.Pawn.Authority=EGASPEnemyAuthority::Recovery; C.SuspendForPhysics(false);}
        if(Mode==3) {C.Pawn.Dead=true; C.SuspendForPhysics(true);}
        if(Mode==4) {C.Pawn.Held=false; Tick(C,1.1);}
        ConsumeStance(C);
        Check(!C.Pawn.bCrouchCommand&&!C.Pawn.Data.Mover.bWantsToCrouch&&!C.Pawn.IsMovementCrouched()&&
              C.Path.IsEmpty()&&C.BurstRemaining==0&&!C.Action.Accepts(Token),
              "R1 disable/reset/authority/death/weapon cleanup still clears pose and ownership");
    }
    UEnemyCombatComponent C; C.Pawn.bCrouchCommand=true; ConsumeStance(C);
    C.ClearIntent(); ConsumeStance(C,false);
    Check(!C.Pawn.bCrouchCommand&&!C.Pawn.Data.Mover.bWantsToCrouch&&C.Pawn.IsMovementCrouched(),
          "stance boundary preserves refused stand instead of pretending request is achieved");
    ConsumeStance(C,true);
    Check(!C.Pawn.IsMovementCrouched(),"actual consumer can achieve stand once expansion is clear");
}
void ObstructedContact(UEnemyCombatComponent& C)
{
    SeedSight(C); C.TestWorld.Box({100,-50,0},{140,50,300});
    Tick(C,1); Tick(C,1.11);
    Check(C.ObstructedSince>=0&&C.ObstructionValidUntil>1.11&&C.TestWorld.Launches==0,
          "R2 actual muzzle rejection records bounded obstruction evidence");
}
void ClearedDistantLane()
{
    UEnemyCombatComponent C; ObstructedContact(C);
    C.TestWorld.Boxes.clear(); C.FreshGround={6500,0,0}; Tick(C,1.25);
    FVector Muzzle,Direction; bool Obstructed=true;
    Check(C.CanShoot(Muzzle,Direction,Obstructed)&&!Obstructed,
          "R2 review reproduction has a current clear actual corridor");
    Check(C.ObstructedSince<0&&C.RangeIntent==CombatAI::RangeIntent::CautiousAdvance,
          "R2 current geometry clears obsolete obstruction before range early return");
    for(int I=0;I<300&&C.FollowCalls==0;++I) Tick(C,1.30+I*.02);
    Check(C.FollowCalls>0&&C.State==EEnemyCombatState::Pursue,
          "R2 normal finite cover scan permits cautious step after clear-lane transition");
    Check(FVector::Dist2D(C.Feet(),C.SearchGoal)<=450&&FVector::Dist2D(C.SearchGoal,C.LastKnownGround)>5500&&
          C.MovementPurpose==CombatAI::MovePurpose::Cautious&&C.bRequestedWalk,
          "R2 restored approach is capped walking step, never target-foot pursuit");
    Check(C.TestWorld.Launches==0,"R2 out-of-range clearance cannot authorize a shot");
    std::cout<<"R2 cleared world="<<C.TestWorld.Now<<" obstruction="<<C.ObstructedSince
             <<" follow="<<C.FollowCalls<<" step="<<FVector::Dist2D(C.Feet(),C.SearchGoal)<<'\n';
    C.ActualFeet=C.SearchGoal; Tick(C,C.TestWorld.Now+.05);
    Check(C.State==EEnemyCombatState::Aim&&C.NextAdvanceAt>C.TestWorld.Now,
          "R2 completed cautious step retains reassessment pause");
    const int Calls=C.FollowCalls; Tick(C,C.TestWorld.Now+.1);
    Check(C.FollowCalls==Calls,"R2 arrival does not bypass cautious-step pause");
}
void BlockedAndHiddenLane()
{
    UEnemyCombatComponent C; ObstructedContact(C); C.FreshGround={6500,0,0};
    for(int I=0;I<360;++I) Tick(C,1.25+I*.02);
    Check(C.ObstructedSince>=0&&C.ObstructionValidUntil>C.TestWorld.Now&&C.RangeIntent==CombatAI::RangeIntent::SeekLane&&
          C.FollowCalls==0&&C.TestWorld.Launches==0,"R2 current blocked lane renews evidence and remains safe across scan expiry");
    C.Pawn.BodyData.Anim.RifleAimAlpha=0; C.Pawn.MovementAlpha=.6f;
    C.TestWorld.Boxes.clear(); Tick(C,C.TestWorld.Now+.02);
    Check(C.ObstructedSince<0&&C.RangeIntent==CombatAI::RangeIntent::CautiousAdvance,
          "R2 physical aim/braking gates do not trap obsolete geometry evidence");
    Check(C.TestWorld.Launches==0,"R2 independent corridor refresh does not bypass physical firing gates");

    UEnemyCombatComponent Hidden; ObstructedContact(Hidden);
    Hidden.FreshSight=false; Hidden.FreshGround={6500,4000,0}; Hidden.TestWorld.Now=1.8; Hidden.ObservePlayer();
    const auto Known=Hidden.LastKnownGround; const auto Queries=Hidden.TestWorld.Queries.size();
    Hidden.RefreshObstruction(1.8,FVector::Dist2D(Hidden.Feet(),Known));
    Check(Hidden.ObstructedSince<0,"R2 obstruction expires after half a world second without permitted revalidation");
    Check(Hidden.LastKnownGround==Known&&Known==FVector(1000,0,0)&&Hidden.TestWorld.Queries.size()==Queries,
          "R2 hidden relocation cannot refresh aim, obstruction corridor or known ground");
    Hidden.FreshSight=true; Hidden.FreshGround={6500,0,0}; Tick(Hidden,1.9);
    Check(Hidden.ObstructedSince>=0&&Hidden.RangeIntent==CombatAI::RangeIntent::SeekLane&&Hidden.FollowCalls==0,
          "R2 reacquisition validates blocked actual corridor before any new distant step");
}
void SharedMuzzleSafety()
{
    UEnemyCombatComponent C; SeedSight(C); C.NextCoverScan=1000;
    C.Pawn.RifleData.Location={160,0,130}; C.TestWorld.Box({100,-50,0},{140,50,300});
    FVector Muzzle,Direction; bool Blocked=false;
    Check(!C.CanShoot(Muzzle,Direction,Blocked)&&Blocked,"shared actual launch corridor rejects torso-to-muzzle clipping");
    C.LastKnownGround={6500,0,0}; C.LastKnownAim={6500,0,130}; C.RefreshObstruction(1,6500);
    Check(C.ObstructedSince>=0,"R2 range corridor also rejects clipped barrel despite clear muzzle-to-target line");
    C.TestWorld.Boxes.clear(); C.RefreshObstruction(1.1,6500);
    Check(C.ObstructedSince<0&&C.CanShoot(Muzzle,Direction,Blocked),"shared actual corridor accepts clear geometry");
    C.Pawn.RifleData.Right={0,1,0};
    Check(!C.CanShoot(Muzzle,Direction,Blocked)&&!Blocked,"shared corridor extraction retains barrel alignment gate");
    C.Pawn.RifleData.Right={1,0,0}; C.Pawn.bCrouchCommand=true;
    Check(!C.CanShoot(Muzzle,Direction,Blocked)&&!Blocked,"shared corridor extraction retains achieved stance gate");
    C.Pawn.bCrouchCommand=false; C.Pawn.MovementAlpha=.5f;
    Check(!C.CanShoot(Muzzle,Direction,Blocked)&&!Blocked,"shared corridor extraction retains actual movement gate");
    C.Pawn.MovementAlpha=0; C.Pawn.BodyData.Anim.RifleAimAlpha=0;
    Check(!C.CanShoot(Muzzle,Direction,Blocked)&&!Blocked,"shared corridor extraction retains animation aim gate");
    C.Pawn.BodyData.Anim.RifleAimAlpha=1; C.FreshSight=false; C.ObservePlayer();
    Check(!C.CanShoot(Muzzle,Direction,Blocked)&&!Blocked,"shared corridor extraction retains current visibility gate");
    C.FreshSight=true; C.FreshGround={1000,0,0}; C.NextSight=0;
    Tick(C,2); Tick(C,2.11);
    Check(C.TestWorld.Launches==1&&C.ObstructedSince<0&&C.ObstructionValidUntil==0,
          "shared corridor extraction retains eligible prompt launch and obstruction cleanup");
}
int main()
{
    SearchHandoffs(); CancellationConsumers(); ClearedDistantLane(); BlockedAndHiddenLane(); SharedMuzzleSafety();
    std::cout<<"correction_assertions="<<Checks<<" failures="<<Failures<<'\n';
    return Failures?1:0;
}
