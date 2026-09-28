# TradeMind AI - Windows Task Scheduler Setup (Self-Elevating & User-Scoped)
# Registers a Windows Scheduled Task to run the 15-Minute Background Updater on Startup / Login.

$TaskName = 'TradeMindAI_15Min_Updater'
$ScriptPath = 'G:\TradeMindAI\scripts\start_hidden_background.vbs'

# Self-elevation check
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Write-Host "=========================================================================="
    Write-Host " TradeMind AI: Requesting Administrator Elevation..."
    Write-Host "=========================================================================="
    try {
        Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
        Write-Host "Task registered via Elevated Administrator PowerShell Window."
        exit
    } catch {
        Write-Host "Administrator elevation declined or failed. Attempting User-Scoped registration..."
    }
}

Write-Host "=========================================================================="
Write-Host " TradeMind AI: Registering Windows Scheduled Task ($TaskName)..."
Write-Host "=========================================================================="

$Action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$ScriptPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description 'TradeMind AI 15-Minute Automated Market Signal and Price Updater' -ErrorAction Stop
    Write-Host "Task successfully registered in Windows Task Scheduler."
    Write-Host "Service will automatically launch in hidden background mode on Windows Startup/Logon."
} catch {
    Write-Host "Error registering scheduled task: $_"
    Write-Host "Alternative: You can manually run the background updater script in any terminal window."
}
