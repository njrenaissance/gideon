# Deployment & Development Guide

This guide covers building Docker images, deploying Gideon, and running integration tests.

## Overview

Gideon uses a **single Docker image** for all backend services (FastAPI, Celery, database migrations).

**Production Compose**: Uses pre-built images from GitHub Container Registry (GHCR).
**Development Compose**: Builds images locally on demand.
**Integration Compose**: Runs tests with ephemeral data volumes for clean test isolation.

---

## Building the Backend Image

### Trigger a Build (GitHub Actions)

The workflow `.github/workflows/build-backend.yml` builds and pushes the backend image to GHCR.

**Prerequisites:**
- GitHub Actions is enabled on the repository
- `GITHUB_TOKEN` has `packages:write` permission (automatic for GitHub Actions)

**To build and push:**

1. Open the **Actions** tab on GitHub
2. Select **Build Backend Image** workflow
3. Click **Run workflow**
4. Enter an optional tag (default: `latest`)
5. Workflow will build, tag, and push to:
   - `ghcr.io/njrenaissance/gideon/backend:latest`
   - `ghcr.io/njrenaissance/gideon/backend:<SHA>` (commit hash)

The image includes all optional extras (e.g., `monitoring` for Flower).

### Image Builds

The workflow uses Docker's layer caching (`type=gha`) to speed up subsequent builds.

---

## Running in Production

Production uses the pre-built image from GHCR.

```bash
cd infrastructure
docker compose -f docker-compose.yml --env-file ../.env up -d
```

**Prerequisites:**
- Docker and Docker Compose installed
- `.env` file in project root with required variables
- Authentication to GHCR (if image is private):
  ```bash
  echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin
  ```

**Stateful volumes** (persistent across restarts):
- `gideon-postgres-data` — PostgreSQL data
- `gideon-qdrant-data` — Vector store (Qdrant)
- `gideon-ollama-models` — Downloaded LLM models

These are created as external Docker volumes before first run. Gideon will not start if they don't exist.

---

## Development (Local Builds)

To develop and test code changes locally, build the image from source:

```bash
cd infrastructure
docker compose -f docker-compose.yml -f docker-compose.local-build.yml --env-file ../.env up
```

The `-f docker-compose.local-build.yml` override replaces `image:` settings with local `build:` contexts.

**Local development volumes** (ephemeral by default):
- Containers can still mount named volumes if needed for data persistence

---

## Integration Testing

Integration tests use a separate compose stack with **ephemeral volumes** for data isolation.

Compose file: `infrastructure/docker-compose.integration.yml`
- Overrides database and vector store to use ephemeral volumes
- Keeps `ollama-models` as an external volume (cached across test runs)
- Disables Flower (monitoring not needed for tests)

**Database names** (separate from production):
- `gideon_test` — API database
- `gideon_tasks_test` — Celery result backend database

The init script (`postgres/init.sql`) creates both databases and task database automatically.

**Running integration tests:**

```bash
cd backend
pytest --compose-up --compose-file ../infrastructure/docker-compose.yml \
       --compose-file ../infrastructure/docker-compose.integration.yml
```

(Assumes pytest-docker is configured in `conftest.py`)

After each test run, tear down with volume cleanup:

```bash
docker compose -f infrastructure/docker-compose.yml \
               -f infrastructure/docker-compose.integration.yml \
               down -v
```

---

## Compose File Structure

| File | Use Case | Build Source | Volumes | Notes |
| --- | --- | --- | --- | --- |
| `docker-compose.yml` | Production | Pre-built (GHCR) | Stateful (external) | Use in production or staging |
| `docker-compose.local-build.yml` | Local dev | Local (from source) | Default (ephemeral) | Stack with base compose for local testing |
| `docker-compose.integration.yml` | Integration tests | Inherit from base | Ephemeral | Stack with base compose for test isolation |

---

## Environment Variables

All environment configuration is loaded from `.env` in the project root.

**Required for production:**
```env
POSTGRES_USER=gideon
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=gideon
GIDEON_AUTH_SECRET_KEY=<random_32_byte_key>
GIDEON_S3_ACCESS_KEY=gideon
GIDEON_S3_SECRET_KEY=<secure_password>
GIDEON_ADMIN_EMAIL=admin@example.com
GIDEON_ADMIN_PASSWORD=<secure_password>
```

See `.env.example` or `CLAUDE.md` for the full reference.

---

## Troubleshooting

### "Image not found" error

Ensure the image has been built and pushed:
```bash
docker pull ghcr.io/njrenaissance/gideon/backend:latest
```

If it fails, either:
1. Trigger a new build via GitHub Actions
2. Use local builds (`docker-compose.local-build.yml`)

### "External volume not found"

Stateful volumes must be created before first run:
```bash
docker volume create gideon-postgres-data
docker volume create gideon-qdrant-data
docker volume create gideon-ollama-models
```

### Tests fail with "database already exists"

Make sure to tear down with `-v` to remove ephemeral volumes:
```bash
docker compose -f infrastructure/docker-compose.yml \
               -f infrastructure/docker-compose.integration.yml \
               down -v
```

---

## Next Steps

- [x] GitHub workflow builds and pushes backend image
- [x] Production compose references pre-built image from GHCR
- [x] Integration tests use ephemeral data volumes
- [ ] Frontend image build & deployment (out of scope for initial release)
- [ ] Kubernetes/Helm manifests (V2 feature)
