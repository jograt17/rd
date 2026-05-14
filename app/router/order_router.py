from fastapi import APIRouter, status, Depends
import logging

from app.model.response import CustomResponseModel
from app.model.order_model import CreateOrderModel
from app.dependency import get_order_service
from app.service.order_service import OrderService
from app.errors.generic_error import CustomError, custom_error_response

LOGGER = logging.getLogger(__name__)

order_router = APIRouter(prefix="/api/orders")


@order_router.get("/")
async def get_order():
    return {"helloword": "test"}


@order_router.post("/", status_code=status.HTTP_201_CREATED, response_model=CustomResponseModel)
async def create_order(
    order_data: CreateOrderModel, order_service: OrderService = Depends(get_order_service)
):
    try:
        result = order_service.create_order(order_data)
        return CustomResponseModel(message="Order successfully created.", data=result)
    except CustomError as e:
        return custom_error_response(e.code, e.name, e.message, e.payload)
    except Exception as e:
        LOGGER.exception(e)
        return custom_error_response(500, "ServerError", order_data)


@order_router.get("/{order_id}")
async def get_order_and(order_id: int, order_service: OrderService = Depends(get_order_service)):
    try:
        result = order_service.get_order_and_items(order_id)
        return CustomResponseModel(message="Order successfully retrieved.", data=result)
    except CustomError as e:
        return custom_error_response(e.code, e.name, e.message, e.payload)
    except Exception as e:
        LOGGER.exception(e)
        return custom_error_response(500, "ServerError", order_id)
