# Semantic Search Service

This project illustrates how to use FastAPI with PGVector (PostgreSQL plugin for vector search) and SentenceTransformers
models to carry out semantic search tasks. Some fake articles are used, but this can be applied to any kind of text media.


## Current Tasks

1. Setup Fastapi (Done)
2. Add Semantic Search endpoint (Done)
3. CRUD for articles (In progress, GET POST done. Missing DEL, PATCH)
4. Docker image for python app.
5. Setup Tests with Docker Compose and TestDB
6. Add custom score function to compare embeddings from suer query to article's title, excerpt and body (Next)

