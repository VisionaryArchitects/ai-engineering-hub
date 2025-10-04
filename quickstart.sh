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
