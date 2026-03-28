# OpenCase CLI Reference

The `opencase` command-line tool is the primary admin and developer
interface for interacting with a running OpenCase instance.

## Installation

The CLI is part of the uv workspace. From the repository root:

```bash
uv sync
```

The `opencase` console script is then available in the virtual
environment.

## Configuration

### Precedence

Settings resolve in this order (highest wins):

1. CLI flags (`--base-url`, `--timeout`)
2. Environment variables (`OPENCASE_BASE_URL`, `OPENCASE_TIMEOUT`)
3. Config file (`~/.opencase/config.toml`)
4. Defaults (`http://localhost:8000`, 30 s timeout)

### Interactive setup

```bash
opencase configure
```

Prompts for base URL and timeout, then writes
`~/.opencase/config.toml`.

## Commands

### Health checks (unauthenticated)

```bash
opencase health              # API health status
opencase ready               # Readiness + service dependency checks
```

`ready` exits with code 1 if any dependency is degraded.

### Authentication

```bash
opencase login --email user@firm.com --password secret
opencase login                                          # interactive prompts
opencase login --email user@firm.com --password s --totp-code 123456  # MFA
opencase logout
opencase whoami              # show current user, role, firm
```

After login, tokens are stored in `~/.opencase/tokens.json`
(mode 0600 on Unix). Subsequent commands use them automatically.

### MFA management

```bash
opencase mfa setup           # shows TOTP secret + provisioning URI
opencase mfa confirm --totp-code 123456
opencase mfa disable --totp-code 123456
```

### Users

```bash
opencase user list
opencase user get <user-id>
opencase user create --email j@firm.com --password secret123! \
  --first-name Jane --last-name Doe --role attorney
opencase user update <user-id> --first-name Janet
```

### Matters

```bash
opencase matter list
opencase matter get <matter-id>
opencase matter create --name "People v. Smith" --client-id <uuid>
opencase matter update <matter-id> --status closed
```

### Matter access

```bash
opencase matter access-list <matter-id>
opencase matter access-grant <matter-id> --user-id <uuid>
opencase matter access-grant <matter-id> --user-id <uuid> --view-work-product
opencase matter access-revoke <matter-id> --user-id <uuid>
```

### Tasks

```bash
opencase task list                          # list all tasks for current firm
opencase task list --status pending         # filter by state
opencase task list --task-name ping         # filter by registered task name
opencase task get <task-id>                 # full task detail + live Celery status
opencase task submit --task-name ping       # submit a registered task
opencase task cancel <task-id>              # revoke a pending/running task
```

Task submission requires Admin or Attorney role. Cancel and update
require Admin. List and get are available to any authenticated user.

Only tasks registered in `TASK_REGISTRY` can be submitted via the
API. Currently registered: `ping`.

### Documents

```bash
# List all documents accessible to the current user
opencase document list
opencase document list --json

# Get metadata for a single document
opencase document get <document-id>

# Upload a single file to a matter
opencase document upload ./evidence.pdf --matter-id <uuid>
opencase document upload ./report.pdf --matter-id <uuid> \
  --source government_production --classification brady \
  --bates-number GOV-001

# Bulk-ingest all supported files from a local directory
opencase document bulk-ingest ./discovery-folder --matter-id <uuid>
opencase document bulk-ingest ./discovery-folder --matter-id <uuid> \
  --source government_production --classification unclassified

# Preview which files would be ingested (no upload)
opencase document bulk-ingest ./discovery-folder --matter-id <uuid> --dry-run

# Non-recursive (top-level files only, skip subdirectories)
opencase document bulk-ingest ./discovery-folder --matter-id <uuid> --no-recursive

# JSON output (machine-readable per-file results)
opencase document bulk-ingest ./discovery-folder --matter-id <uuid> --json
```

**Upload** accepts a file path as a positional argument. The server
computes the SHA-256 hash, checks for duplicates within the matter,
stores the original in MinIO, and returns the document metadata.

**Bulk-ingest** recursively walks a directory (by default), filters to
supported file types (PDF, Word, Excel, PowerPoint, RTF, text, CSV,
HTML, and common image formats), and uploads each file sequentially.

Before uploading, the CLI hashes each file locally and calls the
`/documents/check-duplicate` endpoint. Files that already exist in the
matter are skipped without uploading, saving bandwidth on re-runs.

The summary line reports uploaded, skipped (duplicate), and failed
counts. The exit code is 0 if all files succeeded or were skipped, and
1 if any file failed.

| Option | Default | Description |
| --- | --- | --- |
| `--matter-id` | **required** | Target matter UUID |
| `--source` | `defense` | Document source (`defense`, `government_production`, `court`, `work_product`) |
| `--classification` | `unclassified` | Document classification |
| `--recursive / --no-recursive` | `--recursive` | Walk subdirectories |
| `--dry-run` | off | List files without uploading |
| `--bates-number` | none | Bates number (single upload only) |

### Prompts (stub)

```bash
opencase prompt list
opencase prompt get <prompt-id>
opencase prompt submit --matter-id <uuid> "What Brady material exists?"
```

All prompt endpoints return stub responses. RAG integration
will be added in Feature 9.

### Firm

```bash
opencase firm get                # show current firm details
```

### Utility

```bash
opencase configure           # interactive connection setup
opencase version             # CLI + SDK versions
```

## JSON output

All commands support `--json` for machine-readable output:

```bash
opencase health --json
opencase whoami --json | jq .email
```

## Token storage

Tokens are persisted to `~/.opencase/tokens.json` with restricted
file permissions (0600 on Unix). `opencase logout` clears this file.

On Windows, standard file ACLs apply (chmod is a no-op).

## Global options

Every command accepts:

| Flag | Env var | Description |
| --- | --- | --- |
| `--base-url` | `OPENCASE_BASE_URL` | API base URL |
| `--timeout` | `OPENCASE_TIMEOUT` | Request timeout (seconds) |
| `--json` | — | Machine-readable JSON output |
