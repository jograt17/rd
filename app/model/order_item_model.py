from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class OrderItemCreateModel(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderItemModel(OrderItemCreateModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class OrderItemsSubtotal(BaseModel):
    product_id: int
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    projected_quantity: int
