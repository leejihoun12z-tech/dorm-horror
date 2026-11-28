#include "DormPlayerController.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "InputMappingContext.h"

void ADormPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (UEnhancedInputLocalPlayerSubsystem* Input = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		if (UInputMappingContext* Imc = DefaultMappingContext.LoadSynchronous())
		{
			Input->AddMappingContext(Imc, 0);
		}
	}
	SetInputMode(FInputModeGameOnly());
	bShowMouseCursor = false;
}
