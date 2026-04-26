from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import Base, engine
from .routes import router
from scheduler.jobs import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: create all database tables and start the background scheduler.
    Shutdown: scheduler stops automatically.
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] Database tables created/verified.")

    # Start background scraping scheduler
    scheduler = start_scheduler()
    print("[STARTUP] Background scheduler started. Scraping every 6 hours.")

    yield

    # Shutdown
    scheduler.shutdown()
    print("[SHUTDOWN] Scheduler stopped.")


app = FastAPI(
    title="Price Intelligence Tracker",
    description=(
        "An automated price monitoring system that scrapes e-commerce product pages, "
        "tracks price history in PostgreSQL, and exposes insights via a REST API. "
        "Built with Python, FastAPI, Playwright, and APScheduler."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api", tags=["Products"])


@app.get("/", summary="Health check")
def health_check():
    return {"status": "running", "message": "Price Intelligence Tracker API is live."}
