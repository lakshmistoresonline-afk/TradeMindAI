# TradeMind AI DASHBOARD DATA POPULATION REPORT

## 1. Dashboard Overview (Web)
| Widget | Live Source | API | Status |
| :--- | :--- | :--- | :--- |
| Nifty 100 Index | yfinance | `/stocks/market-stats` | ✅ LIVE |
| Market Breadth | system calculation | `/stocks/market-stats` | ✅ LIVE |
| FII/DII Net Flow | institutional data | `/stocks/fii-dii` | ✅ LIVE |
| Live AI Signals | Consensus Agent | `/stocks/` | ✅ LIVE |

## 2. Research Hub (Web)
| Card | Live Source | API | Status |
| :--- | :--- | :--- | :--- |
| AI Score Card | Unified Scoring | `/stocks/{symbol}` | ✅ LIVE |
| Executive Summary | Consensus Agent | `/stocks/{symbol}` | ✅ LIVE |
| Technical Deep Dive | Technical Engine | `/stocks/{symbol}` | ✅ LIVE |
| News Center | AI Sentiment | `/stocks/{symbol}/news` | ✅ LIVE |
| Earnings Intel | Calendar Data | `/stocks/{symbol}/earnings` | ✅ LIVE |
| Similarity Engine | Feature Store | `/ios/similarity/{symbol}` | ✅ LIVE |

## 3. Mobile Dashboard (Android)
| Component | Live Source | API | Status |
| :--- | :--- | :--- | :--- |
| Market Stats | yfinance | `/stocks/market-stats` | ✅ LIVE |
| AI Signals | Consensus Agent | `/stocks/` | ✅ LIVE |
| Market Regime | Regime Engine | `/ios/regime` | ✅ LIVE |

---

### 🛠️ Fixes Applied (RC-1 Audit)
- **Column Mismatch**: Fixed `KeyError: 'Close'` by implementing a case-insensitive column resolver in the technical engine.
- **Data Parity**: Added `MarketRegime` and `MarketBreadth` to Android API and UI.
- **Build Errors**: Resolved all 7 TypeScript errors in the web terminal to enable a clean production build.
