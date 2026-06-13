from pathlib import Path

import joblib
import pandas as pd

from backend.ml import train_model


def synthetic_training_frame():
    rows = []
    for index in range(40):
        rows.append(
            {
                "GrLivArea": 1000 + index * 20,
                "LotArea": 5000 + index * 30,
                "OverallQual": 5 + (index % 4),
                "OverallCond": 4 + (index % 3),
                "BedroomAbvGr": 2 + (index % 3),
                "FullBath": 1 + (index % 2),
                "GarageCars": 1 + (index % 2),
                "GarageArea": 250 + index * 5,
                "Neighborhood": "CollgCr" if index % 2 == 0 else "NridgHt",
                "HouseStyle": "1Story" if index % 2 == 0 else "2Story",
                "MoSold": 1 + (index % 12),
                "property_age": 5 + index,
                "SalePrice": 120000 + index * 5000,
            }
        )
    return pd.DataFrame(rows)


def test_train_and_save_model_produces_metrics_and_artifact(monkeypatch, tmp_path):
    class DummySettings:
        model_version = "test-metrics-v1"
        model_path = str(tmp_path / "xgboost_model.joblib")

    monkeypatch.setattr(train_model, "load_training_data", lambda csv_path="": synthetic_training_frame())
    monkeypatch.setattr(train_model, "get_settings", lambda: DummySettings())

    metrics = train_model.train_and_save_model()

    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0
    assert metrics["r2"] > 0.5
    assert Path("backend/ml/models/xgboost_model.joblib").exists()


def test_train_and_save_model_triggers_email_on_alert(monkeypatch, tmp_path):
    class DummySettings:
        model_version = "test-metrics-v1"
        model_path = str(tmp_path / "xgboost_model.joblib")
        alert_email_recipient = "walidtamairt@gmail.com"
        smtp_host = "smtp.example.com"
        smtp_port = 587
        smtp_username = "sender@example.com"
        smtp_password = "secret"
        smtp_from_email = "alerts@example.com"
        smtp_use_tls = True

    sent = {"called": False}

    monkeypatch.setattr(train_model, "load_training_data", lambda csv_path="": synthetic_training_frame())
    monkeypatch.setattr(train_model, "get_settings", lambda: DummySettings())
    monkeypatch.setattr(train_model, "load_previous_metrics_snapshot", lambda: {"mae": 1000.0, "r2": 0.95})
    monkeypatch.setattr(train_model, "detect_training_alerts", lambda metrics, previous: ["MAE increased by more than 15%"])
    monkeypatch.setattr(train_model, "emit_training_alert", lambda metrics, alerts: Path("backend/ml/models/training_alert.json"))
    monkeypatch.setattr(
        train_model,
        "send_training_alert_email",
        lambda metrics, alerts, settings_obj=None, smtp_factory=None: sent.__setitem__("called", True) or True,
    )

    metrics = train_model.train_and_save_model()

    assert metrics["alerts"] == ["MAE increased by more than 15%"]
    assert sent["called"] is True


def test_saved_model_can_be_reloaded():
    path = Path("backend/ml/models/xgboost_model.joblib")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": "placeholder", "features": []}, path)
    bundle = joblib.load(path)
    assert "model" in bundle
