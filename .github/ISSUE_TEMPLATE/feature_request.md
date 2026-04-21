---
name: Feature Request
about: Suggest an idea for Gideon
title: ""
labels: enhancement
assignees: ""
---

## Problem or Motivation

Describe the problem this feature would solve, or why this capability is
needed. Is this tied to a real workflow?

## Proposed Solution

Describe how you would like this feature to work. Include mockups, pseudocode,
or concrete examples if helpful.

## Alternatives Considered

What other approaches did you consider? Why did you choose the proposed
solution?

## Non-Negotiables Checklist

Before we discuss this feature, please confirm it aligns with Gideon's core
constraints:

- [ ] **No third-party LLM API calls** — inference and embeddings stay
  on-premise via Ollama
- [ ] **No external telemetry** — all observability stays on-premise; no
  data sent to third-party services
- [ ] **No model training on client data** — discovery materials are never
  used to fine-tune or train models
- [ ] **Client data stays on-premise** — no cloud storage, no external APIs
- [ ] **Security-first** — data isolation, RBAC, audit logging, encryption
  at rest and in transit
- [ ] **Legal hold is immutable** — held documents cannot be deleted or
  modified

If any of the above conflict with your proposal, please explain how your
feature respects these boundaries.

## Additional Context

Add screenshots, research, legal references, or other context that would help
evaluate this request.
