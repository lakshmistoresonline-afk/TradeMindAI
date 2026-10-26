"""
================================================================================
TradeMindAI: Hardened Configuration & Security Settings (SEC-01 & TM-03)
================================================================================
Permanent product boundary: signals only, never order execution.
Requires production signing key and ingest key, removes placeholder LLM credentials.
================================================================================
"""

import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TradeMind AI"

    # Permanent product boundary: signals only, never order execution.
    REAL_TRADING: bool = False
    LIVE_EXECUTION_ENABLED: bool = False
    BROKER_ORDER_EXECUTION_ENABLED: bool = False
    QUARANTINE_ACTIVE: bool = True

    @field_validator(
        "REAL_TRADING",
        "LIVE_EXECUTION_ENABLED",
        "BROKER_ORDER_EXECUTION_ENABLED",
        mode="before",
    )
    @classmethod
    def enforce_signal_only_boundary(cls, value) -> bool:
        if isinstance(value, bool):
            enabled = value
        else:
            enabled = str(value).strip().lower() in {
                "true", "1", "yes", "on", "enable", "enabled"
            }
        if enabled:
            raise ValueError(
                "TradeMindAI is a signal-provider application. "
                "Order execution capabilities are permanently disabled."
            )
        return False

    @field_validator("QUARANTINE_ACTIVE", mode="before")
    @classmethod
    def validate_quarantine_setting(cls, v, info) -> bool:
        if v is False or str(v).lower() in ("false", "0", "no", "off", "disable", "disabled"):
            raise ValueError(
                "CRITICAL SECURITY AUDIT FAILURE: QUARANTINE_ACTIVE is permanently active and cannot be disabled."
            )
        return True

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    REDIS_URL: str = "redis://localhost:6379/0"
    POSTGRES_URL: str = "sqlite:///./local_operational.db"
    ENVIRONMENT: str = "development" # production, development, test
    DEBUG: bool = False

    @field_validator("POSTGRES_URL", mode="before")
    @classmethod
    def fix_postgres_prefix(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    FIREBASE_PROJECT_ID: str = "com-webcraft-trademindai-c8f75"
    GROQ_API_KEY: Optional[str] = None

    # Vision 2.2: Local LLM Support (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:1.7b"
    USE_LOCAL_LLM: bool = False

    GROWW_API_KEY: Optional[str] = None
    GROWW_BASE_URL: str = "https://api.groww.in/v1"

    MARKET_DATA_PROVIDER: str = "yfinance"
    DEFAULT_RISK_REWARD: float = 2.5

    SECRET_KEY: str = "SECRET"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        if info.data.get("ENVIRONMENT") == "production":
            if v == "SECRET" or not v:
                raise ValueError("CRITICAL: SECRET_KEY must be set in production environment via environment variables.")
            if len(v) < 32:
                 raise ValueError("CRITICAL: production SECRET_KEY is too weak (< 32 chars). Security audit failure.")
        return v

    MARKET_DATA_INGEST_KEY: str = "LOCAL_ONLY_DEV_KEY"

    @field_validator("MARKET_DATA_INGEST_KEY")
    @classmethod
    def validate_ingest_key(cls, v: str, info) -> str:
        if info.data.get("ENVIRONMENT") == "production":
            if v == "LOCAL_ONLY_DEV_KEY" or not v:
                raise ValueError("CRITICAL: MARKET_DATA_INGEST_KEY must be set in production.")
            if len(v) < 16:
                raise ValueError("CRITICAL: MARKET_DATA_INGEST_KEY is too weak for production.")
        return v

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    GIT_SHA: str = os.getenv("RENDER_GIT_COMMIT", "LOCAL_HEAD")
    ADMIN_EMAILS: List[str] = []

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
