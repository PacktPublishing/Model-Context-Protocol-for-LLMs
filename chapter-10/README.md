# Chapter 10: MCP and Multi-Agent Systems

Example demonstrating MCP integration with multi-agent frameworks using an AutoGen-inspired pattern.

## Code Examples

### `multi_agent_mcp.py` - Multi-Agent MCP Integration
A complete example showing multiple specialized agents coordinating through an MCP client-server architecture.

```bash
python multi_agent_mcp.py
```

## Features Demonstrated

### MCP Server Simulation
- `DummyServer` exposing tools via `list_tools()` and `call_tool()`
- Async tool execution with simulated latency

### MCP Client
- Tool discovery and forwarding
- Unified interface for agent-server communication

### Specialized Agents
- `ResearchAgent` - Gathers external data (weather)
- `AnalysisAgent` - Performs text analysis (sentiment)

### Orchestration
- Parallel task execution using `asyncio.gather()`
- Agent coordination through shared MCP client

## Expected Output
```
Weather Result: Current weather in New York: sunny and warm
Sentiment Result: Sentiment analysis of 'This is a great day!' shows positive mood
```

## Key Concepts
- Multi-agent system architecture with MCP
- Async agent coordination patterns
- Shared tool access through MCP client
