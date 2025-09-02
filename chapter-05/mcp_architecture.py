#!/usr/bin/env python3
"""
MCP Architecture Overview - Chapter 5
Demonstrates MCP architecture concepts including:
- Client-server architecture
- Core components (resources, tools, prompts)
- Standardized primitives (JSON-RPC)
- Communication mechanisms
- Message formats and protocols
- Security and authentication framework
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


# ============================================================================
# JSON-RPC Message Examples (from Chapter 5)
# ============================================================================

# Example MCP Request Message
EXAMPLE_REQUEST = {
    "jsonrpc": "2.0",
    "id": "request-123",
    "method": "tools/call",
    "params": {
        "name": "search_documents",
        "arguments": {
            "query": "quarterly financial results",
            "limit": 10
        }
    }
}

# Example MCP Response Message
EXAMPLE_RESPONSE = {
    "jsonrpc": "2.0",
    "id": "request-123",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Found 3 documents matching your query..."
            }
        ]
    }
}

# Example MCP Error Message
EXAMPLE_ERROR = {
    "jsonrpc": "2.0",
    "id": "request-123",
    "error": {
        "code": -32000,
        "message": "Tool execution failed",
        "data": {
            "details": "Authentication required for this operation"
        }
    }
}


# ============================================================================
# Simple MCP Server
# ============================================================================

class SimpleMCPServer:
    """A minimal MCP server demonstrating core architecture concepts."""

    def __init__(self):
        self.resources = {
            "company_docs": {
                "name": "company_docs",
                "description": "Company documentation and policies",
                "uri": "internal://docs"
            },
            "employee_handbook": {
                "name": "employee_handbook",
                "description": "Employee handbook and HR policies",
                "uri": "internal://hr/handbook"
            },
            "technical_specs": {
                "name": "technical_specs",
                "description": "Technical specifications and API documentation",
                "uri": "internal://tech/specs"
            }
        }

        self.tools = {
            "search": {
                "name": "search",
                "description": "Search through available resources",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                }
            },
            "summarize": {
                "name": "summarize",
                "description": "Summarize a document or text",
                "parameters": {
                    "content": {"type": "string", "description": "Content to summarize"},
                    "max_length": {"type": "integer", "description": "Maximum summary length"}
                }
            },
            "translate": {
                "name": "translate",
                "description": "Translate text to another language",
                "parameters": {
                    "text": {"type": "string", "description": "Text to translate"},
                    "target_language": {"type": "string", "description": "Target language code"}
                }
            }
        }

        self.prompts = {
            "document_analysis": {
                "name": "document_analysis",
                "description": "Analyze a document for key insights",
                "arguments": [
                    {"name": "document_uri", "description": "URI of document to analyze", "required": True}
                ]
            },
            "query_assistant": {
                "name": "query_assistant",
                "description": "Help formulate effective search queries",
                "arguments": [
                    {"name": "topic", "description": "Topic to search for", "required": True}
                ]
            }
        }

        # Simulated document database
        self._documents = {
            "doc1": {"title": "Q4 Financial Report", "content": "Revenue increased by 15%..."},
            "doc2": {"title": "Annual Budget", "content": "Budget allocation for departments..."},
            "doc3": {"title": "Strategic Plan", "content": "Five-year strategic objectives..."},
            "doc4": {"title": "HR Policy Update", "content": "New remote work guidelines..."},
            "doc5": {"title": "API Documentation", "content": "REST API endpoints and usage..."}
        }

    async def handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests using JSON-RPC format."""
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")

        try:
            if method == "resources/list":
                result = await self.list_resources()
            elif method == "resources/read":
                result = await self.read_resource(params)
            elif method == "tools/list":
                result = await self.list_tools()
            elif method == "tools/call":
                result = await self.call_tool(params)
            elif method == "prompts/list":
                result = await self.list_prompts()
            elif method == "prompts/get":
                result = await self.get_prompt(params)
            elif method == "initialize":
                result = await self.initialize(params)
            else:
                raise ValueError(f"Unknown method: {method}")

            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(e)}
            }

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization/capability negotiation."""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "SimpleMCPServer",
                "version": "1.0.0"
            },
            "capabilities": {
                "resources": {"listChanged": True},
                "tools": {"listChanged": True},
                "prompts": {"listChanged": True}
            }
        }

    async def list_resources(self) -> Dict[str, Any]:
        """Return available resources - demonstrates capability discovery."""
        return {"resources": list(self.resources.values())}

    async def read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read content from a resource."""
        uri = params.get("uri")
        # Simulate reading resource content
        if "docs" in uri:
            content = "Company documentation content: policies, procedures, and guidelines..."
        elif "handbook" in uri:
            content = "Employee handbook: benefits, conduct, and workplace policies..."
        elif "specs" in uri:
            content = "Technical specifications: API docs, architecture diagrams, and code samples..."
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
        
        return {
            "contents": [
                {"uri": uri, "mimeType": "text/plain", "text": content}
            ]
        }

    async def list_tools(self) -> Dict[str, Any]:
        """Return available tools - demonstrates standardized primitives."""
        return {"tools": list(self.tools.values())}

    async def call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "search":
            return await self._execute_search(arguments)
        elif tool_name == "summarize":
            return await self._execute_summarize(arguments)
        elif tool_name == "translate":
            return await self._execute_translate(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _execute_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search tool."""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        
        # Simulate search operation
        results = []
        for doc_id, doc in self._documents.items():
            if query.lower() in doc["title"].lower() or query.lower() in doc["content"].lower():
                results.append({"id": doc_id, "title": doc["title"], "snippet": doc["content"][:50] + "..."})
                if len(results) >= limit:
                    break
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(results)} documents matching '{query}':\n" + 
                            "\n".join([f"- {r['title']}: {r['snippet']}" for r in results])
                }
            ]
        }

    async def _execute_summarize(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute summarize tool."""
        content = arguments.get("content", "")
        max_length = arguments.get("max_length", 100)
        
        # Simulate summarization
        summary = content[:max_length] + "..." if len(content) > max_length else content
        
        return {
            "content": [
                {"type": "text", "text": f"Summary: {summary}"}
            ]
        }

    async def _execute_translate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute translate tool."""
        text = arguments.get("text", "")
        target_language = arguments.get("target_language", "es")
        
        # Simulate translation (just a demo)
        translations = {
            "es": f"[Spanish translation of: {text}]",
            "fr": f"[French translation of: {text}]",
            "de": f"[German translation of: {text}]"
        }
        
        translated = translations.get(target_language, f"[{target_language} translation of: {text}]")
        
        return {
            "content": [
                {"type": "text", "text": translated}
            ]
        }

    async def list_prompts(self) -> Dict[str, Any]:
        """Return available prompts."""
        return {"prompts": list(self.prompts.values())}

    async def get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific prompt template."""
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name == "document_analysis":
            document_uri = arguments.get("document_uri", "unknown")
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Please analyze the document at {document_uri} and provide:\n"
                                   f"1. Key themes and topics\n"
                                   f"2. Important facts and figures\n"
                                   f"3. Recommendations based on the content"
                        }
                    }
                ]
            }
        elif prompt_name == "query_assistant":
            topic = arguments.get("topic", "general")
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Help me formulate effective search queries for finding information about '{topic}'.\n"
                                   f"Suggest 3-5 specific search terms or phrases that would yield comprehensive results."
                        }
                    }
                ]
            }
        else:
            raise ValueError(f"Unknown prompt: {prompt_name}")


# ============================================================================
# Simple MCP Client
# ============================================================================

class SimpleMCPClient:
    """A minimal MCP client demonstrating core architecture concepts."""

    def __init__(self, server: SimpleMCPServer):
        self.server = server
        self.request_id = 0
        self.server_capabilities = None

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        self.request_id += 1
        message = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        # In a real implementation, this would go over a transport layer
        response = await self.server.handle_request(message)
        return response

    async def initialize(self) -> Dict[str, Any]:
        """Initialize connection and perform capability negotiation."""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {
                "name": "SimpleMCPClient",
                "version": "1.0.0"
            },
            "capabilities": {}
        })
        
        if "result" in response:
            self.server_capabilities = response["result"]["capabilities"]
        
        return response

    async def discover_capabilities(self):
        """Discover what the server can do - core MCP primitive."""
        print("\n📋 Discovering Server Capabilities:")
        print("-" * 40)
        
        # List resources
        resources_response = await self.send_request("resources/list")
        if "result" in resources_response:
            print("\n📚 Available Resources:")
            for resource in resources_response["result"]["resources"]:
                print(f"  - {resource['name']}: {resource['description']}")
                print(f"    URI: {resource['uri']}")

        # List tools
        tools_response = await self.send_request("tools/list")
        if "result" in tools_response:
            print("\n🔧 Available Tools:")
            for tool in tools_response["result"]["tools"]:
                print(f"  - {tool['name']}: {tool['description']}")

        # List prompts
        prompts_response = await self.send_request("prompts/list")
        if "result" in prompts_response:
            print("\n💬 Available Prompts:")
            for prompt in prompts_response["result"]["prompts"]:
                print(f"  - {prompt['name']}: {prompt['description']}")

    async def search_documents(self, query: str, limit: int = 5):
        """Use the search tool to find documents."""
        print(f"\n🔍 Searching for: '{query}'")
        print("-" * 40)
        
        response = await self.send_request("tools/call", {
            "name": "search",
            "arguments": {"query": query, "limit": limit}
        })
        
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            print(content)
        else:
            print(f"Search failed: {response['error']['message']}")

    async def read_resource(self, uri: str):
        """Read content from a resource."""
        print(f"\n📖 Reading resource: {uri}")
        print("-" * 40)
        
        response = await self.send_request("resources/read", {"uri": uri})
        
        if "result" in response:
            for content in response["result"]["contents"]:
                print(f"Content: {content['text'][:100]}...")
        else:
            print(f"Read failed: {response['error']['message']}")

    async def get_prompt(self, name: str, arguments: Dict[str, Any] = None):
        """Get a prompt template from the server."""
        print(f"\n💬 Getting prompt: {name}")
        print("-" * 40)
        
        response = await self.send_request("prompts/get", {
            "name": name,
            "arguments": arguments or {}
        })
        
        if "result" in response:
            for message in response["result"]["messages"]:
                print(f"Role: {message['role']}")
                print(f"Content: {message['content']['text']}")
        else:
            print(f"Get prompt failed: {response['error']['message']}")

    async def use_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Generic method to use any tool."""
        print(f"\n⚙️ Using tool: {tool_name}")
        print("-" * 40)
        
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            print(content)
        else:
            print(f"Tool execution failed: {response['error']['message']}")


# ============================================================================
# Security Example (Conceptual)
# ============================================================================

class SecureMessageWrapper:
    """Demonstrates security concepts in MCP communication."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.audit_log: List[Dict[str, Any]] = []
    
    def wrap_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Add authentication headers to a request."""
        # In real implementation, this would be in transport headers
        wrapped = message.copy()
        wrapped["_meta"] = {
            "auth": {"type": "bearer", "token": self.api_key},
            "timestamp": datetime.now().isoformat(),
            "requestId": message.get("id")
        }
        return wrapped
    
    def log_request(self, message: Dict[str, Any], response: Dict[str, Any]):
        """Audit logging for security monitoring."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": message.get("method"),
            "request_id": message.get("id"),
            "success": "error" not in response,
            "error": response.get("error", {}).get("message") if "error" in response else None
        }
        self.audit_log.append(log_entry)
        return log_entry


# ============================================================================
# Demonstration Functions
# ============================================================================

async def demonstrate_mcp_architecture():
    """Demonstrate MCP architecture concepts."""
    print("🏗️  MCP Architecture Demonstration")
    print("=" * 50)
    
    # Create server and client
    server = SimpleMCPServer()
    client = SimpleMCPClient(server)
    
    # Step 1: Initialize connection (capability negotiation)
    print("\n1️⃣  Initializing Connection:")
    print("-" * 40)
    init_response = await client.initialize()
    if "result" in init_response:
        print(f"Server: {init_response['result']['serverInfo']['name']}")
        print(f"Protocol Version: {init_response['result']['protocolVersion']}")
        print(f"Capabilities: {json.dumps(init_response['result']['capabilities'], indent=2)}")
    
    # Step 2: Discover capabilities
    print("\n2️⃣  Capability Discovery:")
    await client.discover_capabilities()
    
    # Step 3: Use the search tool
    print("\n3️⃣  Using Search Tool:")
    await client.search_documents("financial")
    
    # Step 4: Read a resource
    print("\n4️⃣  Reading Resource:")
    await client.read_resource("internal://docs")
    
    # Step 5: Get a prompt template
    print("\n5️⃣  Getting Prompt Template:")
    await client.get_prompt("document_analysis", {"document_uri": "internal://docs/report.pdf"})
    
    # Step 6: Use summarize tool
    print("\n6️⃣  Using Summarize Tool:")
    await client.use_tool("summarize", {
        "content": "This is a comprehensive document about financial performance. "
                   "Revenue increased by 15% year over year. Operating costs decreased by 5%. "
                   "Net profit margin improved to 12.5%.",
        "max_length": 50
    })
    
    # Step 7: Use translate tool
    print("\n7️⃣  Using Translate Tool:")
    await client.use_tool("translate", {
        "text": "Hello, how are you?",
        "target_language": "es"
    })
    
    print("\n" + "=" * 50)
    print("✅ Architecture demonstration complete!")


async def demonstrate_json_rpc_messages():
    """Demonstrate JSON-RPC message formats used in MCP."""
    print("\n📨 JSON-RPC Message Format Examples")
    print("=" * 50)
    
    print("\n1. Request Message:")
    print("-" * 40)
    print(json.dumps(EXAMPLE_REQUEST, indent=2))
    
    print("\n2. Response Message:")
    print("-" * 40)
    print(json.dumps(EXAMPLE_RESPONSE, indent=2))
    
    print("\n3. Error Message:")
    print("-" * 40)
    print(json.dumps(EXAMPLE_ERROR, indent=2))


async def demonstrate_security_concepts():
    """Demonstrate security concepts in MCP."""
    print("\n🔐 Security Concepts Demonstration")
    print("=" * 50)
    
    # Create security wrapper
    security = SecureMessageWrapper(api_key="demo-api-key-12345")
    
    # Example request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "search", "arguments": {"query": "confidential"}}
    }
    
    # Wrap with security metadata
    print("\n1. Original Request:")
    print("-" * 40)
    print(json.dumps(request, indent=2))
    
    wrapped = security.wrap_request(request)
    print("\n2. Request with Security Metadata:")
    print("-" * 40)
    print(json.dumps(wrapped, indent=2))
    
    # Simulate response and audit logging
    response = {"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": "Results..."}]}}
    log_entry = security.log_request(request, response)
    
    print("\n3. Audit Log Entry:")
    print("-" * 40)
    print(json.dumps(log_entry, indent=2))


async def main():
    """Main entry point - runs all demonstrations."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--messages":
            await demonstrate_json_rpc_messages()
        elif sys.argv[1] == "--security":
            await demonstrate_security_concepts()
        elif sys.argv[1] == "--all":
            await demonstrate_mcp_architecture()
            await demonstrate_json_rpc_messages()
            await demonstrate_security_concepts()
        else:
            print("Usage: python mcp_architecture.py [--messages|--security|--all]")
            print("  (no args)   - Run main architecture demo")
            print("  --messages  - Show JSON-RPC message examples")
            print("  --security  - Show security concepts")
            print("  --all       - Run all demonstrations")
    else:
        await demonstrate_mcp_architecture()


if __name__ == "__main__":
    asyncio.run(main())
