from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Identity, String, UniqueConstraint, Integer

from .base import Base


class DiscountEntity(Base):
    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    discount_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    order: Mapped["OrderEntity"] = relationship(back_populates="discount")

    __table_args__ = (
        UniqueConstraint("discount_code", name="unique_discount_code"),
        {"schema": "avoria"},
    )
