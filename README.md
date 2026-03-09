# ACP Skilled Worker — AI News Pipeline

A multi-agent demo that uses [ACP (Agent Communication Protocol)](https://agentcommunicationprotocol.dev/) to orchestrate specialized AI agents running in Docker containers. The agents collaborate through [Ollama](https://ollama.com/) to find trending AI news, analyze it, and produce a daily briefing report.

## What It Does

The pipeline runs 4 agents in sequence to produce an AI news briefing:

1. **Topic Scout** — Scrapes RSS feeds (Hacker News, ArXiv, VentureBeat) for AI-related articles, then uses an LLM to rank and select the top 5 trending topics.
2. **Summarizer** — Takes the selected articles and generates concise 2-3 sentence summaries for each.
3. **Sentiment Analyzer** — Classifies each article's sentiment (positive/negative/neutral) and extracts key themes.
4. **Editor** — Assembles all outputs into a polished, formatted Markdown briefing report.

The final report is saved to `output/ai-news-briefing-YYYY-MM-DD.md`.

## Architecture

```
                          ┌──────────────────────┐
                          │   Local Orchestrator │
                          │   (orchestrate.py)   │
                          └──────────┬───────────┘
                                     │ ACP calls (HTTP)
                 ┌───────────────────┼──────────────────┐
                 │                   │                  │
          ┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐
          │ Topic Scout │    │  Summarizer   │   │  Sentiment  │
          │  :8001      │    │  :8002        │   │  Analyzer   │
          └──────┬──────┘    └───────┬───────┘   │  :8003      │
                 │                   │           └──────┬──────┘
                 │                   │                  │
                 │           ┌───────▼───────┐          │
                 │           │    Editor     │◄─────────┘
                 │           │    :8004      │
                 │           └───────┬───────┘
                 │                   │
                 └─────────┬─────────┘
                           │ LLM inference
                    ┌──────▼──────┐
                    │ Ollama Proxy│
                    │   :8080     │
                    └──────┬──────┘
                           │ serialized requests
                    ┌──────▼──────┐
                    │   Ollama    │
                    │   :11434    │
                    └─────────────┘
```

### How ACP Works Here

Each agent is a standalone Python service using the [acp-sdk](https://pypi.org/project/acp-sdk/). The SDK exposes two key endpoints per agent:

- `GET /agents` — Lists available agents and their capabilities
- `POST /runs` — Executes an agent with input messages and returns output

The orchestrator calls each agent sequentially via these REST endpoints, passing the output of one agent as the input to the next.

### The Ollama Concurrency Problem

Ollama is designed to handle one inference request at a time. When multiple agents try to call Ollama simultaneously, requests can fail or queue unpredictably. The **Ollama Proxy** solves this with an `asyncio.Semaphore(1)` — it accepts requests from all agents but forwards them to Ollama one at a time, queuing the rest. Agents don't need to know about this; they just call the proxy as if it were Ollama.

## Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)
- [Python 3.11+](https://www.python.org/downloads/) (for the local orchestrator)
- ~4GB free RAM for Ollama (more for larger models)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/acp-skilled-worker.git
cd acp-skilled-worker
```

### 2. Create Your Environment File

```bash
cp .env.example .env
```

The `.env` file controls which Ollama model all agents use. The default is `llama3.2` (a good balance of speed and quality). Edit it if you want a different model:

```
OLLAMA_MODEL=llama3.2
```

**Model options:**
| Model | Size | Speed | Quality | Best For |
|---|---|---|---|---|
| `llama3.2:1b` | ~1.3GB | Fast | Lower | Quick testing, low-RAM machines |
| `llama3.2` | ~3.8GB | Medium | Good | Default, general use |
| `llama3.1:8b` | ~4.7GB | Slower | Better | Higher quality output |

### 3. Install the Orchestrator Dependency

The local orchestrator needs one Python package:

```bash
pip install httpx
```

Or if you use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
pip install httpx
```

That's it — Docker handles all other dependencies inside the containers.

## Running

### Step 1: Start All Services

```bash
docker compose up --build
```

First run will take a few minutes to build the container images. Subsequent runs are fast.

This launches 6 containers:

| Service | Port | Description |
|---|---|---|
| `ollama` | 11434 | Local LLM server |
| `ollama-proxy` | 8080 | Request queue/serializer |
| `topic-scout` | 8001 | RSS feed scanner + topic ranker |
| `summarizer` | 8002 | Article summarizer |
| `sentiment-analyzer` | 8003 | Sentiment classifier + theme extractor |
| `editor` | 8004 | Report assembler |

Wait until you see all services report as healthy. You can verify with:

```bash
docker compose ps
```

All services should show `Up` and `healthy`.

### Step 2: Pull a Model into Ollama

On first run only — you need to download the LLM model:

```bash
docker compose exec ollama ollama pull llama3.2
```

This downloads the model (~3.8GB). You only need to do this once; the model is persisted in a Docker volume.

### Step 3: Run the Pipeline

Open a **separate terminal** (keep Docker Compose running in the first one):

```bash
python orchestrate.py
```

You'll see the orchestrator call each agent in sequence:

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

The full pipeline takes 2-5 minutes depending on your hardware and model size.

### Step 4: Read the Report

```bash
cat output/ai-news-briefing-*.md
```

Or open the file in any Markdown viewer. Reports are saved with the date in the filename so they don't overwrite each other.

### Stopping

```bash
# Stop all services (Ctrl+C in the docker compose terminal, or):
docker compose down

# Stop and remove the Ollama model data too:
docker compose down -v
```

## Project Structure

```
acp-skilled-worker/
├── docker-compose.yml          # All services in one file
├── orchestrate.py              # Local CLI that drives the pipeline
├── requirements.txt            # Orchestrator dependencies (httpx)
├── .env.example                # Model configuration template
├── output/                     # Generated briefing reports
└── services/
    ├── ollama-proxy/           # FastAPI proxy with async queue
    │   ├── proxy.py
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── topic-scout/            # ACP agent: RSS → trending topics
    │   ├── agent.py
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── summarizer/             # ACP agent: articles → summaries
    │   ├── agent.py
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── sentiment-analyzer/     # ACP agent: text → sentiment + themes
    │   ├── agent.py
    │   ├── Dockerfile
    │   └── requirements.txt
    └── editor/                 # ACP agent: all data → final report
        ├── agent.py
        ├── Dockerfile
        └── requirements.txt
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `llama3.2` | Ollama model used by all agents |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama server URL (proxy config) |
| `REQUEST_TIMEOUT` | `120` | Proxy timeout per request in seconds |

## GPU Support

To enable GPU acceleration for Ollama, uncomment the GPU section in `docker-compose.yml`:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

## Interacting with Agents Directly

Each agent exposes ACP endpoints. You can call them independently:

```bash
# List agents on the topic-scout service
curl http://localhost:8001/agents

# Run the topic scout manually
curl -X POST http://localhost:8001/runs \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "topic_scout",
    "input": [{"role": "user", "parts": [{"content": "{}", "content_type": "application/json"}]}]
  }'
```

## Troubleshooting

**Ollama is slow or OOM:** Try a smaller model (`llama3.2:1b`) or increase Docker's memory limit.

**Agents can't connect to proxy:** Ensure `docker compose up` shows all services healthy. Check with `docker compose ps`.

**RSS feeds return no articles:** The Topic Scout uses public RSS feeds that may rate-limit. Wait a few minutes and retry.

**Model not found:** Make sure you pulled the model: `docker compose exec ollama ollama pull llama3.2`
