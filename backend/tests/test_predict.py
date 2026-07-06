def test_predict_endpoint(client):
    payload = {
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
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] == 250000.0
    assert data["model_version"] == "test-v1"


def test_predict_endpoint_rejects_missing_feature(client):
    payload = {
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
    }

    response = client.post("/api/predict", json=payload)

    assert response.status_code == 422
    assert "Missing features" in response.json()["detail"]


def test_predict_endpoint_rejects_invalid_numeric_feature(client):
    payload = {
        "GrLivArea": "not-a-number",
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

    response = client.post("/api/predict", json=payload)

    assert response.status_code == 422
    assert "Invalid numeric features" in response.json()["detail"]


def test_predict_endpoint_rejects_invalid_categorical_feature(client):
    payload = {
        "GrLivArea": 1500,
        "LotArea": 8000,
        "OverallQual": 7,
        "OverallCond": 5,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2,
        "GarageArea": 400,
        "Neighborhood": "",
        "HouseStyle": "1Story",
        "MoSold": 6,
        "property_age": 10,
    }

    response = client.post("/api/predict", json=payload)

    assert response.status_code == 422
    assert "Invalid categorical feature" in response.json()["detail"]
