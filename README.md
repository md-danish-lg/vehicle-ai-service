# 🤖 Vehicle AI Service

A FastAPI microservice providing LLM-powered repair history storage and summarization for the Vehicle Service Management System. Uses ChromaDB for vector storage with vehicle-scoped metadata filtering and Groq for LLM inference.

## Tech Stack

- **Python 3** + **FastAPI** — REST API framework
- **Pydantic** — request/response validation
- **Groq API** — LLM inference (llama-3.3-70b-versatile)
- **ChromaDB** — persistent vector database for semantic search
- **python-dotenv** — environment variable management
- **Docker** — containerised deployment

## Architecture

```
Spring Boot → POST /repair-history/add       → ChromaDB (store)
           → POST /repair-history/summarize  → ChromaDB (retrieve) → Groq → summary
```

Records are stored with `vehicle_id` metadata — all queries are scoped to a specific vehicle so a Toyota Corolla's history never bleeds into a Honda Civic's.

## Endpoints

| Method | Endpoint | Request Body | Description |
|--------|----------|-------------|-------------|
| `GET` | `/health` | — | Health check |
| `POST` | `/repair-history/add` | `{"id", "text", "vehicle_id"}` | Store a repair record in ChromaDB |
| `POST` | `/repair-history/search` | `{"text", "vehicle_id", "result_length"}` | Semantic search scoped to a vehicle |
| `POST` | `/repair-history/summarize` | `{"text", "vehicle_id", "result_length"}` | Retrieve records + LLM summary |

All fields are required — no silent defaults.

## Key Concept: Metadata Filtering

Each repair record is stored with `vehicle_id` as metadata:
```python
collection.add(
    documents=["oil change, brake pad replacement"],
    ids=["1"],
    metadatas=[{"vehicle_id": 3}]
)
```

Queries filter by `vehicle_id` so semantic search only returns records for the requested vehicle:
```python
collection.query(
    query_texts=["engine issues"],
    where={"vehicle_id": 3}
)
```

## Getting Started

### Prerequisites
- Python 3.10+
- Groq API key (free at console.groq.com)

### Setup
```bash
pip install fastapi uvicorn groq chromadb python-dotenv
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

### Run locally
```bash
uvicorn main:app --reload
```

### Run with Docker Compose
```bash
docker-compose up --build
```

Service available at `http://localhost:8000`

## Example Requests

**Store a repair record**
```bash
curl -X POST http://localhost:8000/repair-history/add \
  -H "Content-Type: application/json" \
  -d '{"id": "1", "text": "2019 Toyota Corolla — oil change, brake pad replacement", "vehicle_id": 1}'
```

**Get vehicle repair summary**
```bash
curl -X POST http://localhost:8000/repair-history/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "full service history", "vehicle_id": 1, "result_length": 5}'
```

## What I Learned

- Building REST APIs with FastAPI and Pydantic validation
- LLM API integration with Groq
- Vector storage and semantic search with ChromaDB
- Metadata filtering for scoped vector search
- RAG pattern — retrieve relevant context → pass to LLM → grounded response
- PersistentClient for durable Chroma storage across restarts
- Dockerising a Python service for polyglot microservice deployment