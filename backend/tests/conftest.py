import os
from pathlib import Path
import shutil

import joblib
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test_real_estate.db"
os.environ["MODEL_PATH"] = "backend/ml/models/test_model.joblib"
os.environ["MODEL_VERSION"] = "test-v1"
os.environ["OPENROUTER_API_KEY"] = ""

from backend.app.database import Base, SessionLocal, engine
from backend.app.main import app
from backend.app.models import ModelMetric, PropertyTrain


class DummyModel:
    def predict(self, df):
        return [250000.0 for _ in range(len(df))]


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(
        PropertyTrain(
            gr_liv_area=1500,
            lot_area=8000,
            overall_qual=7,
            overall_cond=5,
            bedroom_abv_gr=3,
            full_bath=2,
            garage_cars=2,
            garage_area=400,
            neighborhood="CollgCr",
            house_style="1Story",
            sale_month=6,
            property_age=10,
            sale_price=240000,
        )
    )
    db.add(
        ModelMetric(
            model_name="xgboost",
            model_version="test-v1",
            mae=1000.0,
            rmse=1500.0,
            r2=0.95,
            train_rows=1,
            feature_count=12,
        )
    )
    db.commit()
    db.close()
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
    return TestClient(app)
