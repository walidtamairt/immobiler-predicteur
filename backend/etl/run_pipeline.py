from __future__ import annotations

import argparse
from pathlib import Path

from backend.etl.big_data_duckdb import run_big_data_pipeline
from backend.etl.clean_data import clean_and_save
from backend.etl.fetch_external_context import fetch_external_context
from backend.etl.load_to_neon import load_clean_data
from backend.etl.scrape_market_trends import scrape_market_trends
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def run_full_pipeline(
    train_path: str | Path = "data/train.csv",
    test_path: str | Path = "data/test.csv",
    search_query: str | None = None,
) -> dict[str, object]:
    """
    Orchestrate the complete data pipeline in a single command.

    The execution order follows the project's data flow:
    1. external enrichment
    2. HTML scraping
    3. local cleaning and lake export
    4. DuckDB analytical processing
    5. database loading
    """

    external_csv, external_summary = fetch_external_context()
    scraped_csv, scraped_json, scraped_summary = scrape_market_trends(search_query=search_query)
    train_output, test_output = clean_and_save(train_path, test_path)
    duckdb_outputs = run_big_data_pipeline(train_path, test_path)
    loaded_rows = load_clean_data(train_output)

    return {
        "external_context_csv": str(external_csv),
        "external_context_summary": str(external_summary),
        "scraped_trends_csv": str(scraped_csv),
        "scraped_trends_json": str(scraped_json),
        "scraped_trends_rows": scraped_summary.get("rows_collected"),
        "train_clean_csv": str(train_output),
        "test_clean_csv": str(test_output),
        "duckdb_outputs": duckdb_outputs,
        "loaded_rows": loaded_rows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full Estate AI data pipeline.")
    parser.add_argument("--train-path", default="data/train.csv", help="Path to the training CSV file.")
    parser.add_argument("--test-path", default="data/test.csv", help="Path to the test CSV file.")
    parser.add_argument(
        "--search-query",
        default=None,
        help="Optional DuckDuckGo query used by the scraping step to enrich market trends.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_full_pipeline(
        train_path=args.train_path,
        test_path=args.test_path,
        search_query=args.search_query,
    )
    logger.info("Full pipeline completed successfully.")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
