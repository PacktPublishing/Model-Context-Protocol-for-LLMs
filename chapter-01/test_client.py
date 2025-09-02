import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_hello_server():
    """Test our hello world server."""
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["hello_server.py"]
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test the greet tool with different styles
            test_cases = [
                {"name": "Alice", "style": "formal"},
                {"name": "Bob", "style": "casual"},
                {"name": "Charlie", "style": "enthusiastic"},
                {"name": "Diana"}  # No style specified
            ]
            
            for args in test_cases:
                print(f"\nCalling greet with args: {args}")
                result = await session.call_tool("greet", args)
                for content in result.content:
                    print(f"Response: {content.text}")

if __name__ == "__main__":
    asyncio.run(test_hello_server())

