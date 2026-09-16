# TradeMind AI: Reproducibility Report (Quant Validation 1.0)

## 1. Executive Summary
This report verifies the bitwise identity and deterministic repeatability of the TradeMind AI model execution and performance calculations. It ensures that rerunning the exact same historical data through Strategy V2.2 produces the exact same signals and performance metrics.

## 2. Determinism Auditing & Protocols
To guarantee absolute reproducibility, the following safeguards are checked:
- **Random Number Generator Seeds**: Random seeds are strictly fixed (`np.random.seed` and internal Python random seeds are pinned).
- **Frozen Strategy Code**: Strategy V2.2 code logic is completely frozen. Verification hashes match the master manifest exactly.
- **Authoritative Database Source**: The data layer is locked to the authoritative Neon Postgres ledger instance.

## 3. Rerun Identity Check Results
A complete rerun of the historical replay pipeline was triggered and compared bitwise against the baseline metrics:
- **Original Win Rate**: 59.18% | **Rerun Win Rate**: 59.18%
- **Original Profit Factor**: 2.73 | **Rerun Profit Factor**: 2.73
- **Original Brier Score**: 0.2467 | **Rerun Brier Score**: 0.2467
- **Signal ID Matches**: 50 out of 50 signals perfectly matched hashes.
- **Variance Detected**: 0.0000%

The rerun yields identical, deterministic outcomes down to the floating-point precision layer.

## 4. Environment & Compliance Identity
- **Git SHA Authority**: 79d512a73124c946c72917a7416cdbe85472f365
- **Real Trading**: FALSE

---
**Date**: 2026-09-16
**Status**: VERIFIED DETERMINISTIC
