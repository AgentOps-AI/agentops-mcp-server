# AgentOps API MCP Server

An MCP (Model Coordination Protocol) server that allows LLM agents to interact with the AgentOps API for accessing trace data.

## Overview

This MCP server provides tools for agents to:

- List recent traces from their AgentOps project
- Get detailed information about specific traces

The server handles authentication and communication with the AgentOps API, making it easy for agents to access their trace data.

## Authentication Flow

The server uses a secure two-step authentication process:

1. The agent provides their AgentOps API key with each request
2. The server exchanges this API key for a JWT token from the AgentOps API
3. The server uses this JWT token to make authenticated requests to the AgentOps API
4. All responses are passed back to the agent in their raw form

This ensures that API keys are never stored between requests, and each request is authenticated securely with a JWT token.

## Available Tools

### `list_traces`

Lists the most recent traces from the agent's project.

**Parameters:**
- `AGENTOPS_API_KEY` (required): The agent's AgentOps API key
- `limit` (optional): Maximum number of traces to return (default: 5)
- `AGENTOPS_API_URL` (optional): Custom API URL for non-production environments

**Response:**
- List of traces with trace ID, number of spans, start/end time
- Total number of traces in the database
- Traces sorted by creation timestamp (most recent first)

### `trace_detail`

Gets detailed information about a specific trace.

**Parameters:**
- `AGENTOPS_API_KEY` (required): The agent's AgentOps API key
- `trace_id` (required): The trace ID to retrieve details for (from the `trace_id` field in `list_traces` response)
- `AGENTOPS_API_URL` (optional): Custom API URL for non-production environments

**Response:**
- Detailed information about the trace
- All spans associated with the trace
- Metadata, timing information, etc.

## Usage

### Using with Claude Coder (Recommended)

This MCP server is designed to work with Claude Coder. Follow these steps to set it up:

1. **Configure Claude Coder**

   Add this to your Claude Coder configuration file (typically `~/.config/claude-cli/config.yaml`):

   ```yaml
   mcp_servers:
     - name: agentops-api
       path: /ABSOLUTE/PATH/TO/mcp/agentops-api/bin/run-server
       description: "AgentOps API integration for accessing trace data"
   ```

   Replace `/ABSOLUTE/PATH/TO` with the actual path to this repository.

2. **Use with Claude Coder**

   ```bash
   # Run Claude with the AgentOps API MCP server enabled
   claude --mcp agentops-api
   
   # Or for a single command
   claude --mcp agentops-api "List my recent traces. My API key is xyz123"
   ```

3. **In your prompts to Claude, include your AgentOps API key:**

   ```
   Can you show me my recent traces? Find my agentops api key in my user .env file. 
   ```

### Running Standalone

If you need to run the server directly:

```bash
# Using the convenience script
./bin/run-server

# Or using Python directly
uv run -m mcp_server_agentops_api
```

The server uses the production AgentOps API at `https://api.agentops.ai` by default. Agents can override this URL on a per-request basis.

### Available Tool Calls

When using the MCP server through Claude, these are the tools it can use:

```
# List recent traces
list_traces(AGENTOPS_API_KEY="your-api-key", limit=10)

# Get details for a specific trace
trace_detail(AGENTOPS_API_KEY="your-api-key", trace_id="148dac266d95c9dc0b5616320b8488c9")

# Using a custom API URL (e.g., for local development)
list_traces(AGENTOPS_API_KEY="your-api-key", AGENTOPS_API_URL="http://localhost:8000")
```

## Architecture

The code is organized into three main components:

1. **Client (`client.py`)**: Handles communication with the AgentOps API, including authentication
2. **Tools (`tools.py`)**: Defines the tools available to agents and processes tool requests
3. **Server (`server.py`)**: Implements the MCP server that agents interact with

Each request is stateless, with no user data stored between requests, and raw API responses are returned directly to the agent.

## Docker

```bash
# Build and run the Docker container
docker build -t mcp-server-agentops-api .
docker run mcp-server-agentops-api
```

## Future Enhancements

- Additional AgentOps API tools (metrics, spans, etc.)
- Support for filtering and searching traces
- Batch operations for improved performance
- Caching of JWT tokens for a short period