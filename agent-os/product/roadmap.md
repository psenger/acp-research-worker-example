# Product Roadmap

## Phase 1: MVP

- **ACP Agent Containers** — 3-4 specialized agents each running in their own Docker container, communicating via ACP:
  - **Topic Scout** — Discovers trending AI news topics from configured sources
  - **Summarizer** — Reads and condenses articles into concise summaries
  - **Sentiment Analyzer** — Evaluates tone and sentiment of AI news stories
  - **Editor** — Assembles findings into a coherent daily AI news briefing report
- **Ollama Queue/Proxy** — A request serialization layer in front of Ollama to handle the single-request concurrency limitation, queuing inference requests from multiple agents
- **Local Orchestrator** — A local agent (Claude or CLI-based) that dispatches tasks to the ACP agents, coordinates the pipeline flow, and collects the final AI trending news report
- **Docker Compose Setup** — Single `docker-compose up` to launch the full agent fleet, Ollama proxy, and supporting infrastructure

## Phase 2: Post-Launch

- **Web Dashboard** — A web UI to visualize agent communication in real-time, monitor pipeline status, and browse generated AI news briefings
