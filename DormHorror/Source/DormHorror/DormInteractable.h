#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DormInteractable.generated.h"

class ADormPlayerCharacter;
class UStaticMeshComponent;
class UDormDaySubsystem;

/** E로 쓰는 물건. 무엇을 하는지는 Id로 데이터 표(DT_Interactables)에서 읽는다. */
UCLASS()
class DORMHORROR_API ADormInteractable : public AActor
{
	GENERATED_BODY()

public:
	ADormInteractable();

	/** 데이터 표 행 이름 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dorm")
	FName Id;

	UFUNCTION(BlueprintPure, Category = "Dorm")
	FText GetPrompt() const;

	UFUNCTION(BlueprintPure, Category = "Dorm")
	bool IsActiveNow() const;

	void Interact(ADormPlayerCharacter* By);

	/** 연출용 (블루프린트에서 덧붙임) */
	UFUNCTION(BlueprintImplementableEvent, Category = "Dorm")
	void OnInteracted();

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Dorm")
	TObjectPtr<UStaticMeshComponent> Mesh;

private:
	UDormDaySubsystem* GetDaySystem() const;
};
