static int Failures=0,Checks=0;
void Check(bool Passed,const char* Name) {
    ++Checks; if (!Passed) ++Failures;
    std::cout << (Passed ? "PASS " : "FAIL ") << Name << '\n';
}
bool Solve(UEnemyCombatComponent& C,FVector Goal) {
    if (!C.PlanPath(Goal,45)) return false;
    for (int I=0; I<150 && C.bPlanning; ++I) C.ContinuePath();
    return !C.bPlanning && !C.bPlanFailed && !C.Path.IsEmpty();
}
CombatAI::PositionFeatures ProtectedFeatures() {
    CombatAI::PositionFeatures F;
    F.Supported=F.CapsuleClear=F.RouteClear=true;
    F.OpenDistance[0]=600; F.WeaponMask=1; F.ProtectionMask=124; F.Exposure=.1;
    return F;
}
UEnemyCombatComponent MovingFixture() {
    UEnemyCombatComponent C;
    C.Memory.Observe(0); C.SearchGoal={360,360,0}; C.FixtureFeet=C.SearchGoal;
    C.FixtureFeatures=ProtectedFeatures();
    C.SelectedPosition.Ground=C.SearchGoal;
    C.SelectedPosition.Rating=CombatAI::RatePosition(C.FixtureFeatures);
    C.bSelectedPosition=true; C.TacticalPhase=CombatAI::TacticalPhase::Moving;
    C.Action.Start(1,CombatAI::ActionKind::Move,0);
    C.Transfers.Refresh(0); C.Transfers.Start();
    C.Assignment.Assign(1,CombatAI::TacticalObjective::ProtectedObservation,1,0);
    return C;
}
int main() {
    for (const FVector Goal:{FVector(320,320,0),FVector(360,360,0)}) {
        UEnemyCombatComponent C;
        const bool Found=Solve(C,Goal);
        Check(Found && C.Path.back()==Goal && C.LastPathExpanded<20 && C.MaxConnectorLength<=120,
              Goal.X==320 ? "R1 aligned goal control" : "R1 half-cell goal connects to exact endpoint");
        std::cout << "goal=" << Goal.X << ',' << Goal.Y << " expansions=" << C.LastPathExpanded
                  << " connector_cm=" << C.MaxConnectorLength << '\n';
    }
    bool GridSweep=true;
    int Goals=0;
    for (float Cell:{60.f,80.f,120.f}) for (float X:{0.f,.25f,.5f,.75f}) for (float Y:{0.f,.25f,.5f,.75f}) {
        UEnemyCombatComponent C; C.Tuning.NavigationCell=Cell;
        const FVector Goal((4+X)*Cell,(4+Y)*Cell,0);
        const bool Found=Solve(C,Goal); ++Goals;
        GridSweep &= Found && C.Path.back()==Goal && C.MaxConnectorLength<=1.5f*Cell && C.LastPathExpanded<20;
    }
    Check(GridSweep && Goals==48,"R1 48 cell-size/phase goals retain bounded validated connectors");
    {
        UEnemyCombatComponent C; C.FixtureFeet={13,17,0};
        Check(Solve(C,{360,360,0}) && C.Path.back()==FVector(360,360,0),"R1 displaced off-grid start");
    }
    {
        UEnemyCombatComponent C; C.BlockFirstConnector=true;
        const bool Found=Solve(C,{40,40,0});
        Check(Found && C.ConnectorRejected>0 && C.LastPathExpanded>1 && C.Path.back()==FVector(40,40,0),
            "R1 blocked start connector still expands a useful neighbor");
    }
    {
        UEnemyCombatComponent C; C.BlockAllConnectors=true; C.Tuning.MaxPathExpansions=64;
        Check(!Solve(C,{360,360,0}) && C.Path.IsEmpty() && C.bPlanFailed && C.LastPathExpanded==64 && C.ConnectorRejected>0,
            "R1 all final strips blocked: no path accepted, expansion cap retained");
    }
    {
        UEnemyCombatComponent C; C.UnsupportedGoal=true; C.Tuning.MaxPathExpansions=64;
        Check(!Solve(C,{360,360,0}) && C.Path.IsEmpty() && C.bPlanFailed && C.LastPathExpanded==64 && C.ConnectorChecks==0,
            "R1 unsupported final endpoint never reaches the segment validator");
    }
    {
        UEnemyCombatComponent C; C.MovementPurpose=CombatAI::MovePurpose::Pursuit;
        C.PlanPath({360,360,0},85);
        for (int I=0; I<100 && C.bPlanning; ++I) C.ContinuePath();
        Check(!C.bPlanFailed && !C.Path.IsEmpty() && FVector::Dist2D(C.Path.back(),{360,360,0})<=85 &&
            C.ConnectorChecks==0,"R1 non-tactical pursuit keeps its existing acceptance");
    }
    Primitive Ignore(ECC_WorldStatic,ECR_Ignore,ECR_Ignore);
    Primitive Overlap(ECC_WorldStatic,ECR_Overlap,ECR_Overlap);
    Primitive Block(ECC_WorldStatic,ECR_Block,ECR_Block);
    Primitive Pawn(ECC_Pawn,ECR_Block,ECR_Block);
    Primitive Dynamic(ECC_WorldDynamic,ECR_Block,ECR_Block);
    for (Primitive* Foreground:{&Ignore,&Overlap}) {
        UEnemyCombatComponent C; C.World.Hits={{Foreground,200},{&Block,210}};
        FHitResult Hit;
        const bool Blocked=C.TacticalTrace({},FVector(600,0,0),Hit);
        auto F=ProtectedFeatures(); F.OpenDistance[0]=Blocked ? Hit.Distance : 600;
        Check(Blocked && Hit.Component==&Block && Hit.Distance==210 && !CombatAI::RatePosition(F).Valid &&
            C.World.RayCalls==1 && C.TacticalQueryCount==1,
            Foreground==&Ignore ? "R2 ignored foreground cannot conceal invalid facing wall" : "R2 overlap foreground cannot conceal invalid facing wall");
    }
    {
        UEnemyCombatComponent C; C.World.Hits={{&Block,210}}; FHitResult Hit;
        Check(C.TacticalTrace({},FVector(600,0,0),Hit) && Hit.Distance==210,"R2 blocker-only control");
        C.World.Hits={{&Ignore,200},{&Overlap,205},{&Pawn,210},{&Dynamic,215}};
        Check(!C.TacticalTrace({},FVector(600,0,0),Hit),"R2 no relevant static blocker control");
        C.World.Hits={{&Block,400},{&Ignore,20},{&Pawn,30},{&Block,260},{&Dynamic,5}};
        Check(C.TacticalTrace({},FVector(600,0,0),Hit) && Hit.Distance==260,
            "R2 nearest blocking static surface wins with unordered input and dynamic occluders");
    }
    {
        Primitive PawnOnly(ECC_WorldStatic,ECR_Ignore,ECR_Block);
        UEnemyCombatComponent C; C.World.Hits={{&PawnOnly,10},{&Block,25}}; FHitResult Hit;
        const bool Support=C.TacticalTrace(FVector(0,0,40),FVector(0,0,-40),Hit,ECC_Pawn);
        Check(Support && Hit.Component==&PawnOnly && Hit.Distance==10,"R2 support ray honors pawn response");
        Check(C.TacticalTrace(FVector(0,0,40),FVector(0,0,-40),Hit,ECC_Visibility) && Hit.Component==&Block && Hit.Distance==25,
            "R2 same geometry honors visibility response independently");
    }
    {
        UEnemyCombatComponent C; FHitResult Hit; bool Same=true;
        for (float HiddenDistance:{1.f,100.f,209.f,400.f}) {
            C.World.Hits={{&Pawn,HiddenDistance},{&Dynamic,HiddenDistance/2},{&Ignore,200},{&Block,210}};
            Same &= C.TacticalTrace({},FVector(600,0,0),Hit) && Hit.Component==&Block && Hit.Distance==210;
        }
        Check(Same && C.World.RayCalls==4,"R2 dynamic hidden-object placement does not affect static proposal trace");
    }
    {
        auto C=MovingFixture(); C.FixtureFeet.X-=50; C.AdvanceSearch(1);
        Check(C.bSelectedPosition && !C.bHeldPosition && C.FollowCalls==1 && C.LastFollowAcceptance==45,
            "R1 wider grid connection radius cannot declare actual feet arrived at 50 cm");
    }
    {
        auto C=MovingFixture(); C.FixtureFeet.X-=45; C.FixtureFeatures.ProtectionMask=0; C.AdvanceSearch(1);
        Check(!C.bSelectedPosition && !C.bHeldPosition && C.TacticalPhase==CombatAI::TacticalPhase::Fallback &&
            C.RejectedPositions.Contains(360,360,12.99) && !C.RejectedPositions.Contains(360,360,13),
            "R1 exposed actual feet reject protected arrival for exactly 12 seconds");
        Check(C.AssessedReference==C.FixtureFeet && C.AssessedFrom==C.FixtureFeet && !C.AssessedRoute,
            "R1 arrival assessment uses actual feet rather than selected endpoint");
    }
    {
        auto C=MovingFixture(); C.FixtureFeet.X-=45; C.AdvanceSearch(1);
        Check(!C.bSelectedPosition && C.bHeldPosition && C.TacticalPhase==CombatAI::TacticalPhase::Holding &&
            C.HeldPosition.Ground==C.FixtureFeet && C.VisitedPositions.Contains(C.FixtureFeet.X,C.FixtureFeet.Y,20.99),
            "R1 valid protected actual-feet arrival starts held observation");
        C.HoldTacticalPosition(1.1);
        Check(C.Pawn.Stopped && C.Pawn.Stance==EGASPALSRifleStance::Aim && C.LookSector==0 &&
            C.Pawn.Aim.X>C.FixtureFeet.X+219 && C.Action.Kind==CombatAI::ActionKind::Observe,
            "arrival transitions to stationary outward sector observation");
    }
    {
        auto C=MovingFixture(); C.TraceFacing=true; C.World.Hits={{&Ignore,200},{&Block,210}};
        C.AdvanceSearch(1);
        Check(C.TacticalPhase==CombatAI::TacticalPhase::Fallback && !C.bHeldPosition && C.TacticalRejected==1,
            "R2 newly blocked actual facing prevents arrival acceptance");
    }
    {
        auto C=MovingFixture(); C.AdvanceSearch(1);
        C.TraceFacing=true; C.bTacticalScan=true; C.NextTacticalScan=20;
        const auto Before=C.Assignment.Token;
        C.World.Hits={{&Overlap,200},{&Block,210}}; C.HoldTacticalPosition(2);
        Check(!C.bHeldPosition && !C.bTacticalScan && C.TacticalPhase==CombatAI::TacticalPhase::Fallback &&
            C.NextTacticalScan==2 && !C.Assignment.Accepts(Before) && C.LookSector==-1 &&
            C.Pawn.Stance==EGASPALSRifleStance::Ready,
            "R2 held facing loss invalidates cached scan and requests reassessment");
    }
    {
        auto C=MovingFixture(); C.FixtureFeet.X-=100; C.FollowResult=false; C.AdvanceSearch(1);
        Check(C.TacticalPhase==CombatAI::TacticalPhase::Fallback && !C.bSelectedPosition &&
            C.RejectedPositions.Contains(360,360,12.99),"R1 failed navigation enters bounded destination rejection");
        C.Transfers.Start(); C.bSelectedPosition=true; C.AdvanceSearch(2);
        Check(C.NextTacticalScan==C.Transfers.ResetAt && !C.Transfers.CanStart(),
            "R1 exhausted transfer budget retains retry-window backoff");
    }
    std::cout << "checks=" << Checks << " failures=" << Failures << " grid_cases=" << Goals << '\n';
    return Failures ? 1 : 0;
}
