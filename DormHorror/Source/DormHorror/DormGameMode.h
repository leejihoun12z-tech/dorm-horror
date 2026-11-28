#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "DormGameMode.generated.h"

/** 회색 상자 판 게임 규칙: 사감·컨트롤러·HUD를 정하고, 시간대가 바뀌면 불을 켜고 끈다. */
UCLASS()
class DORMHORROR_API ADormGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ADormGameMode();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

private:
	/** 태그 Dorm_Ceiling 불 = 낮에만, Dorm_Night 불 = 밤에만 */
	void ApplyPhaseLighting();

	FDelegateHandle PhaseHandle;
};
