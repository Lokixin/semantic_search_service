from datetime import datetime, timezone

from semantic_search_service.domain.articles import Article


def make_article(
    title: str | None = None,
    excerpt: str | None = None,
    body: str | None = None,
    updated_at: str | None = None,
    created_at: str | None = None,
) -> Article:
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return Article(
        title=title or "article title",
        excerpt=excerpt or "article excerpt",
        body=body or "article body",
        updated_at=updated_at or current_date,
        created_at=created_at or current_date,
    )
