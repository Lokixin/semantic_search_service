import psycopg
from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool


conn_info = "dbname=vectordb host=localhost user=admin password=admin"

async def config_pool(conn) -> None:
    with psycopg.connect(conn_info, autocommit=True) as _conn:
        _conn.execute("""CREATE EXTENSION IF NOT EXISTS vector""")
    await register_vector_async(conn)

pool = AsyncConnectionPool(
    conninfo=conn_info, open=False, timeout=5, configure=config_pool
)
