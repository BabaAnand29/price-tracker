# Price Intelligence Tracker

An automated price monitoring system built with Python. Tracks product prices from e-commerce pages, stores historical price data in PostgreSQL, and exposes insights via a REST API.

## Architecture

```
price-tracker/
├── scraper/          # Playwright + BeautifulSoup scraping engine
│   ├── scraper.py    # Core scraper — handles JS-rendered pages
│   └── utils.py      # User-agent rotation, request headers, delays
├── api/              # FastAPI backend
│   ├── main.py       # App entry point, DB init, scheduler startup
│   ├── routes.py     # REST API endpoints
│   ├── models.py     # SQLAlchemy ORM models
│   └── database.py   # PostgreSQL connection setup
├── scheduler/        # Automated background jobs
│   └── jobs.py       # APScheduler — re-scrapes every 6 hours
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Tech Stack

- **Python 3.11** — core language
- **FastAPI** — REST API framework
- **Playwright** — headless browser for JS-rendered page scraping
- **BeautifulSoup4** — HTML parsing
- **SQLAlchemy** — ORM for PostgreSQL
- **PostgreSQL (Neon)** — cloud database for time-series price storage
- **APScheduler** — background job scheduling (auto re-scrapes every 6 hours)
- **Docker** — containerised deployment

## Features

- Scrapes JS-rendered product pages using a headless Chromium browser
- Anti-bot handling: randomised user-agent rotation, request throttling, realistic HTTP headers
- Stores time-series price history per product in PostgreSQL
- REST API to add products, query history, and check price drop alerts
- Fully automated background re-scraping on a 6-hour interval
- Containerized with Docker for one-command deployment

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/products` | Add a product URL to track |
| `GET` | `/api/products` | List all tracked products with latest price |
| `GET` | `/api/products/{id}/history` | Full price history for a product |
| `GET` | `/api/products/{id}/alert` | Price drop alert (triggers if >5% drop) |
| `DELETE` | `/api/products/{id}` | Remove a product from tracking |

## Quick Start

### 1. Clone and set up environment

```bash
git clone https://github.com/YOUR_USERNAME/price-tracker.git
cd price-tracker
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure database

Copy `.env` and add your PostgreSQL connection string:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

### 3. Run the API

```bash
uvicorn api.main:app --reload
```

Open `http://localhost:8000/docs` to access the interactive API documentation.

### 4. Add a product to track

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"}'
```

### 5. Run with Docker

```bash
docker-compose up --build
```

## Example Usage

```bash
# Add a product
POST /api/products
{"url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"}

# Check price history
GET /api/products/1/history

# Check for price drop alert
GET /api/products/1/alert
```

## Planned Extensions

- Email/webhook notifications on price drop alert
- Support for multiple e-commerce site parsers
- Redis caching for high-frequency endpoints
- Deployed on AWS EC2 with systemd service
