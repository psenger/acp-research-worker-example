# Tech Stack

## Agents

- Python (FastAPI or Flask) for each ACP agent service
- ACP SDK for agent-to-agent communication
- Ollama Python client for LLM inference

## Infrastructure

- Docker + Docker Compose for container orchestration
- Ollama (local LLM server)
- Custom request queue/proxy (Python) to serialize Ollama requests

## Local Orchestrator

- Claude Code or Python CLI as the local dispatching agent

## Database

- N/A for MVP (agents communicate via ACP messages; briefings stored as files)
