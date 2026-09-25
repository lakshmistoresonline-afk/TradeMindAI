/**
 * TradeMind AI: Automatic Windows Background Market Sync Service (Strategy V2.6)
 * Runs automatically in the background during NSE Pre-Market, Active Trading & Post-Market Closing Sync (08:45 AM - 03:45 PM IST, Mon-Fri):
 * 1. Fetches real live NSE market quotes for all NIFTY-200 stocks via Yahoo Finance API.
 * 2. Regenerates Strategy V2.6 active live signals & 10-year historical shadow ledger.
 * 3. Mirrors fresh signals & market heartbeats directly to Firestore Cloud Database.
 * 4. Builds and deploys fresh static bundle to Firebase Hosting automatically every 15 minutes.
 * 5. Executes a mandatory Post-Market Closing Sync right after 03:30 PM IST market close.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const UPDATE_INTERVAL_MS = 15 * 60 * 1000; // 15 Minutes (900,000 ms)
const LOG_FILE_PATH = path.join(__dirname, 'updater.log');
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

/**
 * Checks if current time is within NSE Active Window (Pre-Market, Session, Post-Market Close)
 * - Window: 08:45 AM to 03:45 PM IST (Mon-Fri)
 */
function isNSEActiveWindow() {
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
  const preMarketOpen = 8 * 60 + 45;    // 08:45 AM IST (525 mins)
  const postMarketClose = 15 * 60 + 45; // 03:45 PM IST (945 mins)

  return totalMinutes >= preMarketOpen && totalMinutes <= postMarketClose;
}

async function runUpdateCycle(forceRun = false) {
  if (isCycleRunning) {
    log("[SKIP] Previous update cycle is still executing. Skipping concurrent overlap.");
    return;
  }

  const activeWindow = isNSEActiveWindow();

  if (!activeWindow && !forceRun) {
    log("NSE Market Closed (Active Session Window: Mon-Fri 08:45 AM - 03:45 PM IST). Sleeping until next 15m cycle...");
    return;
  }

  isCycleRunning = true;

  log("==========================================================================");
  log(`Initiating Live Market Sync & Deployment Cycle (Forced=${forceRun}, ActiveWindow=${activeWindow})...`);
  log("==========================================================================");

  try {
    // 1. Fetch Live Market Data & Mirror Strategy V2.6 Signals to Firestore
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

    log("15-Minute Cycle Complete. Next polling check queued.\n");
  } catch (err) {
    log(`[ERROR] Background update cycle encountered an error: ${err.message}`);
  } finally {
    isCycleRunning = false;
  }
}

log("TradeMind AI Automatic Windows Background Service Initialized (Strategy V2.6).");
log(`Service configured for 15-minute interval polling (${UPDATE_INTERVAL_MS / 60000} minutes) during NSE pre-market, active session, and post-market hours (08:45 AM - 03:45 PM IST).\n`);

// Run initial sync cycle on startup
runUpdateCycle(true);

// Repeat polling every 15 minutes automatically
setInterval(() => runUpdateCycle(false), UPDATE_INTERVAL_MS);
