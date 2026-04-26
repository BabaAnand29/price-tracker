from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

from .database import get_db
from .models import Product, PriceRecord
from scraper.scraper import scrape_product

router = APIRouter()


# ─── Request / Response Schemas ────────────────────────────────────────────────

class ProductIn(BaseModel):
    url: str  # URL of the product page to track


class PriceRecordOut(BaseModel):
    id: int
    price: float
    availability: Optional[str]
    rating: Optional[str]
    scraped_at: datetime

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    url: str
    name: Optional[str]
    created_at: datetime
    latest_price: Optional[float] = None

    class Config:
        from_attributes = True


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/products", response_model=ProductOut, summary="Add a product URL to track")
def add_product(payload: ProductIn, db: Session = Depends(get_db)):
    """
    Add a product URL to the tracking list.
    Immediately scrapes the page to fetch the first price record.
    """
    # Check if product is already being tracked
    existing = db.query(Product).filter(Product.url == payload.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="This product URL is already being tracked.")

    # Scrape the product page immediately
    data = scrape_product(payload.url)
    if not data:
        raise HTTPException(
            status_code=422,
            detail="Could not scrape the provided URL. Make sure it is a valid books.toscrape.com product page."
        )

    # Save product to DB
    product = Product(url=payload.url, name=data["name"])
    db.add(product)
    db.commit()
    db.refresh(product)

    # Save the first price record
    record = PriceRecord(
        product_id=product.id,
        price=data["price"],
        availability=data["availability"],
        rating=data["rating"],
        scraped_at=data["scraped_at"],
    )
    db.add(record)
    db.commit()

    return ProductOut(
        id=product.id,
        url=product.url,
        name=product.name,
        created_at=product.created_at,
        latest_price=data["price"],
    )


@router.get("/products", response_model=List[ProductOut], summary="List all tracked products")
def list_products(db: Session = Depends(get_db)):
    """Return all tracked products with their latest recorded price."""
    products = db.query(Product).all()
    result = []
    for p in products:
        latest = (
            db.query(PriceRecord)
            .filter(PriceRecord.product_id == p.id)
            .order_by(PriceRecord.scraped_at.desc())
            .first()
        )
        result.append(ProductOut(
            id=p.id,
            url=p.url,
            name=p.name,
            created_at=p.created_at,
            latest_price=latest.price if latest else None,
        ))
    return result


@router.get("/products/{product_id}/history", response_model=List[PriceRecordOut], summary="Get price history")
def price_history(product_id: int, db: Session = Depends(get_db)):
    """Return all price records for a specific product, ordered by time (newest first)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    records = (
        db.query(PriceRecord)
        .filter(PriceRecord.product_id == product_id)
        .order_by(PriceRecord.scraped_at.desc())
        .all()
    )
    return records


@router.get("/products/{product_id}/alert", summary="Check for price drop alert")
def price_alert(product_id: int, db: Session = Depends(get_db)):
    """
    Compare the two most recent price records.
    Returns an alert if the price dropped by more than 5%.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    records = (
        db.query(PriceRecord)
        .filter(PriceRecord.product_id == product_id)
        .order_by(PriceRecord.scraped_at.desc())
        .limit(2)
        .all()
    )

    if len(records) < 2:
        return {
            "product": product.name,
            "alert": False,
            "message": "Not enough data yet. Need at least 2 price snapshots to compare."
        }

    latest = records[0]
    previous = records[1]
    drop_percent = ((previous.price - latest.price) / previous.price) * 100

    return {
        "product": product.name,
        "alert": drop_percent > 5.0,
        "drop_percent": round(drop_percent, 2),
        "current_price": latest.price,
        "previous_price": previous.price,
        "message": f"Price dropped by {round(drop_percent, 2)}%!" if drop_percent > 5 else "No significant price drop detected."
    }


@router.delete("/products/{product_id}", summary="Remove a product from tracking")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Stop tracking a product and delete all its price history."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    db.delete(product)
    db.commit()
    return {"message": f"Product '{product.name}' removed from tracking."}
