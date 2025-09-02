from langchain.tools import Tool
from mcp.client import ClientSession

class MCPToolWrapper(Tool):
    def __init__(self, server_url, tool_name, input_schema):
        super().__init__(name=tool_name, description=input_schema.get('description'))
        self.server_url = server_url
        self.tool_name = tool_name
        self.input_schema = input_schema

    async def __call__(self, **kwargs):
        async with ClientSession(self.server_url) as session:
            await session.initialize()
            # call the MCP tool via JSON-RPC
            result = await session.call_tool(self.tool_name, kwargs)
            return result.content[0].text

# Discover tools and register wrappers
async def register_mcp_tools(client, server_url):
    async with ClientSession(server_url) as session:
        await session.initialize()
        tool_defs = (await session.list_tools()).tools
        for tool_def in tool_defs:
            wrapper = MCPToolWrapper(server_url, tool_def.name, tool_def.inputSchema)
            client.add_tool(wrapper)
