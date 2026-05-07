from pydantic import BaseModel, EmailStr


class OrderItem(BaseModel):
    product_id: int
    quantity: int


class CreateOrderModel(BaseModel):
    customer_name: str
    customer_email: EmailStr
    items: list[OrderItem]
