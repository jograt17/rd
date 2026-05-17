import logging
from sqlalchemy import Engine
from sqlalchemy.orm import Session


from app.entity.order_items import OrderItemEntity
from app.model.order_item_model import OrderItemCreateModel
from app.errors.generic_error import DatabaseError

LOGGER = logging.getLogger(__name__)


class OrderItemRepository:

    def __init__(self, engine: Engine):
        self.engine = engine

    def create_order_item(self, session: Session, order_item_create: OrderItemCreateModel):
        try:
            LOGGER.info("get_order_and_items repo start")
            order_item = OrderItemEntity(
                order_id=order_item_create.order_id,
                product_id=order_item_create.product_id,
                quantity=order_item_create.quantity,
                unit_price=order_item_create.unit_price,
                subtotal=order_item_create.subtotal,
            )
            session.add(order_item)
            session.flush()
            return order_item.id

        except Exception as e:
            LOGGER.exception(e)
            raise DatabaseError(order_item_create.model_dump(mode="json")) from e
        finally:
            LOGGER.info("get_order_and_items repo end")
