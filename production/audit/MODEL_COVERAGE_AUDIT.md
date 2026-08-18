# Forensic Model Coverage Audit: Trademind-Equity-v2.2

## 1. Executive Summary
The Shadow Mode run on 2026-08-18 reported **178 symbols with NO_MODEL_FOUND**. 
Our forensic audit of the `model_registry` and filesystem confirms that the production environment is in a **degraded state** due to a mismatch between the certified Strategy v2.2 specification (11 features) and the existing model inventory.

## 2. Definitive Classification of Missing Models
Total Universe: 200 symbols (NIFTY 200)

| Classification | Count | Description |
| :--- | :--- | :--- |
| **Genuinely Missing** | 151 | No entry exists in the `model_registry` database table. |
| **Incompatible (v2.1 Legacy)** | 39 | Models exist and are marked as champions, but use only **7 features**. |
| **Production Ready (v2.2)** | 10 | Models exist, use **11 features**, and pass compatibility checks. |
| **Total Scanned** | 200 | |

### Compatible Symbols (10)
`BHARTIARTL, HDFCBANK, ICICIBANK, INFY, ITC, KOTAKBANK, LT, RELIANCE, SBIN, TCS`

### Incompatible Symbols (39)
`ABB, ACC, ADANIENSOL, ADANIENT, ADANIGREEN, ADANIPORTS, ADANIPOWER, AMBUJACEM, APOLLOHOSP, APOLLOTYRE, BALKRISIND, BANDHANBNK, BANKBARODA, BANKINDIA, BATAINDIA, BEL, BERGEPAINT, BHARATFORG, BHEL, BIOCON, BLUEDART, BOSCHLTD, BPCL, BRITANNIA, CANBK, CANFINHOME, CGPOWER, CHAMBLFERT, CHOLAFIN, CIPLA, COALINDIA, COFORGE, COLPAL, CONCOR, COROMANDEL, CROMPTON, CUMMINSIND, HINDUNILVR, LICI`

## 3. Root Cause Analysis
1.  **Feature Set Shift:** Strategy v2.2 upgraded the feature set from 7 to 11 features. 
2.  **Partial Deployment:** A training run was initiated on 2026-08-17 but only completed for the top 10 symbols before the environment was frozen for Shadow Mode.
3.  **Registry Desync:** The database registry contains stale pointers to legacy models that do not meet the v2.2 "11-feature" requirement.
4.  **Shadow Report Discrepancy:** The report mentions 22 symbols. This is likely due to 12 legacy models passing some initial checks but ultimately failing inference due to feature vector length mismatch, which the Shadow Service might have logged as evaluations but they never reached signal generation.

## 4. Model Compatibility Verification
The certified configuration requires:
- **Engine:** RandomForestClassifier
- **Architecture:** max_depth=5, min_samples_leaf=10
- **Input:** 11 Features (trend_ema_cross, ema_200, sma_20, momentum_rsi, volatility_bb, volume_relative, smc_bullish_ob, smc_bearish_ob, ict_liquidity_void, market_volatility_z, market_cap_class)

**STATUS: CRITICAL** - 190 symbols require certified v2.2 models.

## 5. Decision
**MODEL_RETRAINING_REQUIRED**
Existing models for 190 symbols are either missing or architecturally incompatible with Strategy v2.2. Restoring from backups is not possible as no 11-feature models were found for these symbols in any repository directory.
