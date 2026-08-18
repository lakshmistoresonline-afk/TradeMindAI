# Strategy v2.2 Release Manifest

## 1. Governance
*   **Version ID**: `trademind-equity-v2.2`
*   **Status**: Certified for Controlled Production (Shadow/Paper)
*   **Release Date**: 2026-08-18

## 2. Quantitative Evidence
*   **OOS Win Rate**: 58.77%
*   **OOS Net EV**: 0.3262%
*   **Profit Factor**: 1.25
*   **Max Drawdown**: -12.4%

## 3. Implemented Safety Gates
*   **Drawdown Circuit Breaker**: Disables generation if cumulative shadow drawdown > 15%.
*   **Stale Data Gate**: Rejects signals if market data is > 24h old.
*   **Liquidity Gate**: Rejects symbols with < 10M Average Volume.
*   **Confidence Gate**: Minimum calibrated probability of 0.52.
*   **Fail-Safe**: System returns "No Trade" on any internal dependency failure.

## 4. Dependencies
*   **Model**: Champion Random Forest (Depth 5).
*   **Database**: Postgres (Shadow Schema v1).
*   **Worker**: Shadow Trading Engine v1.0.

## 5. Audit Trail
*   [PHASE4_FINAL_QUANTITATIVE_REPORT.md](file:///D:/TradeMindAI/PHASE4_FINAL_QUANTITATIVE_REPORT.md)
*   [FINAL_PRODUCTION_CERTIFICATION_REPORT.md](file:///D:/TradeMindAI/FINAL_PRODUCTION_CERTIFICATION_REPORT.md)
*   [production_certification.json](file:///D:/TradeMindAI/validation/results/production_certification.json)
