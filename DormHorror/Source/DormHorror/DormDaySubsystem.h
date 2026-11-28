#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DormTypes.h"
#include "DormDaySubsystem.generated.h"

DECLARE_MULTICAST_DELEGATE(FOnDormPhaseChanged);

/** 하루 진행기: 며칠째인지, 지금 시간대, 화면에 잠깐 띄울 말. 시간대 목록은 데이터 표에서 읽는다. */
UCLASS(Config = Game)
class DORMHORROR_API UDormDaySubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	/** 블루프린트·Python에서 꺼내 쓰기 (엔진 기본 함수는 Python에 안 보임) */
	UFUNCTION(BlueprintPure, Category = "Dorm", meta = (WorldContext = "WorldContext"))
	static UDormDaySubsystem* Get(const UObject* WorldContext);

	/** 다음 시간대로. 마지막 시간대 다음은 다음 날 첫 시간대 */
	UFUNCTION(BlueprintCallable, Category = "Dorm")
	void AdvancePhase();

	UFUNCTION(BlueprintPure, Category = "Dorm")
	int32 GetDay() const { return Day; }

	UFUNCTION(BlueprintPure, Category = "Dorm")
	FName GetPhaseId() const;

	UFUNCTION(BlueprintPure, Category = "Dorm")
	bool IsNight() const;

	const FDormPhaseRow* GetPhase() const;
	const FDormInteractableRow* FindInteractable(FName Id) const;

	UFUNCTION(BlueprintCallable, Category = "Dorm")
	void ShowMessage(const FText& Text, float Seconds = 3.5f);

	/** 지금 띄울 말 (시간이 지나면 빈 글) */
	FText GetMessage() const;

	FOnDormPhaseChanged OnPhaseChanged;

private:
	UPROPERTY(Config)
	TSoftObjectPtr<UDataTable> PhaseTable;

	UPROPERTY(Config)
	TSoftObjectPtr<UDataTable> InteractableTable;

	UPROPERTY(Transient)
	TObjectPtr<UDataTable> Phases;

	UPROPERTY(Transient)
	TObjectPtr<UDataTable> Interactables;

	TArray<FName> PhaseOrder;
	int32 PhaseIndex = 0;
	int32 Day = 1;
	FText Message;
	double MessageUntil = 0.0;
};
