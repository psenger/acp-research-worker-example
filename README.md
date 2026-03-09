# ACP Skilled Worker

**A multi-agent AI news pipeline powered by [ACP](https://agentcommunicationprotocol.dev/), [Ollama](https://ollama.com/), and Docker.**

Four specialized agents — each running in its own container — collaborate to discover trending AI news, summarize articles, analyze sentiment, and produce a polished daily briefing. A local orchestrator drives the pipeline, and a custom proxy solves Ollama's single-request concurrency limitation.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [The Agents](#the-agents)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Pipeline](#running-the-pipeline)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [GPU Support](#gpu-support)
- [Interacting with Agents Directly](#interacting-with-agents-directly)
- [Troubleshooting](#troubleshooting)
- [How ACP Works](#how-acp-works)
- [License](#license)

---

## Overview

This project demonstrates how to build a real multi-agent system using the [Agent Communication Protocol (ACP)](https://agentcommunicationprotocol.dev/) — an open standard for agent interoperability developed by the Linux Foundation.

**What happens when you run the pipeline:**

1. The **orchestrator** (a local Python script) sends a task to the first agent
2. Each agent processes its input, calls Ollama for LLM inference, and returns structured output
3. Output flows from one agent to the next: discovery, summarization, analysis, editing
4. The final agent produces a Markdown briefing saved to `output/`

All agent-to-agent communication uses ACP's REST-based protocol (`/agents` for discovery, `/runs` for execution).

---

## Architecture

```
 YOU
  │
  │  python orchestrate.py
  ▼
┌────────────────────────────────────────────────────────────────┐
│                        Local Machine                           │
│                                                                │
│  orchestrate.py ─── ACP calls (HTTP) ──┐                       │
│                                        │                       │
└────────────────────────────────────────┼───────────────────────┘
                                         │
┌────────────────────────────────────────┼───────────────────────┐
│  Docker Compose Network                │                       │
│                                        ▼                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Topic Scout  │  │  Summarizer  │  │  Sentiment   │          │
│  │    :8001     │  │    :8002     │  │  Analyzer    │          │
│  │              │  │              │  │    :8003     │          │
│  │  RSS feeds   │  │  Condense    │  │              │          │
│  │  + LLM rank  │  │  articles    │  │  Classify +  │          │
│  └──────┬───────┘  └──────┬───────┘  │  tag themes  │          │
│         │                 │          └──────┬───────┘          │
│         │                 │                 │                  │
│         │          ┌──────▼───────┐         │                  │
│         │          │   Editor     │◄────────┘                  │
│         │          │    :8004     │                            │
│         │          │              │                            │
│         │          │  Assemble    │                            │
│         │          │  briefing    │                            │
│         │          └──────┬───────┘                            │
│         │                 │                                    │
│         └────────┬────────┘                                    │
│                  │  LLM inference requests                     │
│           ┌──────▼───────┐                                     │
│           │ Ollama Proxy │  Serializes concurrent requests     │
│           │    :8080     │  via asyncio.Semaphore(1)           │
│           └──────┬───────┘                                     │
│                  │  One request at a time                      │
│           ┌──────▼───────┐                                     │
│           │    Ollama    │  Local LLM inference                │
│           │   :11434     │  (llama3.2 by default)              │
│           └──────────────┘                                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Why the Ollama Proxy?

Ollama processes one inference request at a time. When multiple agents call Ollama concurrently, requests fail or behave unpredictably. The proxy sits between all agents and Ollama, using an `asyncio.Semaphore(1)` to serialize requests — agents submit freely, the proxy queues and forwards one at a time. Agents are unaware of this; they call the proxy exactly as they would call Ollama directly.

---

## The Agents

| Agent | Port | Input | Output | What It Does |
|---|---|---|---|---|
| **Topic Scout** | 8001 | Trigger request | JSON array of articles | Fetches RSS feeds (ArXiv, Google News), parses entries, and uses Ollama to rank the top 5 trending AI topics |
| **Summarizer** | 8002 | JSON array of articles | JSON array with summaries | Takes each article and generates a concise 2-3 sentence summary via Ollama |
| **Sentiment Analyzer** | 8003 | JSON array with summaries | JSON array with sentiment + themes | Classifies sentiment (positive/negative/neutral) and extracts keyword themes for each article |
| **Editor** | 8004 | JSON array with full analysis | Markdown report | Assembles all data into a polished daily AI news briefing with executive summary and theme highlights |

Each agent is a standalone Python service built with the [acp-sdk](https://pypi.org/project/acp-sdk/) and runs in its own Docker container.

---

## Prerequisites

Before you begin, make sure you have:

| Requirement | Version | Why |
|----|----|----|
| [Docker Desktop](https://docs.docker.com/get-docker/) | 4.0+ | Runs all agent containers and Ollama |
| [Python](https://www.python.org/downloads/) | 3.11+ | Runs the local orchestrator script |
| Free RAM | ~4GB minimum | Ollama needs memory for the LLM model |
| Free Disk | ~5GB | For Docker images + Ollama model weights |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/acp-skilled-worker.git
cd acp-skilled-worker
```

### 2. Set up the environment file

```bash
cp .env.example .env
```

The `.env` file controls which Ollama model all agents use:

```
OLLAMA_MODEL=llama3.2
```

**Available models:**

| Model | Download Size | Speed | Quality | Best For |
|---|---|---|---|---|
| `llama3.2:1b` | ~1.3 GB | Fast | Lower | Quick testing, low-RAM machines |
| `llama3.2` | ~3.8 GB | Medium | Good | **Default — recommended** |
| `llama3.1:8b` | ~4.7 GB | Slower | Better | Higher quality output |

### 3. Set up the local orchestrator

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

---

## Running the Pipeline

### Step 1 — Start all services

```bash
docker compose up --build -d
```

> First run builds all container images (~2-3 minutes). Subsequent starts are near-instant.

Verify everything is healthy:

```bash
docker compose ps
```

Expected output — all services show **Up** and **healthy**:

```
NAME                      STATUS
ollama-1                  Up (healthy)
ollama-proxy-1            Up (healthy)
topic-scout-1             Up
summarizer-1              Up
sentiment-analyzer-1      Up
editor-1                  Up
```

### Step 2 — Download the LLM model

> **This step is required before your first run.** Without a model, the pipeline will complete but produce an empty report.

```bash
docker compose exec ollama ollama pull llama3.2
```

This downloads ~3.8 GB. You only need to do this **once** — the model is persisted in a Docker volume across restarts.

Confirm the model is ready:

```bash
docker compose exec ollama ollama list
```

You should see `llama3.2` (or whichever model you configured in `.env`).

### Step 3 — Run the pipeline

```bash
python orchestrate.py
```

Output:

```
============================================================
  AI News Pipeline — ACP Orchestrator
============================================================

[1/4] Calling Topic Scout agent...
  Received topics.

[2/4] Calling Summarizer agent...
  Received summaries.

[3/4] Calling Sentiment Analyzer agent...
  Received sentiment analysis.

[4/4] Calling Editor agent...
  Received final briefing.

============================================================
  Briefing saved to: output/ai-news-briefing-2026-03-09.md
============================================================
```

The full pipeline takes **2-5 minutes** depending on your hardware and model.

### Step 4 — Read your briefing

```bash
cat output/ai-news-briefing-*.md
```

Or open the file in any Markdown viewer/editor. Reports include the date in the filename so they accumulate without overwriting.

### Stopping the services

```bash
# Stop all containers:
docker compose down

# Stop and delete the downloaded model (frees ~4 GB):
docker compose down -v
```

---

## Project Structure

```
acp-skilled-worker/
│
├── docker-compose.yml            # Defines all 6 services and networking
├── orchestrate.py                # Local CLI — drives the agent pipeline
├── requirements.txt              # Python dependencies for the orchestrator
├── .env.example                  # Template for model configuration
│
├── services/
│   ├── ollama-proxy/             # Request serializer for Ollama
│   │   ├── proxy.py              # FastAPI app with semaphore-based queue
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── topic-scout/              # Agent: RSS feeds → ranked AI topics
│   │   ├── agent.py              # ACP agent using @server.agent()
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── summarizer/               # Agent: articles → concise summaries
│   │   ├── agent.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── sentiment-analyzer/       # Agent: text → sentiment + themes
│   │   ├── agent.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── editor/                   # Agent: all data → Markdown report
│       ├── agent.py
│       ├── Dockerfile
│       └── requirements.txt
│
└── output/                       # Generated briefing reports land here
```

---

## Configuration

All configuration is through environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2` | The Ollama model all agents use for inference |

These are set internally in `docker-compose.yml` and generally don't need changing:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama server URL (used by the proxy) |
| `OLLAMA_PROXY_URL` | `http://ollama-proxy:8080` | Proxy URL (used by agents) |
| `REQUEST_TIMEOUT` | `120` | Max seconds per Ollama request |

---

## GPU Support

By default, Ollama runs on CPU. To enable GPU acceleration (NVIDIA only), uncomment the deploy section in `docker-compose.yml` under the `ollama` service:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

This requires the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

For Apple Silicon Macs, Ollama uses Metal acceleration automatically — no configuration needed.

---

## Interacting with Agents Directly

Each agent exposes standard ACP endpoints. You can call them independently without the orchestrator.

**List available agents:**

```bash
curl -s http://localhost:8001/agents | python -m json.tool
```

**Run an agent manually:**

```bash
curl -s -X POST http://localhost:8001/runs \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "topic_scout",
    "input": [{
      "role": "user",
      "parts": [{"content": "{}", "content_type": "application/json"}]
    }]
  }' | python -m json.tool
```

**Agent endpoints reference:**

| Endpoint | Method | Description |
|---|---|---|
| `/agents` | GET | List registered agents and their metadata |
| `/runs` | POST | Create a new run (execute an agent) |
| `/runs/{run_id}` | GET | Check the status of a run |

---

## Troubleshooting

### Pipeline completes but the report is empty

The model is not loaded. Run:

```bash
docker compose exec ollama ollama list
```

If no models are listed, pull one:

```bash
docker compose exec ollama ollama pull llama3.2
```

### `Connection refused` when running the orchestrator

The Docker services aren't running. Start them:

```bash
docker compose up --build -d
docker compose ps   # verify all are healthy
```

### Agents crash with `LoopSetupType` error

Version mismatch between `acp-sdk` and `uvicorn`. The agent `requirements.txt` files pin `uvicorn<0.34.0` to prevent this. If you see this error, rebuild:

```bash
docker compose build --no-cache
docker compose up -d
```

### Ollama is slow or runs out of memory

- Switch to a smaller model: set `OLLAMA_MODEL=llama3.2:1b` in `.env` and restart
- Increase Docker Desktop memory: Settings > Resources > Memory (recommend 6 GB+)
- Enable GPU support (see [GPU Support](#gpu-support))

### RSS feeds return no articles

The Topic Scout uses public RSS feeds (ArXiv, Google News) that may rate-limit or block requests from certain networks. Check the logs:

```bash
docker compose logs topic-scout --tail=30
```

If feeds show `entries: 0`, the feeds may be temporarily unavailable. Wait a few minutes and retry.

### Viewing agent logs

```bash
# All services:
docker compose logs -f

# Specific service:
docker compose logs -f topic-scout
docker compose logs -f ollama-proxy
```

---

## How ACP Works

[ACP (Agent Communication Protocol)](https://agentcommunicationprotocol.dev/) is an open standard for AI agent interoperability. Key concepts used in this project:

- **Agents** are registered with the `@server.agent()` decorator from `acp-sdk`
- **Runs** represent a single execution of an agent — created via `POST /runs`
- **Messages** carry structured data between agents using typed parts (JSON, Markdown, plain text)
- **Discovery** happens via `GET /agents`, which returns metadata about available agents

Each agent in this project is a standalone HTTP service. The orchestrator doesn't import any agent code — it communicates purely through ACP's REST API. This means agents can be written in any language, swapped out independently, or scaled horizontally.

**Learn more:**
- [ACP Documentation](https://agentcommunicationprotocol.dev/introduction/welcome)
- [ACP Quickstart](https://agentcommunicationprotocol.dev/introduction/quickstart)
- [acp-sdk on PyPI](https://pypi.org/project/acp-sdk/)
- [ACP GitHub](https://github.com/i-am-bee/acp)

---

## License

This project is for personal learning and exploration. See [LICENSE](LICENSE) for details.
