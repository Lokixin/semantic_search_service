import logging
from typing import LiteralString

import psycopg
import pytest
from psycopg_pool import AsyncConnectionPool

from semantic_search_service.resources import config_pool

conn_info = "dbname=postgres host=postgres user=admin password=admin"
test_db_conn_info = "dbname=testdb host=postgres user=tester password=test_password"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def setup_test_db() -> None:
    drop_old_db_query = """DROP DATABASE IF EXISTS testdb"""
    drop_old_user = """DROP ROLE IF EXISTS tester;"""
    create_db_query = """CREATE DATABASE testdb;"""
    create_user_query = """CREATE USER tester WITH PASSWORD 'test_password';"""
    grant_privileges_query = """GRANT ALL PRIVILEGES ON DATABASE testdb TO tester;"""
    upgrade_to_superuser = """ALTER USER tester WITH SUPERUSER;"""

    with psycopg.connect(conn_info, autocommit=True) as conn:
        logger.info("Creating test database")
        conn.execute(drop_old_db_query)
        conn.execute(drop_old_user)
        conn.execute(create_db_query)
        conn.execute(create_user_query)
        conn.execute(grant_privileges_query)
        conn.execute(upgrade_to_superuser)
        logger.info("Test Database created")


@pytest.fixture(scope="session")
def setup_vector_field(setup_test_db) -> None:
    with psycopg.connect(test_db_conn_info, autocommit=True) as sync_conn:
        sync_conn.execute("""CREATE EXTENSION IF NOT EXISTS vector""")
        logger.info("Created vector field")


@pytest.fixture(scope="session")
async def async_connection_pool(setup_vector_field) -> AsyncConnectionPool:
    pool = AsyncConnectionPool(
        conninfo=test_db_conn_info, open=False, timeout=15, configure=config_pool
    )
    await pool.open()
    yield pool
    await pool.close()


@pytest.fixture(scope="session")
async def create_empty_table(async_connection_pool: AsyncConnectionPool) -> None:
    table_query: LiteralString = """
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(255) NOT NULL,
                excerpt TEXT NOT NULL,
                body TEXT NOT NULL,
                title_embedding vector(384),
                excerpt_embedding vector(384),
                body_embedding vector(384)
            );
        """
    drop_table_query = """DROP TABLE IF EXISTS articles;"""
    async with async_connection_pool.connection() as conn:
        await conn.execute(table_query)
        await conn.commit()
        yield
        await conn.execute(drop_table_query)
        await conn.commit()
