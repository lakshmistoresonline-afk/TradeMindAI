/**
 * TradeMind AI: Automatic Windows Background Market Sync Service (Strategy V5.0)
 * Executed every 15 minutes by Windows Task Scheduler / Startup Service:
 * 1. Fetches real live NSE market quotes for all NIFTY-200 stocks via Yahoo Finance API.
 * 2. Regenerates Strategy V5.0 active live signals & historical shadow ledger.
 * 3. Mirrors fresh signals & market heartbeats directly to Firestore Cloud Database.
 * 4. Builds and deploys fresh static bundle to Firebase Hosting automatically every 15 minutes.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const LOG_FILE_PATH = path.join(__dirname, 'updater.log');
const PID_FILE_PATH = path.join(__dirname, 'updater.pid');

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

async function runUpdateCycle() {
  log("==========================================================================");
  log("Initiating 15-Minute Automated Market Sync & Firebase Deployment (V5.0)...");
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

    log("✓ 15-Minute Automated Sync Cycle Completed Successfully.\n");
  } catch (err) {
    log(`[ERROR] Update cycle encountered an error: ${err.message}`);
  }
}

log("TradeMind AI Automatic Windows Background Service Triggered (Strategy V5.0).");
runUpdateCycle();
