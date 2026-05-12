import logging
from sqlalchemy import Engine

from app.repository.product_repository import ProductRepository
from app.model.product_model import ProductCreateModel, ProductModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class ProductService:
    def __init__(self, engine: Engine, product_repo: ProductRepository):
        self.engine = engine
        self.product_repo = product_repo

    def get_products(self, isActive: bool | None, search: str | None):
        try:
            LOGGER.info("get_products start")
            result = self.product_repo.get_products(is_active=isActive, search=search)
            # dict_list = [utils.to_dict(row) for row in result]
            return result
        except Exception as e:
            LOGGER.exception(e)
        finally:
            LOGGER.info("get_products end")

    def get_product_by_id(self, product_id):
        try:
            LOGGER.info("get_product_by_id Service start")
            result = self.product_repo.get_product_by_id(product_id=product_id)
            if not result:
                raise CustomError(
                    404,
                    "NotFound",
                    "Product not found.",
                    {"product_id": product_id},
                )
            return result
        except CustomError as e:
            LOGGER.exception(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise e
        finally:
            LOGGER.info("get_product_by_id Service end")

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
        result_id = self.product_repo.create_product(product_data)

        LOGGER.info("result_id: %s", result_id)
        return {"product": result_id}

    def patch_product(self, product_id: int, product_data):
        try:
            LOGGER.info("patch_product Service start")
            # check if product exists
            existing_product = self.get_product(product_id=product_id)
            if not existing_product:
                raise CustomError(
                    404,
                    "NotFound",
                    "Product does not exist",
                    product_data.model_dump(mode="json"),
                )

            result = self.product_repo.update_product(product_id, product_data)
            return result
        except CustomError as e:
            LOGGER.exception(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise e
        finally:
            LOGGER.info("patch_product Service end")

    def get_product(self, product_id) -> ProductModel:
        return self.product_repo.get_product_by_id(product_id=product_id)

    def _sku_exists(self, sku) -> bool:
        result = self.product_repo.get_product_by_sku(sku)
        return bool(result)
