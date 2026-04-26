from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from api.database import SessionLocal
from api.models import Product, PriceRecord
from scraper.scraper import scrape_product
from datetime import datetime


def scrape_all_products():
    """
    Scheduled job: iterates over all tracked products, scrapes their current price,
    and saves a new PriceRecord to the database.
    Runs automatically every 6 hours.
    """
    db = SessionLocal()
    try:
        products = db.query(Product).all()

        if not products:
            print(f"[SCHEDULER] {datetime.utcnow()} — No products to scrape.")
            return

        print(f"[SCHEDULER] {datetime.utcnow()} — Starting scrape for {len(products)} products...")

        success_count = 0
        fail_count = 0

        for product in products:
            data = scrape_product(product.url)

            if data:
                record = PriceRecord(
                    product_id=product.id,
                    price=data["price"],
                    availability=data["availability"],
                    rating=data["rating"],
                    scraped_at=data["scraped_at"],
                )
                db.add(record)
                success_count += 1
                print(f"  ✓ {product.name} — £{data['price']}")
            else:
                fail_count += 1
                print(f"  ✗ Failed to scrape: {product.url}")

        db.commit()
        print(f"[SCHEDULER] Done. Success: {success_count}, Failed: {fail_count}")

    except Exception as e:
        print(f"[SCHEDULER ERROR] {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """
    Initialize and start the APScheduler background scheduler.
    The scrape_all_products job runs every 6 hours.
    Returns the scheduler instance so it can be shut down on app exit.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=scrape_all_products,
        trigger=IntervalTrigger(hours=6),
        id="scrape_all",
        name="Scrape all tracked products",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
