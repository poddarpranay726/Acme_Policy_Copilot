# Acme Policy Copilot

An enterprise knowledge assistant powered by Retrieval-Augmented Generation (RAG). Ask questions about company policies and receive context-aware answers grounded in retrieved documents.

## Architecture

```text
                 React Frontend
                       |
                    FastAPI
                       |
              Authentication (JWT)
                       |
              Conversation Manager
                       |
                 Query Rewriter
                       |
             Hybrid Retrieval (RRF)
                /           \
          Dense Search     BM25
                \           /
                 Reranking
                     |
                LLM Generation
                     |
             Answer with Sources
```

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| LLM integration | LangChain, OpenRouter |
| Embeddings | Sentence Transformers, BGE |
| Vector database | Qdrant |
| Keyword retrieval | BM25 |
| Hybrid retrieval | Reciprocal Rank Fusion |
| Reranking | Cross-encoder |
| Database | PostgreSQL |
| Cache | Redis |
| Authentication | JWT |
| Containerization | Docker, Docker Compose |

## Key Features

- Document-based question answering using RAG.
- Dense semantic retrieval and BM25 keyword retrieval.
- Hybrid retrieval using Reciprocal Rank Fusion.
- Cross-encoder reranking.
- Query rewriting.
- Conversational question answering.
- JWT-based user authentication.
- Conversation and message persistence.
- Redis-based conversation caching.
- Streaming responses using Server-Sent Events.
- Source-aware answers.
- Containerized application services.

## Project Structure

```text
Acme_policy_copilot/
├── frontend/
├── src/
│   └── acme_policy_copilot/
│       ├── api/
│       ├── auth/
│       ├── cache/
│       ├── conversation/
│       ├── database/
│       ├── embeddings/
│       ├── generation/
│       ├── ingestion/
│       ├── pipeline/
│       ├── retrieval/
│       └── vectorstore/
├── data/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose
- OpenRouter API key

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Acme_policy_copilot
```

### 2. Configure environment variables

Create your `.env` file using `.env.example`:

```bash
cp .env.example .env
```

Fill in the required API keys, database credentials, Redis configuration and JWT secret.

### 3. Start the application

```bash
docker compose up -d --build
```

### 4. Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API documentation | http://localhost:8000/docs |
| Qdrant dashboard | http://localhost:6333/dashboard |

Make sure the database has been initialized and the required documents have been ingested into Qdrant before querying.

## Useful Docker Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View running containers
docker compose ps

# View backend logs
docker compose logs -f backend

# Rebuild services
docker compose up -d --build

# Stop services and remove containers
docker compose down
```

**Note:** Persistent Docker volumes are used for application data. Avoid `docker compose down -v` unless you intentionally want to delete those volumes.

## Future Improvements

- Production deployment and HTTPS.
- Advanced access-control filtering.
- Observability and tracing.
- Automated testing and CI/CD.
- Further retrieval and generation optimizations.

## License

Add your preferred license before making the repository public.