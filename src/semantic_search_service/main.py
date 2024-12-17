import asyncio
import sys
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI

from semantic_search_service.entrypoints.articles_router import articles_router
from semantic_search_service.entrypoints.search_router import search_router
from semantic_search_service.resources import pool


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncContextManager[None]:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    await pool.open()
    yield
    await pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(search_router)
app.include_router(articles_router)

@app.get("/")
def status():
    return {"status": "Working"}
