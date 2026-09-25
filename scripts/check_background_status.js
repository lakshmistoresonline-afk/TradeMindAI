const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log("==========================================================================");
console.log(" TradeMind AI: Windows Background Service Diagnostics & Status Check");
console.log("==========================================================================");

// 1. Check active background processes using PowerShell
console.log("\n[1] Checking Active Windows Processes...");
try {
  const psOutput = execSync('powershell "Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like \'*windows_background_updater.js*\' } | Select-Object ProcessId, CommandLine, CreationDate"', { encoding: 'utf8' });
  if (psOutput && psOutput.includes('ProcessId')) {
    console.log("✓ BACKGROUND UPDATER SERVICE IS CURRENTLY RUNNING!");
    console.log(psOutput.trim());
  } else {
    console.log("🟡 Background updater process not found in active processes. (You can launch it via start_hidden_background.vbs)");
  }
} catch (e) {
  console.log("Notice checking processes:", e.message);
}

// 2. Read latest entries from updater.log
console.log("\n[2] Reading Latest Log Entries from scripts/updater.log...");
const logPath = path.join(__dirname, 'updater.log');
if (fs.existsSync(logPath)) {
  const logContent = fs.readFileSync(logPath, 'utf8').trim();
  const lines = logContent.split('\n');
  const recentLines = lines.slice(-15);
  console.log("--- Recent Log Entries (Last 15 lines) ---");
  console.log(recentLines.join('\n'));
} else {
  console.log("No updater.log file found yet.");
}

console.log("\n==========================================================================");
