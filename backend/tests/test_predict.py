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
