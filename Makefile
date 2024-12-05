
.PHONY: app reformat

app:
	poetry run uvicorn semantic_search_service.main:app --reload --host localhost --port 8000

reformat:
	poetry run ruff check . --fix
