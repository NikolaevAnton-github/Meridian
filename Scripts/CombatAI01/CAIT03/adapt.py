"""Extend existing engine boundaries; tested production bodies remain unmodified."""
adapters=once(adapters,'using std::vector<T>::operator=;', 'using std::vector<T>::operator=;using std::vector<T>::vector;')
adapters=once(adapters,'static double DegreesToRadians', 'static double Square(double V){return V*V;}\n    static double DegreesToRadians')
adapters=once(adapters,'double SizeSquared()const', 'double Size2D()const{return std::hypot(X,Y);}\n    double SizeSquared()const')
adapters=once(adapters,'struct FQuat{static constexpr int Identity=0;};', '''struct FQuat{
    static constexpr int Identity=0;FVector Axis;double Angle;
    FQuat(FVector A,double V):Axis(A.GetSafeNormal()),Angle(V){}
    FVector RotateVector(FVector P)const{return P*std::cos(Angle)+FVector::CrossProduct(Axis,P)*std::sin(Angle)+Axis*FVector::DotProduct(Axis,P)*(1-std::cos(Angle));}
};''')
adapters=once(adapters,'bool LineTraceSingleByChannel(FHitResult& H', 'bool LineTraceSingleByChannel(FHitResult& H,FVector A,FVector B,ECollisionChannel C,FCollisionQueryParams){return Trace(H,A,B,C,{},false);}\n    bool OverlapBlockingTestByChannel(FVector A,int,ECollisionChannel C,FCollisionShape S,FCollisionQueryParams){FHitResult H;return Trace(H,A,A,C,{S.Radius,S.Radius,S.Height},false);}\n    bool LineTraceSingleByChannel(FHitResult& H')
adapters=once(adapters,'struct UCharacterMoverComponent{UStanceSettings Settings;', 'struct UCharacterMoverComponent{UStanceSettings Settings;FVector Velocity;bool Grounded=true;bool IsOnGround()const{return Grounded;}FVector GetVelocity()const{return Velocity;}')
adapters=once(adapters,'struct UGASPALSRifleAnimInstance{float RifleAlpha=1,RifleAimAlpha=1;};','struct UGASPALSRifleAnimInstance{float RifleAlpha=1,RifleAimAlpha=1,RifleLeanDegrees=0;};')
adapters=once(adapters,'FVector GetSocketLocation(const char*)const{return Location;}', '''bool Named=false;FVector Head,Torso,Pivot,Hand;
    FVector GetSocketLocation(const char* N)const{if(!Named)return Location;std::string S=N;return S=="head"?Head:S=="spine_05"?Torso:S=="spine_01"?Pivot:S=="hand_r"?Hand:Location;}''')
adapters=once(adapters,'bool Dead=false,Ready=true,Held=true', 'bool bWalkCommand=true;float RifleLeanTarget=0;FVector MovementCommand;\n    bool Dead=false,Ready=true,Held=true')
adapters=once(adapters,'APawn Data;APawn* Foundation=&Data;', 'APawn Data;APawn* Foundation=&Data;UCharacterMoverComponent* Mover=&Data.Mover;')
adapters=once(adapters,'float GetRifleMovementAlpha()const{return MovementAlpha;}', 'float GetRifleMovementAlpha()const{return static_cast<float>(Data.Mover.Velocity.Size2D()/100);}\n    CombatAI::FireMotion GetFireMotion()const;void SetRifleLean(float,bool=false);void SetMovementCommand(FVector,bool);')
adapters=once(adapters,'void StopMovementCommand(){++Stops;}', 'void StopMovementCommand();')
adapters=once(adapters,'int64 Launch(AGASPEnemyFixture*,FVector,FVector,float){return ++World->Launches;}', 'int EncounterSeed=CombatAI::DefaultEncounterSeed;uint64 GetEncounterGeneration()const{return 9;}\n    int64 Launch(AGASPEnemyFixture*,FVector P,FVector V,float){LastPosition=P;LastVelocity=V;return ++World->Launches;}\n    FVector LastPosition,LastVelocity;')
adapters=once(adapters,'struct FRandomStream{FVector VRandCone(FVector V,double){return V;}};', 'struct FRandomStream{double LastCone=0;void Initialize(int){}FVector VRandCone(FVector V,double Cone){LastCone=Cone;return V;}};')
