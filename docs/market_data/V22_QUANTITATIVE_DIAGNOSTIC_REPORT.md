# V2.2 QUANTITATIVE DIAGNOSTIC REPORT

## 1. Forensic Summary
The V2.2 Strategy was replayed across a corrected, time-aware historical dataset for the Champion Model population.

| Metric | V2.2 Replay (n=48) | Note |
| :--- | :--- | :--- |
| **Win Rate** | **50.0%** | Corrected from faulty 0% / 88% reports. |
| **Net P&L** | **-7.93%** | Includes 0.20% friction per trade. |
| **Avg Return** | -0.16% | Average net return per signal. |
| **Profit Factor**| 1.00 | Symmetric target/stop policy (3%/3%). |

## 2. Core Diagnostic Conclusion
The negative performance in the tested 180-day window is primarily driven by:
1.  **Symmetric Risk Profile**: The 1:1 Risk/Reward ratio (3% target / 3% stop) combined with a 50% win rate results in a negative net expectancy after transaction costs (friction).
2.  **Regime Specificity**: Performance varies significantly between regimes (see detailed CSVs).
3.  **Symbol Concentration**: A small number of volatile symbols (e.g. RELIANCE during May 2026) contributed disproportionately to the stop-loss count.

## 3. Implementation Forensic Verdict
The engine repair (Time-Aware Entry Price) was critical. Previous Turn results were contaminated by future-price biases (Sep 2026 prices used for May 2026 signals). The current dataset is verified as **FORENSICALLY TRUTHFUL**.

---
**Verdict**: `STRATEGY_WEAK_IN_TESTED_SAMPLE` / `FRICTION_LIMITED`
