from pathlib import Path

import backend.etl.scrape_market_trends as scraper
from backend.etl.clean_data import export_data_lake_snapshot


def test_parse_market_trends_html_extracts_records():
    html = Path("data/external/mock_market_trends.html").read_text(encoding="utf-8")
    records = scraper.parse_market_trends_html(html)

    assert len(records) == 3
    assert records[0]["city"] == "Ames"
    assert records[1]["average_price"] == 312000.0


def test_build_scraping_summary_identifies_top_city():
    summary = scraper.build_scraping_summary(
        [
            {"city": "Ames", "average_price": 248000.0, "trend": "rising", "description": "Test"},
            {"city": "Des Moines", "average_price": 312000.0, "trend": "stable", "description": "Test"},
        ]
    )

    assert summary["rows_collected"] == 2
    assert summary["top_city"]["city"] == "Des Moines"


def test_parse_numbeo_market_page_extracts_metrics():
    html = """
    <html>
      <body>
        <table>
          <tr><td>Prix de l'immobilier aux Etats-Unis</td><td>3,200</td></tr>
          <tr><td>Appartement (1 chambre) dans le Centre-ville</td><td>1,850</td></tr>
        </table>
      </body>
    </html>
    """

    records = scraper.parse_market_trends_html(html)

    assert len(records) == 2
    assert records[0]["city"] == "United States"
    assert records[1]["average_price"] == 1850.0


def test_scrape_market_trends_writes_outputs():
    csv_path, json_path, summary = scraper.scrape_market_trends()

    assert csv_path.exists()
    assert json_path.exists()
    assert summary["rows_collected"] >= 1


def test_scrape_market_trends_search_mode(monkeypatch, tmp_path):
    monkeypatch.setattr(scraper, "DEFAULT_OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(
        scraper,
        "fetch_web_search_results",
        lambda query, max_results=3: [{"title": "Numbeo USA", "url": "https://example.com/numbeo"}],
    )
    monkeypatch.setattr(
        scraper,
        "fetch_html_from_url",
        lambda url: """
        <html>
          <body>
            <table>
              <tr><td>Appartement (1 chambre) dans le Centre-ville</td><td>1,850</td></tr>
            </table>
          </body>
        </html>
        """,
    )

    csv_path, json_path, summary = scraper.scrape_market_trends(search_query="real estate usa prices")

    assert csv_path.exists()
    assert json_path.exists()
    assert summary["search_query"] == "real estate usa prices"
    assert summary["sources"][0]["url"] == "https://example.com/numbeo"


def test_export_data_lake_snapshot_writes_parquet():
    import pandas as pd

    output_path = export_data_lake_snapshot(pd.DataFrame([{"city": "Ames", "price": 250000}]), "sample_snapshot", "raw")

    assert output_path.exists()
    assert output_path.suffixes[-2:] == [".parquet", ".gzip"]
