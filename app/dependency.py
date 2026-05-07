from fastapi import Request, Depends
from app.repository.product_repository import ProductRepository
from app.service.product_service import ProductService
from app.repository.order_repository import OrderRepository
from app.service.order_service import OrderService


def get_engine(request: Request):
    return request.app.state.engine


def get_product_repository(engine=Depends(get_engine)):
    return ProductRepository(engine)


def get_product_service(engine=Depends(get_engine), product_repo=Depends(get_product_repository)):
    return ProductService(engine, product_repo)


def get_order_repository(engine=Depends(get_engine)):
    return OrderRepository(engine=engine)


def get_order_service(
    engine=Depends(get_engine),
    order_repo=Depends(get_order_repository),
    product_repo=Depends(get_product_repository),
):
    return OrderService(engine=engine, order_repo=order_repo, product_repo=product_repo)
