"""MCP server management API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any

from app.core.mcp_manager import mcp_manager, MCP_SERVER_CONFIGS

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


@router.post("/servers/register")
async def register_mcp_server(request: Dict[str, Any]):
    """Register and start an MCP server"""
    try:
        name = request.get("name")
        command = request.get("command")

        if not name or not command:
            raise HTTPException(status_code=400, detail="name and command required")

        success = await mcp_manager.register_server(name, command)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to register server")

        return {"status": "success", "server": name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/list")
async def list_mcp_servers():
    """List all registered MCP servers"""
    return {
        "servers": mcp_manager.list_servers()
    }


@router.get("/servers/presets")
async def get_mcp_presets():
    """Get pre-configured MCP server options"""
    return {
        "presets": [
            {
                "name": name,
                "command": config["command"],
                "description": config["description"]
            }
            for name, config in MCP_SERVER_CONFIGS.items()
        ]
    }


@router.post("/servers/{server_name}/tools/call")
async def call_mcp_tool(server_name: str, request: Dict[str, Any]):
    """Call a tool on an MCP server"""
    try:
        tool_name = request.get("tool")
        arguments = request.get("arguments", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="tool name required")

        result = await mcp_manager.call_tool(server_name, tool_name, arguments)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/servers/{server_name}")
async def shutdown_mcp_server(server_name: str):
    """Shutdown an MCP server"""
    try:
        await mcp_manager.shutdown_server(server_name)
        return {"status": "shutdown", "server": server_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/schemas")
async def get_tool_schemas(server_names: List[str]):
    """Get OpenAI-compatible tool schemas for specified servers"""
    try:
        schemas = mcp_manager.get_tool_schemas_for_model(server_names)
        return {"schemas": schemas}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
