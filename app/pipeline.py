"""Orchestrates the full pipeline: fetch → summarise → save → notify."""

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import BRIEFINGS_DIR, DATA_DIR
from app.fetcher import fetch_all_market_data, fetch_all_news
from app.notifier import send_slack_notification
from app.summariser import generate_briefing

logger = logging.getLogger(__name__)


def run_pipeline() -> dict:
    logger.info("=== Opening Bell pipeline starting ===")

    logger.info("Step 1/4: Fetching market data...")
    market_data = fetch_all_market_data()
    total_instruments = sum(len(v) for v in market_data.values())
    logger.info(f"Fetched {total_instruments} market instruments")

    logger.info("Step 2/4: Fetching news headlines...")
    news_articles = fetch_all_news()
    logger.info(f"Fetched {len(news_articles)} news articles")

    logger.info("Step 3/4: Generating briefing with Claude...")
    briefing = generate_briefing(market_data, news_articles)

    date_str = briefing.get(
        "date",
        datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d"),
    )

    dated_path = BRIEFINGS_DIR / f"{date_str}.json"
    dated_path.write_text(json.dumps(briefing, indent=2))

    latest_path = DATA_DIR / "latest.json"
    latest_path.write_text(json.dumps(briefing, indent=2))
    logger.info(f"Briefing saved to {dated_path}")

    logger.info("Step 4/4: Sending Slack notification...")
    try:
        send_slack_notification(briefing)
    except Exception as e:
        logger.error(f"Slack notification failed (continuing): {e}")

    logger.info("=== Opening Bell pipeline complete ===")
    return briefing


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )
    run_pipeline()
