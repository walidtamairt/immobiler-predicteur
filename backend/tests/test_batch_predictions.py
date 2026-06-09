import pandas as pd

from backend.ml.predict_batch import FEATURES


def test_batch_prediction_feature_set():
    assert "Neighborhood" in FEATURES
    assert "HouseStyle" in FEATURES


def test_prediction_output_shape():
    frame = pd.DataFrame(
        [
            {
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
        ]
    )
    assert list(frame[FEATURES].columns) == FEATURES
