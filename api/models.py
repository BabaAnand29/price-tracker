from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Product(Base):
    """Represents a product URL being tracked."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One product has many price records
    records = relationship("PriceRecord", back_populates="product", cascade="all, delete")


class PriceRecord(Base):
    """Represents a single price snapshot for a product at a point in time."""
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    availability = Column(String, nullable=True)
    rating = Column(String, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    # Many price records belong to one product
    product = relationship("Product", back_populates="records")
