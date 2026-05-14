import logging
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from datetime import datetime
from app.entity.discounts import DiscountEntity
from app.model.discount_model import DiscountModel


class DiscountRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_discount(self, discount_code: str):
        statement = select(DiscountEntity).filter(
            DiscountEntity.discount_code == discount_code.upper()
        )
        with Session(self.engine) as session:
            discount = session.scalar(statement=statement)

        result = None if not discount else DiscountModel.model_validate(discount)
        return result
