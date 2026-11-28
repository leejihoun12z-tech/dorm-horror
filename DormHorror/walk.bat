@echo off
rem Gray box walk: game window without editor. Close with Alt+F4.
start "" "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "%~dp0DormHorror.uproject" -game -windowed -ResX=1600 -ResY=900
