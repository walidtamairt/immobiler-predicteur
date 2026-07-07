from __future__ import annotations

import argparse
import json
import smtplib
from email.message import EmailMessage
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

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
from backend.app.models import PropertyTrain
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
        db = SessionLocal()
        try:
            rows = db.query(
                PropertyTrain.gr_liv_area,
                PropertyTrain.lot_area,
                PropertyTrain.overall_qual,
                PropertyTrain.overall_cond,
                PropertyTrain.bedroom_abv_gr,
                PropertyTrain.full_bath,
                PropertyTrain.garage_cars,
                PropertyTrain.garage_area,
                PropertyTrain.neighborhood,
                PropertyTrain.house_style,
                PropertyTrain.sale_month,
                PropertyTrain.property_age,
                PropertyTrain.sale_price,
            ).all()
        finally:
            db.close()

        if not rows:
            raise FileNotFoundError(f"Training file not found and no database rows were available: {path}")

        return pd.DataFrame(
            rows,
            columns=[
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
                "SalePrice",
            ],
        )
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


def load_previous_metrics_snapshot() -> dict | None:
    db = SessionLocal()
    try:
        row = db.execute(
            text(
                """
                SELECT model_name, model_version, mae, rmse, r2, train_rows, feature_count, created_at
                FROM model_metrics
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
        ).mappings().first()
        if row:
            return dict(row)
    except SQLAlchemyError as exc:
        logger.warning("Unable to load previous metrics from database: %s", exc)
    finally:
        db.close()

    metrics_path = Path("backend/ml/models/metrics.json")
    if not metrics_path.exists():
        return None

    try:
        return json.loads(metrics_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("Unable to load previous metrics from JSON snapshot: %s", exc)
        return None


def detect_training_alerts(metrics: dict, previous_metrics: dict | None) -> list[str]:
    reasons: list[str] = []

    if float(metrics["r2"]) < 0.80:
        reasons.append(f"R2 dropped below threshold: {metrics['r2']:.4f} < 0.80")

    previous_mae = float(previous_metrics["mae"]) if previous_metrics and previous_metrics.get("mae") else None
    if previous_mae and float(metrics["mae"]) > previous_mae * 1.15:
        reasons.append(
            "MAE increased by more than 15% compared to historical baseline: "
            f"{metrics['mae']:.4f} vs {previous_mae:.4f}"
        )

    return reasons


def write_monitoring_report(metrics: dict, previous_metrics: dict | None, alerts: list[str]) -> Path:
    report_path = Path("backend/ml/models/training_monitoring_report.json")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_metrics": metrics,
        "previous_metrics": previous_metrics,
        "alerts": alerts,
        "status": "critical" if alerts else "ok",
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def emit_training_alert(metrics: dict, alerts: list[str]) -> Path:
    alert_path = Path("backend/ml/models/training_alert.json")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "severity": "critical",
        "channel": "simulated-webhook",
        "message": "Model performance drift detected during training.",
        "alerts": alerts,
        "metrics": metrics,
    }
    alert_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.critical("Training quality alert triggered: %s", " | ".join(alerts))
    logger.critical("Simulated webhook payload written to %s", alert_path)
    return alert_path


def send_training_alert_email(
    metrics: dict,
    alerts: list[str],
    settings_obj=None,
    smtp_factory=smtplib.SMTP,
) -> bool:
    settings = settings_obj or get_settings()
    recipient = getattr(settings, "alert_email_recipient", "walidtamairt@gmail.com")
    if not recipient:
        logger.warning("Training alert email skipped because ALERT_EMAIL_RECIPIENT is missing")
        return False

    smtp_host = getattr(settings, "smtp_host", "")
    smtp_port = int(getattr(settings, "smtp_port", 587))
    smtp_username = getattr(settings, "smtp_username", "")
    smtp_password = getattr(settings, "smtp_password", "")
    smtp_from_email = getattr(settings, "smtp_from_email", "")
    smtp_use_tls = bool(getattr(settings, "smtp_use_tls", True))

    if not smtp_host:
        logger.warning("Training alert email skipped because SMTP_HOST is not configured")
        return False

    subject = f"[Estate AI] Training alert for {settings.model_version}"
    body_lines = [
        "A training monitoring alert was triggered.",
        "",
        f"Model version: {metrics.get('model_version')}",
        f"MAE: {metrics.get('mae')}",
        f"RMSE: {metrics.get('rmse')}",
        f"R2: {metrics.get('r2')}",
        "",
        "Alerts:",
    ]
    body_lines.extend(f"- {alert}" for alert in alerts)
    body_lines.append("")
    body_lines.append("This message was generated automatically by the Estate AI monitoring pipeline.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_from_email or smtp_username or recipient
    message["To"] = recipient
    message.set_content("\n".join(body_lines))

    try:
        if smtp_use_tls:
            with smtp_factory(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if smtp_username:
                    server.login(smtp_username, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                if smtp_username:
                    server.login(smtp_username, smtp_password)
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        logger.warning("Unable to send training alert email to %s: %s", recipient, exc)
        return False

    logger.critical("Training alert email sent to %s", recipient)
    return True


def simulate_bad_training_metrics(settings=None) -> dict:
    settings = settings or get_settings()
    return {
        "model_name": "xgboost",
        "model_version": settings.model_version,
        "mae": 14000.0,
        "rmse": 18000.0,
        "r2": 0.72,
        "train_rows": 0,
        "feature_count": len(FEATURES),
    }


def dry_run_training_alert(settings_obj=None, smtp_factory=smtplib.SMTP) -> dict:
    settings = settings_obj or get_settings()
    metrics = simulate_bad_training_metrics(settings)
    previous_metrics = {"mae": 10000.0, "rmse": 15000.0, "r2": 0.88}
    alerts = detect_training_alerts(metrics, previous_metrics)
    email_sent = send_training_alert_email(metrics, alerts, settings_obj=settings, smtp_factory=smtp_factory)
    logger.critical("Dry-run alert simulation executed without saving model artifacts.")
    return {
        "dry_run": True,
        "metrics": metrics,
        "alerts": alerts,
        "email_sent": email_sent,
    }


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
    previous_metrics = load_previous_metrics_snapshot()
    alerts = detect_training_alerts(metrics, previous_metrics)
    save_metrics(metrics)
    if alerts:
        emit_training_alert(metrics, alerts)
        send_training_alert_email(metrics, alerts, settings)
    monitoring_report_path = write_monitoring_report(metrics, previous_metrics, alerts)
    enriched_metrics = {**metrics, "alerts": alerts, "monitoring_report": str(monitoring_report_path)}
    Path("backend/ml/models/metrics.json").write_text(json.dumps(enriched_metrics, indent=2), encoding="utf-8")
    logger.info("Saved model to %s", model_path)
    return enriched_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the model or run a dry-run alert simulation.")
    parser.add_argument("--dry-run-alert", action="store_true", help="Simulate a bad training and send only the alert email.")
    args = parser.parse_args()

    if args.dry_run_alert:
        print(dry_run_training_alert())
    else:
        print(train_and_save_model())
