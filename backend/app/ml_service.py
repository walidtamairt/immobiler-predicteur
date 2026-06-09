import json
from pathlib import Path

import joblib
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .config import get_settings
from .models import PredictionLog
from .schemas import PredictionInput

settings = get_settings()


def load_model_bundle() -> dict:
    model_path = Path(settings.model_path)
    if not model_path.exists():
        raise HTTPException(status_code=503, detail="Model artifact not found. Train the model first.")
    return joblib.load(model_path)


def predict_price(payload: PredictionInput, db: Session) -> dict:
    bundle = load_model_bundle()
    model = bundle["model"]
    sigma = bundle.get("rmse", 0)
    features = pd.DataFrame([payload.model_dump()])
    predicted_price = float(model.predict(features)[0])
    response = {
        "predicted_price": round(predicted_price, 2),
        "lower_bound": round(max(predicted_price - sigma, 0), 2),
        "upper_bound": round(predicted_price + sigma, 2),
        "model_version": bundle.get("model_version", settings.model_version),
    }
    db.add(
        PredictionLog(
            input_payload=json.dumps(payload.model_dump()),
            predicted_price=response["predicted_price"],
            lower_bound=response["lower_bound"],
            upper_bound=response["upper_bound"],
            model_version=response["model_version"],
        )
    )
    db.commit()
    return response
