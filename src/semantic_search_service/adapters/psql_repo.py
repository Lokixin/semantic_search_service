import asyncio
from typing import LiteralString

import psycopg
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

from src.semantic_search_service.domain.articles import ArticleWithEmbeddings


async def config_pool(conn) -> None:
    await register_vector_async(conn)


class PSQLRepo:
    def __init__(self, pool: AsyncConnectionPool, db_name: str) -> None:
        self.pool = pool
        self.db_name = db_name

    async def create_articles_table(self) -> None:
        query: LiteralString = """
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title VARCHAR(255) NOT NULL,
                excerpt TEXT NOT NULL,
                body TEXT NOT NULL
            )
        """
        async with self.pool.connection() as conn:
            await conn.execute(query)
            await conn.commit()

    async def alter_articles_table_add_embeddings(self) -> None:
        query: LiteralString = """
            ALTER TABLE articles
            ADD COLUMN title_embedding vector(384),
            ADD COLUMN excerpt_embedding vector(384),
            ADD COLUMN body_embedding vector(384);
        """
        async with self.pool.connection() as conn:
            await conn.execute(query)
            await conn.commit()

    async def add_many_articles(self, articles: list[ArticleWithEmbeddings]) -> None:
        pass


if __name__ == "__main__":

    async def main():
        conn_info = "dbname=vectordb host=localhost user=admin password=admin"
        with psycopg.connect(conn_info, autocommit=True) as sync_conn:
            sync_conn.execute("""CREATE EXTENSION IF NOT EXISTS vector""")

        pool = AsyncConnectionPool(
            conninfo=conn_info, open=False, timeout=5, configure=config_pool
        )
        await pool.open()
        repo = PSQLRepo(pool, db_name="vectordb")
        try:
            await repo.alter_articles_table_add_embeddings()
        finally:
            await pool.close()

    asyncio.run(main())
