import logging
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from datetime import datetime
from app.entity.order_items import OrderItemEntity
from app.model.order_item_model import OrderItemCreateModel


class OrderItemRepository:

    def __init__(self, engine: Engine):
        self.engine = engine

    def create_order_item(self, session: Session, order_item_create: OrderItemCreateModel):
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
