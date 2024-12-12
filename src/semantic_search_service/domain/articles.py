from pydantic import BaseModel

import numpy as np


class Article(BaseModel):
    title: str
    excerpt: str
    body: str
    updated_at: str | None
    created_at: str | None


class ArticleWithEmbeddings(Article):
    title_embedding: np.ndarray[np.float32]
    excerpt_embedding: np.ndarray[np.float32]
    body_embedding: np.ndarray[np.float32]

    class Config:
        arbitrary_types_allowed = True
