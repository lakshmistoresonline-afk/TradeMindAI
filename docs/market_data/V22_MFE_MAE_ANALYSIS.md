# V2.2 MFE / MAE FORENSIC ANALYSIS

## 1. Distribution Summary
- **Avg MFE**: 2.91%
- **Avg MAE**: -2.24%
- **Max MFE**: 7.34%
- **Max MAE**: -4.61%

## 2. Behavioral Findings
- **Losing trades with > 1% favorable move**: 14
- **Winners with > 1% adverse move**: 10
- **Near-target (> 2.5% MFE) but stopped**: 8
- **Immediate adverse (MFE < 0.1%)**: 3

## 3. Signal Detail (Sample Top MFEs)
| signal_id                  | symbol    | direction   |     mfe |        mae | terminal_state   |
|:---------------------------|:----------|:------------|--------:|-----------:|:-----------------|
| sig_ZYDUSLIFE_202605200000 | ZYDUSLIFE | LONG        | 7.33634 |  0         | TARGET_HIT       |
| sig_ZYDUSLIFE_202605070000 | ZYDUSLIFE | LONG        | 6.1994  | -1.45931   | TARGET_HIT       |
| sig_ZYDUSLIFE_202605080000 | ZYDUSLIFE | LONG        | 6.02999 | -1.61651   | TARGET_HIT       |
| sig_ZYDUSLIFE_202606180000 | ZYDUSLIFE | LONG        | 5.94498 | -0.0753767 | TARGET_HIT       |
| sig_ZYDUSLIFE_202605190000 | ZYDUSLIFE | LONG        | 5.7411  |  0         | TARGET_HIT       |
| sig_ZYDUSLIFE_202605150000 | ZYDUSLIFE | LONG        | 5.67712 | -0.388226  | TARGET_HIT       |
| sig_ZYDUSLIFE_202606220000 | ZYDUSLIFE | LONG        | 5.01494 | -0.579013  | TARGET_HIT       |
| sig_ZYDUSLIFE_202606300000 | ZYDUSLIFE | LONG        | 4.23615 | -2.33658   | TARGET_HIT       |
| sig_ZYDUSLIFE_202605260000 | ZYDUSLIFE | LONG        | 3.96571 | -0.615124  | TARGET_HIT       |
| sig_ZYDUSLIFE_202606260000 | ZYDUSLIFE | LONG        | 3.76793 | -0.572004  | TARGET_HIT       |