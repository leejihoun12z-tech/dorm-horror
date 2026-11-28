#include "DormInteractable.h"
#include "DormDaySubsystem.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ADormInteractable::ADormInteractable()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	RootComponent = Mesh;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Cube.Succeeded())
	{
		Mesh->SetStaticMesh(Cube.Object);
	}
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
}

UDormDaySubsystem* ADormInteractable::GetDaySystem() const
{
	const UGameInstance* GI = GetGameInstance();
	return GI ? GI->GetSubsystem<UDormDaySubsystem>() : nullptr;
}

FText ADormInteractable::GetPrompt() const
{
	const UDormDaySubsystem* Day = GetDaySystem();
	const FDormInteractableRow* Row = Day ? Day->FindInteractable(Id) : nullptr;
	return Row ? Row->Prompt : FText::FromName(Id);
}

bool ADormInteractable::IsActiveNow() const
{
	const UDormDaySubsystem* Day = GetDaySystem();
	const FDormInteractableRow* Row = Day ? Day->FindInteractable(Id) : nullptr;
	return Row && (Row->ActivePhase.IsNone() || Row->ActivePhase == Day->GetPhaseId());
}

void ADormInteractable::Interact(ADormPlayerCharacter* By)
{
	UDormDaySubsystem* Day = GetDaySystem();
	const FDormInteractableRow* Row = Day ? Day->FindInteractable(Id) : nullptr;
	if (!Row)
	{
		return;
	}
	if (!IsActiveNow())
	{
		if (!Row->InactiveMessage.IsEmpty())
		{
			Day->ShowMessage(Row->InactiveMessage);
		}
		return;
	}
	Day->ShowMessage(Row->Message);
	OnInteracted();
	if (Row->bAdvancesPhase)
	{
		Day->AdvancePhase();
	}
}
