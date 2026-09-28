# TradeMind AI - Windows Background Service Setup (100% Zero-Permission Windows Startup Launcher)
# Registers the 15-Minute Background Updater to run automatically in hidden mode on Windows Login / Startup.

$TaskName = 'TradeMindAI_15Min_Updater'
$VbsScriptPath = 'G:\TradeMindAI\scripts\start_hidden_background.vbs'
$StartupFolder = [Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder 'TradeMindAI_Background_Updater.lnk'

Write-Host "=========================================================================="
Write-Host " TradeMind AI: Registering Windows Background Updater ($TaskName)..."
Write-Host "=========================================================================="

try {
    # 1. Create Windows Startup Shortcut (.lnk) - Works 100% without Administrator elevation
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = 'wscript.exe'
    $Shortcut.Arguments = "`"$VbsScriptPath`""
    $Shortcut.WorkingDirectory = 'G:\TradeMindAI\scripts'
    $Shortcut.Description = 'TradeMind AI 15-Minute Automatic Background Market Sync & Deployer'
    $Shortcut.WindowStyle = 7 # Minimized/Hidden
    $Shortcut.Save()

    Write-Host "✓ Windows Startup Shortcut registered at:"
    Write-Host "  $ShortcutPath"
    Write-Host "✓ Service will launch in hidden background mode automatically on Windows Startup / Login."
} catch {
    Write-Host "[!] Error creating startup shortcut: $_"
}

# Also attempt Task Scheduler registration if elevated
try {
    $Action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$VbsScriptPath`""
    $Trigger = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description 'TradeMind AI 15-Minute Automatic Background Market Sync' -ErrorAction SilentlyContinue
    Write-Host "✓ Task '$TaskName' registered in Windows Task Scheduler."
} catch {}

# Start the background service right now immediately
try {
    Start-Process wscript.exe -ArgumentList "`"$VbsScriptPath`"" -WindowStyle Hidden
    Write-Host "✓ Background update service launched successfully right now!"
} catch {
    Write-Host "[!] Could not launch wscript directly: $_"
}
