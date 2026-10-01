# TradeMind AI — V6.0 Architecture Canonicalization

- Database: backend/trade_mind.db (app_market_data, security_master, technical_features)
- Ingestion: RealMarketDataIngestionService (yfinance)
- Security Master: Nifty200UniverseService
- API: FastAPI (/api/v1/equity/signals, /api/v1/equity/features/{symbol})
- Frontend: Vite SPA (web/dist)
