
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette.responses import JSONResponse

from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.domain.articles import Article, ArticlePatch
from semantic_search_service.domain.models import Model
from semantic_search_service.fastapi_dependencies import get_psql_repo
from semantic_search_service.services.articles_services import get_articles_service, insert_new_article_service, \
    patch_article_service

articles_router = APIRouter(prefix="/articles", tags=["articles"])


@articles_router.get("/{article_id}")
async def get_articles(article_id: int, repo: PSQLRepo = Depends(get_psql_repo)) -> Article:
    article =  await get_articles_service(article_id, repo)
    if not article:
        raise HTTPException(status_code=404, detail=f"Article with {article_id=} not found")
    return article


@articles_router.post("/")
async def post_article(article_body: Article, model: Model, repo: PSQLRepo = Depends(get_psql_repo)) -> JSONResponse:
    inserted_id = await insert_new_article_service(article_body, repo, model)
    return JSONResponse({"msg": "Created new article", "id": inserted_id})


@articles_router.delete("/{article_id}")
async def delete_article(article_id: int, repo: PSQLRepo = Depends(get_psql_repo)) -> JSONResponse:
    deleted_id = await repo.delete_article_by_id(article_id)
    if not deleted_id:
        raise HTTPException(status_code=404, detail=f"Article not found for {article_id=}")
    return JSONResponse({"msg": "Deleted article", "id": article_id})


@articles_router.patch("/{article_id}")
async def patch_article(article_id: int, article_body: ArticlePatch, model: Model ,repo: PSQLRepo = Depends(get_psql_repo)) -> Article:
    updated_article = await patch_article_service(article_id, article_body, repo, model)
    if not updated_article:
        raise HTTPException(status_code=404, detail=f"Article not found for {article_id=}")
    return updated_article
