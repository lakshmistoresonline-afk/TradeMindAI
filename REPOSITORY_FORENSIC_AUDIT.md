# TradeMind AI: Repository Forensic Audit

## Audit Summary
Performed on 2026-09-12. This audit identifies critical accuracy-damaging fallbacks, legacy mock data, and hardcoded logic that compromises the integrity of the TradeMind AI system. Multiple findings directly impact the frozen V2.2 logic, requiring immediate remediation to ensure institutional-grade signal quality.

## V2.2 Freeze Status & Audit Scope
- `backend/services/signal_engine.py`: **AUDITED** (Multiple V2.2 Violations)
- `backend/services/outcome_engine.py`: **AUDITED** (Multiple V2.2 Violations)
- `backend/services/risk_engine.py`: **AUDITED** (Multiple V2.2 Violations)
- `backend/core/risk.py`: **AUDITED** (Minor Logic)
- `backend/core/config.py`: **AUDITED** (Hardcoded Defaults)

## Detailed Findings

### 1. Data Integrity: Probability Pipeline Fallback 0.5
- **Defect**: Inference defaults to 0.5 when model metadata or regime sentiment is missing.
- **File**: `backend/services/signal_engine.py`
- **Location**: Lines 61, 62, 111
- **Evidence**: `prob_up = ml_metadata.get("calibrated_probability_up", 0.5)`, `regime_prob = 0.5`.
- **Severity**: Critical.
- **Effect on Accuracy**: Generates "neutral noise" as a genuine signal probability, skewing Expected Value (EV) calculations.
- **Effect on Production**: Can trigger signals based on missing data rather than model confidence.
- **Recommended Action**: Abort signal generation and return `None` if model metadata is incomplete.
- **Touches Frozen V2.2 Logic**: **YES** (SignalEngine is core V2.2).

### 2. Strategy V2.2: Hardcoded Risk Gates
- **Defect**: Arbitrary thresholds for signal rejection and momentum filtering.
- **File**: `backend/services/signal_engine.py`
- **Location**: Lines 140, 163, 166, 167
- **Evidence**: `magnitude < (atr * 0.5)`, `calibrated_prob < 0.52`, `coverage_score < 0.5`, `calibrated_prob < 0.65` (High Vol).
- **Severity**: High.
- **Effect on Accuracy**: Rejects potentially valid signals or accepts weak ones based on non-optimized constants.
- **Effect on Production**: Sub-optimal trade frequency and risk-alignment.
- **Recommended Action**: Move thresholds to `config.py` and validate per horizon/timeframe.
- **Touches Frozen V2.2 Logic**: **YES**.

### 3. Data Integrity: Hardcoded ATR Fallback
- **Defect**: Fallback to `price * 0.02` when ATR is missing from feature store.
- **File**: `backend/services/signal_engine.py`
- **Location**: Line 78
- **Evidence**: `atr = last_features.get("ATR") or ... or (price * 0.02)`.
- **Severity**: High.
- **Effect on Accuracy**: Distorts stop-loss and target placement, leading to incorrect R/R metrics.
- **Effect on Production**: Risk of premature stops or unreachable targets.
- **Recommended Action**: Enforce ATR presence in `FeatureStore`; reject signal if volatility data is missing.
- **Touches Frozen V2.2 Logic**: **YES**.

### 4. Financial Accuracy: Hardcoded P&L Frictions
- **Defect**: Fixed percentages for fees, slippage, and friction in outcome evaluation.
- **File**: `backend/services/outcome_engine.py`
- **Location**: Lines 190-192
- **Evidence**: `friction_pct = 0.20`, `fees_pct = 0.10`, `slippage_pct = 0.10`.
- **Severity**: Medium.
- **Effect on Accuracy**: Reported Net P&L does not reflect real-world variable costs (STT, varying slippage).
- **Effect on Production**: Misleading performance metrics in "Forensic Playback".
- **Recommended Action**: Implement a dynamic `CostModel` that accounts for order size and instrument type.
- **Touches Frozen V2.2 Logic**: **YES**.

### 5. Risk Management: Hardcoded Defaults & Thresholds
- **Defect**: Default capital and risk thresholds hardcoded in engine logic.
- **File**: `backend/services/risk_engine.py`
- **Location**: Lines 10, 11, 44, 45
- **Evidence**: `risk_per_trade = 0.02`, `capital = 1000000.0`, `risk_pct > 15`, `risk_pct < 0.5`.
- **Severity**: Medium.
- **Effect on Accuracy**: Position sizing and risk grading are not adaptive to user portfolio settings.
- **Effect on Production**: Rigid risk management that may not suit all market regimes.
- **Recommended Action**: Fetch capital and risk tolerance from user profile/settings.
- **Touches Frozen V2.2 Logic**: **YES**.

### 6. Legacy Logic: Dummy Option Chains
- **Defect**: Fallback to `_dummy_chain` when provider fails.
- **File**: `backend/infrastructure/repositories/yfinance_provider.py`
- **Location**: `_dummy_chain` method and its usages.
- **Evidence**: `return self._dummy_chain(symbol)` with zeroed-out values.
- **Severity**: Medium.
- **Effect on Accuracy**: Zeroed-out Greeks and OI data in F&O intelligence.
- **Effect on Production**: UI shows "0.0" or "1.0" for critical options metrics (PCR, Max Pain).
- **Recommended Action**: Mark as `DATA_UNAVAILABLE` and disable dependent intelligence features.
- **Touches Frozen V2.2 Logic**: No (Infrastructure layer), but consumed by V2.2 services.

### 7. Data Integrity: Synthetic Signal Injection
- **Defect**: Script for force-populating "production" signals using random distributions.
- **File**: `force_production_population.py`
- **Location**: Throughout the file.
- **Evidence**: Use of `random.randint`, `random.choices` for P&L, outcomes, and timestamps.
- **Severity**: Critical.
- **Effect on Accuracy**: Corrupts production databases with fake performance history.
- **Effect on Production**: Invalidates performance audits and AI training sets if leaked into `signals` collection.
- **Recommended Action**: Move to `tests/` or `scripts/dev/` and add strict environment checks.
- **Touches Frozen V2.2 Logic**: No.

### 8. Accuracy Defect: Placeholder Fundamental Intelligence
- **Defect**: Hardcoded fundamental and institutional scores.
- **File**: `backend/services/stock_intelligence_service.py`
- **Location**: Lines 37, 41
- **Evidence**: `fundamental_score = 0.5`, `composite_intelligence_score = 0.5`.
- **Severity**: Medium.
- **Effect on Accuracy**: Dilutes the "Composite Score" with arbitrary mid-point data.
- **Effect on Production**: Users see "Neutral" fundamental outlooks for all stocks.
- **Recommended Action**: Connect to a real fundamental data provider or mark as `N/A`.
- **Touches Frozen V2.2 Logic**: Indirectly (consumed via `StockIntelligence`).

### 9. Development Risk: Random ML Verification
- **Defect**: Generation of synthetic features for report validation if DB is empty.
- **File**: `ml/test_calibration.py`, `ml/generate_calibration_report.py`
- **Evidence**: `features={"f1": np.random.random()}`, `target=1.0 if np.random.random() > 0.5`.
- **Severity**: Medium.
- **Effect on Accuracy**: Calibration reports may show success based on fake random data.
- **Recommended Action**: Require a minimal "Golden Dataset" for all ML verification scripts.
- **Touches Frozen V2.2 Logic**: No.

### 10. Frontend: Mock Data Exposure
- **Defect**: "SAMPLE" chips and hardcoded letter spacing/transparency.
- **File**: `web/src/pages/EquitySignals.tsx`, `web/src/components/Layout.tsx`
- **Evidence**: `{isSample && <Chip label="SAMPLE" ... />}`, `letterSpacing: 0.5`.
- **Severity**: Low.
- **Effect on Production**: Cluttered UI and potential exposure of engineering test states to end-users.
- **Recommended Action**: Clean up UI constants and ensure `isSample` logic is strictly gated to `development` environments.
- **Touches Frozen V2.2 Logic**: No.

## Audit Verdict
The system demonstrates significant functional maturity but suffers from "Fallback Decay"—a pattern of silent failures where missing real-world data is replaced by neutral constants (0.5). This is particularly dangerous in the **SignalEngine (V2.2)** where it impacts expected value and risk calculations. **Hardening of these fallbacks is the #1 priority for production readiness.**
