import logging
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload
from datetime import datetime
from app.entity.orders import OrderEntity
from app.model.order_model import OrderModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_order(self, session: Session, name, email, total_amt):
        order_info = OrderEntity(
            customer_name=name,
            customer_email=email,
            total_amount=total_amt,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(order_info)
        session.flush()
        return order_info.id

    def get_order_and_items(self, order_id: int):
        try:
            LOGGER.info("get_order_and_items repo start")

            statement = (
                select(OrderEntity)
                .options(selectinload(OrderEntity.order_items))
                .filter(OrderEntity.id == order_id)
            )
            with Session(self.engine) as session:
                order = session.scalars(statement=statement).first()
                # result = self._parse_to_pydantic(order)
            result = OrderModel.model_validate(order)
            return result

        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr({"id": int}) from e
        finally:
            LOGGER.info("get_order_and_items repo end")

    def _parse_to_pydantic(self, order: OrderEntity):
        return OrderModel(
            id=order.id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    def _generic_db_error_bldr(self, data: any):
        return CustomError(
            500,
            "DatabaseError",
            "Database error occured",
            data,
        )
