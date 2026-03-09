"""APScheduler configuration for the 8 AM London time daily briefing."""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import SCHEDULE_HOUR, SCHEDULE_MINUTE, SCHEDULE_TIMEZONE

logger = logging.getLogger(__name__)


def create_scheduler() -> BackgroundScheduler:
    from app.pipeline import run_pipeline

    scheduler = BackgroundScheduler(timezone=SCHEDULE_TIMEZONE)
    scheduler.add_job(
        run_pipeline,
        trigger=CronTrigger(
            hour=SCHEDULE_HOUR,
            minute=SCHEDULE_MINUTE,
            timezone=SCHEDULE_TIMEZONE,
        ),
        id="morning_briefing",
        name="Opening Bell Morning Briefing",
        misfire_grace_time=300,
        replace_existing=True,
    )
    logger.info(
        f"Scheduled daily briefing at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} {SCHEDULE_TIMEZONE}"
    )
    return scheduler
