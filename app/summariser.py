"""Generates structured JSON briefing using the Claude API."""

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

from app.config import CLAUDE_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are Opening Bell, a professional financial analyst AI. "
    "Generate concise, insightful daily financial briefings. "
    "Always respond with valid JSON only — no markdown, no code blocks, no commentary. "
    "Be precise with numbers and focus on market-moving insights."
)


def _get_client() -> anthropic.Anthropic:
    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")
    return anthropic.Anthropic(api_key=api_key)


def _format_news(articles: list[dict]) -> str:
    lines = []
    for a in articles[:25]:
        summary = a.get("summary", "")[:200]
        lines.append(f"[{a['source']}] {a['title']}" + (f": {summary}" if summary else ""))
    return "\n".join(lines)


def generate_briefing(market_data: dict, news_articles: list[dict]) -> dict:
    client = _get_client()
    london_now = datetime.now(ZoneInfo("Europe/London"))

    user_prompt = f"""Today: {london_now.strftime('%A, %d %B %Y')}

MARKET DATA:
{json.dumps(market_data, indent=2)}

NEWS HEADLINES ({len(news_articles)} collected):
{_format_news(news_articles)}

Generate a daily financial briefing as JSON with this exact schema — return ONLY the JSON, nothing else:
{{
  "date": "{london_now.strftime('%Y-%m-%d')}",
  "generated_at": "{london_now.isoformat()}",
  "market_snapshot": [
    {{
      "name": "instrument name",
      "symbol": "ticker symbol",
      "price": 0.00,
      "change_pct": 0.00,
      "direction": "up|down|flat",
      "category": "index|forex|commodity"
    }}
  ],
  "top_stories": [
    {{
      "headline": "concise headline",
      "summary": "2-3 sentence summary of what happened",
      "why_it_matters": "one sentence on market relevance",
      "source": "source name"
    }}
  ],
  "macro_pulse": "2-3 sentences on rates, yields, and central bank policy",
  "sector_spotlight": "1-2 sentences on sectors to watch today",
  "key_takeaway": "single paragraph synthesis of the day's key themes and what to watch"
}}

Rules:
- market_snapshot: include ALL instruments from the market data provided
- top_stories: select the 5 most market-relevant stories
- Use actual price numbers from the market data
- key_takeaway should be actionable and specific, not generic"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = message.content[0].text.strip()

    # Strip markdown code blocks if Claude adds them despite instructions
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    briefing = json.loads(content)
    logger.info(f"Briefing generated: {len(briefing.get('top_stories', []))} stories, "
                f"{len(briefing.get('market_snapshot', []))} instruments")
    return briefing


if __name__ == "__main__":
    import json as _json
    logging.basicConfig(level=logging.INFO)
    from app.fetcher import fetch_all_market_data, fetch_all_news
    market = fetch_all_market_data()
    news = fetch_all_news()
    briefing = generate_briefing(market, news)
    print(_json.dumps(briefing, indent=2))
