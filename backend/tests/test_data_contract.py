import pandas as pd

from backend.etl.clean_data import clean_dataframe


def test_cleaned_columns_are_present_and_removed_columns_absent():
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
                "SalePrice": 220000,
                "PoolArea": 0,
                "Alley": None,
            }
        ]
    )
    cleaned = clean_dataframe(frame, is_train=True)
    expected = {
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
    }
    removed = {"PoolArea", "Alley", "YearBuilt"}
    assert expected.issubset(set(cleaned.columns))
    assert removed.isdisjoint(set(cleaned.columns))
