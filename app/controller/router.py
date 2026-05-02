from fastapi import APIRouter, Request, status
import logging


from app.service.product_service import ProductService
from app.model.product_model import ProductCreateModel
from app.errors.generic_error import custom_error_response, CustomError

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/products")
async def get_products(
    request: Request, is_active: bool | None = None, search: str | None = None
):
    LOGGER.info("is_active: %s, search string: %s", is_active, search)

    state_engine = request.app.state.engine
    product_service = ProductService(engine=state_engine)
    result = product_service.get_products(isActive=is_active, search=search)
    return result


@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(request: Request, product_data: ProductCreateModel):
    try:
        state_engine = request.app.state.engine
        product_service = ProductService(engine=state_engine)
        result = product_service.create_product(product_data)
        return result
    except CustomError as e:
        return custom_error_response(422, e.name, e.message, e.payload)
    except Exception as e:
        return custom_error_response(500, "ServerError", product_data, e)
