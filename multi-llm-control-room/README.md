# Multi-LLM Control Room

> **Production-Ready AI Orchestration Platform** - Collaborate with up to 5 LLMs simultaneously from 7 different providers!

[![Status](https://img.shields.io/badge/status-production%20ready-success)]()
[![Phase](https://img.shields.io/badge/phase-2%20complete-blue)]()
[![Version](https://img.shields.io/badge/version-0.2.0-brightgreen)]()

## 🚀 What Is This?

The Multi-LLM Control Room is a **production-ready web application** that lets you orchestrate multiple AI models from different providers in a single collaborative session. Think of it as your personal "mission control" for AI development, content creation, and experimentation.

### ⚡ Quick Facts

- 🎯 **Up to 5 LLMs** running simultaneously
- 🔌 **7 Providers** supported (local + cloud)
- 🤖 **2 Frameworks** integrated (CrewAI, LangChain)
- 🔧 **MCP Tools** for real-world capabilities
- 💾 **PostgreSQL** persistence
- 💰 **Real-time cost** tracking
- 📤 **Export** to JSON/Markdown
- 🐳 **Docker** ready

---

## 🎯 Key Features

### Multi-Model Chat
- Run **1-5 LLMs simultaneously** in one conversation
- **Real-time streaming** responses
- **Role-based** specialization (Architect, Coder, Reviewer, etc.)
- **Mix local and cloud** models in one session

### 7 Provider Support
- **Local (FREE)**: Ollama, LM Studio, OpenAI-compatible
- **Cloud**: Azure OpenAI, Anthropic Claude, NVIDIA NIM, HuggingFace
- **Cost tracking** for all providers
- **Health monitoring** and fallbacks

### 4 Routing Patterns
- **Broadcast**: All models respond (great for comparisons)
- **Round-Robin**: Models take turns (cost-efficient)
- **Coordinator**: One model delegates tasks (smart workflows)
- **Voting**: Models vote on best answer (consensus)

### Framework Integration
- **CrewAI**: Multi-agent workflows with role-based agents
- **LangChain**: Sequential chain processing
- **MCP**: Tool access (filesystem, web search, databases)

### Session Management
- **Create, pause, resume** sessions
- **Export** conversations (JSON, Markdown)
- **Replay** previous sessions
- **Cost limits** and budget tracking

---

## 🚦 Quick Start (5 Minutes!)

### Prerequisites
- Docker & Docker Compose
- At least one LLM server running (Ollama recommended)

### Installation

```bash
# 1. Navigate to project
cd multi-llm-control-room

# 2. Copy environment template
cp .env.example .env

# 3. Start everything!
docker-compose up
```

### Access the App
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### First Session

1. Open http://localhost:3000
2. Select **Broadcast** routing
3. Add 2-3 models:
   - Ollama / llama2 / "General"
   - Ollama / codellama / "Coder"
4. Click **🚀 Start Session**
5. Send a prompt: "Write a Python function to reverse a linked list"
6. Watch multiple models collaborate!

📖 **[Full Setup Guide →](./GETTING_STARTED.md)**
⚡ **[5-Min Quick Start →](./QUICKSTART.md)**

---

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| **[GETTING_STARTED.md](./GETTING_STARTED.md)** | Complete setup & configuration |
| **[QUICKSTART.md](./QUICKSTART.md)** | 5-minute quick start |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Technical deep-dive (31KB) |
| **[PHASE2_FEATURES.md](./PHASE2_FEATURES.md)** | Phase 2 capabilities |
| **[PROJECT_INVENTORY.md](./PROJECT_INVENTORY.md)** | Complete status report |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Frontend (Next.js + TypeScript)   │
│   • Control Room UI                 │
│   • Real-time chat                  │
│   • Model configuration             │
└─────────────┬───────────────────────┘
              │ WebSocket + REST API
┌─────────────┴───────────────────────┐
│   Backend (FastAPI + Python)        │
│   ├─ Session Manager                │
│   ├─ Message Routers (4 patterns)   │
│   ├─ Model Adapters (7 providers)   │
│   ├─ Framework Plugins (CrewAI, LC) │
│   └─ MCP Server Manager             │
└─────────────┬───────────────────────┘
              │
┌─────────────┴───────────────────────┐
│   Data Layer                        │
│   ├─ PostgreSQL (conversations)     │
│   ├─ Redis (sessions, cache)        │
│   └─ Alembic (migrations)           │
└─────────────────────────────────────┘
```

---

## 🎬 Use Cases

### 1️⃣ YouTube Content Creation
Run multi-LLM collaborations and export full transcripts for video descriptions!

**Example**: "3 AI Models Build a REST API"
- Model 1: Architect (designs structure)
- Model 2: Coder (implements)
- Model 3: Reviewer (finds bugs)
→ Export as Markdown for video description!

### 2️⃣ Model Comparison
Compare GPT-4, Claude, and Llama side-by-side for any task!

### 3️⃣ Cost Optimization
Mix expensive cloud models with free local models strategically.

### 4️⃣ Complex Workflows
Use CrewAI or LangChain to build multi-step AI pipelines.

### 5️⃣ Tool-Augmented LLMs
Give models filesystem access, web search, database queries via MCP!

---

## 🔌 Supported Providers

| Provider | Type | Cost | Status |
|----------|------|------|--------|
| **Ollama** | Local | FREE | ✅ |
| **LM Studio** | Local | FREE | ✅ |
| **Azure OpenAI** | Cloud | Paid | ✅ |
| **Anthropic Claude** | Cloud | Paid | ✅ Phase 2 |
| **NVIDIA NIM** | Cloud | Paid | ✅ Phase 2 |
| **HuggingFace** | Cloud | Free+Paid | ✅ Phase 2 |
| **Generic HTTP** | Any | Varies | ✅ |

**Total: 7 Providers** (mix and match any combination!)

---

## 🤖 Frameworks & Tools

### Agent Frameworks
- ✅ **CrewAI** - Multi-agent collaboration
- ✅ **LangChain** - Sequential chains
- 🔜 **n8n** - Visual workflows (Phase 3)

### MCP (Model Context Protocol)
- ✅ Filesystem operations
- ✅ Web search (Brave)
- ✅ GitHub integration
- ✅ Database queries (PostgreSQL)

---

## 🎮 Routing Patterns

### Broadcast
All models respond to every message.
- **Use for**: Comparisons, brainstorming
- **Cost**: $$$ (all models run)
- **Speed**: Fast (parallel)

### Round-Robin
Models take turns responding.
- **Use for**: Long conversations, cost savings
- **Cost**: $ (one model at a time)
- **Speed**: Very fast

### Coordinator
One model delegates to specialists.
- **Use for**: Complex projects, role-based workflows
- **Cost**: $$ (coordinator + selected models)
- **Speed**: Medium

### Voting
Models vote on best answer.
- **Use for**: Quality consensus, critical decisions
- **Cost**: $$$ (2 rounds: propose + vote)
- **Speed**: Slower

---

## 📊 Project Status

### ✅ Phase 1 - MVP (COMPLETE)
- ✅ Multi-model chat interface
- ✅ 3 providers (Ollama, LM Studio, Azure)
- ✅ 4 routing patterns
- ✅ WebSocket real-time
- ✅ Cost tracking
- ✅ Export functionality

### ✅ Phase 2 - Expansion (COMPLETE)
- ✅ +4 providers (Anthropic, NVIDIA, HuggingFace, Generic)
- ✅ CrewAI integration
- ✅ LangChain integration
- ✅ MCP server manager
- ✅ PostgreSQL persistence
- ✅ Alembic migrations

### 🔜 Phase 3 - Advanced (PLANNED)
- ⏳ Analytics dashboard
- ⏳ Run comparison (A/B testing)
- ⏳ n8n integration
- ⏳ Custom MCP servers
- ⏳ Multi-user support

---

## 💻 Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **WebSocket**: Native FastAPI
- **Database**: PostgreSQL + SQLAlchemy + asyncpg
- **Migrations**: Alembic 1.13.1
- **AI Frameworks**: CrewAI 0.28.0, LangChain 0.1.0
- **MCP**: mcp 0.9.0

### Frontend
- **Framework**: Next.js 14.1.0
- **Language**: TypeScript
- **State**: Zustand 4.5.0
- **Styling**: Tailwind CSS 3.3.0
- **WebSocket**: Native browser API

### Infrastructure
- **Containers**: Docker + Docker Compose
- **Observability**: Prometheus-ready
- **Deployment**: Kubernetes-ready

---

## 📈 Stats

- **Total Files**: 46
- **Lines of Code**: ~4,000
- **Model Adapters**: 9
- **API Endpoints**: 15+
- **Routing Patterns**: 4
- **Frameworks**: 2
- **Documentation**: 5 guides

---

## 🎥 YouTube Content Ideas

### Video Ideas with This Platform

1. **"Claude vs GPT-4 vs Llama - LIVE BATTLE"**
   - 3 models, same prompt, compare results!

2. **"AI Team Builds Full App (CrewAI)"**
   - 5 agents collaborate to build complete project

3. **"LLMs With REAL TOOLS (MCP Demo)"**
   - Models read files, search web, query databases

4. **"7 AI Models Code Together"**
   - All providers in one session!

5. **"Sequential AI Pipeline (LangChain)"**
   - Watch different models handle each stage

---

## 🚀 Deployment

### Local Development
```bash
docker-compose up
```

### Production (Example with Docker)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
Dockerfiles are production-ready. K8s manifests coming in Phase 3!

---

## 🔐 Security

### Implemented
- ✅ Environment variable secrets
- ✅ CORS configuration
- ✅ Input sanitization
- ✅ Error handling

### Recommended
- ⏳ JWT authentication
- ⏳ Rate limiting
- ⏳ HTTPS in production
- ⏳ API key rotation

---

## 📞 Support

### Documentation
- [Getting Started](./GETTING_STARTED.md)
- [Architecture](./ARCHITECTURE.md)
- [Phase 2 Features](./PHASE2_FEATURES.md)

### Issues
GitHub Issues: `VisionaryArchitects/ai-engineering-hub`

---

## 📜 License

MIT License - See [LICENSE](../LICENSE)

---

## 🙏 Credits

Built with love for AI engineers, developers, and content creators who want to push the boundaries of multi-model orchestration!

**Repository**: VisionaryArchitects/ai-engineering-hub
**Project**: multi-llm-control-room
**Status**: Production Ready ✅
**Version**: 0.2.0
**Phase**: 2 Complete 🎉

---

**Ready to orchestrate? `docker-compose up` and let's go! 🚀**
