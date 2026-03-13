# OpenCase Feature Roadmap

## Feature 0 — Project Scaffolding

| ID | Feature | Status |
| --- | --- | --- |
| 0.1 | FastAPI skeleton (health endpoint, package structure) | Done |
| 0.2 | AppConfiguration (JSON + env via pydantic-settings) | Done |
| 0.3 | Logging (Python logging, level from AppConfiguration) | Done |
| 0.4 | Observability (OpenTelemetry traces/spans, metrics) | Done |
| 0.5 | Backend Dockerfile (run app for integration testing) | Done |
| 0.6 | `.env.example` | Pending |
| 0.7a | CI: `format-lint.yml` (ruff) | Pending |
| 0.7b | CI: `unit-tests.yml` (pytest @unit) | Pending |
| 0.7c | CI: `integration-tests.yml` (pytest @integration) | Pending |
| 0.7d | CI: `ai-code-review.yml` (same as Signatrust_v4) | Pending |
| 0.7e | CI: `build-container.yml` (on spec/code change) | Pending |

## Feature 1 — API

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 1.0 | OpenAPI specification (openapi.yml) | Pending | Pending |
| 1.1 | Database foundation (User, Firm, Matter models + Alembic) | Pending | Pending |
| 1.2 | Authentication (JWT, TOTP MFA, login/logout/refresh) | Pending | Pending |
| 1.3 | RBAC middleware (role enforcement, `build_qdrant_filter()`) | Pending | Pending |
| 1.4 | Python REST client SDK (backend/sdk/) | Pending | Pending |
| 1.5 | CLI (built on SDK) | Pending | Pending |
| 1.6 | Configuration + env vars (AuthSettings, DbSettings) | Pending | Pending |
| 1.7 | Observability (auth spans/metrics, DB tracing) | Pending | Pending |

## Feature 2 — Worker Queue

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 2.1 | Redis broker container | Pending | Pending |
| 2.2 | Celery app + task definitions (app/workers/) | Pending | Pending |
| 2.3 | Celery worker container + Dockerfile | Pending | Pending |
| 2.4 | Celery Beat scheduler container | Pending | Pending |
| 2.5 | API integration (Celery client, task.delay() submission) | Pending | Pending |
| 2.6 | Observability (Flower container + OTel Celery instrumentation) | Pending | Pending |
| 2.7 | Task result persistence (separate Postgres instance, task lifecycle table for audit) | Pending | Pending |
| 2.8 | Configuration + env vars (CelerySettings, RedisSettings, FlowerSettings) | Pending | Pending |

## Feature 3 — S3 Storage

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 3.1 | MinIO container setup + default bucket | Pending | Pending |
| 3.2 | API integration (boto3/minio-py, app/storage/) | Pending | Pending |
| 3.3 | Configuration + env vars (S3Settings) | Pending | Pending |
| 3.4 | Observability (S3 operation spans/metrics) | Pending | Pending |

## Feature 4 — Document Extraction

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 4.1 | Tika container setup | Pending | Pending |
| 4.2 | Extraction task definitions (Celery tasks in app/workers/tasks/) | Pending | Pending |
| 4.3 | Configuration + env vars (ExtractionSettings) | Pending | Pending |
| 4.4 | Observability (extraction spans/metrics) | Pending | Pending |

## Feature 5 — Chunking & Embedding

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 5.1 | Infrastructure setup (Qdrant collection, Ollama model pull, health checks) | Pending | Pending |
| 5.2 | Chunking task (Celery task, text splitting, overlap strategy) | Pending | Pending |
| 5.3 | Embedding task (Celery task, Ollama nomic-embed-text) | Pending | Pending |
| 5.4 | Qdrant upsert task (Celery task, vector storage, permission metadata payload) | Pending | Pending |
| 5.5 | Configuration + env vars (ChunkingSettings, QdrantSettings, OllamaSettings) | Pending | Pending |
| 5.6 | Observability (chunking/embedding spans/metrics) | Pending | Pending |

## Feature 6 — Document Ingestion

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 6.1 | Manual upload (async via Celery, SHA-256 dedup, legal hold) | Pending | Pending |
| 6.2 | Cloud ingestion (OneDrive/SharePoint via Graph API) | Pending | Pending |
| 6.3 | Configuration + env vars (IngestionSettings) | Pending | Pending |
| 6.4 | Observability (ingestion spans/metrics) | Pending | Pending |

## Feature 7 — Chatbot / Q&A

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 7.1 | Matter-scoped RAG query | Pending | Pending |
| 7.2 | Citation assembly | Pending | Pending |
| 7.3 | AI disclaimer | Pending | Pending |
| 7.4 | Conversation history | Pending | Pending |
| 7.5 | Audit logging of queries | Pending | Pending |

## Feature 8 — Brady/Giglio Tracker

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 8.1 | CPL 245 disclosure clocks | Pending | Pending |
| 8.2 | CPL 30.30 speedy trial clock | Pending | Pending |
| 8.3 | Demand/response log | Pending | Pending |
| 8.4 | Brady/Giglio classification | Pending | Pending |
| 8.5 | Deadline alerts | Pending | Pending |

## Feature 9 — Document Viewer & Review

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 9.1 | Document retrieval from S3 | Pending | Pending |
| 9.2 | Hit highlighting | Pending | Pending |
| 9.3 | Batch tagging | Pending | Pending |
| 9.4 | Notes/annotations | Pending | Pending |
| 9.5 | Bates number display | Pending | Pending |

## Feature 10 — Witness Index

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 10.1 | Entity extraction | Pending | Pending |
| 10.2 | Giglio flagging | Pending | Pending |
| 10.3 | Jencks material gating | Pending | Pending |
| 10.4 | Witness-document linking | Pending | Pending |

## Feature 11 — RBAC & MFA

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 11.1 | JWT authentication | Pending | Pending |
| 11.2 | MFA (TOTP) | Pending | Pending |
| 11.3 | Four roles (Admin, Attorney, Paralegal, Investigator) | Pending | Pending |
| 11.4 | Matter assignment | Pending | Pending |
| 11.5 | Work product visibility | Pending | Pending |
| 11.6 | Session management (httpOnly cookies) | Pending | Pending |

## Feature 12 — Audit Logging

| ID | Feature | Specs | Code |
| --- | --- | --- | --- |
| 12.1 | Hash-chained log | Pending | Pending |
| 12.2 | Nightly chain validation | Pending | Pending |
| 12.3 | PDF/CSV export | Pending | Pending |
| 12.4 | Event type filtering | Pending | Pending |
