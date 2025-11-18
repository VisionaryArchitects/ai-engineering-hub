# Getting Started with Multi-LLM Control Room

> Get your AI command center up and running in under 10 minutes! 🚀

## Quick Start (TL;DR)

```bash
# 1. Clone and navigate
cd multi-llm-control-room

# 2. Set up environment
cp .env.example .env

# 3. Start everything
docker-compose up

# 4. Open browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

---

## Prerequisites

### Required
- **Docker** & **Docker Compose** (for containerized setup)
  - OR **Python 3.11+** & **Node.js 20+** (for local development)

### At least ONE local LLM server running
- **Ollama** (easiest): https://ollama.ai
  ```bash
  # Install Ollama, then:
  ollama pull llama2
  ollama pull codellama
  ollama pull mistral
  ```

- **LM Studio**: https://lmstudio.ai (GUI-based, beginner-friendly)

- **Oobabooga Text Generation WebUI**: https://github.com/oobabooga/text-generation-webui

### Optional (for cloud models)
- **OpenAI API Key**: https://platform.openai.com/api-keys
- **Azure OpenAI**: Access via Azure portal
- **Anthropic API Key**: https://console.anthropic.com
- **NVIDIA API Key**: https://build.nvidia.com

---

## Installation

### Option 1: Docker (Recommended)

**Step 1: Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys (optional for local-only setup)
```

**Step 2: Start Services**
```bash
docker-compose up
```

**Step 3: Access the App**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Stop Services**
```bash
docker-compose down
```

---

### Option 2: Local Development

**Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run backend
python -m app.main
# Backend will run on http://localhost:8000
```

**Frontend Setup** (in a new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local if needed

# Run frontend
npm run dev
# Frontend will run on http://localhost:3000
```

---

## Your First Multi-LLM Session

### 1. Set Up Local Models (Ollama Example)

```bash
# Install Ollama from https://ollama.ai

# Pull some models
ollama pull llama2
ollama pull codellama
ollama pull mistral

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 2. Create a Session

1. Open http://localhost:3000
2. Select **Routing Pattern**:
   - **Broadcast**: All models respond to every message (great for comparisons)
   - **Round Robin**: Models take turns (efficient for long conversations)
   - **Coordinator**: One model delegates to specialists (complex workflows)
   - **Voting**: Models vote on best answer (quality filtering)

3. **Add Models** (1-5):
   - Provider: `ollama`
   - Model Name: `llama2`
   - Role: `General Assistant`
   - Click **+ Add Model**

   - Provider: `ollama`
   - Model Name: `codellama`
   - Role: `Coder`
   - Click **+ Add Model**

   - Provider: `ollama`
   - Model Name: `mistral`
   - Role: `Reviewer`
   - Click **+ Add Model**

4. Click **🚀 Start Session**

### 3. Start Chatting!

Try these prompts:

**For General Discussion:**
```
Explain the difference between REST and GraphQL APIs
```

**For Coding:**
```
Write a Python function to calculate Fibonacci numbers with memoization
```

**For Debate/Comparison:**
```
What's the best database for a social media app: PostgreSQL or MongoDB?
Compare the approaches.
```

**For Specialized Collaboration:**
```
Design a microservices architecture for an e-commerce platform.
Architect: high-level design
Coder: sample code for key services
Reviewer: identify potential issues
```

### 4. Watch the Magic Happen

- All active models respond in real-time
- See token usage and costs per response
- Different perspectives and approaches
- Export entire conversations as JSON or Markdown

---

## Configuration Examples

### Example 1: Local-Only Setup (Free!)

```
Routing: Broadcast
Models:
  1. Ollama / llama2 (General)
  2. Ollama / codellama (Coder)
  3. Ollama / mistral (Reviewer)
```

### Example 2: Mixed Local + Cloud

```
Routing: Coordinator
Models:
  1. Azure OpenAI / gpt-4 (Coordinator) ← Delegates tasks
  2. Ollama / codellama (Coder) ← Handles code generation
  3. Ollama / llama2 (Documentation) ← Writes docs
  4. Azure OpenAI / gpt-3.5-turbo (QA) ← Quick reviews
```

### Example 3: All Cloud (Maximum Power)

```
Routing: Voting
Models:
  1. Azure OpenAI / gpt-4
  2. Anthropic / claude-3-opus
  3. OpenAI / gpt-4-turbo
  4. NVIDIA / llama-3.1-405b
```
*Note: This will cost more but gives diverse, high-quality outputs*

---

## Troubleshooting

### Backend Won't Start

**Check Python version:**
```bash
python --version  # Should be 3.11+
```

**Check port 8000 is free:**
```bash
# On macOS/Linux
lsof -i :8000

# On Windows
netstat -ano | findstr :8000
```

**Check logs:**
```bash
docker-compose logs backend
```

### Frontend Won't Start

**Clear Next.js cache:**
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

**Check port 3000 is free:**
```bash
lsof -i :3000
```

### Ollama Connection Issues

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**If using Docker:**
The backend connects to Ollama on your host machine via `host.docker.internal:11434`. This should work automatically on Docker Desktop.

**On Linux Docker**, you may need to update `docker-compose.yml`:
```yaml
services:
  backend:
    environment:
      - OLLAMA_BASE_URL=http://172.17.0.1:11434
```

### WebSocket Connection Failed

**Check CORS settings** in `backend/app/core/config.py`:
```python
cors_origins: List[str] = ["http://localhost:3000"]
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
```

### Model Not Found

**For Ollama**, verify model is pulled:
```bash
ollama list
```

**For LM Studio**, check model is loaded in the UI.

**For cloud providers**, verify API keys in `.env`:
```bash
echo $OPENAI_API_KEY
```

---

## Export & Share Sessions

### Export as JSON (Full Data)
Click **Export JSON** in the Control Room header.

Contains:
- Complete conversation history
- Model configurations
- Token usage & costs
- Timestamps & metadata

### Export as Markdown (YouTube-Ready)
Click **Export MD** for a formatted transcript.

Perfect for:
- GitHub README documentation
- YouTube video descriptions
- Blog posts
- Project documentation

---

## Tips for Great Results

### 1. **Assign Roles**
Give each model a specific role:
- Architect, Coder, Reviewer, Tester
- Frontend, Backend, DevOps
- Creative, Analytical, Critical

### 2. **Use Routing Strategically**
- **Broadcast**: Brainstorming, comparisons
- **Round Robin**: Long conversations, cost optimization
- **Coordinator**: Complex projects with delegation
- **Voting**: Critical decisions requiring consensus

### 3. **Mix Model Strengths**
- Fast local models for drafts
- Premium cloud models for final polish
- Code-specialized models for implementation
- General models for explanation

### 4. **Optimize Costs**
- Use local models when possible (free!)
- Use coordinator pattern to minimize cloud API calls
- Set cost limits in session config
- Monitor real-time cost tracking

### 5. **Record YouTube Content**
- Start with clear problem statement
- Watch models collaborate in real-time
- Highlight interesting disagreements or insights
- Export transcript for video description

---

## What's Next?

### Phase 2 Features (Coming Soon)
- **MCP Server Integration**: Connect to filesystem, databases, web tools
- **CrewAI Integration**: Multi-agent workflows
- **LangChain Support**: Complex chains and RAG
- **Run Dashboard**: Track experiments over time
- **A/B Testing**: Compare routing strategies
- **Persistent Database**: PostgreSQL for history

### Try These Experiments

**1. Code Review Challenge**
- Add 3 models: coder, security expert, performance expert
- Ask coder to write a web scraper
- Have other models review for vulnerabilities and optimization

**2. Architecture Debate**
- Add 3-5 different models
- Ask: "Microservices vs Monolith for a startup"
- Watch them build on each other's arguments

**3. Multi-Language Translation**
- Use models with different training data
- Compare translations of technical documentation
- Find consensus on best phrasing

**4. Full-Stack Project**
- Architect (design)
- Frontend Dev (React code)
- Backend Dev (API code)
- DevOps (Docker setup)
- Reviewer (final check)

---

## Community & Support

- **Issues**: https://github.com/VisionaryArchitects/ai-engineering-hub/issues
- **Docs**: See `ARCHITECTURE.md` for technical details
- **YouTube**: Coming soon - multi-LLM collaboration experiments!

---

## Quick Reference

### Supported Providers
- ✅ Ollama (local)
- ✅ LM Studio (local)
- ✅ Azure OpenAI
- ✅ OpenAI-compatible APIs
- 🚧 Anthropic (coming soon)
- 🚧 NVIDIA NIM (coming soon)
- 🚧 HuggingFace (coming soon)

### Routing Patterns
| Pattern | Use Case | Cost | Speed |
|---------|----------|------|-------|
| Broadcast | Comparison, brainstorming | $$$ | Fast (parallel) |
| Round Robin | Long conversations | $ | Very fast (1 model) |
| Coordinator | Complex delegation | $$ | Medium |
| Voting | Quality consensus | $$$ | Slow (2 rounds) |

### Keyboard Shortcuts
- `Enter`: Send message
- `Ctrl+K`: Clear chat
- `Ctrl+E`: Export session

---

**Ready to build? Let's go! 🚀**
