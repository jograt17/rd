from fastapi import APIRouter, Request, status, Depends
import logging


from app.service.product_service import ProductService
from app.model.product_model import ProductCreateModel, ProductPatchModel
from app.model.response import CustomResponseModel
from app.errors.generic_error import custom_error_response, CustomError
from app.dependecy import get_product_service

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/products/{product_id}", response_model=CustomResponseModel)
async def get_product_by_id(
    # request: Request,
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
):
    try:
        LOGGER.info("get_product_by_id controller start")
        result = product_service.get_product_by_id(product_id)
        return CustomResponseModel(message="Successfully retrieved product", data=result)
    except CustomError as e:
        return custom_error_response(e.code, e.name, e.message, e.payload)
    except Exception as e:
        LOGGER.exception(e)
        return custom_error_response(500, "ServerError", product_id)
    finally:
        LOGGER.info("get_product_by_id controller end")


@router.get(
    "/products",
    response_model=CustomResponseModel,
)
async def get_products(
    request: Request,
    is_active: bool | None = None,
    search: str | None = None,
    product_service: ProductService = Depends(get_product_service),
):
    # TODO: error handling
    # LOGGER.info("is_active: %s, search string: %s", is_active, search)

    # state_engine = request.app.state.engine
    # product_service = ProductService(engine=self.engine)
    result = product_service.get_products(isActive=is_active, search=search)
    return CustomResponseModel(message="Product Retrieved", data=result)


@router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=CustomResponseModel,
)
async def create_product(
    request: Request,
    product_data: ProductCreateModel,
    product_service: ProductService = Depends(get_product_service),
):
    try:
        state_engine = request.app.state.engine
        # product_service = ProductService(engine=state_engine)
        result_id = product_service.create_product(product_data)
        return CustomResponseModel(message="Product Created", data=result_id)
    except CustomError as e:
        return custom_error_response(e.code, e.name, e.message, e.payload)
    except Exception as e:
        LOGGER.exception(e)
        return custom_error_response(500, "ServerError", product_data)


@router.patch("/products/{product_id}", response_model=CustomResponseModel)
async def patch_product(
    request: Request,
    product_id: int,
    product_data: ProductPatchModel,
    product_service: ProductService = Depends(get_product_service),
):
    try:
        LOGGER.info("patch_product controller start")
        state_engine = request.app.state.engine
        # product_service = ProductService(engine=state_engine)
        result = product_service.patch_product(product_id=product_id, product_data=product_data)
        return CustomResponseModel(message="Successfully updated product", data=result)
    except CustomError as e:
        return custom_error_response(e.code, e.name, e.message, e.payload)
    except Exception as e:
        LOGGER.exception(e)
        return custom_error_response(500, "ServerError", product_data)
    finally:
        LOGGER.info("patch_product controller end")
