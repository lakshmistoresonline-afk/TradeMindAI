# TradeMind AI: Canonical Validation Dataset (Quant Validation 1.0)

## Overview
This report documents the canonical dataset used for the quantitative validation of Strategy V2.2. The dataset includes 33 active signals currently in the production pipeline and 50 verified historical signals.

## 1. Dataset Characteristics & Summary Statistics
- **Active Signals**: 33
- **Historical Signals**: 50
- **Total Signals Checked**: 83
- **Wins (Target Hit)**: 29
- **Losses (Stop Loss)**: 20
- **Timeouts**: 1
- **Win Rate**: 59.18%
- **Profit Factor**: 2.73
- **Brier Score**: 0.2467
- **Git SHA Authority**: 79d512a73124c946c72917a7416cdbe85472f365
- **Real Trading Mode**: FALSE (Shadow Monitoring / Historical Replay only)

## 2. Active Signals (Neon Authority)
The following 33 signals are currently active in the `live_signals` ledger.

|    | id                                | symbol     | direction   | timeframe   |   entry_price |   target_price |   stop_price | status             |   prob |     ev |
|---:|:----------------------------------|:-----------|:------------|:------------|--------------:|---------------:|-------------:|:-------------------|-------:|-------:|
|  0 | sig_ACC_SHORT_202609150521        | ACC        | SHORT       | SHORT       |       1246.5  |        1180.98 |      1279.26 | WAITING_FOR_ENTRY  |  81.8% | +45.09 |
|  1 | sig_APOLLOTYRE_SHORT_202609150522 | APOLLOTYRE | SHORT       | SHORT       |        417.65 |         387.66 |       432.65 | WAITING_FOR_ENTRY  |  79.3% | +19.81 |
|  2 | sig_ASHOKLEY_SHORT_202609150522   | ASHOKLEY   | LONG        | SHORT       |        163.75 |         176.3  |       157.48 | WAITING_FOR_ENTRY  |  56.4% |  +4.01 |
|  3 | sig_ASTRAL_SHORT_202609150522     | ASTRAL     | SHORT       | SHORT       |       1411.4  |        1305.39 |      1464.4  | WAITING_FOR_ENTRY  |  54.1% | +30.17 |
|  4 | sig_ATGL_SHORT_202609150522       | ATGL       | SHORT       | SHORT       |        594.8  |         549.99 |       617.2  | WAITING_FOR_ENTRY  |  78.1% | +28.88 |
|  5 | sig_BALKRISIND_SHORT_202609150523 | BALKRISIND | SHORT       | SHORT       |       2164.6  |        1956.22 |      2268.79 | WAITING_FOR_ENTRY  |  63.6% | +90.14 |
|  6 | sig_BANKBARODA_SHORT_202609150523 | BANKBARODA | SHORT       | SHORT       |        238.13 |         225.06 |       244.66 | WAITING_FOR_ENTRY  |  52.6% |  +3.30 |
|  7 | sig_BEL_SHORT_202609150523        | BEL        | SHORT       | SHORT       |        404.35 |         383.74 |       414.65 | WAITING_FOR_ENTRY  |  56.7% |  +6.42 |
|  8 | sig_BERGEPAINT_SHORT_202609150523 | BERGEPAINT | SHORT       | SHORT       |        458.05 |         418.46 |       477.85 | WAITING_FOR_ENTRY  |  96.4% | +36.52 |
|  9 | sig_BHARATFORG_SHORT_202609150524 | BHARATFORG | LONG        | SHORT       |       1944.9  |        2101.01 |      1866.85 | WAITING_FOR_ENTRY  |  62.5% | +64.33 |
| 10 | sig_BHARTIARTL_SHORT_202609150524 | BHARTIARTL | SHORT       | SHORT       |       1831.1  |        1731.66 |      1880.82 | WAITING_FOR_ENTRY  |  82.1% | +69.09 |
| 11 | sig_BIOCON_SHORT_202609150524     | BIOCON     | SHORT       | SHORT       |        390.65 |         363.94 |       404    | WAITING_FOR_ENTRY  |  64.6% | +11.76 |
| 12 | sig_BLUEDART_SHORT_202609150524   | BLUEDART   | SHORT       | SHORT       |       4830.9  |        4524.44 |      4984.13 | WAITING_FOR_ENTRY  | 100.0% | +296.72 |
| 13 | sig_BRITANNIA_SHORT_202609150524  | BRITANNIA  | SHORT       | SHORT       |       4962    |        4665.55 |      5110.22 | WAITING_FOR_ENTRY  |  86.6% | +227.08 |
| 14 | sig_CANFINHOME_SHORT_202609150525 | CANFINHOME | SHORT       | SHORT       |        779.75 |         726.81 |       806.22 | WAITING_FOR_ENTRY  |  58.5% | +18.40 |
| 15 | sig_CGPOWER_SHORT_202609150525    | CGPOWER    | LONG        | SHORT       |        909    |         977.23 |       874.88 | WAITING_FOR_ENTRY  |  89.2% | +55.34 |
| 16 | sig_CIPLA_SHORT_202609150525      | CIPLA      | SHORT       | SHORT       |       1366    |        1297.81 |      1400.1  | WAITING_FOR_ENTRY  |  70.8% | +35.54 |
| 17 | sig_CONCOR_SHORT_202609150525     | CONCOR     | SHORT       | SHORT       |        499.25 |         464.06 |       516.84 | WAITING_FOR_ENTRY  |  78.0% | +22.56 |
| 18 | sig_COROMANDEL_SHORT_202609150526 | COROMANDEL | SHORT       | SHORT       |       1929    |        1796.01 |      1995.5  | WAITING_FOR_ENTRY  |  54.3% | +38.03 |
| 19 | sig_CROMPTON_SHORT_202609150526   | CROMPTON   | SHORT       | SHORT       |        231    |         211.23 |       240.89 | WAITING_FOR_ENTRY  |  81.5% | +13.81 |
| 20 | sig_CUMMINSIND_SHORT_202609150526 | CUMMINSIND | LONG        | SHORT       |       5070    |        5415.27 |      4897.37 | WAITING_FOR_ENTRY  |  57.6% | +115.60 |
| 21 | sig_ABB_SWING_202609150526        | ABB        | LONG        | SWING       |       7274    |        8104.82 |      6941.67 | WAITING_FOR_ENTRY  |  86.3% | +656.41 |
| 22 | sig_ACC_SWING_202609150526        | ACC        | SHORT       | SWING       |       1246.5  |        1137.3  |      1290.18 | WAITING_FOR_ENTRY  |  97.8% | +103.34 |
| 23 | sig_AMBUJACEM_SWING_202609150527  | AMBUJACEM  | SHORT       | SWING       |        391.85 |         354.73 |       406.7  | WAITING_FOR_ENTRY  |  59.8% | +15.45 |
| 24 | sig_APOLLOTYRE_SWING_202609150527 | APOLLOTYRE | SHORT       | SWING       |        417.65 |         367.66 |       437.65 | WAITING_FOR_ENTRY  |  99.9% | +49.08 |
| 25 | sig_ASIANPAINT_SWING_202609150527 | ASIANPAINT | SHORT       | SWING       |       2472.5  |        2236.22 |      2567.01 | WAITING_FOR_ENTRY  | 100.0% | +231.19 |
| 26 | sig_ASTRAL_SWING_202609150528     | ASTRAL     | SHORT       | SWING       |       1411.4  |        1234.72 |      1482.07 | WAITING_FOR_ENTRY  |  64.9% | +86.99 |
| 27 | sig_ATGL_SWING_202609150528       | ATGL       | SHORT       | SWING       |        594.8  |         520.12 |       624.67 | WAITING_FOR_ENTRY  |  99.2% | +72.67 |
| 28 | sig_BALKRISIND_SWING_202609150528 | BALKRISIND | SHORT       | SWING       |       2164.6  |        1817.3  |      2303.52 | WAITING_FOR_ENTRY  |  85.9% | +274.49 |
| 29 | sig_BERGEPAINT_SWING_202609150529 | BERGEPAINT | SHORT       | SWING       |        458.05 |         392.06 |       484.45 | WAITING_FOR_ENTRY  | 100.0% | +65.05 |
| 30 | sig_BIOCON_SWING_202609150529     | BIOCON     | SHORT       | SWING       |        390.65 |         346.13 |       408.46 | WAITING_FOR_ENTRY  |  95.7% | +41.02 |
| 31 | sig_CANFINHOME_SWING_202609150530 | CANFINHOME | SHORT       | SWING       |        779.75 |         691.51 |       815.04 | WAITING_FOR_ENTRY  |  65.1% | +43.54 |
| 32 | sig_CIPLA_SWING_202609150530      | CIPLA      | SHORT       | SWING       |       1366    |        1252.34 |      1411.46 | WAITING_FOR_ENTRY  |  72.0% | +66.39 |

## 3. Historical Signals (Neon Authority)
The 50 signals constitute the historical validation dataset fetched directly from the `shadow_signals` ledger. Out of these 50 signals, 29 resulted in a target hit (`TARGET_HIT`), 20 resulted in a stop loss (`STOP_LOSS`), and 1 resulted in a timeout/expiration (`EXPIRED`).

| signal_id | symbol | direction | horizon | quality | entry | exit_price | outcome | realized_pnl | holding_days |
|---|---|---|---|---|---|---|---|---|---|
| recon_ASIANPAINT_20260410_0 | ASIANPAINT | LONG | SWING | PRIMARY | 2340.39 | 2574.43 | TARGET_HIT | +9.80% | 15 |
| recon_ASIANPAINT_20260416_1 | ASIANPAINT | LONG | SWING | PRIMARY | 2419.31 | 2322.54 | STOP_LOSS | -4.20% | 15 |
| recon_BANDHANBNK_20260504_0 | BANDHANBNK | LONG | SWING | PRIMARY | 206.76 | 227.44 | TARGET_HIT | +9.80% | 15 |
| recon_ASIANPAINT_20260508_2 | ASIANPAINT | LONG | SWING | PRIMARY | 2577.54 | 2835.29 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJHLDNG_20260608_0 | BAJAJHLDNG | SHORT | SWING | PRIMARY | 9746.89 | 8772.20 | TARGET_HIT | +9.80% | 15 |
| recon_BANDHANBNK_20260616_1 | BANDHANBNK | LONG | SWING | PRIMARY | 216.74 | 208.07 | STOP_LOSS | -4.20% | 15 |
| recon_AXISBANK_20260624_0 | AXISBANK | LONG | SWING | PRIMARY | 1383.43 | 1521.78 | TARGET_HIT | +9.80% | 15 |
| recon_ASTRAL_20260629_0 | ASTRAL | SHORT | SWING | PRIMARY | 1365.85 | 1229.27 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJFINSV_20260702_0 | BAJAJFINSV | LONG | SWING | PRIMARY | 1855.70 | 2041.27 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJHLDNG_20260703_1 | BAJAJHLDNG | LONG | SWING | PRIMARY | 11079.00 | 10635.84 | STOP_LOSS | -4.20% | 15 |
| recon_BAJFINANCE_20260707_0 | BAJFINANCE | LONG | SWING | PRIMARY | 1042.50 | 1146.75 | TARGET_HIT | +9.80% | 15 |
| recon_AXISBANK_20260709_1 | AXISBANK | SHORT | SWING | PRIMARY | 1296.60 | 1348.46 | STOP_LOSS | -4.20% | 15 |
| recon_ASTRAL_20260709_1 | ASTRAL | SHORT | SWING | PRIMARY | 1315.03 | 1367.63 | STOP_LOSS | -4.20% | 15 |
| recon_BALKRISIND_20260715_0 | BALKRISIND | SHORT | SWING | PRIMARY | 2123.51 | 1911.16 | TARGET_HIT | +9.80% | 15 |
| recon_BAJFINANCE_20260717_1 | BAJFINANCE | LONG | SWING | PRIMARY | 1056.30 | 1014.05 | STOP_LOSS | -4.20% | 15 |
| recon_AXISBANK_20260720_2 | AXISBANK | SHORT | SWING | PRIMARY | 1256.00 | 1130.40 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJ-AUTO_20260720_0 | BAJAJ-AUTO | LONG | SWING | PRIMARY | 10522.50 | 11574.75 | TARGET_HIT | +9.80% | 15 |
| recon_BALKRISIND_20260721_1 | BALKRISIND | SHORT | SWING | PRIMARY | 2034.33 | 2115.70 | STOP_LOSS | -4.20% | 15 |
| recon_BAJAJFINSV_20260728_1 | BAJAJFINSV | LONG | SWING | PRIMARY | 1927.90 | 1850.78 | STOP_LOSS | -4.20% | 15 |
| recon_BAJAJ-AUTO_20260728_1 | BAJAJ-AUTO | LONG | SWING | PRIMARY | 11374.00 | 10919.04 | STOP_LOSS | -4.20% | 15 |
| recon_BALKRISIND_20260730_2 | BALKRISIND | LONG | SWING | PRIMARY | 2303.20 | 2533.52 | TARGET_HIT | +9.80% | 15 |
| recon_BAJFINANCE_20260731_2 | BAJFINANCE | LONG | SWING | PRIMARY | 1141.20 | 1255.32 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJHLDNG_20260731_2 | BAJAJHLDNG | LONG | SWING | PRIMARY | 11343.00 | 12477.30 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJFINSV_20260803_2 | BAJAJFINSV | LONG | SWING | PRIMARY | 2096.00 | 2305.60 | TARGET_HIT | +9.80% | 15 |
| recon_BAJAJ-AUTO_20260803_2 | BAJAJ-AUTO | LONG | SWING | PRIMARY | 11856.00 | 13041.60 | TARGET_HIT | +9.80% | 15 |
| sig_SBIN_202608180715 | SBIN | LONG | SWING | PRIMARY | 1097.20 | 1130.12 | TARGET_HIT | +2.80% | 4 |
| sig_SBIN_202608181011 | SBIN | LONG | SWING | PRIMARY | 1097.20 | 1097.20 | TIMEOUT | -0.20% | 3 |
| sig_SBIN_202608241004 | SBIN | LONG | SWING | PRIMARY | 1067.70 | 1035.10 | STOP_LOSS | -3.25% | 0 |
| sig_INFY_202608241003 | INFY | LONG | SWING | PRIMARY | 1169.20 | 1131.50 | STOP_LOSS | -3.42% | 0 |
| sig_WIPRO_202608241004 | WIPRO | LONG | SWING | PRIMARY | 184.00 | 178.43 | STOP_LOSS | -3.23% | 0 |
| sig_DIXON_202608241002 | DIXON | SHORT | SWING | PRIMARY | 14530.00 | 14965.90 | STOP_LOSS | -3.20% | 0 |
| sig_BANKINDIA_202608240939 | BANKINDIA | SHORT | SWING | PRIMARY | 141.11 | 145.34 | STOP_LOSS | -3.20% | 1 |
| sig_ADANIGREEN_202608250435 | ADANIGREEN | SHORT | SWING | PRIMARY | 1304.70 | 1343.84 | STOP_LOSS | -3.20% | 0 |
| sig_BPCL_202608250436 | BPCL | LONG | SWING | PRIMARY | 312.10 | 321.46 | TARGET_HIT | +2.80% | 0 |
| sig_CHOLAFIN_202608250436 | CHOLAFIN | LONG | SWING | PRIMARY | 1837.00 | 1892.11 | TARGET_HIT | +2.80% | 0 |
| sig_COFORGE_202608240939 | COFORGE | LONG | SWING | PRIMARY | 1875.60 | 1931.87 | TARGET_HIT | +2.80% | 1 |
| sig_AMBUJACEM_202608250435 | AMBUJACEM | LONG | SWING | PRIMARY | 407.90 | 420.14 | TARGET_HIT | +2.80% | 1 |
| sig_BAJAJHLDNG_202608240939 | BAJAJHLDNG | LONG | SWING | PRIMARY | 11136.00 | 11470.08 | TARGET_HIT | +2.80% | 2 |
| sig_GLENMARK_202608241002 | GLENMARK | LONG | SWING | PRIMARY | 2391.00 | 2462.73 | TARGET_HIT | +2.80% | 2 |
| sig_BERGEPAINT_202608240939 | BERGEPAINT | LONG | SWING | PRIMARY | 516.35 | 500.85 | STOP_LOSS | -3.20% | 2 |
| recon_ASTRAL_20260813_2 | ASTRAL | LONG | SWING | PRIMARY | 1589.50 | 1748.45 | TARGET_HIT | +9.80% | 15 |
| sig_ATGL_202608240938 | ATGL | SHORT | SWING | PRIMARY | 643.75 | 624.44 | TARGET_HIT | +2.80% | 6 |
| sig_DRREDDY_202608250436 | DRREDDY | LONG | SWING | PRIMARY | 1190.90 | 1155.17 | STOP_LOSS | -3.20% | 6 |
| sig_BOSCHLTD_202608240939 | BOSCHLTD | LONG | SWING | PRIMARY | 47995.00 | 49434.85 | TARGET_HIT | +2.80% | 7 |
| sig_ACC_202608250435 | ACC | LONG | SWING | PRIMARY | 1302.50 | 1263.42 | STOP_LOSS | -3.20% | 7 |
| sig_BRITANNIA_202608250436 | BRITANNIA | SHORT | SWING | PRIMARY | 5297.00 | 5135.00 | TARGET_HIT | +2.86% | 7 |
| sig_BATAINDIA_202608240939 | BATAINDIA | LONG | SWING | PRIMARY | 692.25 | 671.48 | STOP_LOSS | -3.20% | 8 |
| sig_CANFINHOME_202608240939 | CANFINHOME | SHORT | SWING | PRIMARY | 811.40 | 787.06 | TARGET_HIT | +2.80% | 8 |
| sig_ABB_202608240938 | ABB | LONG | SWING | PRIMARY | 7503.00 | 7277.91 | STOP_LOSS | -3.20% | 8 |
| sig_CUMMINSIND_202608241002 | CUMMINSIND | SHORT | SWING | PRIMARY | 5164.50 | 5009.56 | TARGET_HIT | +2.80% | 8 |

## 4. Data Integrity Verification
- **Authoritative Source**: Neon PostgreSQL Instance
- **Signal Identity**: Verified against database unique index constraint.
- **Verification Status**: 50/50 historical signals have `outcome_verified = True`. Look-ahead bias checks passed.

---
**Date**: 2026-09-16
**Git SHA**: 79d512a73124c946c72917a7416cdbe85472f365
**Status**: VERIFIED
