#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "DormTypes.generated.h"

/** 하루 시간대 한 줄. 원본 data/day_phases.csv → DT_DayPhases. 행 이름 = 시간대 Id */
USTRUCT(BlueprintType)
struct FDormPhaseRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	int32 Order = 0;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FText Label;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FString Clock;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FText Objective;

	/** 밤이면 천장 불이 꺼진다 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	bool bNight = false;
};

/** 상호작용 물건 한 줄. 원본 data/interactables.csv → DT_Interactables. 행 이름 = 물건 Id */
USTRUCT(BlueprintType)
struct FDormInteractableRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FText Prompt;

	/** 이 시간대에만 쓸 수 있음. 비우면 언제나 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FName ActivePhase;

	/** 쓰면 다음 시간대로 넘어감 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	bool bAdvancesPhase = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FText Message;

	/** 지금 시간대가 아닐 때 보여 줄 말 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dorm")
	FText InactiveMessage;
};
