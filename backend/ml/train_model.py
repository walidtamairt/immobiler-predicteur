from __future__ import annotations

import json
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError

import joblib
import pandas as pd
from math import sqrt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

from backend.config.settings import get_settings
from backend.database.db import SessionLocal
from backend.utils.logger import get_logger
from sqlalchemy import text

logger = get_logger(__name__)

FEATURES = [
    "GrLivArea",
    "LotArea",
    "OverallQual",
    "OverallCond",
    "BedroomAbvGr",
    "FullBath",
    "GarageCars",
    "GarageArea",
    "Neighborhood",
    "HouseStyle",
    "MoSold",
    "property_age",
]
NUMERIC_FEATURES = [
    "GrLivArea",
    "LotArea",
    "OverallQual",
    "OverallCond",
    "BedroomAbvGr",
    "FullBath",
    "GarageCars",
    "GarageArea",
    "MoSold",
    "property_age",
]
CATEGORICAL_FEATURES = ["Neighborhood", "HouseStyle"]
TARGET = "SalePrice"


def load_training_data(csv_path: str | Path = "data/processed/train_clean.csv") -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Training file not found: {path}")
    return pd.read_csv(path)


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])


def save_metrics(metrics: dict) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text(
            """
            INSERT INTO model_metrics
            (model_name, model_version, mae, rmse, r2, train_rows, feature_count)
            VALUES
            (:model_name, :model_version, :mae, :rmse, :r2, :train_rows, :feature_count)
            """
            ),
            metrics,
        )
        db.commit()
    except SQLAlchemyError as exc:
        logger.warning("Skipping metrics insert because database is unavailable: %s", exc)
    finally:
        db.close()


def train_and_save_model() -> dict:
    settings = get_settings()
    df = load_training_data()
    df = df.dropna(subset=[TARGET]).reset_index(drop=True)
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_val)

    mae = float(mean_absolute_error(y_val, predictions))
    mse = float(mean_squared_error(y_val, predictions))
    rmse = float(sqrt(mse))
    r2 = float(r2_score(y_val, predictions))

    model_dir = Path("backend/ml/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "xgboost_model.joblib"
    joblib.dump(
        {
            "model": pipeline,
            "features": FEATURES,
            "model_version": settings.model_version,
            "rmse": rmse,
        },
        model_path,
    )

    metrics = {
        "model_name": "xgboost",
        "model_version": settings.model_version,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "train_rows": int(len(df)),
        "feature_count": int(len(FEATURES)),
    }
    save_metrics(metrics)
    Path("backend/ml/models/metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info("Saved model to %s", model_path)
    return metrics


if __name__ == "__main__":
    print(train_and_save_model())
