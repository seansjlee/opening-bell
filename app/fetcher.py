"""Fetches market data via yfinance and news headlines via RSS feedparser."""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import feedparser
import yfinance as yf

from app.config import MARKET_INSTRUMENTS, NEWS_MAX_ARTICLES, RSS_FEEDS

logger = logging.getLogger(__name__)


def fetch_instrument(symbol: str, name: str, category: str) -> dict | None:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = info.last_price
        prev_close = info.previous_close
        if not price or not prev_close:
            return None
        change_pct = ((price - prev_close) / prev_close) * 100
        return {
            "symbol": symbol,
            "name": name,
            "price": round(float(price), 4),
            "change_pct": round(float(change_pct), 2),
            "direction": "up" if change_pct > 0.05 else "down" if change_pct < -0.05 else "flat",
            "category": category,
        }
    except Exception as e:
        logger.warning(f"Failed to fetch {symbol}: {e}")
        return None


def fetch_all_market_data() -> dict:
    result = {}
    for category, instruments in MARKET_INSTRUMENTS.items():
        fetched = []
        for inst in instruments:
            data = fetch_instrument(inst["symbol"], inst["name"], category)
            if data:
                fetched.append(data)
        result[category] = fetched
    return result


def fetch_feed(name: str, url: str, max_articles: int = 8) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:max_articles]:
            articles.append({
                "title": entry.get("title", "").strip(),
                "summary": entry.get("summary", "")[:300].strip(),
                "url": entry.get("link", ""),
                "source": name,
                "published": entry.get("published", ""),
            })
        logger.info(f"Fetched {len(articles)} articles from {name}")
        return articles
    except Exception as e:
        logger.warning(f"Failed to fetch RSS feed {name} ({url}): {e}")
        return []


def fetch_all_news() -> list[dict]:
    all_articles = []
    for feed in RSS_FEEDS:
        articles = fetch_feed(feed["name"], feed["url"])
        all_articles.extend(articles)
    # Deduplicate by title
    seen = set()
    unique = []
    for a in all_articles:
        key = a["title"].lower()[:60]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique[:NEWS_MAX_ARTICLES]


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    market = fetch_all_market_data()
    news = fetch_all_news()
    print(f"Market instruments: {sum(len(v) for v in market.values())}")
    print(f"News articles: {len(news)}")
    print(json.dumps(market, indent=2))
