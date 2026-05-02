import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uvicorn
from app.logging_config import LOGGING_CONFIG

from sqlalchemy import text, Engine, MetaData, Table, inspect, select
from sqlalchemy.orm import Session

from fastapi.exceptions import RequestValidationError


from app.database.connection_pool import engine
from app.controller.router import router
from app.entity import Base, Product, Order, OrderItem
from app.errors.generic_error import CustomError, custom_error_response

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Load ML models or initialize db connection pools

    LOGGER.info("Test")
    LOGGER.info("Starting up...")
    app.state.engine: Engine = engine
    LOGGER.info(app.state.engine)
    if app.state.engine is not None:
        LOGGER.info("Connection pool created successfully")

    yield

    LOGGER.info("Closing DB Pool")
    app.state.engine.dispose()
    LOGGER.info("Engine is disposed")
    LOGGER.info("Shutdown complete.")


app = FastAPI(lifespan=lifespan)
# app = FastAPI()
app.include_router(router=router)
metadata_object = MetaData()


# @app.exception_handler(CustomError)
# async def custom_error_handler()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    LOGGER.info("type: %s", type(exc))
    return custom_error_response(
        422, "RequestValidationError", "error on validation", exc.errors()
    )


@app.get("/")
async def root(request: Request):
    return {"message": "Hello world!"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        log_config=LOGGING_CONFIG,
    )
