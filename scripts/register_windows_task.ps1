# TradeMind AI - Windows Background Service Setup (15-Minute Task Scheduler & Startup Launcher)
# Registers the 15-Minute Background Updater to run automatically every 15 minutes at OS level.

$TaskName = 'TradeMindAI_15Min_Updater'
$VbsScriptPath = 'G:\TradeMindAI\scripts\start_hidden_background.vbs'
$StartupFolder = [Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder 'TradeMindAI_Background_Updater.lnk'

Write-Host '=========================================================================='
Write-Host ' TradeMind AI: Registering Windows 15-Minute Background Task ($TaskName)...'
Write-Host '=========================================================================='

try {
    # 1. Create Windows Startup Shortcut (.lnk) - Runs automatically on Windows logon
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = 'wscript.exe'
    $Shortcut.Arguments = "`"$VbsScriptPath`""
    $Shortcut.WorkingDirectory = 'G:\TradeMindAI\scripts'
    $Shortcut.Description = 'TradeMind AI 15-Minute Automatic Background Market Sync and Deployer'
    $Shortcut.WindowStyle = 7
    $Shortcut.Save()

    Write-Host '✓ Windows Startup Shortcut registered at:'
    Write-Host "  $ShortcutPath"
} catch {
    Write-Host 'Error creating startup shortcut.'
}

# 2. Register Windows Task Scheduler Task with 15-Minute Repeating Interval
try {
    $Action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$VbsScriptPath`""
    $TriggerLogon = New-ScheduledTaskTrigger -AtLogOn
    $Trigger15m = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger @($TriggerLogon, $Trigger15m) -Settings $Settings -Principal $Principal -Description 'TradeMind AI 15-Minute Automatic Background Market Sync' -ErrorAction SilentlyContinue
    Write-Host '✓ Task registered in Windows Task Scheduler with 15-minute repeating interval.'
} catch {
    Write-Host 'Task Scheduler registration notice.'
}

# 3. Execute initial sync cycle right now
try {
    Start-Process wscript.exe -ArgumentList "`"$VbsScriptPath`"" -WindowStyle Hidden
    Write-Host '✓ Initial background update cycle triggered right now!'
} catch {
    Write-Host 'Could not launch wscript directly.'
}
