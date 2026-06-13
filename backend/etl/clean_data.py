from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from backend.etl.ingest_data import ingest_csv
from backend.utils.logger import get_logger

logger = get_logger(__name__)

KEEP_COLUMNS = [
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
    "YearBuilt",
    "SalePrice",
]

NUMERIC_COLUMNS = [
    "GrLivArea",
    "LotArea",
    "OverallQual",
    "OverallCond",
    "BedroomAbvGr",
    "FullBath",
    "GarageCars",
    "GarageArea",
    "MoSold",
    "YearBuilt",
    "SalePrice",
]
CATEGORICAL_COLUMNS = ["Neighborhood", "HouseStyle"]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(column).strip() for column in cleaned.columns]
    return cleaned


def select_relevant_columns(df: pd.DataFrame, is_train: bool) -> pd.DataFrame:
    available = [column for column in KEEP_COLUMNS if column in df.columns]
    if not is_train and "SalePrice" in available:
        available.remove("SalePrice")
    return df.loc[:, available].copy()


def add_property_age(df: pd.DataFrame, reference_year: int = 2010) -> pd.DataFrame:
    frame = df.copy()
    if "YearBuilt" in frame.columns:
        frame["YearBuilt"] = pd.to_numeric(frame["YearBuilt"], errors="coerce")
        frame["property_age"] = (reference_year - frame["YearBuilt"]).clip(lower=0)
    else:
        frame["property_age"] = pd.NA
    return frame


def fill_missing_values(df: pd.DataFrame, is_train: bool) -> pd.DataFrame:
    frame = df.copy()
    for column in CATEGORICAL_COLUMNS:
        if column in frame.columns:
            frame[column] = frame[column].fillna("Unknown").astype(str)
    for column in NUMERIC_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
            median = frame[column].median()
            if pd.isna(median):
                median = 0
            frame[column] = frame[column].fillna(median)
    if "GarageCars" in frame.columns:
        frame["GarageCars"] = frame["GarageCars"].astype(float)
    if "property_age" in frame.columns:
        frame["property_age"] = pd.to_numeric(frame["property_age"], errors="coerce").fillna(0).astype(int)
    if is_train and "SalePrice" in frame.columns:
        frame["SalePrice"] = pd.to_numeric(frame["SalePrice"], errors="coerce")
        frame = frame.dropna(subset=["SalePrice"])
        frame["SalePrice"] = frame["SalePrice"].fillna(frame["SalePrice"].median())
    return frame


def remove_duplicates_and_outliers(df: pd.DataFrame, is_train: bool) -> pd.DataFrame:
    frame = df.drop_duplicates().copy()
    if "GrLivArea" in frame.columns:
        frame = frame[frame["GrLivArea"] < 3000]
    if "LotArea" in frame.columns:
        upper = frame["LotArea"].quantile(0.995)
        frame = frame[frame["LotArea"] <= upper]
    if is_train and "SalePrice" in frame.columns:
        frame = frame[(frame["SalePrice"] >= 10000) & (frame["SalePrice"] <= 1000000)]
    return frame


def finalize_columns(df: pd.DataFrame, is_train: bool) -> pd.DataFrame:
    desired = [
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
    ]
    if is_train:
        desired.append("SalePrice")
    frame = df.loc[:, [column for column in desired if column in df.columns]].copy()
    ordered = [column for column in desired if column in frame.columns]
    return frame.loc[:, ordered]


def clean_dataframe(df: pd.DataFrame, is_train: bool) -> pd.DataFrame:
    frame = standardize_columns(df)
    frame = select_relevant_columns(frame, is_train=is_train)
    frame = add_property_age(frame)
    frame = fill_missing_values(frame, is_train=is_train)
    frame = remove_duplicates_and_outliers(frame, is_train=is_train)
    frame = finalize_columns(frame, is_train=is_train)
    return frame.reset_index(drop=True)


def enforce_row_limit(df: pd.DataFrame, max_rows: int = 110000, random_state: int = 42) -> pd.DataFrame:
    if len(df) <= max_rows:
        return df
    return df.sample(n=max_rows, random_state=random_state).reset_index(drop=True)


def export_data_lake_snapshot(df: pd.DataFrame, dataset_name: str, layer: str) -> Path:
    output_dir = Path("data/lake") / layer
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{dataset_name}.parquet.gzip"
    df.to_parquet(output_path, index=False, compression="gzip")
    logger.info("Saved data lake snapshot to %s", output_path)
    return output_path


def clean_and_save(train_path: str | Path, test_path: str | Path) -> tuple[Path, Path]:
    train_df = ingest_csv(train_path)
    test_df = ingest_csv(test_path)

    clean_train = enforce_row_limit(clean_dataframe(train_df, is_train=True))
    clean_test = enforce_row_limit(clean_dataframe(test_df, is_train=False))

    export_data_lake_snapshot(train_df, "train_raw", "raw")
    export_data_lake_snapshot(test_df, "test_raw", "raw")
    export_data_lake_snapshot(clean_train, "train_clean", "processed")
    export_data_lake_snapshot(clean_test, "test_clean", "processed")

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    train_output = output_dir / "train_clean.csv"
    test_output = output_dir / "test_clean.csv"
    clean_train.to_csv(train_output, index=False)
    clean_test.to_csv(test_output, index=False)
    logger.info("Saved %s and %s", train_output, test_output)
    return train_output, test_output


if __name__ == "__main__":
    clean_and_save("data/raw/train.csv", "data/raw/test.csv")
