"""Tests for the Claude summariser."""
import json
from unittest.mock import MagicMock, patch

import pytest

from app.summariser import generate_briefing, _format_news


SAMPLE_BRIEFING = {
    "date": "2024-01-15",
    "generated_at": "2024-01-15T08:00:00+00:00",
    "market_snapshot": [
        {"name": "S&P 500", "symbol": "^GSPC", "price": 4800.0, "change_pct": 0.5,
         "direction": "up", "category": "index"},
    ],
    "top_stories": [
        {"headline": "Fed signals rate pause", "summary": "The Federal Reserve indicated...",
         "why_it_matters": "Lower rates boost equities.", "source": "Reuters"},
    ],
    "macro_pulse": "The Fed held rates steady at 5.25%.",
    "sector_spotlight": "Technology leads gains.",
    "key_takeaway": "Markets rally on Fed pivot hopes.",
}


def test_generate_briefing_parses_json():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(SAMPLE_BRIEFING))]

    with patch("app.summariser._get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_message
        result = generate_briefing(
            market_data={"indices": [{"name": "S&P 500", "symbol": "^GSPC", "price": 4800.0}]},
            news_articles=[{"title": "Fed news", "source": "Reuters", "summary": "..."}],
        )

    assert result["date"] == "2024-01-15"
    assert len(result["market_snapshot"]) == 1
    assert len(result["top_stories"]) == 1
    assert result["key_takeaway"] == "Markets rally on Fed pivot hopes."


def test_generate_briefing_strips_markdown_code_block():
    wrapped = f"```json\n{json.dumps(SAMPLE_BRIEFING)}\n```"
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=wrapped)]

    with patch("app.summariser._get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_message
        result = generate_briefing({}, [])

    assert result["date"] == "2024-01-15"


def test_format_news_truncates():
    articles = [{"source": "Reuters", "title": "Test", "summary": "x" * 400}]
    formatted = _format_news(articles)
    assert len(formatted) < 1000  # truncated to 200 chars per summary


def test_generate_briefing_raises_on_invalid_json():
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="not valid json at all")]

    with patch("app.summariser._get_client") as mock_client:
        mock_client.return_value.messages.create.return_value = mock_message
        with pytest.raises(json.JSONDecodeError):
            generate_briefing({}, [])
