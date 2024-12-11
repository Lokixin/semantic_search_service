from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.domain.articles import Article
from semantic_search_service.domain.models import Model, get_model


async def semantic_search_service(user_query: str, model: Model, repo: PSQLRepo) -> list[Article]:
    model = get_model(model)
    user_query_embeddings = model.encode(user_query)
    raw_articles = await repo.semantic_search_articles(user_query_embeddings)
    articles = [
        Article(
            title=article[0][0],
            body=article[0][1],
            excerpt=article[0][2],
            updated_at=article[0][3],
            created_at=article[0][4],
        )
        for article in raw_articles
    ]
    return articles
