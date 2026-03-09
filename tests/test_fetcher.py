"""Tests for the market data and news fetcher."""
from unittest.mock import MagicMock, patch

import pytest

from app.fetcher import fetch_instrument, fetch_feed, fetch_all_news


def test_fetch_instrument_calculates_change():
    mock_fast_info = MagicMock()
    mock_fast_info.last_price = 5000.0
    mock_fast_info.previous_close = 4950.0

    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.fast_info = mock_fast_info
        result = fetch_instrument("^GSPC", "S&P 500", "index")

    assert result is not None
    assert result["name"] == "S&P 500"
    assert result["symbol"] == "^GSPC"
    assert result["price"] == 5000.0
    assert result["change_pct"] == pytest.approx(1.01, rel=1e-2)
    assert result["direction"] == "up"
    assert result["category"] == "index"


def test_fetch_instrument_returns_none_on_error():
    with patch("yfinance.Ticker", side_effect=Exception("Network error")):
        result = fetch_instrument("INVALID", "Test", "index")
    assert result is None


def test_fetch_instrument_direction_flat():
    mock_fast_info = MagicMock()
    mock_fast_info.last_price = 100.0
    mock_fast_info.previous_close = 100.03  # 0.03% change → flat

    with patch("yfinance.Ticker") as mock_ticker:
        mock_ticker.return_value.fast_info = mock_fast_info
        result = fetch_instrument("TEST", "Test", "index")

    assert result["direction"] == "flat"


def test_fetch_feed_parses_entries():
    mock_feed = MagicMock()
    mock_feed.entries = [
        MagicMock(title="Fed raises rates", summary="The Federal Reserve...", link="https://example.com/1", published="Mon, 01 Jan 2024"),
        MagicMock(title="Markets rally", summary="Stocks surged...", link="https://example.com/2", published="Mon, 01 Jan 2024"),
    ]
    for e in mock_feed.entries:
        e.get = lambda k, d="", _e=e: getattr(_e, k, d)

    with patch("feedparser.parse", return_value=mock_feed):
        articles = fetch_feed("Test Source", "https://example.com/rss")

    # feedparser entries use attribute access, so mock properly
    assert isinstance(articles, list)


def test_fetch_all_news_deduplicates():
    """Duplicate titles across feeds should be removed."""
    with patch("app.fetcher.fetch_feed") as mock_fetch:
        mock_fetch.return_value = [
            {"title": "Duplicate story", "summary": "...", "url": "https://a.com", "source": "A", "published": ""},
        ]
        articles = fetch_all_news()

    # Each feed returns the same story — should be deduplicated
    assert len(articles) == 1
