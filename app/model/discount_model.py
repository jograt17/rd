from pydantic import BaseModel, ConfigDict
from typing import Optional


class DiscountModel(BaseModel):
    model_config = ConfigDict(from_attributes=True) or None
    id: int
    discount_code: str
    description: Optional[str]
    unit: str
    value: int
