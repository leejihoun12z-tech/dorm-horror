#include "DormHUD.h"
#include "DormDaySubsystem.h"
#include "DormInteractable.h"
#include "DormPlayerCharacter.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/GameViewportClient.h"
#include "Styling/CoreStyle.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"

#define LOCTEXT_NAMESPACE "DormHUD"

namespace
{
	TSharedRef<STextBlock> MakeText(const TAttribute<FText>& Text, int32 Size, ETextJustify::Type Justify)
	{
		// 기본 Slate 글꼴은 한글 대체 글꼴을 포함한다
		return SNew(STextBlock)
			.Text(Text)
			.Font(FCoreStyle::GetDefaultFontStyle("Regular", Size))
			.ColorAndOpacity(FLinearColor::White)
			.ShadowOffset(FVector2D(1.5f, 1.5f))
			.ShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.85f))
			.Justification(Justify);
	}
}

void ADormHUD::BeginPlay()
{
	Super::BeginPlay();
	if (!GEngine || !GEngine->GameViewport)
	{
		return;
	}
	Root = SNew(SOverlay)
		+ SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(28.f)
		[
			MakeText(TAttribute<FText>::Create(TAttribute<FText>::FGetter::CreateUObject(this, &ADormHUD::GetStatusText)), 20, ETextJustify::Left)
		]
		+ SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Center)
		[
			MakeText(FText::FromString(TEXT("·")), 26, ETextJustify::Center)
		]
		+ SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(0.f, 0.f, 0.f, 220.f)
		[
			MakeText(TAttribute<FText>::Create(TAttribute<FText>::FGetter::CreateUObject(this, &ADormHUD::GetPromptText)), 22, ETextJustify::Center)
		]
		+ SOverlay::Slot().HAlign(HAlign_Center).VAlign(VAlign_Bottom).Padding(0.f, 0.f, 0.f, 120.f)
		[
			MakeText(TAttribute<FText>::Create(TAttribute<FText>::FGetter::CreateUObject(this, &ADormHUD::GetMessageText)), 22, ETextJustify::Center)
		];
	GEngine->GameViewport->AddViewportWidgetContent(Root.ToSharedRef(), 10);
}

void ADormHUD::EndPlay(const EEndPlayReason::Type Reason)
{
	if (Root.IsValid() && GEngine && GEngine->GameViewport)
	{
		GEngine->GameViewport->RemoveViewportWidgetContent(Root.ToSharedRef());
	}
	Root.Reset();
	Super::EndPlay(Reason);
}

FText ADormHUD::GetStatusText() const
{
	const UGameInstance* GI = GetGameInstance();
	const UDormDaySubsystem* Day = GI ? GI->GetSubsystem<UDormDaySubsystem>() : nullptr;
	const FDormPhaseRow* Phase = Day ? Day->GetPhase() : nullptr;
	if (!Phase)
	{
		return LOCTEXT("NoPhase", "(시간대 표 없음)");
	}
	return FText::Format(LOCTEXT("Status", "{0}일차 · {1} {2}\n할 일: {3}"),
		FText::AsNumber(Day->GetDay()), Phase->Label, FText::FromString(Phase->Clock), Phase->Objective);
}

FText ADormHUD::GetPromptText() const
{
	const ADormPlayerCharacter* Player = Cast<ADormPlayerCharacter>(GetOwningPawn());
	const ADormInteractable* Focus = Player ? Player->GetFocus() : nullptr;
	if (!Focus)
	{
		return FText::GetEmpty();
	}
	return FText::Format(LOCTEXT("Prompt", "[E] {0}"), Focus->GetPrompt());
}

FText ADormHUD::GetMessageText() const
{
	const UGameInstance* GI = GetGameInstance();
	const UDormDaySubsystem* Day = GI ? GI->GetSubsystem<UDormDaySubsystem>() : nullptr;
	return Day ? Day->GetMessage() : FText::GetEmpty();
}

#undef LOCTEXT_NAMESPACE
