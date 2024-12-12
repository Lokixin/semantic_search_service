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
from semantic_search_service.domain.articles import ArticleWithEmbeddings, Article, ArticlePatch, \
    ArticlePatchWithEmbeddings
from semantic_search_service.domain.models import get_model, Model


async def get_articles_service(article_id: int, repo: PSQLRepo) -> Article:
    return await repo.select_article_by_id(article_id)


async def insert_new_article_service(article: Article, repo: PSQLRepo, model: Model) -> int:
    model = get_model(model)
    title_embedding, excerpt_embedding, body_embedding = model.encode([article.title, article.excerpt, article.body])
    article_with_embeddings = ArticleWithEmbeddings(
        title=article.title,
        excerpt=article.excerpt,
        body=article.body,
        created_at=article.created_at if article.created_at else None,
        updated_at=article.updated_at if article.updated_at else None,
        title_embedding=title_embedding,
        excerpt_embedding=excerpt_embedding,
        body_embedding=body_embedding,
    )
    inserted_id = await repo.insert_new_article(article_with_embeddings)
    return inserted_id


async def delete_article_service(article_id: int, repo: PSQLRepo) -> int | None:
    deleted_id = await repo.delete_article_by_id(article_id)
    return deleted_id


async def patch_article_service(article_id: int, article: ArticlePatch, repo: PSQLRepo, model: Model) -> Article | None:
    article_dict = article.model_dump(exclude_none=True)
    embeddings_to_encode = [
        _k
        for _k, _v in article_dict.items()
        if _k in ["title", "excerpt", "body"] and _v
    ]
    model = get_model(model)
    new_embeddings = model.encode([article_dict[_field] for _field in embeddings_to_encode])
    updated_embeddings = {f"{_field}_embedding": embedding for _field, embedding in zip(embeddings_to_encode, new_embeddings) }
    article_dict.update(updated_embeddings)
    updated_article = await repo.patch_article_by_id(article_id, ArticlePatchWithEmbeddings(**article_dict))
    return updated_article


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