import asyncio
import json
import sys
from pathlib import Path
from typing import Callable

import psycopg
from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool
from sentence_transformers import SentenceTransformer

from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.domain.articles import ArticleWithEmbeddings, Article
from semantic_search_service.domain.models import get_model



async def get_articles_service(article_id: int, repo: PSQLRepo) -> Article:
    return await repo.select_article_by_id(article_id)


async def populate_articles_table(
    data_reader: Callable[[str], list[dict[str, str]]], psql_repo: PSQLRepo, model: str = "mp_net"
) -> None:
    path_to_data = Path(__file__).parent.parent / "adapters" / "data" / "articles.json"
    raw_articles = data_reader(str(path_to_data))
    model = get_model(model)
    articles_with_embeddings = [
        generate_embeddings_from_article(article, model)  for article in raw_articles
    ]
    await psql_repo.add_many_articles(articles_with_embeddings)


def generate_embeddings_from_article(
    article: dict[str, str], model: SentenceTransformer
) -> ArticleWithEmbeddings:
    title_embeddings, excerpt_embeddings, body_embeddings = model.encode(
        [article["title"], article["excerpt"], article["body"]]
    )
    return ArticleWithEmbeddings(
        title=article["title"],
        excerpt=article["excerpt"],
        body=article["body"],
        title_embedding=title_embeddings,
        excerpt_embedding=excerpt_embeddings,
        body_embedding=body_embeddings,
    )


def read_articles_from_json(path_to_data: str) -> list[dict[str, str]]:
    with open(path_to_data, "r", encoding="utf-8") as _fp:
        data = json.load(_fp)
        return data



if __name__ == "__main__":
    async def config_pool(conn) -> None:
        await register_vector_async(conn)


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
            await populate_articles_table(data_reader=read_articles_from_json, psql_repo=repo, model="mini_lm")
        finally:
            await pool.close()

    asyncio.run(main())