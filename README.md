# Opening Bell

A daily global financial trends summariser that automatically generates and delivers a morning briefing every day at **8:00 AM London time** (handles GMT/BST automatically).

## What It Does

1. **Fetch** — Pulls major market indices, forex pairs, and commodities via `yfinance`, and top financial headlines from Reuters, BBC Business, CNBC, MarketWatch, and Yahoo Finance via RSS.
2. **Summarise** — Sends the collected data to the Claude API (`claude-sonnet-4-20250514`) to generate a structured JSON briefing with market snapshot, top stories, macro commentary, and a key takeaway.
3. **Notify** — Sends a compact briefing to Slack via Incoming Webhook using Block Kit (emoji market table, key takeaway, top headlines, dashboard link).
4. **Display** — Hosts a mobile-first dark mode dashboard at your configured URL showing the full briefing with colour-coded market data and expandable story cards.

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/seansjlee/opening-bell.git
cd opening-bell
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
make install
```

### 2. Configure Environment Variables

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `SLACK_WEBHOOK_URL` | Yes | Slack Incoming Webhook URL |
| `DASHBOARD_URL` | Optional | Public URL of your dashboard (shown in Slack messages) |

### 3. Getting Your API Keys

#### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys** -> **Create Key**
4. Copy the key (starts with `sk-ant-...`)

#### Slack Incoming Webhook
1. Go to [api.slack.com/apps](https://api.slack.com/apps) -> **Create New App** -> **From scratch**
2. Name it "Opening Bell", select your workspace
3. In **Features**, click **Incoming Webhooks** -> toggle **Activate Incoming Webhooks** to On
4. Click **Add New Webhook to Workspace** -> choose a channel -> **Allow**
5. Copy the Webhook URL (starts with `https://hooks.slack.com/services/...`)

### 4. Run the Pipeline

```bash
make run          # Full pipeline: fetch -> summarise -> notify -> save
make serve        # Start dashboard with hot-reload (development)
make start        # Start dashboard (production)
```

## Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install Python dependencies |
| `make fetch` | Run only the data fetcher |
| `make summarise` | Run only the Claude summariser (requires existing data) |
| `make notify` | Send Slack notification from latest briefing |
| `make run` | Full pipeline (fetch + summarise + notify + save) |
| `make serve` | Start dashboard with auto-reload (development) |
| `make start` | Start dashboard for production |
| `make test` | Run test suite |

## Dashboard

The dashboard is served by FastAPI at `http://localhost:8000` (or your `PORT`).

**API endpoints:**
- `GET /` — Dashboard UI
- `GET /api/briefing/latest` — Latest briefing JSON
- `GET /api/briefing/{YYYY-MM-DD}` — Specific date briefing
- `GET /api/briefings` — List of available dates
- `GET /health` — Health check

## Scheduler

The scheduler runs inside the FastAPI process using APScheduler. It triggers at **08:00 Europe/London** every day — APScheduler handles the GMT/BST transition automatically via the `zoneinfo` timezone.

When deployed, just run `make start` (or the Railway start command) — no separate worker process needed.

## Deploying to Railway

1. Push to GitHub
2. Go to [railway.app](https://railway.app) -> **New Project** -> **Deploy from GitHub repo**
3. Select `opening-bell`
4. In **Variables**, add:
   - `ANTHROPIC_API_KEY`
   - `SLACK_WEBHOOK_URL`
   - `DASHBOARD_URL` (set this to your Railway app URL after first deploy)
5. Railway auto-detects the start command from `railway.toml`

Railway provides a `PORT` environment variable automatically — the app uses it via `${PORT:-8000}`.

## Project Structure

```
opening-bell/
├── app/
│   ├── config.py          # Environment config, instrument lists, RSS feeds
│   ├── fetcher.py         # yfinance market data + feedparser RSS
│   ├── summariser.py      # Claude API -> structured JSON briefing
│   ├── notifier.py        # Slack Block Kit notification
│   ├── pipeline.py        # Orchestrates fetch -> summarise -> notify -> save
│   ├── scheduler.py       # APScheduler 8 AM London CronTrigger
│   └── dashboard/
│       ├── server.py      # FastAPI app (also starts scheduler)
│       ├── templates/index.html
│       └── static/{style.css,app.js}
├── data/
│   ├── briefings/         # YYYY-MM-DD.json (gitignored)
│   └── latest.json        # Most recent briefing (gitignored)
├── tests/
├── Makefile
├── requirements.txt
├── railway.toml
└── .env.example
```

## Briefing JSON Schema

```json
{
  "date": "2024-01-15",
  "generated_at": "2024-01-15T08:00:00+00:00",
  "market_snapshot": [{ "name": "S&P 500", "symbol": "^GSPC", "price": 4800.0, "change_pct": 0.5, "direction": "up", "category": "index" }],
  "top_stories": [{ "headline": "...", "summary": "2-3 sentences", "why_it_matters": "one sentence", "source": "Reuters" }],
  "macro_pulse": "2-3 sentences on rates and central banks",
  "sector_spotlight": "1-2 sentences on sectors to watch",
  "key_takeaway": "single paragraph synthesis"
}
```
