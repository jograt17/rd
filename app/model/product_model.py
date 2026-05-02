from pydantic import BaseModel, Field
from decimal import Decimal


class ProductCreateModel(BaseModel):
    name: str
    sku: str
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(gt=0)
