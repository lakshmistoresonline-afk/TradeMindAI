/**
 * TradeMind AI: 15-Minute Windows Background Market Sync Service
 * Continuously runs in the background to:
 * 1. Fetch live NSE market quotes for all NIFTY-200 stocks.
 * 2. Regenerate Strategy V2.3 active live signals & 10-year historical ledger.
 * 3. Mirror fresh signals & market heartbeats directly to Firestore Cloud Database.
 * 4. Build and deploy fresh static bundle to Firebase Hosting automatically.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const UPDATE_INTERVAL_MS = 15 * 60 * 1000; // 15 Minutes (900,000 ms)
const LOG_FILE_PATH = path.join(__dirname, 'updater.log');

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
  log("Initiating 15-Minute Live Market Sync & Deployment Cycle...");
  log("==========================================================================");

  try {
    // 1. Fetch Live Market Data & Mirror to Firestore
    const updateDataScript = path.join(__dirname, 'node_update_all_data.js');
    log("Executing node_update_all_data.js...");
    execSync(`node "${updateDataScript}"`, { stdio: 'inherit' });
    log("✓ Live market prices and Firestore signal mirror updated successfully.");

    // 2. Build Web Production Bundle
    const webDir = path.join(__dirname, '../web');
    log("Building web production bundle with updated live price utils...");
    execSync(`cd "${webDir}" && npm run build`, { stdio: 'inherit' });
    log("✓ Web production build complete.");

    // 3. Deploy Live to Firebase Hosting
    log("Deploying live bundle to Firebase Hosting...");
    execSync(`cd "${webDir}" && npx --yes firebase-tools deploy --only hosting --project com-webcraft-trademindai-c8f75`, { stdio: 'inherit' });
    log("✓ Firebase Hosting deployment completed successfully!");

    log("Next scheduled refresh in 15 minutes.\n");
  } catch (err) {
    log(`[ERROR] Background update cycle encountered an error: ${err.message}`);
  }
}

log("TradeMind AI Windows Background Updater Service Initialized.");
log(`Service configured for 15-minute interval polling (${UPDATE_INTERVAL_MS / 60000} minutes).\n`);

// Run immediately upon launch
runUpdateCycle();

// Repeat every 15 minutes
setInterval(runUpdateCycle, UPDATE_INTERVAL_MS);
