from fastapi import APIRouter
import logging

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/products")
async def get_products(is_active: bool | None = None, search: str | None = None):
    LOGGER.info("is_active: %s", is_active)
    return {is_active: is_active, search: search}
