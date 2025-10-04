#!/bin/bash

# AI Engineering Hub - Automated Setup Script
# This script sets up the development environment for the AI Engineering Hub

set -e  # Exit on any error

echo "🚀 AI Engineering Hub - Automated Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.10+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
            print_success "Python version is compatible (3.10+)"
        else
            print_error "Python 3.10+ is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.10+ first."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "ai-engineering-env" ]; then
        python3 -m venv ai-engineering-env
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source ai-engineering-env/bin/activate
    print_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "Pip upgraded"
}

# Install requirements
install_requirements() {
    print_status "Installing common dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Install Ollama
install_ollama() {
    print_status "Checking Ollama installation..."
    if command -v ollama &> /dev/null; then
        print_success "Ollama is already installed"
    else
        print_status "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        print_success "Ollama installed"
    fi
}

# Install Node.js (for MCP servers)
install_nodejs() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_status "Installing Node.js..."
        # Install Node.js using NodeSource repository
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        print_success "Node.js installed"
    fi
}

# Create environment template
create_env_template() {
    print_status "Creating environment template..."
    cat > .env.template << EOF
# AI Engineering Hub - Environment Variables Template
# Copy this file to .env and fill in your API keys

# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your-openai-api-key-here

# FireCrawl API Key (for web scraping)
FIRECRAWL_API_KEY=your-firecrawl-api-key-here

# Ragie API Key (for multimodal RAG)
RAGIE_API_KEY=your-ragie-api-key-here

# DeepSeek API Key (alternative to OpenAI)
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Google API Key (for Gemini models)
GOOGLE_API_KEY=your-google-api-key-here
EOF
    print_success "Environment template created (.env.template)"
}

# Create quick start script
create_quickstart() {
    print_status "Creating quick start script..."
    cat > quickstart.sh << 'EOF'
#!/bin/bash

# AI Engineering Hub - Quick Start Script
# This script helps you quickly start popular projects

echo "🚀 AI Engineering Hub - Quick Start"
echo "==================================="

# Activate virtual environment
source ai-engineering-env/bin/activate

echo "Available projects:"
echo "1. Local ChatGPT (local-chatgpt/)"
echo "2. Simple RAG Workflow (simple-rag-workflow/)"
echo "3. Agentic RAG (agentic_rag/)"
echo "4. Ultimate AI Assistant (ultimate-ai-assitant-using-mcp/)"
echo "5. Document Chat RAG (document-chat-rag/)"
echo ""

read -p "Enter project number (1-5): " choice

case $choice in
    1)
        echo "Starting Local ChatGPT..."
        cd local-chatgpt
        ollama pull llama3.2-vision
        chainlit run app.py -w
        ;;
    2)
        echo "Starting Simple RAG Workflow..."
        cd simple-rag-workflow
        ollama pull llama3.2
        ollama serve &
        jupyter notebook workflow.ipynb
        ;;
    3)
        echo "Starting Agentic RAG..."
        cd agentic_rag
        streamlit run app_deep_seek.py
        ;;
    4)
        echo "Starting Ultimate AI Assistant..."
        cd ultimate-ai-assitant-using-mcp
        streamlit run mcp_streamlit_app.py
        ;;
    5)
        echo "Starting Document Chat RAG..."
        cd document-chat-rag
        jupyter notebook document_chat_rag.ipynb
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        ;;
esac
EOF
    chmod +x quickstart.sh
    print_success "Quick start script created (quickstart.sh)"
}

# Main setup function
main() {
    echo ""
    print_status "Starting setup process..."
    echo ""
    
    # Check prerequisites
    check_python
    
    # Create and activate virtual environment
    create_venv
    activate_venv
    
    # Upgrade pip and install requirements
    upgrade_pip
    install_requirements
    
    # Install additional tools
    install_ollama
    install_nodejs
    
    # Create helper files
    create_env_template
    create_quickstart
    
    echo ""
    print_success "Setup completed successfully! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.template to .env and add your API keys"
    echo "2. Run './quickstart.sh' to start a project"
    echo "3. Read DEPLOYMENT_GUIDE.md for detailed instructions"
    echo ""
    echo "Happy coding! 🚀"
}

# Run main function
main "$@"