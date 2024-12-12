
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette.responses import JSONResponse

from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.domain.articles import Article
from semantic_search_service.fastapi_dependencies import get_psql_repo
from semantic_search_service.services.articles_services import get_articles_service

articles_router = APIRouter(prefix="/articles", tags=["articles"])


@articles_router.get("/{articles_id}")
async def get_articles(articles_id: int, repo: PSQLRepo = Depends(get_psql_repo)) -> Article:
    article =  await get_articles_service(articles_id, repo)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article with {articles_id=} not found")
    return article


@articles_router.post("/")
async def post_article(article_body: Article) -> JSONResponse:
    pass


@articles_router.delete("/{articles_id}")
async def delete_article(articles_id: int) -> JSONResponse:
    pass


@articles_router.put("/{articles_id}")
async def put_article(article_id: int, article_body: Article) -> Article:
    pass
