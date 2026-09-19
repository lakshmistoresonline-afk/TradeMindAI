# Stop-Loss Signal Forensics

## Executive Summary
Analyzed 20 STOP_LOSS signals from the V2.2 population.

### Failure Mechanism Distribution
| failure_classification   |   count |
|:-------------------------|--------:|
| EARLY_NOISE_STOP         |       9 |
| IMMEDIATE_FAILURE        |       5 |
| LATE_REVERSAL            |       3 |
| NEAR_TARGET_REVERSAL     |       3 |

### Detailed Forensic Table
| signal_id                   | symbol     | direction   | timestamp                  |    entry |      stop |    target |   stop_dist_pct |   target_dist_pct |   rr | conviction   |     prob | regime   |    mae |   mfe | failure_classification   |
|:----------------------------|:-----------|:------------|:---------------------------|---------:|----------:|----------:|----------------:|------------------:|-----:|:-------------|---------:|:---------|-------:|------:|:-------------------------|
| recon_BAJAJ-AUTO_20260728_1 | BAJAJ-AUTO | LONG        | 2026-07-27 18:30:00        | 11374    | 10919     | 12511.4   |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -1.92 |  4.79 | LATE_REVERSAL            |
| recon_BAJAJFINSV_20260728_1 | BAJAJFINSV | LONG        | 2026-07-27 18:30:00        |  1927.9  |  1850.78  |  2120.69  |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -1.85 |  9.87 | NEAR_TARGET_REVERSAL     |
| recon_BAJAJHLDNG_20260703_1 | BAJAJHLDNG | LONG        | 2026-07-02 18:30:00        | 11079    | 10635.8   | 12186.9   |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -7.25 |  1.25 | EARLY_NOISE_STOP         |
| recon_BANDHANBNK_20260616_1 | BANDHANBNK | LONG        | 2026-06-15 18:30:00        |   216.74 |   208.07  |   238.414 |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -4.26 |  0.64 | EARLY_NOISE_STOP         |
| sig_BANKINDIA_202608240939  | BANKINDIA  | SHORT       | 2026-08-24 09:39:15.185038 |   141.11 |   145.343 |   136.877 |               3 |                 3 |  1   |              | 0.572325 | BULLISH  |  -3.25 |  0.23 | EARLY_NOISE_STOP         |
| sig_BATAINDIA_202608240939  | BATAINDIA  | LONG        | 2026-08-24 09:39:19.111573 |   692.25 |   671.482 |   713.018 |               3 |                 3 |  1   |              | 0.581128 | BULLISH  |  -3.27 |  0.11 | IMMEDIATE_FAILURE        |
| sig_BERGEPAINT_202608240939 | BERGEPAINT | LONG        | 2026-08-24 09:39:24.325891 |   516.35 |   500.86  |   531.841 |               3 |                 3 |  1   |              | 0.58887  | BULLISH  |  -3    |  0.2  | EARLY_NOISE_STOP         |
| sig_DIXON_202608241002      | DIXON      | SHORT       | 2026-08-24 10:02:36.618518 | 14530    | 14965.9   | 14094.1   |               3 |                 3 |  1   |              | 0.553418 | BULLISH  |  -3.17 |  0.89 | EARLY_NOISE_STOP         |
| sig_INFY_202608241003       | INFY       | LONG        | 2026-08-24 10:03:24.385049 |  1169.2  |  1134.12  |  1204.28  |               3 |                 3 |  1   |              | 0.712123 | BULLISH  |  -3.3  |  0    | IMMEDIATE_FAILURE        |
| recon_ASIANPAINT_20260416_1 | ASIANPAINT | LONG        | 2026-04-15 18:30:00        |  2419.31 |  2322.54  |  2661.24  |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -1.4  |  6.72 | LATE_REVERSAL            |
| recon_ASTRAL_20260709_1     | ASTRAL     | SHORT       | 2026-07-08 18:30:00        |  1315.03 |  1367.63  |  1183.53  |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -4.31 |  0.23 | EARLY_NOISE_STOP         |
| recon_AXISBANK_20260709_1   | AXISBANK   | SHORT       | 2026-07-08 18:30:00        |  1296.6  |  1348.46  |  1166.94  |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -3.95 |  5.97 | LATE_REVERSAL            |
| recon_BAJFINANCE_20260717_1 | BAJFINANCE | LONG        | 2026-07-16 18:30:00        |  1056.3  |  1014.05  |  1161.93  |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  |  -4.17 |  1.7  | EARLY_NOISE_STOP         |
| recon_BALKRISIND_20260721_1 | BALKRISIND | SHORT       | 2026-07-20 18:30:00        |  2034.33 |  2115.7   |  1830.9   |               4 |                10 |  2.5 |              | 0.75     | UNKNOWN  | -12.71 |  2.41 | EARLY_NOISE_STOP         |
| sig_DRREDDY_202608250436    | DRREDDY    | LONG        | 2026-08-25 04:36:44.920792 |  1190.9  |  1155.17  |  1226.63  |               3 |                 3 |  1   |              | 0.573403 | BULLISH  |  -3.06 |  0.35 | EARLY_NOISE_STOP         |
| sig_WIPRO_202608241004      | WIPRO      | LONG        | 2026-08-24 10:04:56.126079 |   184    |   178.48  |   189.52  |               3 |                 3 |  1   |              | 0.589229 | BULLISH  |  -3.03 |  0    | IMMEDIATE_FAILURE        |
| sig_ABB_202608240938        | ABB        | LONG        | 2026-08-24 09:38:34.906715 |  7503    |  7277.91  |  7728.09  |               3 |                 3 |  1   |              | 0.550834 | BULLISH  |  -3.23 |  2.61 | NEAR_TARGET_REVERSAL     |
| sig_ACC_202608250435        | ACC        | LONG        | 2026-08-25 04:35:15.912708 |  1302.5  |  1263.42  |  1341.58  |               3 |                 3 |  1   |              | 0.629816 | BULLISH  |  -3.11 |  2.73 | NEAR_TARGET_REVERSAL     |
| sig_ADANIGREEN_202608250435 | ADANIGREEN | SHORT       | 2026-08-25 04:35:22.197697 |  1304.7  |  1343.84  |  1265.56  |               3 |                 3 |  1   |              | 0.663439 | BULLISH  |  -3    |  0.11 | IMMEDIATE_FAILURE        |
| sig_SBIN_202608241004       | SBIN       | LONG        | 2026-08-24 10:04:21.767664 |  1067.7  |  1035.67  |  1099.73  |               3 |                 3 |  1   |              | 0.578342 | BULLISH  |  -3.33 |  0    | IMMEDIATE_FAILURE        |