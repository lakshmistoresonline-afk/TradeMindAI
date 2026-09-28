# TradeMind AI — Data Source Requirements & Quality Protocols

---

## 1. Primary Data Sources

| Data Domain | Primary Source | Secondary Fallback | Refresh Rate | Historical Depth |
| :--- | :--- | :--- | :--- | :--- |
| **NSE Spot Prices** | Yahoo Finance API (`.NS`) | NSE Direct Feed / Google Finance | 15 Minutes | 10 Years |
| **Options Open Interest** | NSE Options Chain API | Local Options Model | 15 Minutes | 3 Years |
| **Firestore Database** | Google Cloud Firestore | Local Operational SQLite | Real-Time | Full History |
| **Corporate Filings** | BSE/NSE Disclosures API | News Feed Scraping | Daily | 5 Years |

---

## 2. Missing Data & Quality Protocols

1. **No Fake Zero Fill**: Missing data is represented explicitly (`value: None`, `quality: MISSING`) rather than blindly filled with zero.
2. **Median Feed Consensus**: Real-time market quotes require a 3-source median price consensus score ($1.00 = 100\%$).
3. **Concept Drift Testing**: Kolmogorov-Smirnov (KS) p-value testing is conducted on incoming feature distributions ($p \ge 0.05$).
