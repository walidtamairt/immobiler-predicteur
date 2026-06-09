from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from backend.utils.logger import get_logger

logger = get_logger(__name__)
from dotenv import load_dotenv
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

FRED_SERIES = [
    ("MORTGAGE30US", "30-Year Fixed Mortgage Rate"),
    ("CPIAUCSL", "Consumer Price Index"),
    ("UNRATE", "Unemployment Rate"),
]

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

OUTPUT_DIR = Path("data/external")
CSV_FILENAME = "external_market_context.csv"
SUMMARY_FILENAME = "external_market_summary.json"

REQUEST_TIMEOUT = 30


def _fetch_fred_series(series_id: str) -> list[dict[str, Any]]:
    if not FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is not set in environment variables")

    try:
        response = requests.get(
            FRED_BASE_URL,
            params={
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 100,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception("Failed to fetch FRED series %s", series_id)
        return []

    try:
        payload = response.json()
    except ValueError:
        logger.exception("Invalid JSON for FRED series %s", series_id)
        return []

    observations = payload.get("observations", [])
    return observations if isinstance(observations, list) else []


def _build_dataframe(series_id: str, label: str, records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []

    for item in records:
        value = item.get("value")

        if value in (None, ".", ""):
            continue

        try:
            numeric_value = float(value)
        except ValueError:
            continue

        date_raw = item.get("date")
        try:
            year = int(date_raw[:4]) if date_raw else None
        except (TypeError, ValueError):
            year = None

        rows.append(
            {
                "country": "USA",
                "indicator": label,
                "year": year,
                "value": numeric_value,
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return pd.DataFrame(columns=["country", "indicator", "year", "value"])

    df = df.dropna(subset=["year", "value"])
    df = df.sort_values("year", ascending=False).reset_index(drop=True)

    return df


def _fetch_best_dataframe() -> tuple[pd.DataFrame, str]:
    for series_id, label in FRED_SERIES:
        logger.info("Trying FRED series: %s (%s)", series_id, label)

        records = _fetch_fred_series(series_id)
        df = _build_dataframe(series_id, label, records)

        if not df.empty:
            logger.info("Using FRED series %s with %s rows", series_id, len(df))
            return df, series_id

        logger.warning("No usable data for FRED series %s", series_id)

    return pd.DataFrame(columns=["country", "indicator", "year", "value"]), ""


def _build_summary(df: pd.DataFrame, series_id: str) -> dict[str, Any]:
    if df.empty:
        return {
            "source": "FRED API",
            "series_id": series_id,
            "context_usage": "Macroeconomic context for US housing market",
            "rows_collected": 0,
            "latest_observation": {},
            "average_indicator_value": None,
            "summary_text": "No external data available.",
        }

    latest_row = df.iloc[0].to_dict()

    latest = {
        "country": latest_row.get("country"),
        "indicator": latest_row.get("indicator"),
        "year": int(latest_row.get("year")),
        "value": float(latest_row.get("value")),
    }

    avg_value = float(df["value"].mean())

    summary_text = (
        f"Latest US macro-economic context: {latest['indicator']} reached "
        f"{latest['value']} in {latest['year']}. "
        f"This indicator is used as contextual information for housing market analysis."
    )

    return {
        "source": "FRED API",
        "series_id": series_id,
        "context_usage": "Macroeconomic context for US housing market",
        "rows_collected": int(len(df)),
        "latest_observation": latest,
        "average_indicator_value": avg_value,
        "summary_text": summary_text,
    }


def fetch_external_context() -> tuple[Path, Path]:
    df, series_id = _fetch_best_dataframe()
    summary = _build_summary(df, series_id)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / CSV_FILENAME
    summary_path = OUTPUT_DIR / SUMMARY_FILENAME

    df.to_csv(csv_path, index=False)
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info(
        "Saved external context: rows=%s, csv=%s, summary=%s",
        len(df),
        csv_path,
        summary_path,
    )

    return csv_path, summary_path


if __name__ == "__main__":
    print(fetch_external_context())