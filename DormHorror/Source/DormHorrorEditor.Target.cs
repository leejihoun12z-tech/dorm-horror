using UnrealBuildTool;

public class DormHorrorEditorTarget : TargetRules
{
	public DormHorrorEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("DormHorror");
	}
}
