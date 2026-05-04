from pydantic import BaseModel
from typing import Optional, Any


class CustomResponseModel(BaseModel):
    message: str
    data: Optional[Any] = None
