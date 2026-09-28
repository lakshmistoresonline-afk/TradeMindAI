# TradeMind AI — Market Regime Model

---

## 1. Canonical Regime Taxonomy

TradeMindAI enforces one single, unified market regime taxonomy:

```text
BULL
BEAR
SIDEWAYS
HIGH_VOLATILITY
LOW_VOLATILITY
TRANSITION
```

---

## 2. Gaussian Hidden Markov Model (HMM)

Micro-regimes are classified using a 3-State Gaussian Hidden Markov Model trained on daily NIFTY 200 return and volatility distributions:
- **State 0 (`STEADY_BULL_TREND`)**: Low volatility, positive return drift.
- **State 1 (`HIGH_VOLATILITY_CHOP`)**: Elevated ATR, mean-reverting price action.
- **State 2 (`BEAR_DOWNTREND`)**: Negative return drift, expanding volume.
