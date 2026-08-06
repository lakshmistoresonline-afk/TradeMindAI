# TradeMind AI FEATURE TRACEABILITY MATRIX

## 1. Intelligence Data Flow
| Feature | DB Source | API Endpoint | Component | Status |
| :--- | :--- | :--- | :--- | :--- |
| AI Score | `stocks.ai_investment_score` | `/stocks/{symbol}` | `AIScoreCard` | ✅ Connected |
| Market Regime | `market_regimes` | `/ios/regime` | `MarketBrief` | ✅ Connected |
| Signal Consensus | `stocks.analysis.consensus` | `/stocks/{symbol}` | `AIExecutiveSummary` | ✅ Connected |
| News Sentiment | `news` | `/stocks/{symbol}/news` | `AINewsCenter` | ✅ Connected |
| Digital Twin | `stocks.analysis` + `prices` | `/ios/twin/{symbol}` | `DigitalTwin` | ✅ Connected |

## 2. Quantitative & Forensic Flow
| Feature | DB Source | API Endpoint | Component | Status |
| :--- | :--- | :--- | :--- | :--- |
| Historical Accuracy | `backtests` | `/analysis/backtest/{symbol}` | `Analysis.tsx` (Table) | ✅ Connected |
| Risk Metrics | `stocks.analysis.technical_data` | `/stocks/{symbol}` | `QuantitativeAnalysis` | ✅ Connected |
| SMC Structures | `stocks.analysis.technical_data.smc` | `/stocks/{symbol}` | `MarketStructure` | ✅ Connected |

## 3. User & Research Flow
| Feature | DB Source | API Endpoint | Component | Status |
| :--- | :--- | :--- | :--- | :--- |
| Research Notes | `research_notes` | `/ios/notes/{symbol}` | `ResearchNotebook` | ✅ Connected |
| Workspaces | `workspaces` | `/ios/workspaces` | `Layout` (Chips) | ✅ Connected |
| Trade Journal | `trade_journal` | `/ios/journal` | `Journal` | ✅ Connected |

---

### 🔍 Discovery: Gaps in Android Parity
The Android app is currently missing connections to:
- `/ios/regime`
- `/ios/twin/{symbol}`
- `/ios/notes/{symbol}`
- `/ios/journal`

These need to be added to `ApiService.kt` and integrated into the UI.
