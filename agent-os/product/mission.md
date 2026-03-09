# Product Mission

## Problem

Running multiple AI agents that need to collaborate is difficult — especially with local LLMs like Ollama that aren't designed for concurrent requests. There's no easy way to spin up a fleet of specialized agents in containers, have them communicate via ACP (Agent Communication Protocol), and orchestrate them from a local agent. Developers lack a hands-on reference for how ACP-based multi-agent systems work in practice.

## Target Users

Personal learning and exploration — a reference project for understanding ACP-based multi-agent orchestration with local LLMs.

## Solution

A Docker Compose-based demo platform where multiple specialized agents run in separate containers, communicate via ACP, and collaborate through Ollama (with a request queue/proxy to handle concurrency). The demo scenario is an **AI News Pipeline**: agents work together to find trending AI news, analyze sentiment, summarize articles, and produce a polished daily briefing report. A local orchestrator agent (Claude or CLI) dispatches tasks to the ACP agents and collects the final output.
