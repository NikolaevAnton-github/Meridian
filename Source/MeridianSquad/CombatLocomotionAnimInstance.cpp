#include "CombatLocomotionAnimInstance.h"
#include "CombatProjectileWorld.h"
#include "OpeningLobbyCharacter.h"
#include "GASPEnemyFixture.h"
#include "Animation/AnimNotifies/AnimNotify_PlaySound.h"
#include "Sound/SoundBase.h"

bool UCombatLocomotionAnimInstance::HandleNotify(const FAnimNotifyEvent& Event)
{
    if (ACombatProjectileWorld::Find(GetWorld()) && Event.Notify)
    {
        if (Cast<AOpeningLobbyCharacter>(GetOwningActor()))
        {
            const auto* Audio = Cast<UAnimNotify_PlaySound>(Event.Notify);
            if (Audio && Audio->Sound && Audio->Sound->GetPathName().Contains(TEXT("A_TFA_Foley_Footsteps_Cue")))
                return true; // Includes authored jump/land foot sounds; one grounded producer.
        }
        else if (AGASPEnemyFixture::FromFoundation(GetOwningActor()))
        {
            const FString Name = Event.Notify->GetClass()->GetName();
            if (Name.StartsWith(TEXT("BP_AnimNotify_FoleyEvent_Walk_")) ||
                Name.StartsWith(TEXT("BP_AnimNotify_FoleyEvent_Run_")) ||
                Name.StartsWith(TEXT("BP_AnimNotify_FoleyEvent_Crouch_")) ||
                Name.StartsWith(TEXT("BP_AnimNotify_FoleyEvent_Scuff_"))) return true;
            // GASP jump/land and physical foley remain owned by its existing route.
        }
    }
    return Super::HandleNotify(Event);
}
