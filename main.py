from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uvicorn
from app.logging_config import LOGGING_CONFIG

from sqlalchemy import text, Engine, MetaData, Table, inspect

import logging

from app.database.connection_pool import engine
from app.controller.router import router

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


@app.get("/")
async def root(request: Request):
    # try:
    engine1 = request.app.state.engine
    # with engine.connect() as connection:
    # result = connection.execute(text("SELECT 1"))
    # LOGGER.info("🎉 Connection successful!")
    # LOGGER.info(f"Result: {result.scalar()}")
    # messages = Table(
    #     "products", metadata_object, schema="avoria", autoload_with=engine1
    # )

    inspector = inspect(engine1)

    # Target a specific schema
    target_schema = "avoria"

    # 3. Get table names for that schema
    tables = inspector.(schema=target_schema)

    print(f"Tables in {target_schema}:", tables)
    # print(messages.columns.keys)

    return ""
    # except Exception as e:
    #     LOGGER.error("❌ Connection failed!")
    #     LOGGER.error(e)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        log_config=LOGGING_CONFIG,
    )
