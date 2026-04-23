# Gideon Scripts

Operational and testing scripts for Gideon. All scripts are run from the repo root.
All Python scripts read credentials and configuration from `.env` via `dotenv`.

## Task & Document Testing

| Script | Purpose |
| --- | --- |
| `submit_task.py` | Submit a ping task and a 30-second sleep task via the API; poll until completion. Useful for testing Celery worker connectivity. |
| `upload_file.py` | Upload a file (or auto-generated test file) to the first matter, then verify the DB record, S3 object, and download round-trip. |

## Data Management

| Script | Purpose |
| --- | --- |
| `chunk_documents.py` | Submit chunking tasks for existing documents. Reads extracted text from S3 and submits tasks via the API. Supports `--limit` flag. |
| `reset_data.py` | Reset all application data (PostgreSQL, MinIO, Qdrant). Truncates user-data tables, empties MinIO bucket, deletes Qdrant collection. Use `--skip-db`, `--skip-s3` to reset selectively. |

## RAG & Search Testing

| Script | Purpose |
| --- | --- |
| `rag_query.py` | End-to-end RAG query against Gideon stack (runs inside FastAPI container). Embeds query, searches Qdrant, retrieves context, calls Ollama for inference. Requires `--matter-id` and `--firm-id`. |
| `search_qdrant.py` | Semantic search against Qdrant vector store (runs inside FastAPI container). Embeds query, searches, retrieves chunk text from MinIO. |
| `query_model.py` | Query an Ollama model directly (no RAG, no Qdrant). Baseline comparison for `rag_query.py` results. Use `--model`, `--system-prompt`, `--max-tokens` flags. |
| `eval_models.py` | Evaluate exported RAG prompts against multiple Ollama models. Takes JSON from `rag_query.py --export-prompt`. Use `--baseline` flag to compare RAG vs bare-question results. |
