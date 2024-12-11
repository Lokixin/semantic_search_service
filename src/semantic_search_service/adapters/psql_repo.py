import asyncio
from typing import LiteralString
import sys

import numpy as np
import psycopg
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

from semantic_search_service.domain.models import get_model
from src.semantic_search_service.domain.articles import ArticleWithEmbeddings, Article


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
        rows = [
            (article.title, article.excerpt, article.body, article.title_embedding, article.excerpt_embedding,
             article.body_embedding)
            for article in articles
        ]
        query = """INSERT INTO articles (title, excerpt, body, title_embedding, excerpt_embedding, body_embedding) VALUES (%s, %s, %s, %s, %s, %s)"""
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, rows)

            await conn.commit()


    async def semantic_search_articles(self, user_query_embedding: np.ndarray[np.float32]) -> list[tuple[str, str, str, str, str]]:
        query = """SELECT (title, excerpt, body, updated_at, created_at) FROM articles ORDER BY body_embedding <=> %s LIMIT 5;"""
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (user_query_embedding, ))
                res = await cur.fetchall()
                return res



if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def main():
        conn_info = "dbname=vectordb host=localhost user=admin password=admin"
        with psycopg.connect(conn_info, autocommit=True) as sync_conn:
            sync_conn.execute("""CREATE EXTENSION IF NOT EXISTS vector""")

        pool = AsyncConnectionPool(
            conninfo=conn_info, open=False, timeout=5, configure=config_pool
        )
        await pool.open()
        repo = PSQLRepo(pool, db_name="vectordb")

        user_query = "Novedades tecnológicas"
        model = get_model("mini_lm")
        user_query_embedding = model.encode(user_query)
        try:
            res = await repo.semantic_search_articles(user_query_embedding)
            res = [Article(*_res[0]) for _res in res]
            for idx, _res in enumerate(res):
                print(f"{idx}. {_res.title}\n")
        finally:
            await pool.close()

    asyncio.run(main())
