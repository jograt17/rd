import os

import asyncpg
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


async def create_pool():
    return await asyncpg.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        min_size=5,
        max_size=10,
        command_timeout=60,
    )
