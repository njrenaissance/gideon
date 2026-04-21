---
name: Bug Report
about: Report a bug or unexpected behavior
title: ""
labels: bug
assignees: ""
---

## Describe the Bug

A clear and concise description of what the bug is.

## Steps to Reproduce

Steps to reproduce the behavior:

1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior

Describe what you expected to happen.

## Actual Behavior

Describe what actually happened instead.

## Environment

Run the environment collection script from the repo root to gather this automatically:

**Linux/macOS:**

```bash
bash scripts/collect-environment.sh
```

**Windows (PowerShell):**

```powershell
.\scripts\collect-environment.ps1
```

Or provide manually:

- **OS**: (e.g., Ubuntu 22.04, macOS 13, Windows 11)
- **Docker version**: (output of `docker --version`)
- **Docker Compose version**: (output of `docker compose --version`)
- **Gideon version/commit**: (git SHA from `git log --oneline -1`)
- **Python version** (if running outside Docker): (output of `python --version`)

## Logs

If applicable, attach relevant logs (scrubbed of client names, case numbers, or
sensitive discovery materials):

```
Paste logs here
```

Run `docker compose logs <service-name>` to get logs from a specific service
(e.g., `docker compose logs fastapi`).

## Additional Context

Add any other context about the problem here.
