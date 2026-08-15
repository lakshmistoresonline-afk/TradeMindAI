# TRADEMIND AI — TERMINAL MASTER RUN GUIDE

This folder contains the authoritative scripts required to synchronize the TradeMind AI terminal with a fresh or updated Neon database. These scripts handle schema migrations, asset master population, and multi-segment signal generation (Equity, Futures, Options).

---

## 🛠️ EXECUTION PREREQUISITES
1. Ensure the Python virtual environment is active.
2. Verify that `backend/.env` contains the correct `POSTGRES_URL`.
3. Commands must be run from the **project root** directory.

---

## 🚀 SYNCHRONIZATION SEQUENCE

Execute the scripts in the following order to ensure data integrity:

### **STEP 1: Schema Migration**
Adds additive F&O columns and outcome tracking fields to the database.
```powershell
python terminal_master_scripts/01_migrate_neon_schema.py
```

### **STEP 2: Asset Master Population**
Populates the `stocks` table with Nifty 200 constituents, lot sizes, and F&O flags.
```powershell
python terminal_master_scripts/02_populate_stocks_master.py
```

### **STEP 3: Instrument Seeding**
Populates the `instruments` table with current derivative contract definitions.
```powershell
python terminal_master_scripts/03_seed_derivative_instruments.py
```

### **STEP 4: Live Signal Generation**
Generates fresh active setups for Equity, Futures, and Options segments.
```powershell
python terminal_master_scripts/04_generate_live_signals.py
```

### **STEP 5: Historical Archive Population**
Injects forensically accurate resolved signals for performance auditing.
```powershell
python terminal_master_scripts/05_generate_historical_archive.py
```

---

## 📊 VERIFICATION
After running Step 5, refresh your terminal at:
[https://com-webcraft-trademindai-c8f75.web.app](https://com-webcraft-trademindai-c8f75.web.app)

**Check for:**
- **Dashboard**: 3 separate carousels (Equity, Futures, Options) populated.
- **Signals Tab**: Ability to switch between asset classes.
- **History Tab**: Resolved signals visible in the Audit Log.
- **Data Integrity**: Verified entry vs outcome prices with correct lot-size logic.

---

## 🛡️ DATABASE SAFETY
- These scripts are **ADDITIVE** only. 
- They will not delete existing historical data.
- Signal IDs are prefixed with `master_` or `audit_` to prevent collisions with organic AI signals.
