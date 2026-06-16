from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="", alias="DATABASE_URL")
    database_fallback_url: str = Field(default="", alias="DATABASE_FALLBACK_URL")
    database_connect_timeout: int = Field(default=5, alias="DATABASE_CONNECT_TIMEOUT")
    model_version: str = Field(default="xgboost_v1", alias="MODEL_VERSION")
    model_path: str = Field(default="backend/ml/models/xgboost_model.joblib", alias="MODEL_PATH")
    api_key: str = Field(default="estate-ai-dev-key", alias="API_KEY")
    demo_username: str = Field(default="demo-user", alias="DEMO_USERNAME")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openrouter/auto", alias="OPENROUTER_MODEL")
    openrouter_site_url: str = Field(default="http://localhost:5173", alias="OPENROUTER_SITE_URL")
    openrouter_app_name: str = Field(default="Estate AI", alias="OPENROUTER_APP_NAME")
    alert_email_recipient: str = Field(default="walidtamairt@gmail.com", alias="ALERT_EMAIL_RECIPIENT")
    smtp_host: str = Field(default="", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str = Field(default="", alias="SMTP_USERNAME")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="", alias="SMTP_FROM_EMAIL")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

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
