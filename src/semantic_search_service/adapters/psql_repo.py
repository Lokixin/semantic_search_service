import asyncio
from typing import LiteralString
import sys

import numpy as np
import psycopg
from psycopg import sql
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

from src.semantic_search_service.domain.articles import ArticleWithEmbeddings, Article, ArticlePatch, \
    ArticlePatchWithEmbeddings


async def config_pool(conn) -> None:
    await register_vector_async(conn)


class PSQLRepo:
    def __init__(self, pool: AsyncConnectionPool, db_name: str) -> None:
        self.pool = pool
        self.db_name = db_name

    async def select_article_by_id(self, article_id: int) -> Article | None:
        query: LiteralString = """SELECT (title, excerpt, body, updated_at, created_at) FROM articles WHERE id=%s"""
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (article_id,))
                raw_article = await cur.fetchone()
                if not raw_article:
                    return None
                raw_article = raw_article[0]
                return Article(
                    title=raw_article[0],
                    excerpt=raw_article[1],
                    body=raw_article[2],
                    updated_at=raw_article[3],
                    created_at=raw_article[4],
                )

    async def insert_new_article(self, article: ArticleWithEmbeddings) -> int:
        article_dict = article.model_dump(exclude_none=True)

        query = sql.SQL("INSERT INTO articles ({}) VALUES ({}) RETURNING id").format(
        sql.SQL(', ').join(map(sql.Identifier, article_dict.keys())),
            sql.SQL(', ').join(map(sql.Placeholder, article_dict.keys())),
        )
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, article_dict)
                inserted_id = await cur.fetchone()
            await conn.commit()
            return inserted_id

    async def delete_article_by_id(self, article_id: int) -> int | None:
        query: LiteralString = """
            DELETE FROM articles WHERE id=%s RETURNING id
        """
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (article_id,))
                deleted_id = await cur.fetchone()
            await conn.commit()
            return deleted_id

    async def patch_article_by_id(self, article_id: int, article: ArticlePatchWithEmbeddings) -> Article | None:
        article_dict = article.model_dump(exclude_none=True)
        if "updated_at" not in article_dict:
            # THIS IS SATAN. FIX IT LATER
            article_dict["updated_at"] = "NOW()"


        query = sql.SQL("UPDATE articles SET {} WHERE id={} RETURNING title, excerpt, body, updated_at, created_at").format(
            sql.SQL(", ").join(
                sql.SQL("=").join([sql.Identifier(_key), sql.Placeholder(_key)])
                for _key in article_dict.keys()
            ),
            sql.Placeholder("id")
        )
        article_dict["id"] = article_id
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, article_dict)
                res = await cur.fetchone()
            await conn.commit()
            if not res:
                return None
            return Article(
                title=res[0],
                excerpt=res[1],
                body=res[2],
                updated_at=str(res[3]),
                created_at=str(res[4]),
            )


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
        try:
            res = await repo.patch_article_by_id(article_id=11, article=ArticlePatch(title="blah", excerpt="blo"))
            print(res)
        finally:
            await pool.close()

    asyncio.run(main())
