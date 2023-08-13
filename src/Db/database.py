import os
from contextlib import asynccontextmanager

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy_utils import create_database, database_exists

from src.Entities.base import Base

db_user = os.getenv('DB_USER')
if db_user is None:
    db_user = 'postgres'
db_password = os.getenv('DB_PASSWORD')
if db_password is None:
    db_password = 'qwerty'
db_address = os.getenv('DB_ADDRESS')
if db_address is None:
    db_address = 'localhost'
db_name = os.getenv('DB_NAME')
if db_name is None:
    db_name = 'mydb'

sqlalchemy_database_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_address}:5432/{db_name}'
engine: AsyncEngine = create_async_engine(sqlalchemy_database_url, poolclass=NullPool)


async def init_db() -> None:
    global engine
    async with engine.begin() as async_session:
        db_exists = await async_session.run_sync(lambda session, url: database_exists(url), sqlalchemy_database_url)
        if not db_exists:
            await async_session.run_sync(create_database(engine.url))
        await async_session.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
