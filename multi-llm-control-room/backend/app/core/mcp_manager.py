"""MCP (Model Context Protocol) Server Manager"""
import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess


@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPServer:
    """MCP server instance"""
    name: str
    command: List[str]
    tools: List[MCPTool]
    process: Optional[asyncio.subprocess.Process] = None
    available: bool = False


class MCPServerManager:
    """Manage MCP servers and expose tools to models"""

    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}

    async def register_server(self, name: str, command: List[str]) -> bool:
        """Register and start an MCP server"""
        try:
            # Start server process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Initialize server
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "multi-llm-control-room",
                        "version": "0.1.0"
                    }
                }
            }

            # Send initialize request
            process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()

            # Read response
            response_line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=5.0
            )

            if not response_line:
                raise Exception("No response from server")

            response = json.loads(response_line.decode())

            # List tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }

            process.stdin.write((json.dumps(list_tools_request) + "\n").encode())
            await process.stdin.drain()

            tools_response = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=5.0
            )

            tools_data = json.loads(tools_response.decode())

            # Parse tools
            tools = []
            if "result" in tools_data and "tools" in tools_data["result"]:
                for tool_def in tools_data["result"]["tools"]:
                    tools.append(MCPTool(
                        name=tool_def["name"],
                        description=tool_def["description"],
                        input_schema=tool_def.get("inputSchema", {})
                    ))

            # Store server
            self.servers[name] = MCPServer(
                name=name,
                command=command,
                tools=tools,
                process=process,
                available=True
            )

            print(f"✅ MCP Server '{name}' registered with {len(tools)} tools")
            return True

        except Exception as e:
            print(f"❌ Failed to register MCP server '{name}': {e}")
            if process:
                process.terminate()
                await process.wait()
            return False

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool on an MCP server"""
        server = self.servers.get(server_name)

        if not server or not server.available:
            raise ValueError(f"MCP server '{server_name}' not available")

        try:
            # Call tool request
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }

            server.process.stdin.write((json.dumps(call_request) + "\n").encode())
            await server.process.stdin.drain()

            # Read response
            response_line = await asyncio.wait_for(
                server.process.stdout.readline(),
                timeout=30.0
            )

            response = json.loads(response_line.decode())

            if "error" in response:
                raise Exception(response["error"]["message"])

            return response.get("result", {})

        except Exception as e:
            raise Exception(f"MCP tool call failed: {str(e)}")

    def get_tool_schemas_for_model(self, server_names: List[str]) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for specified servers"""
        schemas = []

        for server_name in server_names:
            server = self.servers.get(server_name)
            if not server or not server.available:
                continue

            for tool in server.tools:
                schemas.append({
                    "type": "function",
                    "function": {
                        "name": f"{server_name}:{tool.name}",
                        "description": tool.description,
                        "parameters": tool.input_schema
                    }
                })

        return schemas

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all registered servers"""
        return [
            {
                "name": server.name,
                "available": server.available,
                "tools": len(server.tools),
                "tool_names": [t.name for t in server.tools]
            }
            for server in self.servers.values()
        ]

    async def shutdown_server(self, name: str):
        """Shutdown an MCP server"""
        server = self.servers.get(name)
        if server and server.process:
            server.process.terminate()
            await server.process.wait()
            server.available = False

    async def shutdown_all(self):
        """Shutdown all MCP servers"""
        for name in list(self.servers.keys()):
            await self.shutdown_server(name)


# Global MCP manager instance
mcp_manager = MCPServerManager()


# Pre-configured MCP servers
MCP_SERVER_CONFIGS = {
    "filesystem": {
        "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "description": "Access filesystem operations"
    },
    "brave_search": {
        "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
        "description": "Web search via Brave Search API"
    },
    "github": {
        "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
        "description": "GitHub repository operations"
    },
    "postgres": {
        "command": ["npx", "-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/db"],
        "description": "PostgreSQL database operations"
    },
}
