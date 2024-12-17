
.PHONY: app reformat docker-app down integration

app:
	poetry run uvicorn semantic_search_service.main:app --reload --host localhost --port 8000

reformat:
	poetry run ruff check . --fix

docker-app:
	docker-compose up --build

down:
	docker-compose down

integration:
	docker-compose up integration --build

