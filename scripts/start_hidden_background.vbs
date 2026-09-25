' TradeMind AI - Hidden Windows Background Launcher
' Runs the 15-minute market updater in 100% background mode without opening a console window.

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c ""G:\TradeMindAI\scripts\start_background_service.bat""", 0, False
