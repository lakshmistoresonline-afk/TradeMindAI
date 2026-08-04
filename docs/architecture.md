# TradeMind AI Architecture

## Overview
TradeMind AI is a production-quality NSE Stock Intelligence Platform built with a multi-layered architecture.

## Frontend
- **Android App**: Built with Jetpack Compose, Hilt, Retrofit, and Room.
- **Web App**: Built with React, TypeScript, and Tailwind CSS.

## Backend
- **FastAPI**: High-performance REST API.
- **PostgreSQL**: Relational database for structured data.
- **Redis**: Caching and Celery broker.
- **Celery**: Background workers for data collection and analysis.

## AI Engine
- **LangGraph**: Multi-agent orchestration.
- **Ollama/DeepSeek**: LLM models for qualitative analysis.
- **Transformers (FinBERT)**: Sentiment analysis.

## ML Engine
- **LSTM/XGBoost**: Quantitative price prediction.

## Data Layer
- **yfinance**: Market data source.
- **SQLAlchemy**: ORM.
