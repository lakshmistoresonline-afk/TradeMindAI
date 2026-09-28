# TradeMind AI — ML Architecture V3

---

## 1. Ensemble Architecture

The Machine Learning engine in TradeMindAI combines a **Two-Stage Selective Meta-Labeling Ensemble**:

```text
FEATURE MATRIX (8 Families)
           │
           ▼
STAGE 1: DIRECTION MODEL (ExtraTrees / XGBoost Classifier)
           │ P(LONG), P(SHORT), P(NEUTRAL)
           ▼
STAGE 2: META-LABEL MODEL (Selective Tradeability Filter)
           │ P(TRADEABLE) >= 0.70
           ▼
VENN-ABERS CALIBRATOR (Inductive Conformal Bounds)
           │
           ▼
PUBLISHED SIGNAL PROBABILITY
```

---

## 2. Validation & Purging Rules

1. **Chronological Splitting**: Random K-Fold cross-validation is strictly prohibited due to temporal leakage.
2. **Purged Time-Series Cross-Validation**: Overlapping trade label windows between training and test sets are purged.
3. **Embargo Periods**: A 5-day embargo is enforced after every test split before subsequent training folds begin.
