import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
BRIEFINGS_DIR = DATA_DIR / "briefings"

BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Required environment variable {key!r} is not set")
    return value


def _optional_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


ANTHROPIC_API_KEY: str = ""  # loaded lazily to avoid startup errors
SLACK_WEBHOOK_URL: str = ""
DASHBOARD_URL: str = _optional_env("DASHBOARD_URL", "http://localhost:8000")
API_SECRET: str = _optional_env("API_SECRET", "")

CLAUDE_MODEL = "claude-sonnet-4-20250514"

SCHEDULE_HOUR = 8
SCHEDULE_MINUTE = 0
SCHEDULE_TIMEZONE = "Europe/London"

MARKET_INSTRUMENTS = {
    "indices": [
        {"symbol": "^GSPC", "name": "S&P 500"},
        {"symbol": "^FTSE", "name": "FTSE 100"},
        {"symbol": "^GDAXI", "name": "DAX"},
        {"symbol": "^N225", "name": "Nikkei 225"},
        {"symbol": "^KS11", "name": "KOSPI"},
        {"symbol": "000300.SS", "name": "CSI 300"},
    ],
    "forex": [
        {"symbol": "GBPUSD=X", "name": "GBP/USD"},
        {"symbol": "GBPKRW=X", "name": "GBP/KRW"},
        {"symbol": "USDKRW=X", "name": "USD/KRW"},
        {"symbol": "EURUSD=X", "name": "EUR/USD"},
        {"symbol": "USDJPY=X", "name": "USD/JPY"},
    ],
    "commodities": [
        {"symbol": "GC=F", "name": "Gold"},
        {"symbol": "CL=F", "name": "WTI Oil"},
        {"symbol": "^TNX", "name": "US 10Y Treasury"},
        {"symbol": "BTC-USD", "name": "Bitcoin"},
    ],
}

RSS_FEEDS = [
    {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"name": "Bloomberg Markets", "url": "https://feeds.bloomberg.com/markets/news.rss"},
    {"name": "FT Economics", "url": "https://www.ft.com/economics?format=rss"},
    {"name": "WSJ Markets", "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"},
    {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar"},
]

NEWS_MAX_ARTICLES = 30
