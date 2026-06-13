import json
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


def _replace_table_records(db, table_name: str, insert_sql: str, records: list[dict], batch_size: int = 5000) -> int:
    inserted = 0
    db.execute(text(f"DELETE FROM {table_name}"))
    for start in range(0, len(records), batch_size):
        chunk = records[start : start + batch_size]
        if not chunk:
            continue
        db.execute(text(insert_sql), chunk)
        inserted += len(chunk)
    return inserted


def load_external_market_context(csv_path: str | Path = "data/external/external_market_context.csv", batch_size: int = 5000) -> int:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"External market context file not found: {path}")

    load_schema()
    df = pd.read_csv(path)
    records = df.to_dict(orient="records")
    db = SessionLocal()
    try:
        inserted = _replace_table_records(
            db,
            "external_market_context",
            """
            INSERT INTO external_market_context
            (source, country, indicator, year, value)
            VALUES
            (:source, :country, :indicator, :year, :value)
            """,
            [
                {
                    "source": "FRED API",
                    "country": record.get("country"),
                    "indicator": record.get("indicator"),
                    "year": record.get("year"),
                    "value": record.get("value"),
                }
                for record in records
            ],
            batch_size=batch_size,
        )
        db.commit()
        logger.info("Inserted %s rows into external_market_context", inserted)
        return inserted
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"Failed to load external market context into Neon: {exc}") from exc
    finally:
        db.close()


def load_scraped_market_trends(csv_path: str | Path = "data/external/scraped_market_trends.csv", batch_size: int = 5000) -> int:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Scraped market trends file not found: {path}")

    load_schema()
    df = pd.read_csv(path)
    records = df.fillna("").to_dict(orient="records")
    db = SessionLocal()
    try:
        inserted = _replace_table_records(
            db,
            "scraped_market_trends",
            """
            INSERT INTO scraped_market_trends
            (city, average_price, trend, description, source_url, source_title)
            VALUES
            (:city, :average_price, :trend, :description, :source_url, :source_title)
            """,
            [
                {
                    "city": record.get("city"),
                    "average_price": record.get("average_price") if record.get("average_price") != "" else None,
                    "trend": record.get("trend"),
                    "description": record.get("description"),
                    "source_url": record.get("source_url") or None,
                    "source_title": record.get("source_title") or None,
                }
                for record in records
            ],
            batch_size=batch_size,
        )
        db.commit()
        logger.info("Inserted %s rows into scraped_market_trends", inserted)
        return inserted
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"Failed to load scraped market trends into Neon: {exc}") from exc
    finally:
        db.close()


def load_external_summary(summary_path: str | Path, summary_kind: str, source: str) -> int:
    path = Path(summary_path)
    if not path.exists():
        raise FileNotFoundError(f"External summary file not found: {path}")

    load_schema()
    payload = pd.read_json(path, typ="series").to_dict()
    db = SessionLocal()
    try:
        db.execute(
            text("DELETE FROM external_context_summaries WHERE summary_kind = :summary_kind"),
            {"summary_kind": summary_kind},
        )
        db.execute(
            text(
                """
                INSERT INTO external_context_summaries
                (summary_kind, source, summary_text, rows_collected, average_indicator_value, payload_json)
                VALUES
                (:summary_kind, :source, :summary_text, :rows_collected, :average_indicator_value, :payload_json)
                """
            ),
            {
                "summary_kind": summary_kind,
                "source": source,
                "summary_text": payload.get("summary_text"),
                "rows_collected": payload.get("rows_collected"),
                "average_indicator_value": payload.get("average_indicator_value"),
                "payload_json": json.dumps(payload, ensure_ascii=False),
            },
        )
        db.commit()
        logger.info("Upserted summary %s into external_context_summaries", summary_kind)
        return 1
    except Exception as exc:
        db.rollback()
        raise RuntimeError(f"Failed to load external summary into Neon: {exc}") from exc
    finally:
        db.close()


def load_all_project_data() -> dict[str, int]:
    results = {"properties_train": load_clean_data()}

    external_context_path = Path("data/external/external_market_context.csv")
    if external_context_path.exists():
        results["external_market_context"] = load_external_market_context(external_context_path)

    scraped_trends_path = Path("data/external/scraped_market_trends.csv")
    if scraped_trends_path.exists():
        results["scraped_market_trends"] = load_scraped_market_trends(scraped_trends_path)

    external_summary_path = Path("data/external/external_market_summary.json")
    if external_summary_path.exists():
        load_external_summary(external_summary_path, summary_kind="external_api", source="FRED API")
        results["external_api_summary"] = 1

    scraped_summary_path = Path("data/external/scraped_market_trends_summary.json")
    if scraped_summary_path.exists():
        load_external_summary(scraped_summary_path, summary_kind="html_scraping", source="HTML scraping")
        results["html_scraping_summary"] = 1

    return results


if __name__ == "__main__":
    print(load_all_project_data())
