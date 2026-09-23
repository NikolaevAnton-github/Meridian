// Extensions to the preserved CAIT01 deterministic adapters. Collision is a
// conservative 2D support/clearance model, not an Unreal world or gameplay run.
struct NavigationBox {
    float MinX, MinY, MaxX, MaxY;
    bool Contains(FVector P) const { return P.X>=MinX && P.X<=MaxX && P.Y>=MinY && P.Y<=MaxY; }
};
struct NavigationCollision {
    NavigationBox Floor{-3000,-1200,3000,1200};
    std::vector<NavigationBox> Blockers;
    bool NoSupport=false, BlockAllStrips=false, IgnoreFloor=false;
    mutable int SupportQueries=0, StripQueries=0;
    bool Ground(FVector Reference,FVector& Result) const {
        ++SupportQueries;
        if (NoSupport || !std::isfinite(Reference.X) || !std::isfinite(Reference.Y) ||
            !std::isfinite(Reference.Z) || std::abs(Reference.Z)>40 ||
            (!IgnoreFloor && !Floor.Contains(Reference))) return false;
        for (const auto& Box:Blockers) if (Box.Contains(Reference)) return false;
        Result={Reference.X,Reference.Y,0}; return true;
    }
    bool Strip(FVector From,FVector To) const {
        ++StripQueries;
        if (BlockAllStrips) return false;
        // The unchanged native support/sweep bodies are byte-compared separately.
        // This unit adapter checks each 10 cm sample against expanded solid bounds.
        const int Count=std::max(1,static_cast<int>(std::ceil(FVector::Dist2D(From,To)/10)));
        for (int I=0; I<=Count; ++I) {
            const double Alpha=double(I)/Count;
            FVector GroundPoint;
            if (!Ground(From*(1-Alpha)+To*Alpha,GroundPoint)) return false;
        }
        return true;
    }
};
enum class EGASPEnemyAuthority { Locomotion, Recovery };
