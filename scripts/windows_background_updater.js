/**
 * TradeMind AI: Automatic Windows Background Market Sync Service (Strategy V5.0)
 * Runs continuously every 15 minutes 24/7/365:
 * 1. Fetches real live NSE market quotes for all NIFTY-200 stocks via Yahoo Finance API.
 * 2. Regenerates Strategy V5.0 active live signals & historical shadow ledger.
 * 3. Mirrors fresh signals & market heartbeats directly to Firestore Cloud Database.
 * 4. Builds and deploys fresh static bundle to Firebase Hosting automatically every 15 minutes.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const UPDATE_INTERVAL_MS = 15 * 60 * 1000; // 15 Minutes (900,000 ms)
const LOG_FILE_PATH = path.join(__dirname, 'updater.log');
const PID_FILE_PATH = path.join(__dirname, 'updater.pid');

let isCycleRunning = false;

function log(msg) {
  const timestamp = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
  const logLine = `[${timestamp} IST] ${msg}\n`;
  console.log(logLine.trim());
  try {
    fs.appendFileSync(LOG_FILE_PATH, logLine, 'utf8');
  } catch (e) {
    console.error("Log file write error:", e);
  }
}

// Ensure single instance process
function enforceSingleInstance() {
  if (fs.existsSync(PID_FILE_PATH)) {
    try {
      const oldPid = parseInt(fs.readFileSync(PID_FILE_PATH, 'utf8').trim(), 10);
      if (oldPid && oldPid !== process.pid) {
        try {
          process.kill(oldPid, 0);
          log(`[INFO] Previous updater process PID ${oldPid} is active. Exiting duplicate instance.`);
          process.exit(0);
        } catch {
          // PID is stale
        }
      }
    } catch {}
  }
  fs.writeFileSync(PID_FILE_PATH, process.pid.toString(), 'utf8');
}

async function runUpdateCycle(forceRun = true) {
  if (isCycleRunning) {
    log("[SKIP] Previous update cycle is still executing. Skipping concurrent overlap.");
    return;
  }

  isCycleRunning = true;

  log("==========================================================================");
  log(`Initiating Live Market Sync & Deployment Cycle (Strategy V5.0)...`);
  log("==========================================================================");

  try {
    // 1. Fetch Live Market Data & Mirror Strategy V5.0 Signals to Firestore
    const updateDataScript = path.join(__dirname, 'node_update_all_data.js');
    log("Executing node_update_all_data.js...");
    execSync(`node "${updateDataScript}"`, { stdio: 'inherit' });
    log("✓ Live market prices and Firestore signal mirror updated successfully.");

    // 2. Build Web Production Bundle
    const webDir = path.join(__dirname, '../web');
    log("Building web production bundle with fresh live price utils...");
    execSync(`cd "${webDir}" && npm run build`, { stdio: 'inherit' });
    log("✓ Web production build complete.");

    // 3. Deploy Live to Firebase Hosting
    log("Deploying live bundle to Firebase Hosting...");
    execSync(`cd "${webDir}" && npx --yes firebase-tools deploy --only hosting --project com-webcraft-trademindai-c8f75`, { stdio: 'inherit' });
    log("✓ Firebase Hosting deployment completed successfully!");

    log("15-Minute Cycle Complete. Next polling check queued in 15 minutes.\n");
  } catch (err) {
    log(`[ERROR] Background update cycle encountered an error: ${err.message}`);
  } finally {
    isCycleRunning = false;
  }
}

enforceSingleInstance();

log("TradeMind AI Automatic Windows Background Service Initialized (Strategy V5.0).");
log(`Service configured for continuous 15-minute polling (${UPDATE_INTERVAL_MS / 60000} minutes) 24/7/365.\n`);

// Run initial sync cycle immediately on startup
runUpdateCycle(true);

// Repeat polling every 15 minutes automatically
setInterval(() => runUpdateCycle(true), UPDATE_INTERVAL_MS);
