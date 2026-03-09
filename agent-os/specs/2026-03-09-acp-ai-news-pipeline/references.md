# References for ACP AI News Pipeline

## ACP SDK

- **PyPI:** https://pypi.org/project/acp-sdk/
- **GitHub:** https://github.com/i-am-bee/acp
- **Quickstart:** https://agentcommunicationprotocol.dev/introduction/quickstart
- **Relevance:** Core SDK for building agents — uses `@server.agent()` decorator, async generators for streaming
- **Key patterns:**
  - `Server()` + `@server.agent()` to register agent functions
  - `Message` model for input/output
  - `Context` for session state
  - Server runs on port 8000 by default
  - Client SDK for calling remote agents

## ACP Agent Discovery

- **Docs:** https://agentcommunicationprotocol.dev/core-concepts/agent-discovery
- **Relevance:** How agents find each other in the Docker network
- **Key patterns:**
  - `/agents` endpoint for listing available agents
  - `/runs` endpoint for executing agent tasks
  - Manifest-based discovery for container environments

## Docker Compose for Agents

- **GitHub:** https://github.com/docker/compose-for-agents
- **Docs:** https://docs.docker.com/guides/agentic-ai/
- **Relevance:** Reference architecture for multi-agent Docker Compose setups
- **Key patterns:**
  - Single `compose.yaml` for all services
  - Shared network for inter-agent communication
  - Environment variables for model config

## Ollama API

- **Docs:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **Relevance:** Understanding the API shape the proxy needs to replicate
- **Key patterns:**
  - `POST /api/generate` for text generation
  - `POST /api/chat` for chat completions
  - Streaming responses via newline-delimited JSON
