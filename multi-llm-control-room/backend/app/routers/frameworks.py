"""Framework execution API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.core.session_manager import session_manager
from app.plugins.crewai_plugin import CrewAIPlugin, CrewAIConfig, EXAMPLE_CREWAI_CONFIG
from app.plugins.langchain_plugin import LangChainPlugin, LangChainConfig, EXAMPLE_LANGCHAIN_CONFIG

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


@router.post("/crewai/execute")
async def execute_crewai(request: Dict[str, Any]):
    """Execute a CrewAI workflow"""
    try:
        session_id = request.get("session_id")
        config_data = request.get("config")
        inputs = request.get("inputs", {})

        if not session_id or not config_data:
            raise HTTPException(status_code=400, detail="session_id and config required")

        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Build model adapter map
        model_adapters = {model.id: adapter for model, adapter in zip(session.model_configs, session.models)}

        # Parse config
        crew_config = CrewAIConfig(
            agents=config_data["agents"],
            tasks=config_data["tasks"],
            process=config_data.get("process", "sequential"),
            verbose=config_data.get("verbose", True)
        )

        # Execute
        plugin = CrewAIPlugin(model_adapters)
        result = await plugin.execute(crew_config, inputs)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/langchain/execute")
async def execute_langchain(request: Dict[str, Any]):
    """Execute a LangChain workflow"""
    try:
        session_id = request.get("session_id")
        config_data = request.get("config")
        inputs = request.get("inputs", {})

        if not session_id or not config_data:
            raise HTTPException(status_code=400, detail="session_id and config required")

        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Build model adapter map
        model_adapters = {model.id: adapter for model, adapter in zip(session.model_configs, session.models)}

        # Parse config
        langchain_config = LangChainConfig(
            chain_type=config_data["chain_type"],
            steps=config_data["steps"],
            input_variables=config_data["input_variables"],
            output_variables=config_data["output_variables"]
        )

        # Execute
        plugin = LangChainPlugin(model_adapters)
        result = await plugin.execute(langchain_config, inputs)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crewai/example")
async def get_crewai_example():
    """Get example CrewAI configuration"""
    return EXAMPLE_CREWAI_CONFIG


@router.get("/langchain/example")
async def get_langchain_example():
    """Get example LangChain configuration"""
    return EXAMPLE_LANGCHAIN_CONFIG


@router.get("/list")
async def list_frameworks():
    """List available frameworks"""
    return {
        "frameworks": [
            {
                "name": "crewai",
                "description": "Multi-agent collaboration framework",
                "capabilities": ["sequential", "hierarchical"],
                "example_endpoint": "/api/frameworks/crewai/example"
            },
            {
                "name": "langchain",
                "description": "Chain-based LLM orchestration",
                "capabilities": ["sequential", "map_reduce", "stuff"],
                "example_endpoint": "/api/frameworks/langchain/example"
            }
        ]
    }
