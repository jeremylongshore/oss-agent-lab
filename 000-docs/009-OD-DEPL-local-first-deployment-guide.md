# 009-OD-DEPL: Local-First Deployment Guide

**Category:** Operations Document -- Deployment
**Status:** Final
**Date:** 2026-03-16
**Author:** Jeremy Longshore

---

## Philosophy

Local-first. Self-hosted by default. No SaaS dependencies. No telemetry. No phone-home. Deploy wherever you want.

OSS Agent Lab runs on your machine, under your control. Cloud deployment is optional and documented, but the project is designed so that `pip install -e .` on a laptop is the primary and best-supported path. If your internet goes down, the orchestration layer still works -- only specialists that need live data (scoring sources, paper searches) degrade gracefully.

---

## Deployment Targets

| Target | Support Level | Notes |
|--------|--------------|-------|
| **Local machine** | First-class | `pip install -e .`, works offline for orchestration |
| **Self-hosted server** | First-class | Same install as local, add persistent memory directory |
| **Docker** | Documented | Dockerfile included, single-container deployment |
| **Google Cloud Run** | Documented | Optional, suitable for persistent API deployment |
| **Any cloud VM** | Bring-your-own | Standard Python app, no cloud-specific dependencies |
| **Serverless (Lambda, Cloud Functions)** | Not targeted | Against local-first philosophy, cold-start incompatible |

---

## Local Setup

### Prerequisites

- Python 3.11 or later
- An Anthropic API key (for Claude-based orchestration and specialists)
- Git (for cloning the repository)

### Installation

```bash
# Clone the repository
git clone https://github.com/jeremylongshore/oss-agent-lab.git
cd oss-agent-lab

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode (includes all dependencies)
pip install -e .

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your-key-here

# Verify the installation
python -m oss_agent_lab --help
```

### First Run

```bash
# Run a test query through the full pipeline
python -m oss_agent_lab run "test query"

# Run a specific specialist directly
oss-lab run autoresearch "What are the latest advances in test-time compute?"

# Score a repository
python scoring/scorer.py --repo karpathy/autoresearch
```

### Development Setup

For contributors who want to run tests and linting:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run linting
ruff check .

# Run type checking
mypy src/
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml requirements.txt ./
COPY src/ src/
COPY agents/ agents/
COPY scoring/ scoring/

# Install the package
RUN pip install --no-cache-dir -e .

# Create memory directory
RUN mkdir -p /app/data/memory

# Set default environment
ENV OSS_LAB_MEMORY_DIR=/app/data/memory
ENV OSS_LAB_LOG_LEVEL=INFO

ENTRYPOINT ["python", "-m", "oss_agent_lab"]
```

### Building and Running

```bash
# Build the image
docker build -t oss-agent-lab .

# Run with API key passed as environment variable
docker run --rm \
  -e ANTHROPIC_API_KEY=your-key-here \
  -v $(pwd)/data:/app/data \
  oss-agent-lab run "your query here"

# Run as a persistent service (REST API mode)
docker run -d \
  --name oss-agent-lab \
  -e ANTHROPIC_API_KEY=your-key-here \
  -v $(pwd)/data:/app/data \
  -p 8080:8080 \
  oss-agent-lab serve --port 8080
```

### Docker Compose (optional)

```yaml
version: "3.8"

services:
  oss-agent-lab:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OSS_LAB_MEMORY_DIR=/app/data/memory
      - OSS_LAB_LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    ports:
      - "8080:8080"
    command: serve --port 8080
    restart: unless-stopped
```

---

## Google Cloud Run Deployment

Cloud Run is documented as an optional target for users who want managed scaling and a persistent HTTPS endpoint. Nothing in the codebase requires Cloud Run -- this is a convenience path.

### Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- Artifact Registry repository for container images

### Deployment Steps

```bash
# Set your project ID
export PROJECT_ID=your-project-id
export REGION=us-central1

# Build and push the container image
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/oss-agent-lab/app:latest

# Deploy to Cloud Run
gcloud run deploy oss-agent-lab \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/oss-agent-lab/app:latest \
  --region ${REGION} \
  --platform managed \
  --set-env-vars "OSS_LAB_MEMORY_DIR=/tmp/memory,OSS_LAB_LOG_LEVEL=INFO" \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --port 8080 \
  --command "python" \
  --args "-m,oss_agent_lab,serve,--port,8080"
```

### Cloud Run Considerations

- **Cold starts**: With `min-instances=0`, the first request after idle has a cold start of 10-30 seconds. Set `min-instances=1` if latency matters.
- **Memory persistence**: Cloud Run instances are ephemeral. Memory stored in `/tmp` is lost on instance shutdown. For persistent memory, mount a Cloud Storage bucket via Cloud Run volume mounts or use an external database.
- **Secrets**: Use Google Secret Manager for the Anthropic API key. Never pass it as a plain environment variable in production.
- **Costs**: With `max-instances=3` and `min-instances=0`, costs scale to zero when idle.

---

## LLM Flexibility

### Default: Claude via Anthropic SDK

OSS Agent Lab ships with Claude as the default LLM. The conductor, router, and all core orchestration use the Anthropic SDK directly. This is the tested, supported, and recommended path.

### LiteLLM Adapter Layer

Specialists that benefit from a different model (e.g., a specialist wrapping a tool that works better with a specific model) can use the LiteLLM adapter layer. LiteLLM provides a unified interface to 100+ LLM providers with the same API shape.

The adapter is configured at the specialist level, not the orchestration level. The conductor and router always use Claude.

```python
# In a specialist's agent.py, using LiteLLM for a specific task:
from litellm import completion

response = completion(
    model="gpt-4o",  # or any LiteLLM-supported model
    messages=[{"role": "user", "content": prompt}],
)
```

### Model Swapping via Configuration

Users can override the default model for all specialists without touching code:

```yaml
# config.yaml
llm:
  default_model: claude-sonnet-4-20250514
  specialist_overrides:
    autoresearch: claude-sonnet-4-20250514
    stock_analyst: gpt-4o
```

Or via environment variable:

```bash
# Override default model for all specialists
export LITELLM_MODEL=claude-sonnet-4-20250514
```

The orchestration layer (conductor + router) is not affected by `LITELLM_MODEL`. It always uses the Anthropic SDK directly.

---

## Environment Variables

All configuration is done through environment variables or `config.yaml`. Environment variables take precedence over config file values.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | None | Anthropic API key for Claude-based orchestration and specialists. Required for all deployments. |
| `LITELLM_MODEL` | No | None | Override default model for specialist LLM calls. Does not affect conductor or router. Accepts any LiteLLM model identifier. |
| `OSS_LAB_MEMORY_DIR` | No | `~/.oss-agent-lab/memory` | Directory for cognee memory persistence. Must be writable. Created automatically if it does not exist. |
| `OSS_LAB_LOG_LEVEL` | No | `INFO` | Logging level. Accepts: DEBUG, INFO, WARNING, ERROR. DEBUG is verbose and includes LLM request/response logs. |
| `OSS_LAB_CONFIG` | No | `./config.yaml` | Path to config file. If the file does not exist, defaults are used. |
| `OSS_LAB_SCORING_CACHE_DIR` | No | `~/.oss-agent-lab/scoring-cache` | Directory for caching scoring source API responses. Reduces API calls during development. |
| `GITHUB_TOKEN` | No | None | GitHub personal access token. Increases API rate limits for scoring sources and repo-scanner. Not required but recommended. |

---

## Directory Structure at Runtime

After installation and first run, the following directories are created:

```
~/.oss-agent-lab/               # Default data directory
  memory/                       # cognee memory persistence
    knowledge_graph/            # Graph storage
    embeddings/                 # Vector embeddings
    sessions/                   # Session state
  scoring-cache/                # Cached scoring source responses
    github/                     # GitHub API response cache
    hackernews/                 # HN API response cache
    reddit/                     # Reddit API response cache
  logs/                         # Log files (when file logging is enabled)
```

The data directory location is controlled by `OSS_LAB_MEMORY_DIR` (for memory) and `OSS_LAB_SCORING_CACHE_DIR` (for scoring cache). Both can be pointed at the same parent directory or different locations depending on your storage requirements.

---

## Offline Operation

The orchestration layer (conductor, router, specialist dispatch) works offline as long as the Anthropic API is reachable. Specialists that depend on external data sources degrade gracefully:

| Component | Offline Behavior |
|-----------|-----------------|
| Conductor | Fully functional (requires Anthropic API) |
| Router | Fully functional (requires Anthropic API) |
| Specialists (local tools) | Fully functional |
| Specialists (network tools) | Return error with clear message |
| Scoring engine | Uses cached data, skips live fetches |
| Memory layer | Fully functional (local persistence) |

"Offline" here means no internet access beyond the Anthropic API endpoint. The Anthropic API itself is a network dependency that cannot be avoided when using Claude as the LLM.

---

## Troubleshooting

### Common Issues

**`ModuleNotFoundError: No module named 'oss_agent_lab'`**
You are not in the virtual environment or the package is not installed. Run `source .venv/bin/activate && pip install -e .`.

**`anthropic.AuthenticationError: Invalid API key`**
The `ANTHROPIC_API_KEY` environment variable is missing or incorrect. Verify with `echo $ANTHROPIC_API_KEY`.

**`Permission denied: ~/.oss-agent-lab/memory`**
The memory directory is not writable. Set `OSS_LAB_MEMORY_DIR` to a writable path or fix permissions with `chmod -R u+rw ~/.oss-agent-lab`.

**Docker container exits immediately**
Check logs with `docker logs oss-agent-lab`. Most common cause: missing `ANTHROPIC_API_KEY` environment variable.

**Cloud Run returns 503**
Instance is starting up (cold start). Wait 10-30 seconds and retry. If persistent, check Cloud Run logs in the Google Cloud Console for startup errors.

**Scoring engine returns all zeros**
API rate limits have been hit. Set `GITHUB_TOKEN` to increase GitHub rate limits. Check `~/.oss-agent-lab/scoring-cache/` for cached responses.
