import logging
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from app.entity.discounts import DiscountEntity
from app.model.discount_model import DiscountModel
from app.errors.generic_error import DatabaseError

LOGGER = logging.getLogger(__name__)


class DiscountRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_discount(self, discount_code: str):
        try:
            LOGGER.info("get_discount repo end")
            statement = select(DiscountEntity).filter(
                DiscountEntity.discount_code == discount_code.upper()
            )
            with Session(self.engine) as session:
                discount = session.scalar(statement=statement)

            result = None if not discount else DiscountModel.model_validate(discount)
            return result

        except Exception as e:
            LOGGER.exception(e)
            raise DatabaseError({"discount_code": discount_code}) from e
        finally:
            LOGGER.info("get_discount repo end")
