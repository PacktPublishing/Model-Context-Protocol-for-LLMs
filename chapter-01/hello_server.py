import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create a server instance
server = Server("hello-world-server")

@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="greet",
            description="Generate a personalized greeting",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["formal", "casual", "enthusiastic"],
                        "description": "The style of greeting"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "greet":
        person_name = arguments.get("name", "World")
        style = arguments.get("style", "casual")
        
        greetings = {
            "formal": f"Good day, {person_name}. I hope this message finds you well.",
            "casual": f"Hey {person_name}! How's it going?",
            "enthusiastic": f"Hello there, {person_name}! Great to meet you! 🎉"
        }
        
        greeting = greetings.get(style, greetings["casual"])
        
        return [TextContent(
            type="text",
            text=greeting
        )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main server function."""
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)

if __name__ == "__main__":
    asyncio.run(main())

