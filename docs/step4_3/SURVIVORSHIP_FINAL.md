# Step 4.3.1 Survivorship Audit Final

## Methodology
The backtest uses the **current NIFTY 200 constituents** (as of August 2026) applied to historical data starting from 2017. 

## Risk Assessment
**STATUS**: `SURVIVORSHIP_BIAS_WARNING`

Because point-in-time historical constituent lists were unavailable during this validation phase, the strategy has only been tested on companies that were successful enough to remain in the NIFTY 200 until 2026. Companies that were delisted, merged, or demoted from the index between 2017 and 2026 are excluded.

## Quantitative Sensitivity
- **Impact**: Typically, survivorship bias can inflate annual returns by 2-5%. 
- **Mitigation**: The strategy's high liquidity filter (10M Average Volume) partially mitigates this by focusing on robust large-cap stocks which are less prone to delisting than small-caps.

## Conclusion
The results should be interpreted as the performance of the strategy on the **currently strongest 200 companies in India**. Future validation in Phase 8 should incorporate point-in-time historical membership if institutional data providers are integrated.
