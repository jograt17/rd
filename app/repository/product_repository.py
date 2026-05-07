import logging
from sqlalchemy import Engine, select, or_, update
from sqlalchemy.orm import Session
from app.entity.products import Product
from datetime import datetime

from app.model.product_model import ProductCreateModel, ProductPatchModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_products(self, is_active: bool | None, search: str | None):
        try:
            LOGGER.info("get_products start")
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
            with Session(self.engine) as session:
                result = session.scalars(statement=statement).all()
            return result
        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr({"is_active": is_active, "search": search}) from e
        finally:
            LOGGER.info("get_products end")

    def get_product_by_id(self, product_id):
        try:
            LOGGER.info("get_product_by_id repo start")
            statement = select(Product).filter(Product.id == product_id)
            with Session(self.engine) as session:
                result = session.scalars(statement=statement).first()
            return result
        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr({"product_id": product_id}) from e
        finally:
            LOGGER.info("get_product_by_id repo end")

    def get_product_by_sku(self, sku):
        statement = select(Product).filter(Product.sku == sku)
        with Session(self.engine) as session:
            result = session.scalars(statement=statement).first()
        return result

    def get_products_by_ids(self, ids: list[int]):
        try:
            LOGGER.info("get_products_by_ids repo start")
            statement = select(Product.id, Product.stock_quantity).filter(Product.id.in_(ids))
            with Session(self.engine) as session:
                rows = session.execute(statement).mappings().all()
                # LOGGER.info("statement: %s", statement)
                LOGGER.info("statement params: %s", statement.compile())
                LOGGER.info("statement params: %s", statement.compile().params)
                LOGGER.info("resutlt: %s", rows)

            result = [dict(row) for row in rows]
            return result
        except Exception as e:
            raise self._generic_db_error_bldr({"product_ids": ids}) from e
        finally:
            LOGGER.info("get_products_by_ids repo end")

    def create_product(self, product_data: ProductCreateModel):
        try:
            LOGGER.info("create_product repo start")
            product = Product(
                name=product_data.name,
                sku=product_data.sku,
                price=product_data.price,
                stock_quantity=product_data.stock_quantity,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            with Session(self.engine) as session:
                session.add(product)
                session.commit()
                session.refresh(product)
            return product.id
        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr(product_data.model_dump(mode="json")) from e
        finally:
            LOGGER.info("create_product repo end")

    def update_product(
        self,
        product_id: int,
        product_data: ProductPatchModel,
    ):
        try:
            LOGGER.info("update_product Repository start")
            set_values = product_data.model_dump(exclude_none=True)
            set_values.update({"updated_at": datetime.now()})
            statement = (
                update(Product)
                .where(Product.id == product_id)
                .values(set_values)
                .returning(Product.id)
            )
            with Session(self.engine) as session:
                result = session.execute(statement=statement)
                updated_id = result.scalars().first()
                LOGGER.info("result: %s", updated_id)
                session.commit()
            return {"updated_id": updated_id}
        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr(product_data.model_dump(mode="json")) from e
        finally:
            LOGGER.info("update_product Repository end")

    def _generic_db_error_bldr(self, data: any):
        return CustomError(
            500,
            "DatabaseError",
            "Database error occured",
            data,
        )
