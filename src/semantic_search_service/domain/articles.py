from pydantic import BaseModel, ConfigDict

import numpy as np


class ArticlePatch(BaseModel):
    title: str | None = None
    excerpt: str | None = None
    body: str | None = None
    updated_at: str | None = None
    created_at: str | None = None

class ArticlePatchWithEmbeddings(ArticlePatch):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    title_embedding: np.ndarray[np.float32] | None = None
    excerpt_embedding: np.ndarray[np.float32] | None = None
    body_embedding: np.ndarray[np.float32] | None = None


class Article(BaseModel):
    title: str
    excerpt: str
    body: str
    updated_at: str | None
    created_at: str | None


class ArticleWithEmbeddings(Article):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    title_embedding: np.ndarray[np.float32]
    excerpt_embedding: np.ndarray[np.float32]
    body_embedding: np.ndarray[np.float32]

