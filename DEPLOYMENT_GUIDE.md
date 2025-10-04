# AI Engineering Hub - Deployment & Setup Guide 🚀

Welcome to the AI Engineering Hub! This guide will help you deploy and set up this comprehensive collection of AI/ML projects and tutorials.

## 📋 Repository Overview

This repository contains **80+ AI/ML projects** organized into several categories:

### 🎯 Main Project Categories:
- **RAG Systems**: Agentic RAG, Simple RAG, Multimodal RAG, etc.
- **AI Agents**: CrewAI agents, Multi-agent systems, Voice agents
- **Local LLMs**: ChatGPT alternatives, Ollama integrations
- **MCP Tools**: Model Context Protocol implementations
- **Computer Vision**: OCR, Image analysis, Video processing
- **Audio Processing**: Voice agents, Audio analysis
- **Web Scraping**: FireCrawl integrations, Browser automation
- **Content Creation**: AI writers, Content planners

## 🛠️ Prerequisites

Before starting, ensure you have:

- **Python 3.10+** (recommended: Python 3.11)
- **Git** (for cloning and version control)
- **Node.js** (for some MCP servers)
- **Docker** (optional, for containerized deployments)

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd ai-engineering-hub
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv ai-engineering-env

# Activate environment
# On Linux/Mac:
source ai-engineering-env/bin/activate
# On Windows:
ai-engineering-env\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Common Dependencies
```bash
# Install from main requirements file
pip install -r requirements.txt

# Install additional common packages
pip install jupyter notebook streamlit chainlit
```

## 📦 Project-Specific Setup

### 🔥 Popular Projects to Start With:

#### 1. **Local ChatGPT** (`local-chatgpt/`)
Perfect for beginners - a local ChatGPT alternative using Llama 3.2 Vision.

```bash
cd local-chatgpt
pip install pydantic==2.10.1 chainlit ollama

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.2 Vision model
ollama pull llama3.2-vision

# Run the app
chainlit run app.py -w
```

#### 2. **Simple RAG Workflow** (`simple-rag-workflow/`)
Basic RAG implementation using LlamaIndex.

```bash
cd simple-rag-workflow
pip install llama-index ollama

# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.2 model
ollama pull llama3.2

# Start Ollama service
ollama serve

# Run the workflow
jupyter notebook workflow.ipynb
```

#### 3. **Agentic RAG** (`agentic_rag/`)
Advanced RAG with CrewAI and web search fallback.

```bash
cd agentic_rag
pip install crewai crewai-tools chonkie[semantic] markitdown qdrant-client fastembed streamlit

# Get FireCrawl API key from https://www.firecrawl.dev/i/api
# Create .env file with your API key
echo "FIRECRAWL_API_KEY=your-api-key-here" > .env

# Run with DeepSeek
streamlit run app_deep_seek.py

# Or run with Llama 3.2
streamlit run app_llama3.2.py
```

#### 4. **Ultimate AI Assistant** (`ultimate-ai-assitant-using-mcp/`)
MCP-powered assistant with multiple tools.

```bash
cd ultimate-ai-assitant-using-mcp
pip install streamlit python-dotenv langchain-openai langchain-ollama mcp-use asyncio

# Create .env file with API keys
cat > .env << EOF
OPENAI_API_KEY=your-openai-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key
RAGIE_API_KEY=your-ragie-api-key
EOF

# Run the app
streamlit run mcp_streamlit_app.py
```

## 🔧 Environment Setup

### Required API Keys:
Many projects require API keys. Create a `.env` file in the project directory:

```env
# OpenAI (for GPT models)
OPENAI_API_KEY=your-openai-api-key

# FireCrawl (for web scraping)
FIRECRAWL_API_KEY=your-firecrawl-api-key

# Ragie (for multimodal RAG)
RAGIE_API_KEY=your-ragie-api-key

# DeepSeek (alternative to OpenAI)
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### Get API Keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **FireCrawl**: https://www.firecrawl.dev/i/api
- **Ragie**: https://ragie.ai/
- **DeepSeek**: https://platform.deepseek.com/

## 🐳 Docker Deployment (Optional)

Some projects include Docker support:

```bash
# Example for multimodal-rag-assemblyai
cd multimodal-rag-assemblyai
docker-compose up -d
```

## 📚 Learning Path Recommendations

### 🎯 For Beginners:
1. Start with **Local ChatGPT** - simple local LLM setup
2. Try **Simple RAG Workflow** - understand RAG basics
3. Explore **Document Chat RAG** - practical document processing

### 🚀 For Intermediate Users:
1. **Agentic RAG** - advanced RAG with agents
2. **Multi-Agent Systems** - complex agent workflows
3. **MCP Tools** - Model Context Protocol integration

### 🔬 For Advanced Users:
1. **Custom Agent Development** - build your own agents
2. **Multimodal RAG** - handle text, images, audio
3. **Performance Optimization** - fastest RAG implementations

## 🧪 Testing Your Setup

Run these commands to verify your installation:

```bash
# Test Python environment
python --version
pip list

# Test Ollama (if using local models)
ollama list

# Test Streamlit
streamlit hello

# Test Chainlit
chainlit hello
```

## 🆘 Troubleshooting

### Common Issues:

1. **Python Version**: Ensure Python 3.10+ is installed
2. **Virtual Environment**: Always use a virtual environment
3. **API Keys**: Double-check your API keys are correct
4. **Dependencies**: Some packages may require system dependencies
5. **Ollama**: Ensure Ollama is running (`ollama serve`)

### Getting Help:
- Check individual project README files
- Look for `.example` files for configuration templates
- Review error messages carefully
- Ensure all prerequisites are installed

## 🎉 Next Steps

1. **Explore Projects**: Browse different project directories
2. **Read Documentation**: Each project has its own README
3. **Experiment**: Modify code and experiment with different models
4. **Contribute**: Submit improvements and new projects
5. **Join Community**: Connect with other AI engineers

## 📞 Support

- **Issues**: Create GitHub issues for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **Newsletter**: Subscribe for updates and tutorials

Happy coding! 🎉