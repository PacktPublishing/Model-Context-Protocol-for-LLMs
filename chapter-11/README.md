# Chapter 11: MCP for Retrieval-Augmented Generation

Example demonstrating a simplified RAG system using MCP-style data sources.

## Code Examples

### `mcp_rag_system.py` - MCP RAG System
A self-contained RAG system that simulates MCP servers using in-memory dictionaries.

```bash
python mcp_rag_system.py
```

## Features Demonstrated

### MCPRAGSystem
- Multiple data source registration (simulating MCP server connections)
- Jaccard similarity-based document retrieval
- Response generation from retrieved context

### RAG Pipeline
- Document ingestion from multiple sources
- Query-based relevance scoring
- Context-augmented response generation

## Expected Output
```
Retrieved information: [{'source': 'server1', 'uri': 'doc2', ...}, ...]
Generated response: Based on the available information:
...
Summary: The query 'What does MCP do in RAG systems?' is related to X document(s)...
```

## Key Concepts
- Retrieval-Augmented Generation with MCP
- Multi-source document retrieval
- Similarity-based relevance scoring
