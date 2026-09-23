#include "CombatAISenses.h"
#include "CombatAITactics.h"
#include <iostream>
#include <limits>
#include <string>

using namespace CombatAI;
static int Failures=0, Checks=0;
static void Check(bool Value, const char* Name)
{ ++Checks; if (!Value) { ++Failures; std::cout<<"FAIL "<<Name<<'\n'; } }
static StimulusData Evidence(std::uint64_t Id, Sense Kind, double Time, Position P={100,200,0})
{
    StimulusData S; S.Id=Id; S.Generation=9; S.Kind=Kind; S.OccurredWorld=S.ReceivedWorld=Time;
    S.Region=P; S.Confidence=.7; S.Uncertainty=200; S.Category=SourceTeam::Player;
    if (Kind==Sense::Sight) { S.Confidence=1; S.Uncertainty=0; S.KnownIdentity=1; }
    return S;
}
static PositionFeatures Features(double Exposure, double Travel, unsigned Protected=0)
{
    PositionFeatures F; F.Supported=F.CapsuleClear=F.RouteClear=true;
    F.OpenDistance.fill(600); F.WeaponMask=F.EscapeMask=255;
    F.ProtectionMask=Protected; F.Exposure=Exposure; F.Travel=Travel;
    return F;
}
int main()
{
    Knowledge K; K.Reset(9);
    auto S=Evidence(1,Sense::Sight,1);
    Check(K.Accept(Stimulus(S),1),"current sight accepted");
    Check(K.Alert && K.RetainsContact(1.49) && !K.RetainsContact(1.51),"bounded world contact retention");
    Check(!K.Accept(Stimulus(S),1),"duplicate sight cannot update revision");
    auto Sound=Evidence(2,Sense::Shot,1.15,{700,800,0}); Sound.SimulationTime=123;
    Check(K.Accept(Stimulus(Sound),1.15),"sound admitted without sight or live actor");
    Check(K.Dominant(1.15,false)->Evidence.Get().Id==2,"fresh unseen shot redirects recent sight");
    Check(K.Dominant(1.15,true)->Evidence.Get().Kind==Sense::Sight,"current sight remains authoritative");
    Check(K.Dominant(2,false)->Evidence.Get().SimulationTime==123,"simulation time not world response clock");
    const auto Region=K.Dominant(2,false)->Evidence.Get().Region;
    Check(K.Dominant(5,false)->Evidence.Get().Region==Region,"silence ages confidence without hidden movement");
    Check(K.Dominant(5,false)->ConfidenceAt(5)<.7,"world-age confidence decay");
    auto Duplicate=Sound; Duplicate.Region={9999,9999,0};
    Check(!K.Accept(Stimulus(Duplicate),1.2),"duplicate cannot inject a different point");
    Knowledge ShotReceipts; ShotReceipts.Reset(9);
    auto ShotA=Evidence(1000,Sense::Shot,2);ShotA.Shot=55;ShotA.ProjectileGeneration=4;
    Check(ShotReceipts.Accept(Stimulus(ShotA),2),"first shot/listener receipt");
    auto ShotB=ShotA;ShotB.Id=1001;ShotB.Region={900,900,0};
    Check(!ShotReceipts.Accept(Stimulus(ShotB),2),"same shot with different transport event ID still deduplicated");
    ShotB.Kind=Sense::Damage;ShotB.Uncertainty=650;
    Check(ShotReceipts.Accept(Stimulus(ShotB),2),"same bullet may provide distinct victim bearing");
    ShotB.Id=1002;
    Check(!ShotReceipts.Accept(Stimulus(ShotB),2),"duplicate contact bearing cannot update memory");
    auto Stale=Evidence(3,Sense::Step,1.2);
    Check(!K.Accept(Stimulus(Stale),4),"stale step rejected");
    auto Wrong=Evidence(4,Sense::Shot,1.2); Wrong.Generation=8;
    Check(!K.Accept(Stimulus(Wrong),1.2),"old generation rejected");
    auto Future=Evidence(5,Sense::Shot,4);
    Check(!K.Accept(Stimulus(Future),3),"future receipt rejected");
    auto Leaked=Evidence(6,Sense::Step,2); Leaked.KnownIdentity=1;
    Check(!K.Accept(Stimulus(Leaked),2),"sound actor identity forbidden");
    Leaked.KnownIdentity=0; Leaked.Uncertainty=0;
    Check(!K.Accept(Stimulus(Leaked),2),"exact hidden sound localization forbidden");
    auto Masked=Evidence(7,Sense::Step,1.3);
    Check(!K.Accept(Stimulus(Masked),1.3),"loud sound masks close weak step");
    for (int I=0; I<100; ++I)
    {
        auto E=Evidence(static_cast<std::uint64_t>(100+I),Sense::Step,2+I*.1,{I*200.0,0,0});
        K.Accept(Stimulus(E),E.ReceivedWorld);
    }
    int Count=0; for (const auto& H:K.Hypotheses) Count+=H.Valid;
    Check(Count<=4,"hypothesis storage bounded under many footsteps");
    K.Reset(10);
    Check(!K.Alert && !K.Dominant(20,false) && !K.Accept(Stimulus(Sound),20),"reset clears memory and rejects old delivery");
    Check(!EligibleSound(SourceTeam::Enemy,Sense::Step,false),"friendly movement filtered");
    Check(!EligibleSound(SourceTeam::Player,Sense::Damage,false),"damage bearing only to actual victim");
    Check(EligibleSound(SourceTeam::Unknown,Sense::Impact,false),"unidentified impact can be investigated");
    Check(LocalizeSound({123,456,0},700,900,false).Audible,"walk in open audible");
    Check(!LocalizeSound({123,456,0},700,900,true).Audible,"column attenuates distant walk");
    Check(LocalizeSound({123,456,0},700,2000,true).Audible,"run heard at same obstructed range");
    const auto Heard=LocalizeSound({123,456,0},200,900,true);
    Check(Heard.Radius>=350 && !(Heard.Region==Position{123,456,0}),"obstructed location is uncertain quantized region");
    Check(Distance2D(Heard.Region,{123,456,0})<=Heard.Radius,"region covers source without exact aim");
    Check(!LocalizeSound({0,0,0},181,180,false).Audible,"quiet crouch range");

    GroundTravel G;
    MotionSample M{{0,0,0},0,1,true,false,false,true};
    Check(G.Advance(M).Kind==MotionEvent::None,"spawn silent");
    for (int I=1; I<10; ++I) { M.WorldTime=I*.1; Check(G.Advance(M).Kind==MotionEvent::None,"blocked/stationary silent"); }
    M.Feet.X=80; M.WorldTime=1; Check(G.Advance(M).Kind==MotionEvent::None,"partial stride silent");
    M.Feet.X=160; M.WorldTime=1.2; auto Walk=G.Advance(M);
    Check(Walk.Kind==MotionEvent::Step && Walk.Range==900,"paid grounded walk stride");
    M.Running=true; M.Feet.X=250; M.WorldTime=1.35; G.Advance(M);
    M.Feet.X=340; M.WorldTime=1.5; auto Run=G.Advance(M);
    Check(Run.Kind==MotionEvent::Step && Run.Range>Walk.Range && Run.Volume>Walk.Volume,"running intensity from same grounded producer");
    M.Crouched=true; M.Feet.X=460; M.WorldTime=1.7; const auto Crouch=G.Advance(M);
    Check(Crouch.Kind==MotionEvent::Step && Crouch.Volume<Walk.Volume && Crouch.Range<Walk.Range,"crouch audio and hearing agree");
    M.Grounded=false; M.Feet.Z=20; M.WorldTime=1.85; Check(G.Advance(M).Kind==MotionEvent::None,"takeoff emits no step");
    M.Feet={530,0,65}; M.WorldTime=2; Check(G.Advance(M).Kind==MotionEvent::None,"air travel emits no step");
    M.Feet={600,0,0}; M.Grounded=true; M.WorldTime=2.2;
    Check(G.Advance(M).Kind==MotionEvent::Landing,"one actual landing");
    M.WorldTime=2.3; Check(G.Advance(M).Kind==MotionEvent::None,"no duplicate stationary landing");
    M.Generation=2; M.Feet.X=9990; M.WorldTime=2.4;
    Check(G.Advance(M).Kind==MotionEvent::None,"encounter reset ignores displaced travel");
    M.Generation=2; M.Feet.X=0; M.WorldTime=2.5;
    Check(G.Advance(M).Kind==MotionEvent::None,"teleport cannot produce a stride");
    M.Enabled=false; M.Feet.X=100; M.WorldTime=2.6; G.Advance(M);
    M.Enabled=true; M.Feet.X=200; M.WorldTime=2.7;
    Check(G.Advance(M).Kind==MotionEvent::None,"physical recovery release rebases step accumulator");
    GroundTravel SlowSteps; MotionSample Slow{{0,0,0},0,1,true,true,false,true}; SlowSteps.Advance(Slow);
    int QuietCount=0;
    for(int I=1;I<=720;++I)
    {
        Slow.WorldTime=I/144.0; Slow.Feet.X=I*.2;
        QuietCount+=SlowSteps.Advance(Slow).Kind==MotionEvent::Step;
    }
    Check(QuietCount==1,"slow actual crouch travel remains audible at high update rate");

    auto Exposed=RatePosition(Features(.9,80,0b11111000));
    auto Safer=RatePosition(Features(.25,500,0b00000010));
    Check(Safer.Score>Exposed.Score,"low exposure beats rear-column rewards");
    Check(WorthSwitching(Exposed,Safer,10,70,false,4,10,6),"useful sub-meter move admitted");
    Check(!WorthSwitching(Safer,Exposed,100,70,false,4,10,6),"view and escapes cannot buy exposure increase");
    Check(PreferNearbySafe(.2,.23,85,500,80,2000),"nearest comparably safe wins despite view score");
    Check(!PreferNearbySafe(.2,.5,30,500,2000,0),"near exposed point loses to safety");
    auto BadArrival=Safer; BadArrival.Exposure+=.1;
    Check(!AcceptTacticalArrival(Safer,BadArrival),"actual-feet exposure drift rejected");
    Check(AcceptTacticalArrival(Safer,Safer),"matching actual feet accepted");
    Check(!WorthSwitching(Exposed,Safer,.5,200,false,4,10,6),"switch commitment survives equivalent sensory updates");

    // Obstacle [-100,100]^2. Endpoints behind it require supported side travel.
    std::array<Position,4> Corners{{{-150,-150,0},{150,-150,0},{150,150,0},{-150,150,0}}};
    int Calls=0;
    auto Strip=[&](Position A,Position B)
    {
        ++Calls;
        for (int I=0; I<=100; ++I)
        {
            const double T=I/100.0, X=A.X+(B.X-A.X)*T,Y=A.Y+(B.Y-A.Y)*T;
            if (std::abs(X)<120 && std::abs(Y)<120) return false;
        }
        return true;
    };
    auto Route=AroundColumn({-250,0,0},{250,0,0},Corners,Strip);
    Check(Route.Valid && Route.Count>=3 && Route.Length<1000,"protected side reached by short checked column route");
    Check(Calls<=13,"column feasibility trace strips bounded");
    auto NoRoute=AroundColumn({-250,0,0},{250,0,0},Corners,[](Position,Position){return false;});
    Check(!NoRoute.Valid,"blocked column route rejected without retry loop");
    auto Direct=AroundColumn({-250,-250,0},{250,-250,0},Corners,[](Position,Position){return true;});
    Check(Direct.Valid && Direct.Count==1,"direct supported route remains cheapest");
    ResponseGates Gates; Gates.ContactUntil=2; Gates.AimUntil=3; Gates.PauseUntil=4; Gates.ReloadUntil=5;
    Gates.Sight(ContactKind::Brief,1,.65);
    Check(Gates.ReadyAt(6)==6 && Gates.ContactUntil==2 && Gates.ReloadUntil==5,"retained contact cannot bypass weapon deadlines");
    std::cout<<Checks<<" assertions; "<<Failures<<" failures\n";
    return Failures ? 1 : 0;
}
