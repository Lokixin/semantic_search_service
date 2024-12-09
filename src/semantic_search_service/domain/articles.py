from dataclasses import dataclass

import numpy as np


@dataclass
class ArticleWithEmbeddings:
    title: str
    excerpt: str
    body: str
    title_embedding: np.ndarray[np.float32]
    excerpt_embedding: np.ndarray[np.float32]
    body_embedding: np.ndarray[np.float32]
    updated_at: str | None = None
    created_at: str | None = None
