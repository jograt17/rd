from pydantic import BaseModel, Field, model_validator, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional


class ProductCreateModel(BaseModel):
    name: str
    sku: str
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(gt=0)


class ProductPatchModel(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    sku: Optional[str] = Field(default=None, min_length=1)
    price: Optional[Decimal] = Field(default=None, gt=0)
    stock_quantity: Optional[int] = Field(default=None)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def check_if_all_null(self):
        if (
            self.name is None
            and self.sku is None
            and self.price is None
            and self.stock_quantity is None
            and self.is_active is None
        ):
            raise ValueError("There are no fields to update.")
        return self


class ProductModel(BaseModel):
    model_config = ConfigDict(from_attributes=True) or None
    id: int
    name: str
    sku: str
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime
