from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TradeMind AI"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    REDIS_URL: str = "redis://localhost:6379/0"
    POSTGRES_URL: str = "sqlite:///./local_operational.db"
    DEBUG: bool = False

    @validator("POSTGRES_URL", pre=True)
    def fix_postgres_prefix(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    FIREBASE_PROJECT_ID: str = "com-webcraft-trademindai-c8f75"
    GROQ_API_KEY: str = "YOUR_GROQ_API_KEY"

    # Vision 2.2: Local LLM Support (Ollama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:1.7b" # Exact tag for your installed 1.7B version
    USE_LOCAL_LLM: bool = False

    GROWW_API_KEY: Optional[str] = None
    GROWW_BASE_URL: str = "https://api.groww.in/v1"

    MARKET_DATA_PROVIDER: str = "yfinance" # or "groww"

    SECRET_KEY: str = "SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
