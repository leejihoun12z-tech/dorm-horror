#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "DormHUD.generated.h"

class SWidget;

/** 회색 상자 판 글자 화면: 며칠째·시간대·할 일 / 가운데 점 / 상호작용 안내 / 잠깐 뜨는 말 */
UCLASS()
class DORMHORROR_API ADormHUD : public AHUD
{
	GENERATED_BODY()

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

private:
	FText GetStatusText() const;
	FText GetPromptText() const;
	FText GetMessageText() const;

	TSharedPtr<SWidget> Root;
};
