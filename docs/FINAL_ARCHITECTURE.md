# TradeMind AI: Final Consolidated Architecture

## Overview
The TradeMind AI system has been consolidated into a production-grade NIFTY-200 Equity Intelligence platform. It enforces one authoritative path from real data to the web application.

## Authoritative Path
Real Data (YFinance) -> Validated Data (HistoricalDataService) -> Feature Snapshot -> V2.2 Decision (SignalEngine) -> Neon Ledger (SignalLedgerService) -> Firestore Mirror -> Equity API -> Dynamic Web App.

## Key Services
- **SignalLedgerService**: Authority for signal writes/reads in Neon/Postgres.
- **SignalLifecycleService**: Manages state machine (ACTIVE, TARGET_HIT, etc.).
- **PnlService**: Unified implementation for all P&L calculations.
- **OutcomeService**: Authoritative outcome resolution.
- **MarketDataService**: Abstracted price and status retrieval.
- **ResearchReplayService**: Robust historical replay with accounting.

## Data Integrity
- **Universe Integrity**: Exactly 200 monitored NIFTY-200 symbols.
- **Temporal Integrity**: Enforced lineage timestamps (`data <= feature <= prediction <= signal`).
- **Data Quality**: Freshness and coverage scores for every signal.

## Research & Isolation
- **V2.2 Frozen**: Canonical implementation hashes stored in `V22_FREEZE_MANIFEST.json`.
- **Research Indicators**: Isolated calculation for ADX, MACD, etc., in `ResearchFeatureEngine`.
- **Challenger Models**: Separate from production v2.2.
