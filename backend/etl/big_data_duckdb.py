from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.utils.logger import get_logger

logger = get_logger(__name__)

RAW_OUTPUT_DIR = Path("data/lake/raw")
ANALYTICS_OUTPUT_DIR = Path("data/lake/analytics")


def _sql_string(value: str) -> str:
    """Return a SQL string literal safely quoted for DuckDB statements."""

    return "'" + value.replace("'", "''") + "'"


def _load_duckdb():
    """
    Import DuckDB lazily so the rest of the project keeps working even if the
    optional dependency is not installed yet.
    """

    try:
        import duckdb  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency availability varies by environment
        raise RuntimeError(
            "DuckDB is required for backend.etl.big_data_duckdb. "
            "Install it with: pip install duckdb"
        ) from exc
    return duckdb


def export_csv_to_parquet_with_duckdb(
    source_csv: str | Path,
    destination_parquet: str | Path,
) -> Path:
    """
    Convert a CSV file to Parquet using DuckDB's vectorized engine.
    """

    duckdb = _load_duckdb()
    source_path = Path(source_csv)
    destination_path = Path(destination_parquet)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(database=":memory:")
    try:
        # DuckDB expects filesystem paths embedded as SQL literals here.
        connection.execute(
            f"""
            COPY (
                SELECT *
                FROM read_csv_auto({_sql_string(source_path.as_posix())}, header = true)
            )
            TO {_sql_string(destination_path.as_posix())}
            (FORMAT PARQUET, COMPRESSION ZSTD)
            """
        )
    finally:
        connection.close()

    logger.info("DuckDB converted %s to %s", source_path, destination_path)
    return destination_path


def build_neighborhood_analytics(
    train_parquet_path: str | Path,
    output_csv_path: str | Path,
    output_parquet_path: str | Path,
) -> tuple[Path, Path]:
    """
    Run an analytical SQL aggregation with DuckDB on Parquet data.

    The query is intentionally SQL-heavy to simulate a "big data" analytical
    workload while staying local and lightweight.
    """

    duckdb = _load_duckdb()
    train_path = Path(train_parquet_path)
    output_csv = Path(output_csv_path)
    output_parquet = Path(output_parquet_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_parquet.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(database=":memory:")
    try:
        analytics_df = connection.execute(
            """
            WITH train_data AS (
                SELECT
                    Neighborhood,
                    HouseStyle,
                    MoSold,
                    GrLivArea,
                    SalePrice
                FROM read_parquet(?)
                WHERE SalePrice IS NOT NULL
            ),
            neighborhood_month AS (
                SELECT
                    Neighborhood,
                    HouseStyle,
                    MoSold AS sale_month,
                    COUNT(*) AS property_count,
                    AVG(SalePrice) AS average_sale_price,
                    MEDIAN(SalePrice) AS median_sale_price,
                    AVG(GrLivArea) AS average_living_area,
                    AVG(SalePrice / NULLIF(GrLivArea, 0)) AS average_price_per_sqft
                FROM train_data
                GROUP BY Neighborhood, HouseStyle, MoSold
            ),
            ranked_segments AS (
                SELECT
                    *,
                    DENSE_RANK() OVER (
                        PARTITION BY sale_month
                        ORDER BY average_sale_price DESC
                    ) AS price_rank_in_month
                FROM neighborhood_month
            )
            SELECT *
            FROM ranked_segments
            ORDER BY sale_month, price_rank_in_month, Neighborhood
            """,
            [str(train_path)],
        ).fetchdf()
    finally:
        connection.close()

    analytics_df.to_csv(output_csv, index=False)
    analytics_df.to_parquet(output_parquet, index=False, compression="gzip")
    logger.info("DuckDB analytics exported to %s and %s", output_csv, output_parquet)
    return output_csv, output_parquet


def run_big_data_pipeline(
    train_csv_path: str | Path = "data/train.csv",
    test_csv_path: str | Path = "data/test.csv",
) -> dict[str, str]:
    """
    End-to-end local "big data" style pipeline:

    1. Convert raw CSV assets to Parquet.
    2. Execute an analytical DuckDB SQL workload on Parquet.
    3. Persist aggregated outputs for downstream reporting or dashboards.
    """

    RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ANALYTICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_parquet = export_csv_to_parquet_with_duckdb(train_csv_path, RAW_OUTPUT_DIR / "train_bigdata.parquet")
    test_parquet = export_csv_to_parquet_with_duckdb(test_csv_path, RAW_OUTPUT_DIR / "test_bigdata.parquet")

    analytics_csv, analytics_parquet = build_neighborhood_analytics(
        train_parquet,
        ANALYTICS_OUTPUT_DIR / "neighborhood_month_metrics.csv",
        ANALYTICS_OUTPUT_DIR / "neighborhood_month_metrics.parquet.gzip",
    )

    return {
        "train_parquet": str(train_parquet),
        "test_parquet": str(test_parquet),
        "analytics_csv": str(analytics_csv),
        "analytics_parquet": str(analytics_parquet),
    }


if __name__ == "__main__":
    print(run_big_data_pipeline())
