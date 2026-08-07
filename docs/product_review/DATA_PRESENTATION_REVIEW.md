# DATA PRESENTATION & EXPLAINABILITY REVIEW

## 📊 CORE PRINCIPLE: "SO WHAT?"
Every data point must answer the user's implicit question: *"How does this affect my trade?"*

### 1. The "DNA" Metaphor (Digital Twin)
**Current**: List of metrics.
**Improvement**: Use the **"Health-Posture-Momentum"** triad. Group technicals into "Posture," fundamentals into "Health," and price-action into "Momentum."

### 2. Highlighting Unusual Values
**Current**: Standard text color.
**Improvement**: If P/E Ratio is > 50 (Historical high), highlight in **Amber**. If ROI is in the top 1% of the sector, add a **Badge** (e.g. "Sector Leader").

### 3. Explaining Conflicting Indicators
**Current**: Signal is shown regardless of conflict.
**Improvement**: If RSI is Bearish but SMC is Bullish, add a **"Conflict Alert"** to the Consensus box. Explain why the AI chose one over the other (e.g., *"Price action and SMC priority overrides momentum oversold status"*).

---

## 🛡️ TRUST ANCHORS
- **Evidence Tags**: Attach small tags to the summary (e.g. `[VIA SMC]`, `[VIA FII FLOW]`).
- **Confidence Calibration**: Instead of just "85%," show a **Reliability Scale** (Low/Med/High) based on the specific symbol's 10Y backtest win-rate.
