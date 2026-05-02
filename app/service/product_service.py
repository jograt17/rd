import logging
from sqlalchemy import Engine
from fastapi import HTTPException

from app.repository.product_repository import ProductRepository
from app.model.product_model import ProductCreateModel
from app.errors.generic_error import custom_error_response, CustomError

LOGGER = logging.getLogger(__name__)


class ProductService:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.product_repo = ProductRepository()

    def get_products(self, isActive: bool | None, search: str | None):
        result = self.product_repo.get_products(
            self.engine, is_active=isActive, search=search
        )
        return result

    def get_product_by_id(self, product_id):
        result = self.product_repo.get_product_by_id(self.engine, product_id=product_id)
        return result

    def create_product(self, product_data: ProductCreateModel):
        # validate product_data
        ## check if product id exists
        if self._sku_exists(sku=product_data.sku):
            raise CustomError(
                422,
                "RequestValidationError",
                "SKU Exists",
                product_data.model_dump(mode="json"),
            )
        result = self.product_repo.create_product(self.engine, product_data)

        LOGGER.info("result: %s", result)
        return {"product": "WIP"}

    def _product_exists(self, product_id) -> int:
        result = self.product_repo.get_product_by_id(self.engine, product_id=product_id)

    def _sku_exists(self, sku) -> bool:
        result = self.product_repo.get_product_by_sku(self.engine, sku)
        return bool(result)
