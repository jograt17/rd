import logging
import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uvicorn
from app.logging_config import LOGGING_CONFIG
from dotenv import load_dotenv, find_dotenv

from sqlalchemy import Engine, MetaData

from fastapi.exceptions import RequestValidationError


from app.database.connection_pool import engine
from app.controller.router import router
from app.errors.generic_error import custom_error_response

LOGGER = logging.getLogger(__name__)


load_dotenv(find_dotenv())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Load ML models or initialize db connection pools

    LOGGER.info("Starting up...")
    if os.getenv("TESTING") != "true":
        app.state.engine = engine
    else:
        LOGGER.info("TESTING mode — skipping real DB connection")
    if app.state.engine is not None:
        LOGGER.info("Connection pool created successfully")

    yield

    if os.getenv("TESTING") != "true":
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
    return custom_error_response(422, "RequestValidationError", "error on validation", exc.errors())


@app.get("/")
async def root(request: Request):
    return {"message": "Hello world!"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        log_config=LOGGING_CONFIG,
    )
