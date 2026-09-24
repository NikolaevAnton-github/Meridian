// Focused checks of the real production header. No world, actors or gameplay.
#include "CombatAIMobile.h"
#include <cstdlib>
#include <iostream>
#include <limits>

int main()
{
    using namespace CombatAI;
    int Checks=0;
    auto Check=[&](bool Value,const char* Name)
    { ++Checks; if (!Value) { std::cerr<<Name<<'\n'; std::exit(1); } };
    // Source walking can shoot at achieved directional speed, without the old
    // 360 cm/s cap granting a source walk permission it has not achieved.
    for (double Speed:{200.,180.,150.,225.})
    {
        FireMotion M{Speed,0,true,true,true,Speed};
        Check(M.Gate()==MotionGate::Ready,"source directional walk/crouch gate");
        Check(M.SpreadCost(2)==2,"spread uses actual source speed limit");
        M.Speed=Speed+2;
        Check(M.Gate()==MotionGate::Speed,"overspeed rejected against source cap");
    }
    Check(FireMotion{200,0,true,true,true,150}.Gate()==MotionGate::Speed,"backward cap differs from forward");
    Check(FireMotion{500,0,true,true,false,500}.Gate()==MotionGate::Gait,"running still refuses fire");
    Check(FireMotion{0,0,true,true,false,500}.Gate()==MotionGate::Ready,"stationary source run gait may aim");
    Check(FireMotion{100,0,false,true,true,200}.Gate()==MotionGate::Authority,"physical authority refuses fire");
    Check(FireMotion{100,0,true,false,true,200}.Gate()==MotionGate::Airborne,"airborne refuses fire");
    Check(FireMotion{100,46,true,true,true,200}.Gate()==MotionGate::Vertical,"vertical movement refuses fire");
    Check(FireMotion{0,0,true,true,true,0}.Gate()==MotionGate::Speed,"invalid CMC cap fails closed");
    Check(FireMotion{0,0,true,true,true,std::numeric_limits<double>::quiet_NaN()}.Gate()==MotionGate::Speed,"nonfinite cap fails closed");
    Check(FireMotion{100,0,true,true,true,200}.SpreadCost(2)==1,"half-speed source spread");
    std::cout<<Checks<<" production motion-gate assertions passed\n";
}
