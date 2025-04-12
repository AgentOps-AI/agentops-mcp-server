from .server import serve

# Default API endpoint
DEFAULT_API_URL = "https://api.agentops.ai"

def main():
    """MCP AgentOps API Server - Integration with AgentOps API for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="Provide MCP tools for interacting with the AgentOps API"
    )
    parser.add_argument("--api-url", type=str, default=DEFAULT_API_URL, 
                        help=f"Base URL for AgentOps API (default: {DEFAULT_API_URL})")
    
    args = parser.parse_args()
    
    print(f"Starting AgentOps API MCP server with API URL: {args.api_url}")
    asyncio.run(serve(args.api_url))


if __name__ == "__main__":
    main()