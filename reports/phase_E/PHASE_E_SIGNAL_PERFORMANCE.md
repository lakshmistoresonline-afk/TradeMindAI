# TradeMindAI — Phase E Signal Performance Report

**Service Component**: [backend/services/outcome_service.py](file:///D:/TradeMindAI/backend/services/outcome_service.py) & [backend/services/signal_quality_service.py](file:///D:/TradeMindAI/backend/services/signal_quality_service.py)

---

## 1. Strategy Outcome Performance Metrics

Strategy-level research outcome metrics recorded across audited signal executions:
- **Total Signals Generated**: Total signals passing publication gates.
- **Completed Outcomes**: Signals reaching `TARGET_HIT` or `STOP_LOSS`.
- **Win Rate**: $\frac{\text{Target Hit Count}}{\text{Completed Outcomes Count}} \times 100\%$.
- **Loss Rate**: $\frac{\text{Stop Loss Count}}{\text{Completed Outcomes Count}} \times 100\%$.
- **Neutral / Unresolved Outcomes**: Signals in `EXPIRED`, `CANCELLED`, or `AMBIGUOUS` states.
- **Average Return / Expected Value ($EV$)**:
  $$EV = (P_{\text{win}} \times \text{Reward}) - ((1 - P_{\text{win}}) \times \text{Risk})$$
- **Profit Factor**: $\frac{\text{Gross Wins}}{\text{Gross Losses}}$.
- **Max Drawdown**: Peak-to-trough decline in cumulative strategy equity.

---

## 2. Hard Quality Publication Gate

Signal publication is restricted to signals passing `SignalQualityService.should_publish()`:
- `calibrated_probability >= 0.52`
- Champion model test size $\ge 20$
- ROC AUC $> 0.52$ (SWING) / $> 0.65$ (LONG)
