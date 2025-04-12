from typing import Dict, Any, Optional
import httpx
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR
from pydantic import BaseModel, Field
from typing import Annotated

# Define the AgentOps API models
class ListTraces(BaseModel):
    """Parameters for listing AgentOps API traces.
    
    The response includes:
    - List of traces with trace ID, number of spans, start time, and end time
    - Total number of traces for this project in the database
    - Traces are sorted by creation timestamp (most recent first)
    """
    limit: Annotated[int, Field(
        default=5,
        description="Maximum number of traces to return",
        gt=0,
        lt=100
    )]

class TraceDetail(BaseModel):
    """Parameters for retrieving a specific trace from AgentOps API.
    
    The response includes:
    - Detailed information about the trace
    - All spans associated with the trace
    - Metadata, start time, end time, etc.
    """
    trace_id: Annotated[str, Field(
        description="Trace ID to retrieve details for (from trace_id field in list_traces response)"
    )]

class AgentOpsApiClient:
    """Client for the AgentOps API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.agentops.ai"):
        """Initialize the AgentOps API client.
        
        Args:
            api_key: AgentOps API key
            base_url: Base URL for the AgentOps API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.jwt_token = None
        self.project_id = None
    
    async def _get_auth_token(self) -> None:
        """Get a JWT token from the AgentOps API using the API key.
        
        Raises:
            McpError: If authentication fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v3/auth/token",
                    json={"api_key": self.api_key},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                self.jwt_token = data.get("token")
                self.project_id = data.get("project_id")
                
                if not self.jwt_token:
                    raise McpError(ErrorData(
                        code=INTERNAL_ERROR,
                        message="Failed to get JWT token from AgentOps API: No token in response"
                    ))
            except httpx.HTTPError as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to authenticate with AgentOps API: {e!r}"
                ))
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests, including authorization.
        
        Returns:
            Headers dictionary with Authorization and Content-Type
            
        Raises:
            McpError: If authentication fails
        """
        if not self.jwt_token:
            await self._get_auth_token()
            
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
    
    async def list_traces(self, limit: int = 5) -> str:
        """List traces from the AgentOps API.
        
        Retrieves a list of traces from the project, sorted by creation time (most recent first).
        
        Args:
            limit: Maximum number of traces to return
            
        Returns:
            Raw API response text
            
        Raises:
            McpError: If the API request fails
        """
        params = {"limit": limit}
        
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/v4/traces",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to list AgentOps API traces: {e!r}"
                ))
                
    async def trace_detail(self, trace_id: str) -> str:
        """Get detailed information about a specific trace.
        
        Retrieves complete information about a trace, including all spans.
        
        Args:
            trace_id: The trace ID to retrieve details for (from trace_id field in list_traces response)
            
        Returns:
            Raw API response text
            
        Raises:
            McpError: If the API request fails
        """
        if not trace_id:
            raise ValueError("trace_id is required")
        
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/v4/traces/{trace_id}",
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to get trace detail for {trace_id}: {e!r}"
                ))