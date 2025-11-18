# ⚡ QUICKSTART - Multi-LLM Control Room

Get up and running in **5 minutes**!

## Prerequisites Checklist

- [ ] Docker & Docker Compose installed
- [ ] Ollama running with at least 2 models
  ```bash
  ollama pull llama2
  ollama pull codellama
  ```

## 3 Steps to Launch

### 1️⃣ Start the System
```bash
cd multi-llm-control-room
docker-compose up
```

### 2️⃣ Open Your Browser
- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000/docs**

### 3️⃣ Create Your First Session

1. **Select Routing**: Choose `Broadcast` (all models respond)

2. **Add 2-3 Models**:
   ```
   Provider: ollama
   Model: llama2
   Role: General Assistant
   [+ Add Model]

   Provider: ollama
   Model: codellama
   Role: Coder
   [+ Add Model]
   ```

3. **Click 🚀 Start Session**

4. **Try This Prompt**:
   ```
   Write a Python function to reverse a linked list
   ```

5. **Watch the magic** ✨
   - Both models respond simultaneously
   - See different approaches
   - Compare token usage and responses

## What You Can Do NOW

### Experiment 1: Model Comparison
```
Prompt: "Explain microservices architecture in simple terms"
Pattern: Broadcast
Models: llama2, mistral, codellama
→ See 3 different explanations!
```

### Experiment 2: Specialized Team
```
Prompt: "Build a REST API for a todo app"
Pattern: Coordinator
Models:
  - GPT-4 (Architect) ← Coordinator
  - codellama (Backend Dev)
  - llama2 (Documentation)
→ Watch them collaborate!
```

### Experiment 3: Consensus Building
```
Prompt: "Should I use MongoDB or PostgreSQL for a blog?"
Pattern: Voting
Models: llama2, mistral, codellama
→ They'll debate and vote!
```

## Export Your Session

Click **Export MD** → Perfect for:
- YouTube video descriptions
- GitHub README
- Blog posts
- Documentation

## Troubleshooting

**Backend won't start?**
```bash
docker-compose logs backend
```

**Frontend showing connection error?**
- Check backend is running: `curl http://localhost:8000/health`
- Check Ollama: `curl http://localhost:11434/api/tags`

**Models not responding?**
```bash
# Verify Ollama models
ollama list

# Test Ollama directly
ollama run llama2 "hello"
```

## Next Steps

1. Read [GETTING_STARTED.md](./GETTING_STARTED.md) for advanced features
2. Check [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
3. Try all 4 routing patterns
4. Mix local + cloud models (add Azure/OpenAI keys to `.env`)
5. Record your first YouTube video! 🎥

---

**You're ready! Start collaborating with multiple AI minds! 🧠🧠🧠**
