"""Sends the daily briefing to Slack via Incoming Webhook using Block Kit."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)


def _direction_emoji(direction: str) -> str:
    return {"up": "🟢", "down": "🔴", "flat": "⚪️"}.get(direction, "⚪️")


def _change_str(change_pct: float) -> str:
    sign = "+" if change_pct >= 0 else ""
    return f"{sign}{change_pct:.2f}%"


def build_slack_blocks(briefing: dict, dashboard_url: str) -> list:
    date = briefing.get("date", "today")

    # Market snapshot — two columns, up to 6 instruments
    snapshot = briefing.get("market_snapshot", [])
    snapshot_text = "\n".join(
        f"{_direction_emoji(item['direction'])} *{item['name']}* {_change_str(item['change_pct'])}"
        for item in snapshot[:6]
    )

    # Top 3 stories as bullet points
    stories = briefing.get("top_stories", [])[:3]
    story_lines = "\n".join(f"• {s['headline']}" for s in stories)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"🔔 Opening Bell — {date}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": snapshot_text or "_No market data available_"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Key Takeaway*\n{briefing.get('key_takeaway', '_No summary available_')}",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Top Stories*\n{story_lines or '_No stories available_'}",
            },
        },
    ]

    if dashboard_url:
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 View Full Dashboard"},
                    "url": dashboard_url,
                    "style": "primary",
                }
            ],
        })

    return blocks


def send_slack_notification(briefing: dict) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("SLACK_WEBHOOK_URL environment variable is not set")

    dashboard_url = os.getenv("DASHBOARD_URL", "")
    blocks = build_slack_blocks(briefing, dashboard_url)

    response = httpx.post(webhook_url, json={"blocks": blocks}, timeout=10)
    response.raise_for_status()
    logger.info("Slack notification sent successfully")


if __name__ == "__main__":
    import json
    from pathlib import Path
    logging.basicConfig(level=logging.INFO)
    latest = Path(__file__).parent.parent / "data" / "latest.json"
    if latest.exists():
        briefing = json.loads(latest.read_text())
        send_slack_notification(briefing)
    else:
        print("No latest.json found. Run `make run` first.")
