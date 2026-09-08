# NSE PUBLIC DATA COLLECTION REPORT

## 1. Collection Methodology
TradeMind utilizes a **Hybrid Gateway** approach to collect NSE data:
- **Primary**: Local Scraper (Windows) fetching from `nseindia.com/api`.
- **Protocol**: HTTP/1.1 with automated session and cookie management.
- **Security**: Local-first collection ensures no reliance on shared cloud proxies.

## 2. Capability Matrix
| Feature | Source | Accuracy | Status |
| :--- | :--- | :--- | :--- |
| **Equity LTP** | `quote-equity` | **HIGH** | OPERATIONAL |
| **Index LTP** | `option-chain-indices` | **HIGH** | OPERATIONAL |
| **F&O LTP** | `option-chain-derivatives` | **HIGH** | IMPLEMENTED |
| **Historical EOD** | Bhavcopy | **EXACT** | READY |

## 3. Reliability Findings
The public endpoints are highly reliable but subject to rate limiting (typically 1 request per second). TradeMind implements exponential backoff and persistent session reuse to maximize throughput.

---
**Verdict**: NSE_OPEN_DATA_OPERATIONAL.
