# Chapter 13: Integrating MCP with AutoGen

Example demonstrating how to wrap MCP tools for use with AutoGen-style multi-agent systems.

## Code Examples

### `autogen_mcp_integration.py` - AutoGen MCP Integration
A complete example showing MCP tool wrapping, client discovery, and multi-agent conversation.

```bash
python autogen_mcp_integration.py
```

## Features Demonstrated

### DummyMCPServer
- Tool registration with `list_tools()` and `call_tool()`
- `search` tool - Document search with keyword matching
- `analyze` tool - Basic sentiment analysis

### MCPClient
- Automatic tool discovery on initialization
- Tool forwarding to the MCP server

### Multi-Agent Conversation
- `ResearchAgent` - Searches for documents via MCP tools
- `AnalysisAgent` - Analyzes retrieved data via MCP tools
- Sequential agent collaboration pattern

## Expected Output
```
ResearchAgent: searching for 'remote work' via MCP...
ResearchAgent: found documents:
Stanford study: Remote work improves productivity by 13%.
MIT and Microsoft report: company-wide remote work reduces cross-team collaboration.

AnalysisAgent: analyzing data via MCP...
AnalysisAgent: Analysis summary: 1 positive signal(s), 1 negative signal(s).
```

## Key Concepts
- MCP tool wrapping for agent frameworks
- Agent-to-MCP communication patterns
- Multi-agent coordination through shared tools
