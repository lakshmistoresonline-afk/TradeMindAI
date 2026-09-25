/**
 * TradeMind AI: Automatic Windows Background Market Sync Service
 * Runs automatically on Windows in the background during NSE Trading Hours (09:15 AM - 03:30 PM IST, Mon-Fri):
 * 1. Fetches real live NSE market quotes for all NIFTY-200 stocks via Yahoo Finance API.
 * 2. Regenerates Strategy V2.3 active live signals & 10-year historical ledger.
 * 3. Mirrors fresh signals & market heartbeats directly to Firestore Cloud Database.
 * 4. Builds and deploys fresh static bundle to Firebase Hosting automatically every 15 minutes.
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

/**
 * Checks if current time is within NSE Trading Session (09:15 AM to 03:30 PM IST, Monday - Friday)
 */
function isNSETradingHours() {
  const now = new Date();
  const options = { timeZone: 'Asia/Kolkata', hour12: false };
  const istString = now.toLocaleString('en-US', options);

  const istDate = new Date(istString);
  const dayOfWeek = istDate.getDay(); // 0 = Sun, 6 = Sat
  const hours = istDate.getHours();
  const minutes = istDate.getMinutes();

  // Weekend check
  if (dayOfWeek === 0 || dayOfWeek === 6) return false;

  const totalMinutes = hours * 60 + minutes;
  const marketOpen = 9 * 60 + 15;  // 09:15 AM IST (555 mins)
  const marketClose = 15 * 60 + 30; // 03:30 PM IST (930 mins)

  return totalMinutes >= marketOpen && totalMinutes <= marketClose;
}

async function runUpdateCycle(forceRun = false) {
  const open = isNSETradingHours();

  if (!open && !forceRun) {
    log("NSE Market Closed (Trading Window: Mon-Fri 09:15 AM - 03:30 PM IST). Sleeping until next cycle...");
    return;
  }

  log("==========================================================================");
  log(`Initiating Live Market Sync & Deployment Cycle (Forced=${forceRun}, MarketOpen=${open})...`);
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

    log("Cycle complete. Next 15-minute polling check queued.\n");
  } catch (err) {
    log(`[ERROR] Background update cycle encountered an error: ${err.message}`);
  }
}

log("TradeMind AI Automatic Windows Background Service Initialized.");
log(`Service configured for 15-minute interval polling (${UPDATE_INTERVAL_MS / 60000} minutes) during NSE market hours.\n`);

// Run initial sync cycle on startup
runUpdateCycle(true);

// Repeat polling every 15 minutes automatically
setInterval(() => runUpdateCycle(false), UPDATE_INTERVAL_MS);
