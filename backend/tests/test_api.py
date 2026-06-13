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


def test_chat_endpoint_local_mode(client):
    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Quel quartier semble le plus cher ?"}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "local"
    assert "answer" in data


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


def test_chat_endpoint_openrouter_mock(client, monkeypatch):
    from backend.app import api

    monkeypatch.setattr(api.settings, "openrouter_api_key", "test-key")
    monkeypatch.setattr(api, "call_openrouter", lambda messages: "Mocked OpenRouter answer")

    response = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Quelle saison est la plus favorable ?"}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "openrouter"
    assert data["answer"] == "Mocked OpenRouter answer"
