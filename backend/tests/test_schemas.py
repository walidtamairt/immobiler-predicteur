from datetime import datetime, timezone

from backend.app.schemas import ModelMetricsHistoryResponse, ModelMetricsResponse


def test_model_metrics_response_schema_validation():
    payload = ModelMetricsResponse(
        model_name="xgboost",
        model_version="test-v1",
        mae=1234.5,
        rmse=2345.6,
        r2=0.91,
        train_rows=100,
        feature_count=12,
        created_at=datetime.now(timezone.utc),
    )

    assert payload.model_name == "xgboost"
    assert payload.feature_count == 12


def test_model_metrics_history_response_schema_validation():
    item = ModelMetricsResponse(
        model_name="xgboost",
        model_version="test-v1",
        mae=1234.5,
        rmse=2345.6,
        r2=0.91,
        train_rows=100,
        feature_count=12,
        created_at=datetime.now(timezone.utc),
    )
    payload = ModelMetricsHistoryResponse(items=[item])

    assert len(payload.items) == 1
