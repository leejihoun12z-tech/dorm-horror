#include "DormPlayerCharacter.h"
#include "DormInteractable.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SpotLightComponent.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputAction.h"

ADormPlayerCharacter::ADormPlayerCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(30.f, 88.f);
	bUseControllerRotationYaw = true;
	bUseControllerRotationPitch = false;

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(GetCapsuleComponent());
	Camera->SetRelativeLocation(FVector(0.f, 0.f, EyeHeight));
	Camera->bUsePawnControlRotation = true;
	Camera->SetFieldOfView(80.f);

	Flashlight = CreateDefaultSubobject<USpotLightComponent>(TEXT("Flashlight"));
	Flashlight->SetupAttachment(Camera);
	Flashlight->SetRelativeLocation(FVector(10.f, 15.f, -12.f));
	Flashlight->SetIntensityUnits(ELightUnits::Candelas);
	Flashlight->SetIntensity(60.f);
	Flashlight->SetAttenuationRadius(1400.f);
	Flashlight->SetOuterConeAngle(21.f);
	Flashlight->SetInnerConeAngle(10.f);
	Flashlight->SetVisibility(false);

	// 걷기 값은 엔진 시험 걸어 보기와 같게 (engine-test-corridor §5-5) [작업값]
	UCharacterMovementComponent* Move = GetCharacterMovement();
	Move->MaxWalkSpeed = 260.f;
	Move->MaxWalkSpeedCrouched = 120.f;
	Move->MaxAcceleration = 1200.f;
	Move->BrakingDecelerationWalking = 1400.f;
	Move->JumpZVelocity = 360.f;
	Move->AirControl = 0.3f;
	Move->GetNavAgentPropertiesRef().bCanCrouch = true;
	Move->SetCrouchedHalfHeight(50.f);
}

void ADormPlayerCharacter::BeginPlay()
{
	Super::BeginPlay();
	EyeZ = EyeHeight;
}

void ADormPlayerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!Input)
	{
		return;
	}
	if (UInputAction* A = MoveAction.LoadSynchronous())
	{
		Input->BindAction(A, ETriggerEvent::Triggered, this, &ADormPlayerCharacter::Move);
	}
	if (UInputAction* A = LookAction.LoadSynchronous())
	{
		Input->BindAction(A, ETriggerEvent::Triggered, this, &ADormPlayerCharacter::Look);
	}
	if (UInputAction* A = JumpAction.LoadSynchronous())
	{
		Input->BindAction(A, ETriggerEvent::Started, this, &ACharacter::Jump);
		Input->BindAction(A, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	}
	if (UInputAction* A = CrouchAction.LoadSynchronous())
	{
		Input->BindAction(A, ETriggerEvent::Started, this, &ADormPlayerCharacter::CrouchStart);
		Input->BindAction(A, ETriggerEvent::Completed, this, &ADormPlayerCharacter::CrouchStop);
	}
	if (UInputAction* A = InteractAction.LoadSynchronous())
	{
		Input->BindAction(A, ETriggerEvent::Started, this, &ADormPlayerCharacter::Interact);
	}
	if (UInputAction* A = FlashlightAction.LoadSynchronous())
	{
		Input->BindAction(A, ETriggerEvent::Started, this, &ADormPlayerCharacter::ToggleFlashlight);
	}
}

void ADormPlayerCharacter::Move(const FInputActionValue& Value)
{
	const FVector2D V = Value.Get<FVector2D>();
	AddMovementInput(GetActorForwardVector(), V.Y);
	AddMovementInput(GetActorRightVector(), V.X);
}

void ADormPlayerCharacter::Look(const FInputActionValue& Value)
{
	const FVector2D V = Value.Get<FVector2D>();
	AddControllerYawInput(V.X * LookScale);
	AddControllerPitchInput(V.Y * LookScale);
}

void ADormPlayerCharacter::CrouchStart()
{
	Crouch();
}

void ADormPlayerCharacter::CrouchStop()
{
	UnCrouch();
}

void ADormPlayerCharacter::OnStartCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust)
{
	Super::OnStartCrouch(HalfHeightAdjust, ScaledHalfHeightAdjust);
	// 캡슐 중심이 내려간 만큼 카메라를 올려 두고, Tick에서 천천히 내린다 (눈높이 순간 이동 방지)
	EyeZ += ScaledHalfHeightAdjust;
}

void ADormPlayerCharacter::OnEndCrouch(float HalfHeightAdjust, float ScaledHalfHeightAdjust)
{
	Super::OnEndCrouch(HalfHeightAdjust, ScaledHalfHeightAdjust);
	EyeZ -= ScaledHalfHeightAdjust;
}

void ADormPlayerCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	const float Target = bIsCrouched ? CrouchEyeHeight : EyeHeight;
	EyeZ = FMath::FInterpTo(EyeZ, Target, DeltaSeconds, EyeInterpSpeed);
	Camera->SetRelativeLocation(FVector(0.f, 0.f, EyeZ));
	UpdateFocus();
}

void ADormPlayerCharacter::UpdateFocus()
{
	const FVector Start = Camera->GetComponentLocation();
	const FVector End = Start + Camera->GetForwardVector() * InteractRange;
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(DormInteract), false, this);
	Focus = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params)
		? Cast<ADormInteractable>(Hit.GetActor())
		: nullptr;
}

void ADormPlayerCharacter::Interact()
{
	if (Focus)
	{
		Focus->Interact(this);
	}
}

void ADormPlayerCharacter::ToggleFlashlight()
{
	SetFlashlight(!IsFlashlightOn());
}

void ADormPlayerCharacter::SetFlashlight(bool bOn)
{
	Flashlight->SetVisibility(bOn);
}

bool ADormPlayerCharacter::IsFlashlightOn() const
{
	return Flashlight->IsVisible();
}
