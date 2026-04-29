from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.database.connection_pool import create_pool
from app.controller.router import router

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Load ML models or initialize db connection pools

    LOGGER.info("Starting up...")
    app.state.db_pool = await create_pool()
    print("Pool created")
    LOGGER.info(app.state.db_pool)

    if app.state.db_pool is not None:
        LOGGER.info("Connection pool created successfully")
    print(app.state.db_pool)

    yield

    LOGGER.info("Closing DB Pool")
    await app.state.db_pool.close()
    LOGGER.info("DB POOL closed")
    print("Shutdown complete.")


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
