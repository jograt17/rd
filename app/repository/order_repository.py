import logging
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload
from datetime import datetime
from app.entity.orders import OrderEntity
from app.model.order_model import OrderModel, OrderInfoModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_order(self, session: Session, order_info: OrderInfoModel):
        order_record = OrderEntity(
            customer_name=order_info.customer_name,
            customer_email=order_info.customer_email,
            total_amount=order_info.total_amount,
            discount_id=order_info.discount_id,
            final_amount=order_info.final_amount,
            discount_amount=order_info.discount_amount,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(order_record)
        session.flush()
        return order_record.id

    def get_order_and_items(self, order_id: int):
        try:
            LOGGER.info("get_order_and_items repo start")
            statement = (
                select(OrderEntity)
                .options(selectinload(OrderEntity.order_items))
                .options(selectinload(OrderEntity.discount))
                .filter(OrderEntity.id == order_id)
            )
            with Session(self.engine) as session:
                order = session.scalars(statement=statement).first()
            result = None if not order else OrderModel.model_validate(order)
            return result

        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr({"id": order_id}) from e
        finally:
            LOGGER.info("get_order_and_items repo end")

    def _generic_db_error_bldr(self, data: any):
        return CustomError(
            500,
            "DatabaseError",
            "Database error occured",
            data,
        )
