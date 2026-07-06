import os
from pathlib import Path
import shutil

import joblib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ["DATABASE_URL"] = "sqlite:///./test_real_estate.db"
os.environ["MODEL_PATH"] = "backend/ml/models/test_model.joblib"
os.environ["MODEL_VERSION"] = "test-v1"
os.environ["API_KEY"] = "test-api-key"
os.environ["OPENROUTER_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""

from backend.app.database import Base, SessionLocal, engine
from backend.app.main import app
from backend.app.models import (
    BatchPrediction,
    ExternalContextSummary,
    ExternalMarketContext,
    ModelMetric,
    PropertyTrain,
    ScrapedMarketTrend,
    UserPrediction,
)


class DummyModel:
    def predict(self, df):
        return [250000.0 for _ in range(len(df))]


@pytest.fixture(autouse=True)
def setup_database():
    engine.dispose()
    schema_path = Path("backend/database/schema.sql")
    with engine.begin() as connection:
        for statement in schema_path.read_text(encoding="utf-8").split(";"):
            sql = statement.strip()
            if sql:
                connection.execute(text(sql))
        for table_name in [
            "external_context_summaries",
            "scraped_market_trends",
            "external_market_context",
            "user_predictions",
            "batch_predictions",
            "model_metrics",
            "properties_train",
        ]:
            connection.execute(text(f"DELETE FROM {table_name}"))
        connection.execute(
            text(
                """
                INSERT INTO properties_train
                (gr_liv_area, lot_area, overall_qual, overall_cond, bedroom_abv_gr, full_bath,
                 garage_cars, garage_area, neighborhood, house_style, sale_month, property_age, sale_price, created_at)
                VALUES
                (:gr_liv_area, :lot_area, :overall_qual, :overall_cond, :bedroom_abv_gr, :full_bath,
                 :garage_cars, :garage_area, :neighborhood, :house_style, :sale_month, :property_age, :sale_price, CURRENT_TIMESTAMP)
                """
            ),
            {
                "gr_liv_area": 1500,
                "lot_area": 8000,
                "overall_qual": 7,
                "overall_cond": 5,
                "bedroom_abv_gr": 3,
                "full_bath": 2,
                "garage_cars": 2,
                "garage_area": 400,
                "neighborhood": "CollgCr",
                "house_style": "1Story",
                "sale_month": 6,
                "property_age": 10,
                "sale_price": 240000,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO model_metrics
                (model_name, model_version, mae, rmse, r2, train_rows, feature_count, created_at)
                VALUES
                (:model_name, :model_version, :mae, :rmse, :r2, :train_rows, :feature_count, CURRENT_TIMESTAMP)
                """
            ),
            {
                "model_name": "xgboost",
                "model_version": "test-v1",
                "mae": 1000.0,
                "rmse": 1500.0,
                "r2": 0.95,
                "train_rows": 1,
                "feature_count": 12,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO external_context_summaries
                (summary_kind, source, summary_text, rows_collected, average_indicator_value, payload_json, created_at)
                VALUES
                (:summary_kind, :source, :summary_text, :rows_collected, :average_indicator_value, :payload_json, CURRENT_TIMESTAMP)
                """
            ),
            {
                "summary_kind": "external_api",
                "source": "FRED API",
                "summary_text": "Mortgage rates remain elevated while US housing prices stay resilient.",
                "rows_collected": 3,
                "average_indicator_value": 5.4,
                "payload_json": '{"summary_text":"Mortgage rates remain elevated while US housing prices stay resilient."}',
            },
        )
    Path("backend/ml/models").mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": DummyModel(), "rmse": 15000.0, "model_version": "test-v1"}, "backend/ml/models/test_model.joblib")
    yield
    engine.dispose()
    model_path = Path("backend/ml/models/test_model.joblib")
    if model_path.exists():
        model_path.unlink()


@pytest.fixture
def tmp_path():
    path = Path("tmp_pytest")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    yield path
    if path.exists():
        shutil.rmtree(path)


@pytest.fixture
def client():
    return TestClient(app, headers={"X-API-Key": os.environ["API_KEY"]})
