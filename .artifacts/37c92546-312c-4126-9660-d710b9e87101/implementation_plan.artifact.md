# Detailed AI Analysis Engine for NSE Stocks

This plan covers enhancing the AI multi-agent workflow to provide institutional-grade analysis for all NSE stocks, including Smart Money Concepts (SMC) and batch processing.

## Proposed Changes

### AI Agents & Workflow
#### [MODIFY] [agents.py](file:///D:/TradeMindAI/backend/ai/agents.py)
- Enhance `TechnicalAgent` to interpret RSI, EMA crossovers, MACD, and Smart Money Concepts (Order Blocks, FVG).
- Enhance `FundamentalAgent` to analyze P/E, P/B, and Market Cap context.
- [NEW] `SentimentAgent` to incorporate news sentiment data.
- Update `AgentState` to hold more granular analysis data.

#### [MODIFY] [workflow.py](file:///D:/TradeMindAI/backend/ai/workflow.py)
- Add the `SentimentAgent` to the LangGraph workflow.
- Update the sequence: Technical -> Fundamental -> Sentiment -> Consensus.

### Data Processing
#### [MODIFY] [tasks.py](file:///D:/TradeMindAI/backend/workers/tasks.py)
- Add a new task `analyze_all_nse_stocks` that fetches a list of NSE symbols and triggers `analyze_stock_task` for each.
- Update `analyze_stock_task` to include SMC analysis before invoking the AI.
- Store the full detailed analysis JSON in Firestore.

### Web Frontend
#### [MODIFY] [client.ts](file:///D:/TradeMindAI/web/src/api/client.ts)
- Add endpoint to fetch detailed analysis for a specific symbol.

#### [NEW] [AnalysisReport.tsx](file:///D:/TradeMindAI/web/src/components/AnalysisReport.tsx)
- Create a component to render the detailed multi-agent report.

#### [MODIFY] [Analysis.tsx](file:///D:/TradeMindAI/web/src/pages/Analysis.tsx)
- Connect to the detailed analysis data and allow searching for specific stock reports.

## Verification Plan
### Automated Tests
- Run `analyze_file` on updated backend modules.
- Check Celery logs for successful batch processing.

### Manual Verification
- Verify that "Analysis" page in the web app shows detailed breakdowns from different agents.
