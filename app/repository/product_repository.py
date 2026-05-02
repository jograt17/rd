import logging
from sqlalchemy import Engine, select, func, or_, insert
from sqlalchemy.orm import Session
from app.entity import Product
from datetime import datetime

from app.model.product_model import ProductCreateModel

LOGGER = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self):
        pass

    def get_products(self, engine: Engine, is_active: bool | None, search: str | None):
        LOGGER.info("is_active %s", is_active)
        session = Session(engine)
        statement = select(Product)

        if is_active:
            statement = statement.filter(Product.is_active.is_(True))
        if search:
            # TODO: optimize search
            statement = statement.filter(
                or_(Product.name.ilike(f"%{search}%"), Product.sku.ilike(f"%{search}%"))
            )
        # compiled = statement.compile(dialect=postgresql.dialect())
        # LOGGER.info("statement: %s", statement)
        # LOGGER.info("params: %s", compiled.params)
        result = session.scalars(statement=statement).all()
        return result

    def get_product_by_id(self, engine: Engine, product_id):
        session = Session(engine)
        statement = select(Product).filter(Product.id == product_id)
        result = session.scalars(statement=statement).first()
        return result

    def get_product_by_sku(self, engine: Engine, sku):
        session = Session(engine)
        statement = select(Product).filter(Product.sku == sku)
        result = session.scalars(statement=statement).first()
        return result

    def create_product(self, engine: Engine, product_data: ProductCreateModel):
        session = Session(engine)
        product = Product(
            name=product_data.name,
            sku=product_data.sku,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
