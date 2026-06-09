from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.config.settings import get_settings
from backend.database.db import SessionLocal
from backend.utils.logger import get_logger
from backend.ml.train_model import FEATURES

logger = get_logger(__name__)


def load_model():
    settings = get_settings()
    model_path = Path(settings.model_path)
    if not model_path.exists():
        model_path = Path("backend/ml/models/xgboost_model.joblib")
    if not model_path.exists():
        raise FileNotFoundError("Model artifact not found")
    return joblib.load(model_path)


def load_test_data(csv_path: str | Path = "data/processed/test_clean.csv") -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Test file not found: {path}")
    return pd.read_csv(path)


def save_batch_predictions(df: pd.DataFrame) -> int:
    db = SessionLocal()
    inserted = 0
    try:
        db.execute(text("DELETE FROM batch_predictions"))
        records = df.to_dict(orient="records")
        for row in records:
            db.execute(
                text(
                    """
                    INSERT INTO batch_predictions
                    (source_row_id, gr_liv_area, lot_area, overall_qual, overall_cond, bedroom_abv_gr,
                     full_bath, garage_cars, garage_area, neighborhood, house_style, sale_month, property_age,
                     predicted_price, model_version)
                    VALUES
                    (:source_row_id, :GrLivArea, :LotArea, :OverallQual, :OverallCond, :BedroomAbvGr,
                     :FullBath, :GarageCars, :GarageArea, :Neighborhood, :HouseStyle, :MoSold, :property_age,
                     :predicted_price, :model_version)
                    """
                ),
                row,
            )
            inserted += 1
        db.commit()
        return inserted
    except SQLAlchemyError as exc:
        logger.warning("Skipping batch_predictions insert because database is unavailable: %s", exc)
        return 0
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"Failed to save batch predictions: {exc}") from exc
    finally:
        db.close()


def predict_batch() -> Path:
    bundle = load_model()
    model = bundle["model"]
    model_version = bundle.get("model_version", get_settings().model_version)

    df = load_test_data()
    source = df.copy()
    source["source_row_id"] = range(len(source))
    preds = model.predict(df[FEATURES])
    output = source[[c for c in FEATURES if c in source.columns] + ["source_row_id"]].copy()
    output["predicted_price"] = preds
    output["model_version"] = model_version

    output_path = Path("data/processed/predictions.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    save_batch_predictions(output)
    logger.info("Saved predictions to %s", output_path)
    return output_path


if __name__ == "__main__":
    print(predict_batch())
