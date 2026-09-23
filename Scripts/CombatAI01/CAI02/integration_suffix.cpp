int main()
{
    int Passed=0,Failed=0;
    auto Check=[&](bool Ok,const char* Name){if(Ok)++Passed;else{++Failed;std::cout<<"FAIL "<<Name<<'\n';}};
    UEnemyCombatComponent A;
    CombatAI::StimulusData S;S.Id=10;S.Generation=9;S.Kind=CombatAI::Sense::Step;
    S.Region={800,400,0};S.Uncertainty=200;S.Confidence=.7;S.OccurredWorld=S.ReceivedWorld=1;
    A.ReceiveStimulus(CombatAI::Stimulus(S));
    Check(A.Memory.Alert && A.bEvidencePending && A.ClearCalls==0,"delivery records memory without tactical mutation");
    A.ApplyEvidenceIntent(1);
    Check(A.State==EEnemyCombatState::Search && A.Assignment.Objective==CombatAI::TacticalObjective::ProtectedObservation,"fresh hearing reaches live protected policy");
    Check(A.LastKnownGround.X==800 && A.SearchAnchor.Y==400 && A.Fixture.AimCalls==1,"captured region becomes investigation and attention");
    Check(A.NextSight<=1.05 && A.NextLookAt==1.35,"sound prompts bounded world-time resensing");
    const auto Revision=A.Knowledge.Revision; A.ReceiveStimulus(CombatAI::Stimulus(S));
    Check(A.Knowledge.Revision==Revision && !A.bEvidencePending,"duplicate consumer delivery has no effect");
    UEnemyCombatComponent B=A;
    // Neither production method accepts a hidden actor transform or velocity.
    for(int I=0;I<10;++I){A.Clock.Time=B.Clock.Time=1.1+I*.1;A.ApplyEvidenceIntent(A.Clock.Time);B.ApplyEvidenceIntent(B.Clock.Time);}
    Check(A.LastKnownGround.X==B.LastKnownGround.X && A.SearchAnchor.Y==B.SearchAnchor.Y && A.Knowledge.Revision==B.Knowledge.Revision,"paired unseen histories have identical policy memory");
    S.Id=11; S.Region={-1000,0,0}; S.OccurredWorld=S.ReceivedWorld=1;
    A.Clock.Time=5; A.ReceiveStimulus(CombatAI::Stimulus(S)); A.ApplyEvidenceIntent(5);
    Check(A.LastKnownGround.X==800,"stale movement cannot redirect intent");
    S.Id=12; S.OccurredWorld=S.ReceivedWorld=5; S.Kind=CombatAI::Sense::Damage;
    A.State=EEnemyCombatState::Recovery; A.ReceiveStimulus(CombatAI::Stimulus(S));
    Check(A.Knowledge.Alert && A.bEvidencePending && A.State==EEnemyCombatState::Recovery,"incoming evidence retained while physical authority owns execution");
    A.State=EEnemyCombatState::Search; A.ApplyEvidenceIntent(5);
    Check(A.LastKnownGround.X==-1000,"recovery release consumes retained bearing region");
    A.State=EEnemyCombatState::Reload; A.Gates.ReloadUntil=8;
    S.Id=13;S.Kind=CombatAI::Sense::Shot;S.Region={100,900,0};S.OccurredWorld=S.ReceivedWorld=6;
    A.Clock.Time=6; A.ReceiveStimulus(CombatAI::Stimulus(S));A.ApplyEvidenceIntent(6);
    Check(A.State==EEnemyCombatState::Reload && A.Gates.ReloadUntil==8 && A.bEvidencePending,"sound cannot reset unpaid reload");
    A.bTargetVisible=true; A.State=EEnemyCombatState::Search; A.ApplyEvidenceIntent(6);
    Check(A.LastKnownGround.X==-1000,"visible combat not overwritten by sound");
    A.bTargetVisible=false;A.ApplyEvidenceIntent(6);
    Check(A.LastKnownGround.X==100,"pending sound consumed after sight loss");
    A.Fixture.Dead=true; S.Id=14; const auto Before=A.Knowledge.Revision;
    A.ReceiveStimulus(CombatAI::Stimulus(S));Check(A.Knowledge.Revision==Before,"dead listener rejects evidence");

    UEnemyCombatComponent Shooter;
    auto Token=Shooter.Action.Start(9,CombatAI::ActionKind::Burst,1);
    Shooter.bTargetVisible=true;Shooter.FreshSight=false;
    Check(!Shooter.Fire(1,Token) && Shooter.Clock.Launches==0 && Shooter.Magazine==5,"actual Fire vetoes cached sight at birth");
    Shooter.FreshSight=true;Shooter.MuzzleClear=false;
    Check(!Shooter.Fire(1,Token) && Shooter.Clock.Launches==0,"actual Fire vetoes blocked muzzle");
    Shooter.MuzzleClear=true;Shooter.Clock.AcceptLaunch=false;
    Check(!Shooter.Fire(1,Token) && Shooter.Magazine==5,"rejected launch does not consume magazine");
    Shooter.Clock.AcceptLaunch=true;
    Check(Shooter.Fire(1,Token) && Shooter.Magazine==4 && Shooter.Clock.Launches==1,"current sight and safe muzzle birth one finite round");
    Check(std::abs(Shooter.NextShot-1.18)<.00001,"unchanged cadence paid on world time");
    Token.Generation=8;Check(!Shooter.Fire(1,Token),"stale generation cannot launch");
    Check(CombatAI::FirstVisibleSample(3,[](int I){return I==1;})==1,"blocked camera allows actually visible torso");
    Check(CombatAI::FirstVisibleSample(3,[](int){return false;})==-1,"all obstructed samples reject current sight");
    int Samples=0;CombatAI::FirstVisibleSample(100,[&](int){++Samples;return false;});
    Check(Samples==3,"body query count bounded");
    std::cout<<Passed<<" passed; "<<Failed<<" failed\n";
    return Failed?1:0;
}
