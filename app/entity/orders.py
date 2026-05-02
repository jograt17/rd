from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Numeric,
    DateTime,
    BigInteger,
    Identity,
    Enum,
)
from datetime import datetime
from decimal import Decimal
import enum

from .base import Base


class OrderStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus, name="order_status", create_constraint=False, native_enum=True
        ),
        server_default="pending",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    order_items: Mapped[list["OrderItem"] | None] = relationship(back_populates="order")

    __table_args__ = {"schema": "avoria"}
