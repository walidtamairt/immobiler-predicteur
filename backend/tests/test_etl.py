from pathlib import Path

import pandas as pd

from backend.etl.clean_data import clean_dataframe, enforce_row_limit
from backend.etl import load_to_neon
from backend.etl import run_pipeline


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


def test_load_all_project_data_runs_duckdb_pipeline(monkeypatch):
    monkeypatch.setattr(load_to_neon, "load_clean_data", lambda: 321)
    monkeypatch.setattr(load_to_neon, "run_big_data_pipeline", lambda: {"train_parquet": "a", "analytics_csv": "b"})
    monkeypatch.setattr(load_to_neon, "load_external_market_context", lambda *args, **kwargs: 0)
    monkeypatch.setattr(load_to_neon, "load_scraped_market_trends", lambda *args, **kwargs: 0)
    monkeypatch.setattr(load_to_neon, "load_external_summary", lambda *args, **kwargs: 0)

    results = load_to_neon.load_all_project_data()

    assert results["properties_train"] == 321
    assert results["duckdb_big_data"] == 1
    assert results["duckdb_big_data_artifacts"] == 2


def test_run_full_pipeline_orchestrates_all_steps(monkeypatch):
    monkeypatch.setattr(run_pipeline, "fetch_external_context", lambda: ("external.csv", "summary.json"))
    monkeypatch.setattr(
        run_pipeline,
        "scrape_market_trends",
        lambda search_query=None: ("scraped.csv", "scraped.json", {"rows_collected": 3}),
    )
    monkeypatch.setattr(run_pipeline, "clean_and_save", lambda train_path, test_path: ("train_clean.csv", "test_clean.csv"))
    monkeypatch.setattr(
        run_pipeline,
        "run_big_data_pipeline",
        lambda train_path, test_path: {"analytics_csv": "analytics.csv", "analytics_parquet": "analytics.parquet"},
    )
    monkeypatch.setattr(run_pipeline, "load_clean_data", lambda csv_path: 1434)

    result = run_pipeline.run_full_pipeline()

    assert result["external_context_csv"] == "external.csv"
    assert result["scraped_trends_rows"] == 3
    assert result["loaded_rows"] == 1434
