import logging
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload, noload
from datetime import datetime

from app.entity.orders import OrderEntity
from app.model.order_model import OrderModel, OrderInfoModel, OrdersModel
from app.errors.generic_error import DatabaseError

LOGGER = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def create_order(self, session: Session, order_info: OrderInfoModel):
        try:
            LOGGER.info("create_order repo start")
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
        except Exception as e:
            LOGGER.exception(e)
            raise DatabaseError(order_info.model_dump(mode="json")) from e
        finally:
            LOGGER.info("create_order repo end")

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
            raise DatabaseError({"id": order_id}) from e
        finally:
            LOGGER.info("get_order_and_items repo end")

    def get_orders(self):
        try:
            LOGGER.info("get_order_and_items repo start")
            statement = select(OrderEntity).options(
                noload(OrderEntity.order_items), noload(OrderEntity.discount)
            )
            with Session(self.engine) as session:
                orders = session.scalars(statement=statement).all()
                result = (
                    [] if not orders else [OrdersModel.model_validate(order) for order in orders]
                )
                return result
        except Exception as e:
            LOGGER.exception(e)
            raise DatabaseError() from e
        finally:
            LOGGER.info("get_order_and_items repo end")
