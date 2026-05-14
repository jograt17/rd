from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.model.order_item_model import OrderItemModel
from app.model.discount_model import DiscountModel


class Items(BaseModel):
    product_id: int
    quantity: int


class CreateOrderModel(BaseModel):
    customer_name: str
    customer_email: EmailStr
    items: list[Items]
    discount_code: Optional[str] = None


class OrderInfoModel(BaseModel):
    customer_name: str
    customer_email: EmailStr
    total_amount: Decimal
    discount_code: Optional[str] = None
    discount_amount: Optional[Decimal] = 0
    final_amount: Decimal
    discount_id: Optional[int] = None


class OrderModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_name: str
    customer_email: str
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    order_items: list[OrderItemModel]
    # discounts
    discount_id: Optional[int] = None
    discount_amount: Optional[Decimal] = 0
    discount: Optional[DiscountModel] = None
    final_amount: Decimal
