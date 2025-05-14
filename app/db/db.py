import asyncpg
import os

from fastapi import HTTPException

POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "db")


def get_db_url():
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)

    async def init(self):
        with open("./init.sql", "r") as f:
            query = f.read()
        await self.execute(query)

    async def test_insert(self):
        with open("./insert.sql", "r") as f:
            query = f.read()
        await self.execute(query)

    async def fetch(self, query: str, *args):
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetch(query, *args)
        except:
            raise HTTPException(status_code=500, detail="Database error")

    async def fetchrow(self, query: str, *args):
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetchrow(query, *args)
        except:
            raise HTTPException(status_code=500, detail="Database error")

    async def execute(self, query: str, *args):
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(query, *args)
        except:
            raise HTTPException(status_code=500, detail="Database error")

    async def close(self):
        await self.pool.close()


db = Database(dsn=get_db_url())
