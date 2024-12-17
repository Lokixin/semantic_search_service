# Semantic Search Service

This project illustrates how to use FastAPI with PGVector (PostgreSQL plugin for vector search) and SentenceTransformers
models to carry out semantic search tasks. Some fake articles are used, but this can be applied to any kind of text media.


## Current Tasks

1. Setup Fastapi (Done)
2. Add Semantic Search endpoint (Done)
3. CRUD for articles (Done)
4. Docker image for python app (Next).
5. Setup Tests with Docker Compose and TestDB (Next)
6. Add custom score function to compare embeddings from user query to article's title, excerpt and body (Next)
