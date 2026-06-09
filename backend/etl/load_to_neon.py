from pathlib import Path

import pandas as pd
from sqlalchemy import text

from backend.database.db import SessionLocal, engine
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def load_schema() -> None:
    schema_path = Path("backend/database/schema.sql")
    with engine.begin() as connection:
        for statement in schema_path.read_text(encoding="utf-8").split(";"):
            sql = statement.strip()
            if sql:
                connection.execute(text(sql))


def limit_rows(df: pd.DataFrame, max_rows: int = 110000) -> pd.DataFrame:
    if len(df) <= max_rows:
        return df
    return df.sample(n=max_rows, random_state=42).reset_index(drop=True)


def load_clean_data(csv_path: str | Path = "data/processed/train_clean.csv", batch_size: int = 5000) -> int:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Clean train file not found: {path}")

    load_schema()
    df = limit_rows(pd.read_csv(path))
    records = df.to_dict(orient="records")
    inserted = 0

    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM properties_train"))
        for start in range(0, len(records), batch_size):
            chunk = records[start : start + batch_size]
            db.execute(
                text(
                    """
                    INSERT INTO properties_train
                    (gr_liv_area, lot_area, overall_qual, overall_cond, bedroom_abv_gr, full_bath,
                     garage_cars, garage_area, neighborhood, house_style, sale_month, property_age, sale_price)
                    VALUES
                    (:GrLivArea, :LotArea, :OverallQual, :OverallCond, :BedroomAbvGr, :FullBath,
                     :GarageCars, :GarageArea, :Neighborhood, :HouseStyle, :MoSold, :property_age, :SalePrice)
                    """
                ),
                chunk,
            )
            inserted += len(chunk)
        db.commit()
        logger.info("Inserted %s rows into properties_train", inserted)
        return inserted
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"Failed to load data into Neon: {exc}") from exc
    finally:
        db.close()


if __name__ == "__main__":
    load_clean_data()
