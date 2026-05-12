from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Numeric,
    Integer,
    Boolean,
    DateTime,
    BigInteger,
    Identity,
    CheckConstraint,
    UniqueConstraint,
)
from datetime import datetime
from decimal import Decimal

from .base import Base


class ProductEntity(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    order_items: Mapped[list["OrderItemEntity"] | None] = relationship(back_populates="product")

    __table_args__ = (
        CheckConstraint("price > 0", name="check_price_positive"),
        CheckConstraint("stock_quantity >= 0", name="check_not_negative_stock"),
        UniqueConstraint("sku", name="unique_sku"),
        {"schema": "avoria"},
    )
