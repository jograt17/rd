import logging
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from app.entity.orders import Order

LOGGER = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
