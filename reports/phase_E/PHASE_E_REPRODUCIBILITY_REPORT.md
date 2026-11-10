# TradeMindAI — Phase E Reproducibility Report

**Audit Focus**: Research Experiment Provenance, Seeds, Versioning, and Audit Metadata

---

## 1. Reproducible Research Metadata Specification

Every historical backtest run, walk-forward cycle, and model training experiment logs a complete reproducibility payload:
- **`universe_version`**: `NIFTY500_2026_V1`
- **`feature_schema_version`**: `v5.6.2`
- **`strategy_version`**: `v2.2`
- **`random_seed`**: `42` (ensures deterministic tree ensemble and cross-validation splits)
- **`commit_hash`**: Full 40-character Git commit hash (e.g. `a97300dcd7669434be2833631803377b305d5f35`)
- **`model_artifact_hash`**: SHA-256 hash of `.joblib` model weight file
- **`run_timestamp`**: ISO 8601 UTC timestamp

---

## 2. Test Execution Evidence

- `test_phase_e_reproducible_run_metadata`: **PASSED**
