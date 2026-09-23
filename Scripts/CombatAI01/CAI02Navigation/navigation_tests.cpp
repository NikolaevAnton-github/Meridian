int Checks=0;
void Check(bool Pass,const char* Name) {
    ++Checks;
    if (!Pass) { std::cerr<<"FAIL "<<Name<<'\n'; std::exit(1); }
}
UEnemyCombatComponent Fixture(FVector Start={-950,-320,0}) {
    UEnemyCombatComponent C;
    C.Home={-950,-320,0}; C.FixtureFeet=Start;
    LoadRetainedColumns(C);
    return C;
}
void Complete(UEnemyCombatComponent& C,bool AdvanceWorld=false) {
    for (int Update=0; C.bPlanning && Update<200; ++Update) {
        const int Before=C.LastPathExpanded;
        C.ContinuePath();
        if (C.LastPathExpanded-Before>16) { std::cerr<<"per-update work cap failed\n"; std::exit(2); }
        if (C.Nodes.Num()>1+8*C.LastPathExpanded || C.OpenNodes.Num()>C.Nodes.Num()) {
            std::cerr<<"finite node/open-set bound failed\n"; std::exit(3);
        }
        if (AdvanceWorld) C.World.Now+=1./60;
    }
    Check(!C.bPlanning,"planning terminates within total/update bounds");
}
void ExpectPath(UEnemyCombatComponent& C,FVector Goal,CombatAI::MovePurpose Purpose,float Acceptance) {
    C.MovementPurpose=Purpose;
    Check(C.PlanPath(Goal,Acceptance),"far-room request admitted");
    Complete(C,true);
    Check(!C.bPlanFailed && !C.Path.IsEmpty(),"far-room path ready");
    Check(C.LastPathExpanded<=C.Tuning.MaxPathExpansions && C.World.Now<5,"far path stays within retained plan budgets");
    FVector Previous=C.FixtureFeet;
    for (FVector Next:C.Path) {
        Check(C.Collision.Strip(Previous,Next),"all returned strips retain support/clearance adapter checks");
        Previous=Next;
    }
    Check(FVector::Dist2D(C.Path.back(),Goal)<=Acceptance,"path reaches requested acceptance");
    std::cout<<"far_route expanded="<<C.LastPathExpanded<<" nodes="<<C.Nodes.Num()<<" updates_world="<<C.World.Now<<'\n';
}
int main() {
    const FVector FarGoal{2800,-400,0};
    auto Old=Fixture(); Old.Tuning.NavigationRadius=2800;
    Check(!Old.PlanPath(FarGoal,820),"old 28m radius reproduces rejection");
    auto Far=Fixture();
    Check(Far.Tuning.NavigationRadius==4500 && Far.Tuning.PursuitSeconds==24,"actual reflected defaults extracted");
    ExpectPath(Far,FarGoal,CombatAI::MovePurpose::Pursuit,820);
    Check(Far.FollowPath(FarGoal,820,Far.World.Now+.1,CombatAI::MovePurpose::Pursuit) && Far.Pawn.MovementCalls==1,
        "far ready path submits production movement");
    auto Across=Fixture({-1850,400,0});
    ExpectPath(Across,{2800,400,0},CombatAI::MovePurpose::Pursuit,820);
    auto Reverse=Fixture({2800,400,0});
    ExpectPath(Reverse,{-1850,400,0},CombatAI::MovePurpose::Pursuit,820);
    auto FarTactical=Fixture({2600,-400,0});
    ExpectPath(FarTactical,{2820,-300,0},CombatAI::MovePurpose::Search,25);
    Check(FarTactical.Path.back()==FVector(2820,-300,0),"far tactical exact endpoint retained");
    FarTactical.Pawn.bCrouchCommand=true;
    Check(FarTactical.FollowPath({2820,-300,0},25,FarTactical.World.Now+.1,CombatAI::MovePurpose::Search) &&
        FarTactical.Pawn.RequestedWalk,"far tactical route retains crouch walking");

    auto Outside=Fixture();
    Check(!Outside.PlanPath(Outside.Home+FVector(4501,0,0),25),"default home radius remains finite");
    Outside.Tuning.NavigationRadius=100000;
    Check(!Outside.PlanPath(Outside.Home+FVector(5001,0,0),25),"configured oversized radius remains clamped");
    Outside.Tuning.NavigationRadius=1;
    Check(!Outside.PlanPath(Outside.Home+FVector(401,0,0),25),"minimum radius clamp retained");
    auto Layer=Fixture();
    Check(!Layer.PlanPath({2800,-400,161},25),"unsupported floor layer rejected");
    auto Start=Fixture(); Start.Collision.NoSupport=true;
    Check(!Start.PlanPath(FarGoal,25),"unsupported start rejected");
    auto OutsideStart=Fixture({3600,0,0});
    Check(!OutsideStart.PlanPath(FarGoal,25),"start outside home region rejected");

    auto Unsupported=Fixture(); Unsupported.UnsupportedGoal=true;
    Check(Unsupported.PlanPath(FarGoal,25),"unsupported endpoint request reaches bounded planner");
    Complete(Unsupported);
    Check(Unsupported.bPlanFailed && Unsupported.Path.IsEmpty(),"unsupported tactical endpoint never accepted");
    Check(Unsupported.LastPathExpanded==1200,"default expansion cap unchanged for unreachable far endpoint");
    auto Blocked=Fixture(); Blocked.Collision.BlockAllStrips=true;
    Check(Blocked.PlanPath(FarGoal,25),"blocked strip setup"); Complete(Blocked);
    Check(Blocked.bPlanFailed && Blocked.Path.IsEmpty(),"no path through blocked strips");
    auto Floor=Fixture();
    Check(Floor.PlanPath({2800,1350,0},25),"outside support inside radius is bounded request"); Complete(Floor);
    Check(Floor.bPlanFailed && Floor.Path.IsEmpty(),"larger radius grants no nonexistent floor support");
    auto Cap=Fixture(); Cap.UnsupportedGoal=true; Cap.Tuning.MaxPathExpansions=1;
    Check(Cap.PlanPath(FarGoal,25),"low expansion budget setup"); Complete(Cap);
    Check(Cap.LastPathExpanded==64 && Cap.bPlanFailed,"minimum expansion clamp retained");
    auto MaxCap=Fixture(); MaxCap.UnsupportedGoal=true; MaxCap.Tuning.MaxPathExpansions=100000;
    MaxCap.Collision.IgnoreFloor=true; MaxCap.Collision.Blockers.clear();
    Check(MaxCap.PlanPath(FarGoal,25),"high expansion budget setup"); Complete(MaxCap);
    Check(MaxCap.LastPathExpanded==2000 && MaxCap.bPlanFailed,"hard expansion cap retained");

    auto Timed=Fixture(); Check(Timed.PlanPath(FarGoal,25),"world timeout setup");
    Timed.World.Now=5.01; Timed.ContinuePath();
    Check(!Timed.bPlanning && Timed.bPlanFailed && Timed.LastPathExpanded==0,"five-world-second planning timeout retained");
    auto Soft=Fixture(); Check(Soft.PlanPath(FarGoal,25),"soft per-update time setup");
    FPlatformTime::Step=.002; Soft.ContinuePath(); FPlatformTime::Step=0;
    Check(Soft.LastPathExpanded==1 && Soft.bPlanning,"soft real-time boundary stops between expansions");
    Check(!Far.PursuitExpired(21,0) && Far.PursuitExpired(24.01,0),"24 world seconds permit crossing and still expire");
    Check(!Far.PursuitExpired(6,0),"slowdown six elapsed world seconds do not spend 24 real seconds of deadline");
    Far.Tuning.PursuitSeconds=100000;
    Check(!Far.PursuitExpired(60,0) && Far.PursuitExpired(60.01,0),"pursuit deadline hard clamp retained");

    auto Stale=Fixture(); Check(Stale.PlanPath(FarGoal,25),"stale token setup");
    Stale.Action.Start(Stale.EncounterGeneration,CombatAI::ActionKind::Observe,1); Stale.ContinuePath();
    Check(!Stale.bPlanning && Stale.bPlanFailed && Stale.Nodes.IsEmpty() && Stale.OpenNodes.IsEmpty(),"replaced action cannot resume far plan");
    auto Generation=Fixture(); Check(Generation.PlanPath(FarGoal,25),"stale generation setup");
    ++Generation.EncounterGeneration; Generation.ContinuePath();
    Check(!Generation.bPlanning && Generation.bPlanFailed && Generation.Nodes.IsEmpty(),"reset generation rejects far plan");
    auto Cancel=Fixture(); Check(Cancel.PlanPath(FarGoal,25),"authority cancellation setup");
    Cancel.ClearIntent(CombatAI::ActionFailure::Authority);
    Check(!Cancel.bPlanning && Cancel.Path.IsEmpty() && Cancel.Nodes.IsEmpty() && Cancel.CellNodes.empty() &&
        Cancel.Pawn.Stopped && Cancel.PathRequest==CombatAI::ActionToken{},"production clear intent stops and releases far navigation");
    auto Replace=Fixture(); Check(Replace.PlanPath(FarGoal,25),"moving-goal replacement setup");
    const auto Token=Replace.PathRequest;
    Check(Replace.FollowPath({2700,400,0},25,1,CombatAI::MovePurpose::Pursuit) && Replace.PathRequest!=Token &&
        Replace.PathGoal==FVector(2700,400,0) && Replace.Pawn.MovementCalls==0 && Replace.Pawn.Stopped,
        "changed evidence goal cancels old request before submitting motion");
    auto Failure=Fixture(); Failure.Collision.NoSupport=true;
    Check(Failure.FollowPath(FarGoal,25,0,CombatAI::MovePurpose::Pursuit),"first route failure has bounded retry");
    Check(!Failure.FollowPath(FarGoal,25,1,CombatAI::MovePurpose::Pursuit) && Failure.FailedAttempts==2 && Failure.Pawn.Stopped,
        "second route failure terminates retry pair");
    auto Physical=Fixture(); Physical.Pawn.Authority=EGASPEnemyAuthority::Recovery;
    Check(!Physical.FollowPath(FarGoal,25,0,CombatAI::MovePurpose::Pursuit) && Physical.Pawn.MovementCalls==0,"physical authority receives no navigation movement");
    Physical.Pawn.Authority=EGASPEnemyAuthority::Locomotion; Physical.Pawn.Dead=true;
    Check(!Physical.FollowPath(FarGoal,25,0,CombatAI::MovePurpose::Pursuit) && Physical.Pawn.MovementCalls==0,"dead enemy receives no navigation movement");
    std::cout<<"PASS "<<Checks<<" affected navigation assertions\n";
}
