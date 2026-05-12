from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from decimal import Decimal

from app.model.order_item_model import OrderItemModel


class Items(BaseModel):
    product_id: int
    quantity: int


class CreateOrderModel(BaseModel):
    customer_name: str
    customer_email: EmailStr
    items: list[Items]


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
