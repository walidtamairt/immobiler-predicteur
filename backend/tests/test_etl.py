from pathlib import Path

import pandas as pd

from backend.etl.clean_data import clean_dataframe, enforce_row_limit


def test_clean_dataframe_keeps_expected_columns():
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
                "YearBuilt": 2000,
                "SalePrice": 200000,
            }
        ]
    )
    cleaned = clean_dataframe(frame, is_train=True)
    assert list(cleaned.columns) == [
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
    ]


def test_enforce_row_limit():
    frame = pd.DataFrame({"a": range(120000)})
    limited = enforce_row_limit(frame, max_rows=110000)
    assert len(limited) == 110000
