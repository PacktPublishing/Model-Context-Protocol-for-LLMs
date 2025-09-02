# Chapter 5: MCP Architecture Overview

Examples demonstrating MCP's architecture including client-server interactions, JSON-RPC communication, and security concepts.

## Code Examples

### `mcp_architecture.py` - Architecture Demonstration
A minimal but complete example illustrating MCP's architectural concepts.

```bash
# Run main architecture demo
python mcp_architecture.py

# Show JSON-RPC message examples
python mcp_architecture.py --messages

# Show security concepts
python mcp_architecture.py --security

# Run all demonstrations
python mcp_architecture.py --all
```

## Features Demonstrated

### SimpleMCPServer
- Resources (company_docs, employee_handbook, technical_specs)
- Tools (search, summarize, translate)
- Prompts (document_analysis, query_assistant)
- JSON-RPC request handling
- Capability negotiation via `initialize`

### SimpleMCPClient
- Connection initialization
- Capability discovery
- Resource reading
- Tool execution
- Prompt retrieval

### JSON-RPC Message Formats
- Request messages
- Response messages
- Error messages

### Security Concepts
- Authentication (bearer tokens)
- Request metadata (_meta field)
- Audit logging

## Expected Output
```
🏗️  MCP Architecture Demonstration
==================================================

1️⃣  Initializing Connection:
Server: SimpleMCPServer
Protocol Version: 2024-11-05
Capabilities: {"resources": {"listChanged": true}, ...}

2️⃣  Capability Discovery:
📚 Available Resources:
  - company_docs: Company documentation and policies
  - employee_handbook: Employee handbook and HR policies
  - technical_specs: Technical specifications and API documentation

🔧 Available Tools:
  - search: Search through available resources
  - summarize: Summarize a document or text
  - translate: Translate text to another language

💬 Available Prompts:
  - document_analysis: Analyze a document for key insights
  - query_assistant: Help formulate effective search queries

... (more demo output)

==================================================
✅ Architecture demonstration complete!
```

## Key Concepts
- Client-server architecture
- JSON-RPC 2.0 message format
- Capability discovery and negotiation
- Transport-agnostic communication
- Security layers (authentication, audit logging)
