from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "job-2.0")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./job2.db")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    openrouter_model_chain: list[str] = [
        m.strip()
        for m in os.getenv(
            "OPENROUTER_MODEL_CHAIN",
            "meta-llama/llama-3.1-8b-instruct:free,mistralai/mistral-7b-instruct:free",
        ).split(",")
        if m.strip()
    ]
    autopilot_interval_seconds: int = int(os.getenv("AUTOPILOT_INTERVAL_SECONDS", "60"))
    autopilot_max_per_cycle: int = int(os.getenv("AUTOPILOT_MAX_PER_CYCLE", "20"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
