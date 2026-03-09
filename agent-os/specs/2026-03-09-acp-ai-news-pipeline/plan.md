# ACP AI News Pipeline — Plan

## Task 1: Save Spec Documentation
Create `agent-os/specs/2026-03-09-acp-ai-news-pipeline/` with plan.md, shape.md, references.md.

## Task 2: Project Scaffold
- Create directory structure:
  ```
  services/
  ├── ollama-proxy/
  ├── topic-scout/
  ├── summarizer/
  ├── sentiment-analyzer/
  └── editor/
  ```
- Each service gets: `agent.py`, `Dockerfile`, `requirements.txt`
- Python >= 3.11

## Task 3: Ollama Queue/Proxy
- FastAPI service with `asyncio.Queue` serializing Ollama requests
- Exposes `/v1/generate` endpoint matching Ollama's API shape
- Agents call the proxy instead of Ollama directly
- Proxy forwards requests one at a time, queuing the rest

## Task 4: Topic Scout Agent
- ACP agent using `@server.agent()` from `acp-sdk`
- Discovers trending AI news via RSS feeds (Hacker News, TechCrunch AI, ArXiv)
- Returns topics with titles, URLs, brief descriptions
- Uses Ollama (via proxy) to rank/filter for relevant AI topics

## Task 5: Summarizer Agent
- ACP agent accepting article URLs/text
- Uses Ollama (via proxy) to generate concise summaries
- Returns structured summaries per article

## Task 6: Sentiment Analyzer Agent
- ACP agent accepting article text/summaries
- Uses Ollama (via proxy) to classify sentiment and extract themes
- Returns sentiment scores and theme tags

## Task 7: Editor Agent
- ACP agent receiving all pipeline outputs
- Uses Ollama (via proxy) to assemble polished daily briefing
- Outputs formatted markdown report

## Task 8: Docker Compose
- Single `docker-compose.yml`: ollama, ollama-proxy, topic-scout, summarizer, sentiment-analyzer, editor
- Ollama official image with GPU passthrough
- All agents depend on ollama-proxy
- Shared Docker network for ACP communication

## Task 9: Local Orchestrator
- Python CLI (`orchestrate.py`) that:
  1. Calls Topic Scout → get trending AI topics
  2. Passes topics → Summarizer
  3. Passes summaries → Sentiment Analyzer
  4. Sends all → Editor
  5. Saves final briefing to `output/`
- Uses `acp-sdk` client for ACP communication
