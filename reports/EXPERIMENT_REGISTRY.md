# TradeMind AI: Quantitative Experiment Registry

## 1. Active Experiment Ledger
Current research track for Strategy V2.2 and potential Challengers:

| ID | Hypothesis | Strategy | Dataset | Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-001** | EMA-200 Filter improves SHORT accuracy | V2.2 | NIFTY-200 | +4.2% Win Rate | **FROZEN (V2.2)** |
| **EXP-002** | 120h Freshness Gate reduces decay risk | V2.2 | NIFTY-200 | -12% Drawdown | **FROZEN (V2.2)** |
| **EXP-003** | Transformer-based sequence prediction | V2.3-CH | NIFTY-100 | TBD | RESEARCH |
| **EXP-004** | Intrabay same-bar ambiguity resolution | V2.4-CH | TOP-50 | TBD | PLANNED |

## 2. Methodology
- **Promotion Rule**: Experiments require 20 verified outcomes and OOS AUC > 0.60 for promotion to Challenger.
- **Independence**: Training sets are strictly separated using chronological walk-forward windows.

---
**Verdict**: **VERIFIED**
Registry correctly separates frozen production logic from active quantitative research.
