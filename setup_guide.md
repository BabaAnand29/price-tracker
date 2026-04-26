# Price Tracker — Complete Setup Guide

> Follow this exactly, top to bottom. Do not skip any step.

---

## What Files Got Created (for reference)

```
C:\Users\SAMRIDHI\OneDrive\Desktop\price-tracker\
├── scraper\
│   ├── __init__.py
│   ├── scraper.py       ← core Playwright scraper
│   └── utils.py         ← anti-bot helpers
├── api\
│   ├── __init__.py
│   ├── main.py          ← FastAPI app entry point
│   ├── routes.py        ← all API endpoints
│   ├── models.py        ← database table definitions
│   └── database.py      ← PostgreSQL connection
├── scheduler\
│   ├── __init__.py
│   └── jobs.py          ← auto-scraping every 6 hours
├── .env                 ← your database URL goes here
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## STEP 1 — Set Up Your Neon Database (5 minutes)

**Neon is a free cloud PostgreSQL. No installation needed.**

1. Open your browser and go to: **https://neon.tech**
2. Click the big **"Sign Up"** button (top right)
3. Click **"Continue with Google"** — use your Gmail account
4. After login, it will ask you to create a project:
   - **Project name**: type `price-tracker`
   - **Database name**: leave it as `neondb` (default)
   - **Region**: choose the closest to you (Asia Pacific if available)
   - Click **"Create Project"**
5. After it creates, you will see a page with **Connection Details**
6. Look for a box that says **"Connection string"**
7. It looks like this:
   ```
   postgresql://piyush:somepassword@ep-xyz-123.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
8. **Copy that entire string** (click the copy icon next to it)

---

## STEP 2 — Paste Your Database URL in the .env File (1 minute)

1. Go to `C:\Users\SAMRIDHI\OneDrive\Desktop\price-tracker\`
2. Open the `.env` file (open it in VS Code or Notepad)
3. It currently says:
   ```
   DATABASE_URL=postgresql://your_user:your_password@your_host/your_dbname?sslmode=require
   ```
4. **Delete that line completely**
5. Paste your Neon connection string like this:
   ```
   DATABASE_URL=postgresql://piyush:somepassword@ep-xyz-123.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
6. Save the file (Ctrl + S)

> [!IMPORTANT]
> Make sure there are **no spaces** around the `=` sign. It must be exactly `DATABASE_URL=your_string_here`

---

## STEP 3 — Open Terminal in the Project Folder (1 minute)

1. Open **VS Code**
2. Go to **File → Open Folder**
3. Navigate to `C:\Users\SAMRIDHI\OneDrive\Desktop\price-tracker`
4. Click **Select Folder**
5. Now open the **Terminal** inside VS Code: Press **Ctrl + `** (backtick key, top-left of keyboard)

You should see a terminal that shows something like:
```
PS C:\Users\SAMRIDHI\OneDrive\Desktop\price-tracker>
```

**All commands below are run in this terminal.**

---

## STEP 4 — Create Python Virtual Environment (2 minutes)

Run these commands **one by one**:

```bash
python -m venv venv
```
Wait for it to finish. Then:

```bash
venv\Scripts\activate
```

After this, your terminal prompt will change to show `(venv)` at the start:
```
(venv) PS C:\Users\SAMRIDHI\OneDrive\Desktop\price-tracker>
```

> [!IMPORTANT]
> If you see an error like "cannot be loaded because running scripts is disabled", run this first:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
> Then run `venv\Scripts\activate` again.

---

## STEP 5 — Install All Dependencies (3–5 minutes)

```bash
pip install -r requirements.txt
```

This will download and install all libraries. Wait until it says "Successfully installed..." at the end.

---

## STEP 6 — Install Playwright's Browser (2–3 minutes)

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright uses to scrape JS pages. It's about 150MB, so it takes a minute.

Wait until you see it finish with no errors.

---

## STEP 7 — Run the API (30 seconds)

```bash
uvicorn api.main:app --reload
```

If everything is correct, you will see output like:
```
[STARTUP] Database tables created/verified.
[STARTUP] Background scheduler started. Scraping every 6 hours.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

> [!IMPORTANT]
> If you see a **database connection error**, go back to Step 2 and double-check your `.env` file. The most common mistake is a wrong or incomplete connection string.

---

## STEP 8 — Test the API in Your Browser (2 minutes)

1. Open your browser
2. Go to: **http://localhost:8000/docs**
3. You will see a page called **"Price Intelligence Tracker"** with all API endpoints listed
4. This is the auto-generated interactive API docs (Swagger UI)
5. You can test each endpoint directly from here

---

## STEP 9 — Add Your First Product (the actual test)

### Option A — Using the Swagger UI (easiest)

1. On the `http://localhost:8000/docs` page
2. Click on **`POST /api/products`**
3. Click **"Try it out"** (button on the right)
4. In the **Request body** box, paste this:
   ```json
   {
     "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
   }
   ```
5. Click **"Execute"**
6. Wait 10–15 seconds (it's scraping the page with a real browser)
7. You should see a response like:
   ```json
   {
     "id": 1,
     "url": "https://books.toscrape.com/...",
     "name": "A Light in the Attic",
     "created_at": "2026-04-26T...",
     "latest_price": 51.77
   }
   ```

**If you see this — the project works perfectly.**

### Option B — Using curl in terminal

Open a **new terminal window** (keep the first one running) and run:

```bash
curl -X POST http://localhost:8000/api/products -H "Content-Type: application/json" -d "{\"url\": \"https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html\"}"
```

---

## STEP 10 — Test Other Endpoints

After adding a product, test these in the Swagger UI at `http://localhost:8000/docs`:

| Endpoint | What to do | What you should see |
|---|---|---|
| `GET /api/products` | Click Execute | List of tracked products with latest prices |
| `GET /api/products/1/history` | Set id=1, Execute | Price records with timestamps |
| `GET /api/products/1/alert` | Set id=1, Execute | `"Not enough data yet"` (needs 2 snapshots) |

---

## STEP 11 — Push to GitHub (5 minutes)

This makes the project publicly visible on your GitHub profile, which you link on your resume.

### First time only — install Git if not already installed:
Check if Git is installed: `git --version`
If not installed: download from https://git-scm.com/download/win and install it.

### Create a new repo on GitHub:
1. Go to **https://github.com**
2. Click the **"+"** button (top right) → **"New repository"**
3. Repository name: `price-tracker`
4. Description: `Automated price monitoring system — Python, FastAPI, Playwright, PostgreSQL`
5. Set to **Public**
6. Do NOT check "Add README" (we already have one)
7. Click **"Create repository"**
8. GitHub will show you a page with commands. **Copy the repo URL** (looks like `https://github.com/YourName/price-tracker.git`)

### Push from terminal:

```bash
git init
git add .
git commit -m "Initial commit: Price Intelligence Tracker with FastAPI, Playwright, PostgreSQL"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/price-tracker.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

> [!CAUTION]
> The `.gitignore` file already excludes `.env` from being pushed. 
> **Never push your `.env` file to GitHub** — it contains your database password.

---

## STEP 12 — What to Put on Your Resume

Add this as a project entry:

---

**Price Intelligence Tracker** | [GitHub Link] | *Python, FastAPI, Playwright, PostgreSQL, APScheduler, Docker*

- Engineered an automated price monitoring system using **Python + Playwright** to scrape product data from JS-rendered e-commerce pages, with anti-bot handling via randomised user-agent rotation and request throttling.
- Built a **FastAPI** REST API exposing endpoints for product tracking (`POST /products`), full price history retrieval, and price drop alerts — backed by a **PostgreSQL** schema tracking time-series data.
- Automated scraping via **APScheduler** background jobs to re-crawl all tracked URLs every 6 hours, detecting and storing price changes with timestamps.
- Containerised the full application with **Docker**, enabling one-command local and cloud deployment.

---

## Troubleshooting — Common Errors

| Error | Cause | Fix |
|---|---|---|
| `DATABASE_URL is not set` | .env file missing or wrong format | Open `.env`, check the DATABASE_URL line has no spaces |
| `connection refused` or `could not connect` | Wrong Neon connection string | Go to Neon dashboard, copy the connection string again |
| `playwright: command not found` | Playwright not installed | Run `pip install playwright` then `playwright install chromium` |
| `ModuleNotFoundError: No module named 'scraper'` | Not running from the right folder | Make sure terminal is in `price-tracker/` folder |
| `(venv)` not showing in terminal | Virtual env not activated | Run `venv\Scripts\activate` again |
| Scraper returns `None` | Site selector might have changed | Open the URL manually in browser and check if it loads |

---

## Quick Reference — Commands You'll Use

```bash
# Activate virtual environment (run this every time you open a new terminal)
venv\Scripts\activate

# Run the API
uvicorn api.main:app --reload

# Open API docs
# Go to: http://localhost:8000/docs

# Push updates to GitHub
git add .
git commit -m "your message here"
git push
```
