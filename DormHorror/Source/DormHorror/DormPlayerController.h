#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "DormPlayerController.generated.h"

class UInputMappingContext;

/** 키 연결 묶음(IMC)을 켜는 일만 한다. 경로는 DefaultGame.ini */
UCLASS(Config = Game)
class DORMHORROR_API ADormPlayerController : public APlayerController
{
	GENERATED_BODY()

protected:
	virtual void BeginPlay() override;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputMappingContext> DefaultMappingContext;
};
