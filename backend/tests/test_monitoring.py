import json
from pathlib import Path

from backend.ml.train_model import (
    detect_training_alerts,
    emit_training_alert,
    send_training_alert_email,
    write_monitoring_report,
)


def test_detect_training_alerts_for_low_r2_and_mae_drift():
    metrics = {"mae": 14000.0, "rmse": 18000.0, "r2": 0.72}
    previous = {"mae": 10000.0, "rmse": 15000.0, "r2": 0.88}

    alerts = detect_training_alerts(metrics, previous)

    assert len(alerts) == 2
    assert "R2 dropped below threshold" in alerts[0]
    assert "MAE increased by more than 15%" in alerts[1]


def test_monitoring_report_and_alert_artifacts_are_written():
    metrics = {"mae": 14000.0, "rmse": 18000.0, "r2": 0.72}
    previous = {"mae": 10000.0, "rmse": 15000.0, "r2": 0.88}
    alerts = detect_training_alerts(metrics, previous)

    report_path = write_monitoring_report(metrics, previous, alerts)
    alert_path = emit_training_alert(metrics, alerts)

    assert report_path.exists()
    assert alert_path.exists()
    assert json.loads(Path(report_path).read_text(encoding="utf-8"))["status"] == "critical"
    assert json.loads(Path(alert_path).read_text(encoding="utf-8"))["severity"] == "critical"


def test_send_training_alert_email_uses_configured_recipient(monkeypatch):
    sent_messages = []

    class DummySMTP:
        def __init__(self, host, port, timeout=20):
            self.host = host
            self.port = port
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def ehlo(self):
            return None

        def starttls(self):
            return None

        def login(self, username, password):
            self.username = username
            self.password = password

        def send_message(self, message):
            sent_messages.append(message)

    class DummySettings:
        model_version = "test-v1"
        alert_email_recipient = "walidtamairt@gmail.com"
        smtp_host = "smtp.example.com"
        smtp_port = 587
        smtp_username = "sender@example.com"
        smtp_password = "secret"
        smtp_from_email = "alerts@example.com"
        smtp_use_tls = True

    ok = send_training_alert_email(
        {"model_version": "test-v1", "mae": 14000.0, "rmse": 18000.0, "r2": 0.72},
        ["R2 dropped below threshold: 0.7200 < 0.80"],
        settings_obj=DummySettings(),
        smtp_factory=DummySMTP,
    )

    assert ok is True
    assert sent_messages[0]["To"] == "walidtamairt@gmail.com"
