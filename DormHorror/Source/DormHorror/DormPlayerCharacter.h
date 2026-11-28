#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "DormPlayerCharacter.generated.h"

class UCameraComponent;
class USpotLightComponent;
class UInputAction;
class ADormInteractable;
struct FInputActionValue;

/** 사감 1인칭: 걷기·시선·점프·숙이기(누르는 동안)·손전등·E 상호작용. 키 연결은 IMC_Dorm 자산에. */
UCLASS(Config = Game)
class DORMHORROR_API ADormPlayerCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ADormPlayerCharacter();

	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;
	virtual void OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust) override;

	UFUNCTION(BlueprintCallable, Category = "Dorm")
	void Interact();

	UFUNCTION(BlueprintCallable, Category = "Dorm")
	void ToggleFlashlight();

	UFUNCTION(BlueprintCallable, Category = "Dorm")
	void SetFlashlight(bool bOn);

	UFUNCTION(BlueprintPure, Category = "Dorm")
	bool IsFlashlightOn() const;

	UFUNCTION(BlueprintPure, Category = "Dorm")
	ADormInteractable* GetFocus() const { return Focus; }

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Dorm")
	TObjectPtr<UCameraComponent> Camera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Dorm")
	TObjectPtr<USpotLightComponent> Flashlight;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputAction> MoveAction;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputAction> LookAction;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputAction> JumpAction;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputAction> CrouchAction;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputAction> InteractAction;

	UPROPERTY(Config)
	TSoftObjectPtr<UInputAction> FlashlightAction;

	/** 서 있을 때 눈높이(캡슐 중심 기준, cm). 캡슐 반높이 88 + 72 = 바닥에서 160 [작업값] */
	UPROPERTY(EditAnywhere, Category = "Dorm|Move")
	float EyeHeight = 72.f;

	/** 숙였을 때 눈높이(캡슐 중심 기준). 반높이 50 + 40 = 바닥에서 90 [작업값] */
	UPROPERTY(EditAnywhere, Category = "Dorm|Move")
	float CrouchEyeHeight = 40.f;

	/** 눈높이가 따라가는 빠르기 */
	UPROPERTY(EditAnywhere, Category = "Dorm|Move")
	float EyeInterpSpeed = 10.f;

	UPROPERTY(EditAnywhere, Category = "Dorm|Interact")
	float InteractRange = 250.f;

	UPROPERTY(EditAnywhere, Config, Category = "Dorm|Look")
	float LookScale = 1.f;

private:
	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void CrouchStart();
	void CrouchStop();
	void UpdateFocus();

	UPROPERTY(Transient)
	TObjectPtr<ADormInteractable> Focus;

	float EyeZ = 72.f;
};
