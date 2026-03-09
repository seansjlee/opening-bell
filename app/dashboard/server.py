"""FastAPI dashboard server with embedded APScheduler."""

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import BRIEFINGS_DIR, DATA_DIR
from app.scheduler import create_scheduler

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started")
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


app = FastAPI(title="Opening Bell", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/briefing/latest")
async def get_latest():
    path = DATA_DIR / "latest.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No briefing available yet. Run `make run` to generate one.")
    return JSONResponse(json.loads(path.read_text()))


@app.get("/api/briefing/{date}")
async def get_by_date(date: str):
    path = BRIEFINGS_DIR / f"{date}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No briefing found for {date}")
    return JSONResponse(json.loads(path.read_text()))


@app.get("/api/briefings")
async def list_briefings():
    if not BRIEFINGS_DIR.exists():
        return JSONResponse([])
    dates = sorted([p.stem for p in BRIEFINGS_DIR.glob("*.json")], reverse=True)
    return JSONResponse(dates)


@app.get("/health")
async def health():
    return {"status": "ok"}
