// Class/default/component data boundaries. No stance change or actor simulation.
struct UCapsuleComponent {
    float Radius=50,HalfHeight=86;FVector Scale{1,1,1};
    float GetUnscaledCapsuleRadius()const{return Radius;}
    float GetUnscaledCapsuleHalfHeight()const{return HalfHeight;}
    FVector GetComponentScale()const{return Scale;}
    float GetScaledCapsuleRadius()const{return float(Radius*std::min(Scale.X,Scale.Y));}
    float GetScaledCapsuleHalfHeight()const{return float(HalfHeight*Scale.Z);}
};
struct UCharacterMovementComponent {float CrouchedHalfHeight=60;float GetCrouchedHalfHeight()const{return CrouchedHalfHeight;}};
struct UStanceSettings{float CrouchHalfHeight=55;};
struct UCharacterMoverComponent{UStanceSettings Settings;template<class T>const T* FindSharedSettings()const{return &Settings;}};
struct APawn {
    virtual ~APawn()=default;UCapsuleComponent Capsule,Original;UCharacterMoverComponent Mover;bool HasCapsule=true,HasMover=true;
    template<class T>const T* FindComponentByClass()const{
        if constexpr(std::is_same_v<T,UCapsuleComponent>)return HasCapsule?&Capsule:nullptr;
        else return HasMover?&Mover:nullptr;
    }
};
struct ACharacter:APawn {
    UCharacterMovementComponent CMC;bool HasCMC=true;ACharacter* Defaults=nullptr;
    struct ClassInfo {ACharacter* Default=nullptr;template<class T>const T* GetDefaultObject()const{return Default;}};
    mutable ClassInfo Class;
    ACharacter(){HasMover=false;}
    const UCapsuleComponent* GetCapsuleComponent()const{return HasCapsule?&Capsule:nullptr;}
    const UCharacterMovementComponent* GetCharacterMovement()const{return HasCMC?&CMC:nullptr;}
    const ClassInfo* GetClass()const{Class.Default=Defaults;return &Class;}
};
struct UMovementUtils{template<class T>static const T* GetOriginalComponentType(APawn* P){return &P->Original;}};
