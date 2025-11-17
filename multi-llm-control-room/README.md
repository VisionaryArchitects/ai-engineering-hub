# Multi-LLM Control Room

> Your AI Development Command Center - Orchestrate up to 5 LLMs simultaneously for collaborative problem-solving, experimentation, and content creation.

## Overview

The Multi-LLM Control Room is a comprehensive web application that enables you to run multiple AI models from different providers (Ollama, Azure OpenAI, NVIDIA, HuggingFace, etc.) in a single collaborative session. Think of it as a "mission control" for AI orchestration.

### Key Features

- **Multi-Model Chat**: Run up to 5 LLMs simultaneously in one conversation
- **Flexible Routing**: Broadcast, coordinator, round-robin, or voting patterns
- **Provider Agnostic**: Mix local (Ollama, LM Studio) and cloud (Azure, NVIDIA) models
- **Framework Integration**: Plug in CrewAI, LangChain, n8n, MCP servers
- **Full Reproducibility**: Save and replay entire experiments
- **YouTube Ready**: Track episodes with metadata, transcripts, shareable configs
- **Cost Tracking**: Real-time token usage and cost monitoring
- **Observable**: Complete telemetry, logs, and metrics

## Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd multi-llm-control-room

# Install dependencies (coming soon)
# npm install
# pip install -r requirements.txt

# Start services with Docker Compose (coming soon)
# docker-compose up
```

## Documentation

- **[Architecture Blueprint](./ARCHITECTURE.md)** - Complete system design and technical specifications
- **[Getting Started](./GETTING_STARTED.md)** *(coming soon)* - Setup and configuration guide
- **[API Documentation](./API.md)** *(coming soon)* - REST API and WebSocket endpoints
- **[Database Schema](./DATABASE_SCHEMA.md)** *(coming soon)* - Data models and migrations
- **[UI Specifications](./UI_SPECIFICATIONS.md)** *(coming soon)* - Screen layouts and components

## Architecture at a Glance

```
Frontend (Next.js)
    ↓ WebSocket + REST
Orchestrator API (FastAPI)
    ├─ Model Connectors (Ollama, Azure, NVIDIA, etc.)
    ├─ Framework Plugins (CrewAI, LangChain, MCP)
    └─ Data Layer (PostgreSQL, Redis, S3)
```

## Use Cases

### 1. Multi-Model Comparison
Compare responses from GPT-4, Claude, Llama, and DeepSeek side-by-side

### 2. Specialized Agent Teams
Create role-based teams: Architect + Coder + Reviewer, each using optimal models

### 3. YouTube Content Creation
Run reproducible experiments with full transcripts and shareable configs

### 4. Cost Optimization
Mix expensive cloud models with free local models strategically

### 5. Framework Experimentation
Test CrewAI agents with different model combinations

## Supported Providers

- ✅ Ollama (local)
- ✅ LM Studio (local)
- ✅ Oobabooga/Text-Generation-WebUI (local)
- ✅ Azure OpenAI / Azure AI Foundry
- ✅ NVIDIA NIM
- ✅ Hugging Face Inference API
- ✅ Generic HTTP API (bring your own)

## Supported Frameworks

- ✅ CrewAI
- ✅ LangChain
- ✅ n8n
- ✅ MCP (Model Context Protocol) Servers
- ✅ Direct API (no framework)

## Routing Patterns

1. **Broadcast**: All models respond to every message
2. **Coordinator**: One model delegates to specialists
3. **Round-Robin**: Models take turns responding
4. **Voting**: Models propose answers and vote on the best

## Development Roadmap

### Phase 0: MVP (Current)
- [ ] Basic multi-model chat (Ollama + OpenAI)
- [ ] Broadcast routing
- [ ] Simple UI

### Phase 1: Core Features
- [ ] All provider adapters
- [ ] All routing patterns
- [ ] Cost tracking
- [ ] Authentication

### Phase 2: Frameworks
- [ ] CrewAI integration
- [ ] LangChain integration
- [ ] MCP server manager

### Phase 3: YouTube Features
- [ ] Run tracking
- [ ] Export/replay
- [ ] Shareable configs

### Phase 4: Pro Lab
- [ ] Custom routing
- [ ] A/B testing
- [ ] Grafana dashboards
- [ ] Multi-user support

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python), Celery, Pydantic
- **Database**: PostgreSQL, Redis
- **Storage**: MinIO/S3
- **Observability**: Prometheus, Grafana, Loki
- **Deployment**: Docker, Docker Compose, Kubernetes-ready

## Contributing

This project is currently in the design/planning phase. Contributions welcome once MVP is released!

See [CONTRIBUTING.md](./CONTRIBUTING.md) *(coming soon)* for guidelines.

## License

[MIT License](../LICENSE)

## Project Status

🚧 **Status**: Architecture & Design Phase

The complete architecture blueprint is available in [ARCHITECTURE.md](./ARCHITECTURE.md). Implementation starting soon!

## Contact

For questions or collaboration opportunities, please open an issue.

---

**Built for AI engineers, developers, and content creators who want to push the boundaries of multi-model orchestration.**
