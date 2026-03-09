# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Agent OS** workspace — a system for managing coding standards, specs, and product documentation that works alongside AI tools (Claude Code, Cursor, etc.). It is language/framework agnostic.

The default tech stack profile is React 18 + TypeScript, Tailwind CSS v4, Vite, Node.js/Express, and PostgreSQL (see `agent-os/profiles/default/global/tech-stack.md`).

## Architecture

### Agent OS (`agent-os/`)

- **`commands/agent-os/`** — Slash command definitions (markdown files) that define interactive workflows:
  - `discover-standards` — Extract codebase patterns into documented standards
  - `inject-standards` — Inject relevant standards into context (auto-suggest or explicit mode)
  - `shape-spec` — Structured planning workflow (must run in plan mode)
  - `index-standards` — Rebuild `agent-os/standards/index.yml`
  - `plan-product` — Create mission, roadmap, and tech-stack docs in `agent-os/product/`
- **`profiles/`** — Profiles with inheritable standards. Config in `config.yml` defines default profile and inheritance chains.
- **`scripts/`** — Installation scripts. `project-install.sh` copies commands to `.claude/commands/agent-os/` and standards to `agent-os/standards/`.
- **`standards/`** (created per-project after install) — Project-specific standards with `index.yml` for discovery.
- **`specs/`** (created by shape-spec) — Timestamped spec folders containing plan, shape notes, standards, references, and visuals.
- **`product/`** (created by plan-product) — `mission.md`, `roadmap.md`, `tech-stack.md`.

### Skills (`.agents/skills/`)

Installed skills from external sources. Tracked in `skills-lock.json`.

## Key Conventions

- All commands use `AskUserQuestion` for user interaction — never assume, always ask
- Standards must be concise (bullet points, code examples) to minimize token usage when injected
- Standards index (`index.yml`) uses alphabetized folders/files with one-line descriptions
- Profile inheritance: later profiles override earlier ones; circular dependencies are detected and rejected
- Spec folders use `YYYY-MM-DD-HHMM-{feature-slug}/` naming

## Installation

```bash
# From a project directory (not the agent-os base dir):
./agent-os/scripts/project-install.sh
./agent-os/scripts/project-install.sh --profile <name>
./agent-os/scripts/project-install.sh --commands-only  # skip standards
```
