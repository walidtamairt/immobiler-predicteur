from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="", alias="DATABASE_URL")
    model_version: str = Field(default="xgboost_v1", alias="MODEL_VERSION")
    model_path: str = Field(default="backend/ml/models/xgboost_model.joblib", alias="MODEL_PATH")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openrouter/auto", alias="OPENROUTER_MODEL")
    openrouter_site_url: str = Field(default="http://localhost:5173", alias="OPENROUTER_SITE_URL")
    openrouter_app_name: str = Field(default="Estate AI", alias="OPENROUTER_APP_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def model_path_obj(self) -> Path:
        return Path(self.model_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()
