import asyncio
import json
from typing import Dict, Any, List

from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    INVALID_PARAMS,
)

from .tools import AgentOpsApiToolRegistry

class AgentOpsApiServer:
    """MCP Server for AgentOps API integration."""
    
    def __init__(self, default_api_url: str = "https://api.agentops.ai"):
        """Initialize the AgentOps API server.
        
        Args:
            default_api_url: Default URL for the AgentOps API
        """
        self.server = Server("mcp-agentops-api")
        self.default_api_url = default_api_url
        self.tool_registry = AgentOpsApiToolRegistry(default_api_url)
        
        # Register MCP handlers
        self._list_tools_handler = self.server.list_tools()(self._list_tools)
        self._call_tool_handler = self.server.call_tool()(self._call_tool)
    
    async def _list_tools(self) -> List[Tool]:
        """List available AgentOps API tools."""
        return self.tool_registry.get_tools_list()
    
    async def _call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Call an AgentOps API tool by name with the provided arguments.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent with the tool results
            
        Raises:
            McpError: If the tool is not found or arguments are invalid
        """
        handler = self.tool_registry.get_handler(name)
        if not handler:
            raise McpError(ErrorData(
                code=INVALID_PARAMS,
                message=f"Unknown AgentOps API tool: {name}"
            ))
        
        try:
            result = await handler(arguments)
            return [TextContent(
                type="text",
                text=result
            )]
        except ValueError as e:
            raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    
    async def run(self):
        """Run the AgentOps API MCP server."""
        options = self.server.create_initialization_options()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, options, raise_exceptions=True)

async def serve(default_api_url: str = "https://api.agentops.ai") -> None:
    """Run the AgentOps API MCP server.
    
    Args:
        default_api_url: Default URL for the AgentOps API (can be overridden per-request)
    """
    server = AgentOpsApiServer(default_api_url)
    await server.run()