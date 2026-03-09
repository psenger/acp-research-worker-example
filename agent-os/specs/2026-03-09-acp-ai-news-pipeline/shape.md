# ACP AI News Pipeline — Shaping Notes

## Scope

Build a Docker Compose-based demo platform where 4 specialized ACP agents collaborate to produce an AI trending news briefing report. Agents communicate via ACP (Agent Communication Protocol), use Ollama for LLM inference through a shared queue/proxy, and are orchestrated by a local CLI script.

### Agents
- **Topic Scout** — Discovers trending AI news from RSS/web sources
- **Summarizer** — Condenses articles into concise summaries
- **Sentiment Analyzer** — Evaluates tone and extracts themes
- **Editor** — Assembles everything into a polished daily briefing

### Infrastructure
- Ollama Queue/Proxy to serialize concurrent LLM requests
- Docker Compose for single-command deployment
- Local orchestrator (Python CLI) to drive the pipeline

## Decisions

- **ACP SDK (`acp-sdk`)** for agent registration and communication — uses `@server.agent()` decorator pattern
- **FastAPI** for the Ollama proxy service (lightweight, async-native)
- **asyncio.Queue** pattern for Ollama request serialization — simple, no external dependencies
- **RSS feeds** as primary news source for Topic Scout (no API keys required for MVP)
- **Python >= 3.11** required by acp-sdk
- **No database** for MVP — agents communicate via ACP messages, final reports saved as files

## Context

- **Visuals:** None
- **References:** No existing code in this codebase; ACP SDK quickstart and Docker Compose for Agents examples used as reference
- **Product alignment:** Directly implements Phase 1 MVP from roadmap — all 4 agents, Ollama proxy, Docker Compose, local orchestrator

## Standards Applied

- No project standards defined yet (index.yml is empty)
