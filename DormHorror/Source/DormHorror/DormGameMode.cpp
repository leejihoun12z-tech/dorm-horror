#include "DormGameMode.h"
#include "DormDaySubsystem.h"
#include "DormHUD.h"
#include "DormPlayerCharacter.h"
#include "DormPlayerController.h"
#include "Components/LightComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/Light.h"
#include "EngineUtils.h"

ADormGameMode::ADormGameMode()
{
	DefaultPawnClass = ADormPlayerCharacter::StaticClass();
	PlayerControllerClass = ADormPlayerController::StaticClass();
	HUDClass = ADormHUD::StaticClass();
}

void ADormGameMode::BeginPlay()
{
	Super::BeginPlay();
	if (UDormDaySubsystem* Day = GetGameInstance()->GetSubsystem<UDormDaySubsystem>())
	{
		PhaseHandle = Day->OnPhaseChanged.AddUObject(this, &ADormGameMode::ApplyPhaseLighting);
	}
	ApplyPhaseLighting();
}

void ADormGameMode::EndPlay(const EEndPlayReason::Type Reason)
{
	if (UGameInstance* GI = GetGameInstance())
	{
		if (UDormDaySubsystem* Day = GI->GetSubsystem<UDormDaySubsystem>())
		{
			Day->OnPhaseChanged.Remove(PhaseHandle);
		}
	}
	Super::EndPlay(Reason);
}

void ADormGameMode::ApplyPhaseLighting()
{
	const UDormDaySubsystem* Day = GetGameInstance()->GetSubsystem<UDormDaySubsystem>();
	const bool bNight = Day && Day->IsNight();
	for (TActorIterator<ALight> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("Dorm_Ceiling")))
		{
			It->GetLightComponent()->SetVisibility(!bNight);
		}
		else if (It->ActorHasTag(TEXT("Dorm_Night")))
		{
			It->GetLightComponent()->SetVisibility(bNight);
		}
	}
}
