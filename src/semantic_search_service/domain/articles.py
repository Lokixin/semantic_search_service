from dataclasses import dataclass

import numpy as np

@dataclass
class Article:
    title: str
    excerpt: str
    body: str
    updated_at: str | None
    created_at: str | None


@dataclass
class ArticleWithEmbeddings(Article):
    title_embedding: np.ndarray[np.float32]
    excerpt_embedding: np.ndarray[np.float32]
    body_embedding: np.ndarray[np.float32]
