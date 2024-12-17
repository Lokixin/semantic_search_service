import pytest
from psycopg_pool import AsyncConnectionPool

from tests.factories import make_article
from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.domain.models import Model
from semantic_search_service.services.articles_services import insert_new_article_service


@pytest.mark.anyio
async def test_db_connection(async_connection_pool: AsyncConnectionPool) -> None:
    async with async_connection_pool.connection() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT 1")
            assert await cursor.fetchone() == (1,)


@pytest.mark.anyio
async def test_insert_new_article_service(async_connection_pool: AsyncConnectionPool, create_empty_table) -> None:
    article = make_article()
    repo = PSQLRepo(pool=async_connection_pool, db_name="test_db")

    inserted_id = await insert_new_article_service(article=article, repo=repo, model=Model.MINI_LM)
    inserted_article = await repo.select_article_by_id(inserted_id)

    expected_article = article.model_dump()
    assert inserted_article.model_dump() == expected_article
