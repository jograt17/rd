import logging
from datetime import datetime
from sqlalchemy import Engine, select, or_, update
from sqlalchemy.orm import Session

from app.entity.products import ProductEntity
from app.model.product_model import ProductCreateModel, ProductPatchModel, ProductModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_products(self, is_active: bool | None, search: str | None):
        try:
            LOGGER.info("get_products start")
            statement = select(ProductEntity)
            if is_active is not None:
                statement = statement.filter(ProductEntity.is_active.is_(is_active))
            if search:
                # TODO: optimize search
                statement = statement.filter(
                    or_(
                        ProductEntity.name.ilike(f"%{search}%"),
                        ProductEntity.sku.ilike(f"%{search}%"),
                    )
                )
            statement = statement.order_by(ProductEntity.id.asc())
            with Session(self.engine) as session:
                products = session.scalars(statement=statement).all()
            result = (
                []
                if not products
                else [ProductModel.model_validate(product) for product in products]
            )
            return result
        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr({"is_active": is_active, "search": search}) from e
        finally:
            LOGGER.info("get_products end")

    def get_product_by_id(self, product_id):
        try:
            LOGGER.info("get_product_by_id repo start")
            statement = select(ProductEntity).filter(ProductEntity.id == product_id)
            with Session(self.engine) as session:
                product = session.scalars(statement=statement).first()
            result = None if not product else ProductModel.model_validate(product)
            return result
        except Exception as e:
            LOGGER.exception(e)
            raise self._generic_db_error_bldr({"product_id": product_id}) from e
        finally:
            LOGGER.info("get_product_by_id repo end")

    def get_product_by_sku(self, sku):
        statement = select(ProductEntity).filter(ProductEntity.sku == sku)
        with Session(self.engine) as session:
            product = session.scalars(statement=statement).first()
            result = None if not product else ProductModel.model_validate(product)
        return result

    def get_products_by_ids(self, ids: list[int]):
        try:
            LOGGER.info("get_products_by_ids repo start")
            statement = select(ProductEntity).filter(ProductEntity.id.in_(ids))
            with Session(self.engine) as session:
                products = session.scalars(statement).all()
            result = (
                []
                if not products
                else [ProductModel.model_validate(product) for product in products]
            )
            return result
        except Exception as e:
            raise self._generic_db_error_bldr({"product_ids": ids}) from e
        finally:
            LOGGER.info("get_products_by_ids repo end")

    def create_product(self, product_data: ProductCreateModel):
        try:
            LOGGER.info("create_product repo start")
            product = ProductEntity(
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
        self, product_id: int, product_data: ProductPatchModel, session: Session = None
    ):
        try:
            LOGGER.info("update_product Repository start")
            set_values = product_data.model_dump(exclude_none=True)
            set_values.update({"updated_at": datetime.now()})
            statement = (
                update(ProductEntity)
                .where(ProductEntity.id == product_id)
                .values(set_values)
                .returning(ProductEntity.id)
            )
            if not session:
                with Session(self.engine) as session:
                    result = session.execute(statement=statement)
                    updated_id = result.scalars().first()
                    LOGGER.info("result: %s", updated_id)
                    session.commit()
            else:
                result = session.execute(statement=statement)
                updated_id = result.scalars().first()
                LOGGER.info("result: %s", updated_id)
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
