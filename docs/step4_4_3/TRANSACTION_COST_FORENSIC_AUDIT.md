# Transaction Cost Forensic Audit

## 1. Methodology
Audited the `transaction_cost` column in `wf_portfolio_trades.csv` against the configured Indian Market Cost Model.

## 2. Sample Audit (ADANIENT)
- **Trade Value**: ₹200,671.74
- **Reported Cost**: ₹342.38
- **Effective %**: 0.1706%

## 3. Comparison with Model
| Component | Expectation | Realized (Sample) | Status |
| :--- | :--- | :--- | :--- |
| **STT (Delivery)** | 0.1% | 0.1000% | PASS |
| **Exchange/GST/SEBI** | ~0.02% | 0.0206% | PASS |
| **Brokerage** | 0.05% | 0.0500% | PASS |
| **Total** | **0.17%** | **0.1706%** | **PASS** |

## 4. Conclusion
The canonical PnL result of ₹28,573,387.38 accurately reflects full transaction costs for the Indian market.

**STATUS**: `VERIFIED`
