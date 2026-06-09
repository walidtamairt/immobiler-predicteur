from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./real_estate.db", alias="DATABASE_URL")
    model_path: str = Field(default="backend/ml/artifacts/real_estate_model.joblib", alias="MODEL_PATH")
    model_version: str = Field(default="v1.0.0", alias="MODEL_VERSION")

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
