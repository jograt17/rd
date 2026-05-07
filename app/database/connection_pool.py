import os
from sqlalchemy import URL, create_engine

url = URL.create(
    drivername="postgresql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
)

engine = create_engine(url=url, pool_size=20, max_overflow=0)
