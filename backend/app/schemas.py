from datetime import datetime

from pydantic import BaseModel


class ModelMetricsResponse(BaseModel):
    model_name: str | None
    model_version: str | None
    mae: float | None
    rmse: float | None
    r2: float | None
    train_rows: int | None
    feature_count: int | None
    created_at: datetime | None


class ModelMetricsHistoryResponse(BaseModel):
    items: list[ModelMetricsResponse]
