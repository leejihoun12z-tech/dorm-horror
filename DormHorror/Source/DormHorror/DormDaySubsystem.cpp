#include "DormDaySubsystem.h"

DEFINE_LOG_CATEGORY_STATIC(LogDorm, Log, All);

void UDormDaySubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	Phases = PhaseTable.LoadSynchronous();
	Interactables = InteractableTable.LoadSynchronous();
	if (!Phases)
	{
		UE_LOG(LogDorm, Error, TEXT("시간대 표를 못 읽음: %s"), *PhaseTable.ToString());
		return;
	}
	if (!Interactables)
	{
		UE_LOG(LogDorm, Error, TEXT("상호작용 표를 못 읽음: %s"), *InteractableTable.ToString());
	}

	PhaseOrder = Phases->GetRowNames();
	PhaseOrder.Sort([this](const FName& A, const FName& B)
	{
		const FDormPhaseRow* RA = Phases->FindRow<FDormPhaseRow>(A, TEXT(""));
		const FDormPhaseRow* RB = Phases->FindRow<FDormPhaseRow>(B, TEXT(""));
		return (RA ? RA->Order : 0) < (RB ? RB->Order : 0);
	});
	PhaseIndex = 0;
	Day = 1;
	UE_LOG(LogDorm, Log, TEXT("하루 진행기 시작: 시간대 %d개"), PhaseOrder.Num());
}

UDormDaySubsystem* UDormDaySubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(WorldContext, EGetWorldErrorMode::ReturnNull) : nullptr;
	const UGameInstance* GI = World ? World->GetGameInstance() : nullptr;
	return GI ? GI->GetSubsystem<UDormDaySubsystem>() : nullptr;
}

void UDormDaySubsystem::AdvancePhase()
{
	if (PhaseOrder.Num() == 0)
	{
		return;
	}
	PhaseIndex++;
	if (PhaseIndex >= PhaseOrder.Num())
	{
		PhaseIndex = 0;
		Day++;
	}
	UE_LOG(LogDorm, Log, TEXT("%d일차 %s"), Day, *GetPhaseId().ToString());
	OnPhaseChanged.Broadcast();
}

FName UDormDaySubsystem::GetPhaseId() const
{
	return PhaseOrder.IsValidIndex(PhaseIndex) ? PhaseOrder[PhaseIndex] : NAME_None;
}

bool UDormDaySubsystem::IsNight() const
{
	const FDormPhaseRow* Row = GetPhase();
	return Row && Row->bNight;
}

const FDormPhaseRow* UDormDaySubsystem::GetPhase() const
{
	return Phases ? Phases->FindRow<FDormPhaseRow>(GetPhaseId(), TEXT("GetPhase"), false) : nullptr;
}

const FDormInteractableRow* UDormDaySubsystem::FindInteractable(FName Id) const
{
	return Interactables ? Interactables->FindRow<FDormInteractableRow>(Id, TEXT("FindInteractable"), false) : nullptr;
}

void UDormDaySubsystem::ShowMessage(const FText& Text, float Seconds)
{
	Message = Text;
	MessageUntil = FPlatformTime::Seconds() + Seconds;
}

FText UDormDaySubsystem::GetMessage() const
{
	return FPlatformTime::Seconds() < MessageUntil ? Message : FText::GetEmpty();
}
