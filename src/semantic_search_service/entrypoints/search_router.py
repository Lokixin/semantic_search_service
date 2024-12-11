from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.params import Depends

from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.domain.articles import Article
from semantic_search_service.domain.models import Model
from semantic_search_service.fastapi_dependencies import get_psql_repo
from semantic_search_service.services.search_services import semantic_search_service

search_router = APIRouter(
    prefix="/search",
    tags=["search"],
)

user_query_param = Query(example="News about global economy")


@search_router.get("/", response_model=list[Article])
async def search(user_query: Annotated[str, user_query_param], model: Model, repo: PSQLRepo = Depends(get_psql_repo)) -> list[Article]:
    return await semantic_search_service(
        repo=repo,
        model=model,
        user_query=user_query,
    )
