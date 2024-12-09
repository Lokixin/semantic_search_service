import json
from typing import Callable

from sentence_transformers import SentenceTransformer

from semantic_search_service.domain.articles import ArticleWithEmbeddings


async def populate_articles_table(
    data_reader: Callable[[str], list[dict[str, str]]],
) -> None:
    path_to_data = "./data/articles_data.json"
    raw_articles = data_reader(path_to_data)
    print(raw_articles)


def generate_embeddings_from_article(
    article: dict[str, str], model: SentenceTransformer
) -> ArticleWithEmbeddings:
    title_embeddings, excerpt_embeddings, body_embeddings = model.encode(
        [article["title"], article["excerpt"], article["body"]]
    )
    return ArticleWithEmbeddings(
        title=article["title"],
        excerpt=article["excerpt"],
        body=article["body"],
        title_embedding=title_embeddings,
        excerpt_embedding=excerpt_embeddings,
        body_embedding=body_embeddings,
    )


def read_articles_from_json(path_to_data: str) -> list[dict[str, str]]:
    with open(path_to_data, "r") as _fp:
        data = json.load(_fp)
        return data
