from pathlib import Path

import pandas as pd

REQUIRED_TRAIN_COLUMNS = {"SalePrice"}


def resolve_data_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.exists():
        return candidate
    fallback = Path("data") / candidate.name
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"File not found: {candidate}")


def ingest_csv(path: str | Path) -> pd.DataFrame:
    csv_path = resolve_data_path(path)
    try:
        return pd.read_csv(csv_path)
    except Exception as exc:
        raise ValueError(f"Unable to read CSV: {csv_path}") from exc


def validate_train_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_TRAIN_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required train columns: {sorted(missing)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest Ames Housing CSV")
    parser.add_argument("csv_path")
    args = parser.parse_args()
    frame = ingest_csv(args.csv_path)
    print(f"Loaded {len(frame)} rows and {len(frame.columns)} columns")
