from fastapi.testclient import TestClient

from backend.app.main import app


def test_overview_endpoint(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_properties"] == 1
    assert data["average_price"] > 0


def test_filters_endpoint(client):
    response = client.get("/api/filters")
    assert response.status_code == 200
    data = response.json()
    assert "CollgCr" in data["neighborhoods"]


def test_market_data_endpoint(client):
    response = client.get("/api/market-data")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["neighborhood"] == "CollgCr"


def test_prediction_history_endpoint(client):
    predict_payload = {
        "GrLivArea": 1500,
        "LotArea": 8000,
        "OverallQual": 7,
        "OverallCond": 5,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2,
        "GarageArea": 400,
        "Neighborhood": "CollgCr",
        "HouseStyle": "1Story",
        "MoSold": 6,
        "property_age": 10,
    }
    client.post("/api/predict", json=predict_payload)
    response = client.get("/api/prediction-history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_market_dashboard_endpoint(client):
    response = client.get("/api/market-dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "byNeighborhood" in data
    assert "priceVsSurface" in data
    assert "analysis" in data
    assert "summary" in data["analysis"]
    assert "Mortgage rates remain elevated" in data["analysis"]["externalContext"]


def test_latest_model_metrics_endpoint(client):
    response = client.get("/api/model-metrics/latest")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "mae" in data


def test_model_metrics_history_endpoint(client):
    response = client.get("/api/model-metrics/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_model_metrics_endpoints_are_public_for_prediction_page():
    unauthenticated_client = TestClient(app)

    latest_response = unauthenticated_client.get("/api/model-metrics/latest")
    history_response = unauthenticated_client.get("/api/model-metrics/history")

    assert latest_response.status_code == 200
    assert history_response.status_code == 200


