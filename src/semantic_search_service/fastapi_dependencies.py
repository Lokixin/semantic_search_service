from semantic_search_service.adapters.psql_repo import PSQLRepo
from semantic_search_service.resources import pool


def get_psql_repo() -> PSQLRepo:
    return PSQLRepo(pool=pool, db_name="vectordb")
