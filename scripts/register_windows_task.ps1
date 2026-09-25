# TradeMind AI - Windows Task Scheduler Setup
# Registers a Windows Scheduled Task to run the 15-Minute Background Updater on Startup / Login.

$TaskName = "TradeMindAI_15Min_Updater"
$ScriptPath = "G:\TradeMindAI\scripts\start_hidden_background.vbs"

Write-Host "=========================================================================="
Write-Host " TradeMind AI: Registering Windows Scheduled Task ($TaskName)..."
Write-Host "=========================================================================="

$Action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$ScriptPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "TradeMind AI 15-Minute Live Market Data & Signal Sync Service"
    Write-Host "✓ Task '$TaskName' successfully registered in Windows Task Scheduler."
    Write-Host "✓ Service will automatically launch in hidden background mode on Windows Startup/Logon."
} catch {
    Write-Host "[!] Error registering task: $_"
}
