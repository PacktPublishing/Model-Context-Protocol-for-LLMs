# Chapter 12: MCP and LangChain Integration

Examples demonstrating how MCP integrates with LangChain for document management, tool wrapping, memory, and complete application workflows.

## Code Examples

### `mcp_document_store.py` - MCP Document Store
In-memory MCP server as a document store for retrieval-augmented generation.
```bash
pip install scikit-learn numpy
python mcp_document_store.py
```

### `mcp_langchain_tools.py` - MCP Tools as LangChain Tools
Wrapping MCP tools as LangChain-compatible tools using `MCPToolWrapper`.
```bash
pip install langchain mcp
```
> **Note:** Requires `langchain` and `mcp` packages for actual execution.

### `mcp_langchain_memory.py` - MCP Resource Providers as LangChain Memory
Using MCP resource providers to persist conversation history.

### `langchain_research_workflow.py` - Complete LangChain Application Workflow
Pseudocode demonstrating a research assistant workflow combining MCP document retrieval, tool execution, and memory.
> **Note:** This is pseudocode illustrating the end-to-end workflow pattern.

## Features Demonstrated

### MCP as Document Store
- `DummyMCPServer` with `list_resources()` and `read_resource()`
- TF-IDF vectorizer for document search

### MCP Tools as LangChain Tools
- `MCPToolWrapper` extending LangChain's `Tool` class
- Automatic tool discovery and registration via `register_mcp_tools()`

### MCP as LangChain Memory
- `MemoryMCPServer` for conversation history storage
- Read/write resource interface for context persistence

### Complete Workflow
- Document retrieval → Summarization → Memory storage → Response generation

## Key Concepts
- MCP-LangChain integration patterns
- Tool wrapping and discovery
- Memory persistence through MCP resources
- End-to-end RAG workflows
