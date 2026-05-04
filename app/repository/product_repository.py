import logging
from sqlalchemy import Engine, select, func, or_, insert, update
from sqlalchemy.orm import Session
from app.entity import Product
from datetime import datetime

from app.model.product_model import ProductCreateModel, ProductPatchModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self):
        pass

    def get_products(self, engine: Engine, is_active: bool | None, search: str | None):
        try:
            LOGGER.info("get_products start")
            session = Session(engine)
            statement = select(Product)

            if is_active:
                statement = statement.filter(Product.is_active.is_(True)).ord
            if search:
                # TODO: optimize search
                statement = statement.filter(
                    or_(
                        Product.name.ilike(f"%{search}%"),
                        Product.sku.ilike(f"%{search}%"),
                    )
                )
            statement = statement.order_by(Product.id.asc())
            result = session.scalars(statement=statement).all()
            return result
        except Exception as e:
            LOGGER.exception(e)
            raise CustomError(
                500,
                "DatabaseError",
                "Database error occured",
                {"is_active": is_active, "search": search},
            ) from e
        finally:
            LOGGER.info("get_products end")

    def get_product_by_id(self, engine: Engine, product_id):
        try:
            LOGGER.info("get_product_by_id repo start")
            session = Session(engine)
            statement = select(Product).filter(Product.id == product_id)
            result = session.scalars(statement=statement).first()
            return result
        except Exception as e:
            LOGGER.exception(e)
            raise CustomError(
                500,
                "DatabaseError",
                "Database error occured",
                {"product_id": product_id},
            ) from e
        finally:
            LOGGER.info("get_product_by_id repo end")

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
        return product.id

    def update_product(
        self,
        engine: Engine,
        product_id: int,
        product_data: ProductPatchModel,
    ):
        try:
            LOGGER.info("patch_product Repository start")
            set_values = product_data.model_dump(exclude_none=True)
            set_values.update({"updated_at": datetime.now()})
            session = Session(engine)
            statement = (
                update(Product)
                .where(Product.id == product_id)
                .values(set_values)
                .returning(Product.id)
            )
            result = session.execute(statement=statement)
            updated_id = result.scalars().first()
            LOGGER.info("result: %s", updated_id)
            session.commit()
            return {"updated_id": updated_id}
        except Exception as e:
            LOGGER.exception(e)
            raise CustomError(
                500,
                "DatabaseError",
                "Database error occured",
                product_data.model_dump(mode="json"),
            ) from e
        finally:
            LOGGER.info("patch_product Repository send")
