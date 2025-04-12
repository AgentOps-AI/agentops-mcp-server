import json
from typing import Dict, Any, List, Callable, Awaitable, Optional
from mcp.types import Tool

from .client import AgentOpsApiClient, ListTraces, TraceDetail

class AgentOpsApiToolRegistry:
    """Registry of tools for the AgentOps API MCP server."""
    
    def __init__(self, default_api_url: str = "https://api.agentops.ai"):
        """Initialize the AgentOps API tool registry.
        
        Args:
            default_api_url: Default URL for the AgentOps API
        """
        self.default_api_url = default_api_url
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[str]]] = {}
        
        # Define tool descriptions with proper formatting
        list_traces_desc = """
        List traces from AgentOps API.
        
        Returns the most recent traces from your project, including:
        - Trace ID, number of spans, start time, and end time
        - Total number of traces in the database
        
        This tool requires:
        - AGENTOPS_API_KEY: Your AgentOps API authentication key
        
        Optional parameters:
        - AGENTOPS_API_URL: Override the default API endpoint (default: {})
        """.format(self.default_api_url)
        
        trace_detail_desc = """
        Get detailed information about a specific trace from AgentOps API.
        
        Returns complete information about a trace, including:
        - All spans in the trace
        - Detailed metadata
        - Timing information
        
        This tool requires:
        - AGENTOPS_API_KEY: Your AgentOps API authentication key
        - trace_id: The trace ID to retrieve (from the trace_id field in list_traces response)
        
        Optional parameters:
        - AGENTOPS_API_URL: Override the default API endpoint (default: {})
        """.format(self.default_api_url)
        
        # Register available tools
        self._register_tool(
            name="list_traces",
            description=list_traces_desc,
            schema=self._get_list_traces_schema(),
            handler=self._handle_list_traces
        )
        
        self._register_tool(
            name="trace_detail",
            description=trace_detail_desc,
            schema=self._get_trace_detail_schema(),
            handler=self._handle_trace_detail
        )
    
    def _get_list_traces_schema(self) -> Dict[str, Any]:
        """Get the schema for list_traces with added API key parameter.
        
        Returns:
            Tool input schema
        """
        schema = ListTraces.model_json_schema()
        
        # Add AGENTOPS_API_KEY as a required parameter and AGENTOPS_API_URL as optional
        properties = schema.get("properties", {})
        
        # Define property descriptions with proper formatting
        api_key_desc = """
        AgentOps API key for authentication.
        This key is required for all API requests.
        """
        
        api_url_desc = """
        Optional custom URL for AgentOps API.
        Use this to override the default endpoint when connecting to a non-production server.
        Default: {}
        """.format(self.default_api_url)
        
        properties["AGENTOPS_API_KEY"] = {
            "type": "string",
            "description": api_key_desc
        }
        
        properties["AGENTOPS_API_URL"] = {
            "type": "string",
            "description": api_url_desc,
            "default": self.default_api_url
        }
        
        required = schema.get("required", [])
        if "required" not in schema:
            schema["required"] = []
        schema["required"].append("AGENTOPS_API_KEY")
        
        return schema
        
    def _get_trace_detail_schema(self) -> Dict[str, Any]:
        """Get the schema for trace_detail with added API key parameter.
        
        Returns:
            Tool input schema
        """
        schema = TraceDetail.model_json_schema()
        
        # Add AGENTOPS_API_KEY as a required parameter and AGENTOPS_API_URL as optional
        properties = schema.get("properties", {})
        
        # Define property descriptions with proper formatting
        api_key_desc = """
        AgentOps API key for authentication.
        This key is required for all API requests.
        """
        
        api_url_desc = """
        Optional custom URL for AgentOps API.
        Use this to override the default endpoint when connecting to a non-production server.
        Default: {}
        """.format(self.default_api_url)
        
        properties["AGENTOPS_API_KEY"] = {
            "type": "string",
            "description": api_key_desc
        }
        
        properties["AGENTOPS_API_URL"] = {
            "type": "string",
            "description": api_url_desc,
            "default": self.default_api_url
        }
        
        required = schema.get("required", [])
        if "required" not in schema:
            schema["required"] = []
        schema["required"].append("AGENTOPS_API_KEY")
        
        return schema
    
    def _register_tool(self, name: str, description: str, schema: Dict[str, Any], 
                       handler: Callable[[Dict[str, Any]], Awaitable[str]]) -> None:
        """Register an AgentOps API tool.
        
        Args:
            name: Tool name
            description: Tool description
            schema: Tool input schema
            handler: Tool handler function
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "schema": schema
        }
        self._handlers[name] = handler
    
    def get_tools_list(self) -> List[Tool]:
        """Get the list of available AgentOps API tools.
        
        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name=info["name"],
                description=info["description"],
                inputSchema=info["schema"]
            )
            for info in self._tools.values()
        ]
    
    def get_handler(self, name: str) -> Optional[Callable[[Dict[str, Any]], Awaitable[str]]]:
        """Get an AgentOps API tool handler by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool handler function or None if not found
        """
        return self._handlers.get(name)
    
    async def _handle_list_traces(self, arguments: Dict[str, Any]) -> str:
        """Handle the list_traces tool for AgentOps API.
        
        Args:
            arguments: Tool arguments including AGENTOPS_API_KEY
            
        Returns:
            Formatted result as a string
            
        Raises:
            ValueError: If arguments are invalid
        """
        # Extract API key and URL
        api_key = arguments.pop("AGENTOPS_API_KEY", None)
        api_url = arguments.pop("AGENTOPS_API_URL", self.default_api_url)
        
        if not api_key:
            raise ValueError("AGENTOPS_API_KEY is required")
        
        # Create a client with the provided API key and URL
        client = AgentOpsApiClient(api_key, api_url)
        
        # Process the request
        args = ListTraces(**arguments)
        result = await client.list_traces(args.limit)
        
        # Return the raw response
        return result
        
    async def _handle_trace_detail(self, arguments: Dict[str, Any]) -> str:
        """Handle the trace_detail tool for AgentOps API.
        
        Args:
            arguments: Tool arguments including AGENTOPS_API_KEY and trace_id
            
        Returns:
            Formatted result as a string
            
        Raises:
            ValueError: If arguments are invalid
        """
        # Extract API key and URL
        api_key = arguments.pop("AGENTOPS_API_KEY", None)
        api_url = arguments.pop("AGENTOPS_API_URL", self.default_api_url)
        
        if not api_key:
            raise ValueError("AGENTOPS_API_KEY is required")
        
        # Create a client with the provided API key and URL
        client = AgentOpsApiClient(api_key, api_url)
        
        # Process the request
        args = TraceDetail(**arguments)
        result = await client.trace_detail(args.trace_id)
        
        # Return the raw response
        return result