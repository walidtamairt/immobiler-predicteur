from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

from backend.etl.load_to_neon import load_external_summary, load_scraped_market_trends
from backend.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_HTML_SOURCE = Path("data/external/mock_market_trends.html")
FALLBACK_HTML_SOURCE = Path(__file__).resolve().parents[2] / "data" / "external" / "mock_market_trends.html"
DEFAULT_OUTPUT_DIR = Path("data/external")
DEFAULT_SEARCH_QUERY = "real estate usa prices by city"
DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
REQUEST_TIMEOUT = 20


@dataclass(slots=True)
class ScrapedSource:
    url: str
    title: str


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split()).strip()


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    stripped = "".join(character for character in normalized if not unicodedata.combining(character))
    return _normalize_whitespace(stripped).lower()


def fetch_html_document(source: str | Path | None = None) -> str:
    target = source or DEFAULT_HTML_SOURCE
    if isinstance(target, Path):
        if target.exists():
            return target.read_text(encoding="utf-8")
        if source is None and FALLBACK_HTML_SOURCE.exists():
            return FALLBACK_HTML_SOURCE.read_text(encoding="utf-8")
        raise FileNotFoundError(f"HTML source not found: {target}")

    if str(target).startswith(("http://", "https://")):
        return fetch_html_from_url(str(target))

    path = Path(target)
    if path.exists():
        return path.read_text(encoding="utf-8")
    if source is None and FALLBACK_HTML_SOURCE.exists():
        return FALLBACK_HTML_SOURCE.read_text(encoding="utf-8")
    raise FileNotFoundError(f"HTML source not found: {path}")


def fetch_html_from_url(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def fetch_web_search_results(query: str, max_results: int = 3) -> list[dict[str, str]]:
    response = requests.get(
        DUCKDUCKGO_HTML_URL,
        params={"q": query},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results: list[dict[str, str]] = []

    for anchor in soup.select("a.result__a"):
        href = anchor.get("href")
        title = _normalize_whitespace(anchor.get_text(" ", strip=True))
        if not href or not title:
            continue
        results.append({"title": title, "url": href})
        if len(results) >= max_results:
            break

    return results


def _extract_text(node: Any) -> str:
    if isinstance(node, str):
        return _normalize_whitespace(node)
    if node is None:
        return ""
    return _normalize_whitespace(node.get_text(" ", strip=True))


def _parse_price(raw_value: str | None) -> float | None:
    if not raw_value:
        return None

    cleaned = (
        str(raw_value)
        .replace("EUR", "")
        .replace("€", "")
        .replace("$", "")
        .replace("USD", "")
        .replace(",", "")
        .replace(" ", "")
        .strip()
    )
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None

    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_numbeo_market_page(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []

    for row in soup.select("table tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue

        label = _normalize_text(cells[0])
        value_text = cells[1]
        value = _parse_price(value_text)

        if "immobilier" in label or "appartement" in label or "apartment" in label or "rent" in label or "prix" in label:
            records.append(
                {
                    "city": "United States",
                    "average_price": value,
                    "trend": cells[0],
                    "description": f"{cells[0]}: {cells[1]}",
                }
            )

    return records


def parse_market_trends_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []

    for card in soup.select(".market-trend"):
        city = card.get("data-city") or card.select_one(".city")
        avg_price = card.get("data-average-price") or card.select_one(".average-price")
        trend = card.get("data-trend") or card.select_one(".trend")
        description = card.select_one(".description")

        city_value = _extract_text(city)
        avg_price_value = _extract_text(avg_price)
        trend_value = _extract_text(trend)
        description_value = _extract_text(description)

        if not city_value:
            continue

        records.append(
            {
                "city": city_value,
                "average_price": _parse_price(avg_price_value),
                "trend": trend_value or "stable",
                "description": description_value,
            }
        )

    if records:
        return records

    numbeo_records = parse_numbeo_market_page(html)
    if numbeo_records:
        return numbeo_records

    for row in soup.select("table.market-trends tbody tr"):
        columns = row.find_all(["td", "th"])
        if len(columns) < 4:
            continue
        records.append(
            {
                "city": columns[0].get_text(strip=True),
                "average_price": _parse_price(columns[1].get_text(strip=True)),
                "trend": columns[2].get_text(strip=True),
                "description": columns[3].get_text(strip=True),
            }
        )

    return records


def build_scraping_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "rows_collected": 0,
            "top_city": None,
            "summary_text": "No market trend rows could be extracted from the HTML source.",
        }

    comparable_rows = [row for row in records if row.get("average_price") is not None]
    top_city = max(comparable_rows, key=lambda item: item["average_price"]) if comparable_rows else None

    summary_parts = [f"{row['city']} ({row['trend']})" for row in records[:3]]
    summary_text = "Neighborhood and city signals scraped from HTML: " + ", ".join(summary_parts) + "."

    return {
        "rows_collected": len(records),
        "top_city": top_city,
        "summary_text": summary_text,
    }


def save_scraped_outputs(records: list[dict[str, Any]], summary: dict[str, Any]) -> tuple[Path, Path]:
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DEFAULT_OUTPUT_DIR / "scraped_market_trends.csv"
    json_path = DEFAULT_OUTPUT_DIR / "scraped_market_trends_summary.json"
    pd.DataFrame(records).to_csv(csv_path, index=False)
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved scraping outputs to %s and %s", csv_path, json_path)
    try:
        load_scraped_market_trends(csv_path)
        load_external_summary(json_path, summary_kind="html_scraping", source="HTML scraping")
    except Exception as exc:
        logger.warning("Scraped outputs were saved locally but not loaded into Neon: %s", exc)
    return csv_path, json_path


def scrape_market_trends(
    source: str | Path | None = None,
    *,
    search_query: str | None = None,
    search_results: int = 3,
) -> tuple[Path, Path, dict[str, Any]]:
    if search_query:
        search_hits = fetch_web_search_results(search_query, max_results=search_results)
        combined_records: list[dict[str, Any]] = []
        source_details: list[ScrapedSource] = []

        for hit in search_hits:
            try:
                html = fetch_html_from_url(hit["url"])
            except requests.RequestException as exc:
                logger.warning("Skipping search result %s because it could not be fetched: %s", hit["url"], exc)
                continue

            source_details.append(ScrapedSource(url=hit["url"], title=hit["title"]))
            parsed = parse_market_trends_html(html)
            if not parsed:
                parsed = [
                    {
                        "city": hit["title"],
                        "average_price": None,
                        "trend": "search-result",
                        "description": _normalize_whitespace(BeautifulSoup(html, "html.parser").get_text(" ", strip=True))[:400],
                        "source_url": hit["url"],
                        "source_title": hit["title"],
                    }
                ]
            else:
                for item in parsed:
                    item["source_url"] = hit["url"]
                    item["source_title"] = hit["title"]
            combined_records.extend(parsed)

        summary = build_scraping_summary(combined_records)
        summary["search_query"] = search_query
        summary["search_hits"] = search_hits
        summary["sources"] = [{"url": source.url, "title": source.title} for source in source_details]
        csv_path, json_path = save_scraped_outputs(combined_records, summary)
        return csv_path, json_path, summary

    html = fetch_html_document(source)
    records = parse_market_trends_html(html)
    summary = build_scraping_summary(records)
    csv_path, json_path = save_scraped_outputs(records, summary)
    return csv_path, json_path, summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape market trends from HTML or search the web.")
    parser.add_argument("--source", default=None, help="Local path or URL to scrape.")
    parser.add_argument("--search", default=None, help="Web search query to discover pages to scrape.")
    parser.add_argument("--results", type=int, default=3, help="Number of search results to inspect.")
    args = parser.parse_args()

    print(
        scrape_market_trends(
            source=args.source,
            search_query=args.search,
            search_results=args.results,
        )
    )
