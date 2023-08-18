import os
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Connection
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.Entities.base import Base

engine: AsyncEngine


async def init_db() -> None:
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

    await connect_create_if_not_exists(db_address, db_user, db_password, db_name)

    sqlalchemy_database_url = f'postgresql+asyncpg://{db_user}:{db_password}@{db_address}:5432/{db_name}'
    global engine
    engine = create_async_engine(sqlalchemy_database_url, poolclass=NullPool)

    async with engine.begin() as async_session:
        await async_session.run_sync(Base.metadata.create_all)


async def connect_create_if_not_exists(address: str, user: str, password: str, database: str) -> None:
    try:

        conn: Connection = await asyncpg.connect(host=address, user=user, password=password,  # type: ignore
                                                 database=database)
        await conn.close()
    except asyncpg.InvalidCatalogNameError:
        sys_conn = await asyncpg.connect(
            host=address, user=user, password=password, database='template1'
        )
        await sys_conn.execute(
            f'CREATE DATABASE "{database}" OWNER "{user}"'
        )
        await sys_conn.close()


@asynccontextmanager
async def get_session() -> AsyncSession:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
