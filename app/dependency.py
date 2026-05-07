from fastapi import Request, Depends
from app.repository.product_repository import ProductRepository
from app.service.product_service import ProductService


def get_engine(request: Request):
    return request.app.state.engine


def get_product_repository(engine=Depends(get_engine)):
    return ProductRepository(engine)


def get_product_service(engine=Depends(get_engine), product_repo=Depends(get_product_repository)):
    return ProductService(engine, product_repo)
