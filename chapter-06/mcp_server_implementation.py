#!/usr/bin/env python3
"""
Server-Side Implementation - Chapter 6
Demonstrates MCP server-side implementation concepts including:
- Design principles for MCP servers (discoverable, context-aware, resilient)
- Implementing resource providers
- Implementing tool providers
- Implementing prompt providers
- Handling authentication and authorization
- Scalability and performance considerations
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# Data Models
# ============================================================================

class UserRole(Enum):
    GUEST = "guest"
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class DocumentType(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class Document:
    id: str
    title: str
    summary: str
    content: str
    doc_type: DocumentType
    created_at: datetime
    updated_at: datetime
    author: str
    tags: List[str] = field(default_factory=list)
    access_roles: List[UserRole] = field(default_factory=list)


@dataclass
class UserContext:
    user_id: str
    user_role: UserRole
    department: str
    recent_searches: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Document MCP Server - Main Implementation
# ============================================================================

class DocumentMCPServer:
    """A comprehensive MCP server demonstrating core server-side concepts."""

    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.request_cache: Dict[str, Any] = {}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize sample data
        self._initialize_documents()
        self._initialize_tools()
        self._initialize_prompts()

    def _initialize_documents(self):
        """Create sample documents for demonstration."""
        sample_docs = [
            Document(
                id="doc1", title="Company Overview",
                summary="Public information about the company",
                content="Our company was founded in 2010 and has grown to serve millions of customers...",
                doc_type=DocumentType.PUBLIC,
                created_at=datetime.now() - timedelta(days=30),
                updated_at=datetime.now() - timedelta(days=5),
                author="marketing",
                tags=["company", "public", "overview"],
                access_roles=[UserRole.GUEST, UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.ADMIN]
            ),
            Document(
                id="doc2", title="Employee Handbook",
                summary="Guidelines and policies for employees",
                content="This handbook outlines the company policies, benefits, and expectations...",
                doc_type=DocumentType.INTERNAL,
                created_at=datetime.now() - timedelta(days=60),
                updated_at=datetime.now() - timedelta(days=10),
                author="hr",
                tags=["hr", "policies", "employees"],
                access_roles=[UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.ADMIN]
            ),
            Document(
                id="doc3", title="Q4 Financial Report",
                summary="Quarterly financial results and analysis",
                content="Revenue increased by 15% year-over-year. Operating margins improved to 22%...",
                doc_type=DocumentType.CONFIDENTIAL,
                created_at=datetime.now() - timedelta(days=15),
                updated_at=datetime.now() - timedelta(days=2),
                author="finance",
                tags=["finance", "quarterly", "reports"],
                access_roles=[UserRole.MANAGER, UserRole.ADMIN]
            ),
            Document(
                id="doc4", title="Strategic Plan 2026",
                summary="Long-term strategic objectives and initiatives",
                content="Our five-year strategic plan focuses on market expansion and product innovation...",
                doc_type=DocumentType.RESTRICTED,
                created_at=datetime.now() - timedelta(days=45),
                updated_at=datetime.now() - timedelta(days=1),
                author="executive",
                tags=["strategy", "planning", "confidential"],
                access_roles=[UserRole.ADMIN]
            ),
            Document(
                id="doc5", title="API Documentation",
                summary="Technical documentation for internal APIs",
                content="REST API endpoints: GET /users, POST /orders, PUT /products...",
                doc_type=DocumentType.INTERNAL,
                created_at=datetime.now() - timedelta(days=20),
                updated_at=datetime.now(),
                author="engineering",
                tags=["api", "technical", "documentation"],
                access_roles=[UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.ADMIN]
            ),
            Document(
                id="doc6", title="Customer Support Guidelines",
                summary="Best practices for customer interactions",
                content="Always greet customers warmly. Listen actively to their concerns...",
                doc_type=DocumentType.INTERNAL,
                created_at=datetime.now() - timedelta(days=90),
                updated_at=datetime.now() - timedelta(days=7),
                author="support",
                tags=["support", "customer", "guidelines"],
                access_roles=[UserRole.EMPLOYEE, UserRole.MANAGER, UserRole.ADMIN]
            )
        ]
        for doc in sample_docs:
            self.documents[doc.id] = doc

    def _initialize_tools(self):
        """Initialize available tools."""
        self.tools = {
            "search": {
                "name": "search",
                "description": "Search through documents based on query and context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Maximum results", "default": 10},
                        "doc_type": {"type": "string", "description": "Filter by document type"}
                    },
                    "required": ["query"]
                }
            },
            "summarize": {
                "name": "summarize",
                "description": "Generate a summary of a document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of document to summarize"},
                        "max_length": {"type": "integer", "description": "Maximum summary length"}
                    },
                    "required": ["document_id"]
                }
            },
            "analyze": {
                "name": "analyze",
                "description": "Analyze document for key insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of document to analyze"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["sentiment", "keywords", "entities", "summary"],
                            "description": "Type of analysis"
                        }
                    },
                    "required": ["document_id", "analysis_type"]
                }
            },
            "compare": {
                "name": "compare",
                "description": "Compare two documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id_1": {"type": "string", "description": "First document ID"},
                        "document_id_2": {"type": "string", "description": "Second document ID"}
                    },
                    "required": ["document_id_1", "document_id_2"]
                }
            }
        }

    def _initialize_prompts(self):
        """Initialize available prompts."""
        self.prompts = {
            "document_analysis": {
                "name": "document_analysis",
                "description": "Analyze a document for key insights and recommendations",
                "arguments": [
                    {"name": "document_id", "description": "ID of the document", "required": True},
                    {"name": "focus_area", "description": "Specific area to focus on", "required": False}
                ]
            },
            "search_assistant": {
                "name": "search_assistant",
                "description": "Help formulate effective search queries",
                "arguments": [
                    {"name": "topic", "description": "Topic to search for", "required": True},
                    {"name": "context", "description": "Additional context", "required": False}
                ]
            },
            "report_generator": {
                "name": "report_generator",
                "description": "Generate a report based on multiple documents",
                "arguments": [
                    {"name": "document_ids", "description": "List of document IDs", "required": True},
                    {"name": "report_type", "description": "Type of report", "required": True}
                ]
            }
        }

    # ========================================================================
    # Main Request Handler
    # ========================================================================

    async def handle_request(self, message: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Handle incoming MCP requests with context awareness."""
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")

        # Log request for audit
        self._log_request(message, context)

        try:
            if method == "initialize":
                result = await self.initialize(params)
            elif method == "resources/list":
                result = await self.list_resources(context)
            elif method == "resources/read":
                result = await self.read_resource(params, context)
            elif method == "tools/list":
                result = await self.list_tools(context)
            elif method == "tools/call":
                result = await self.call_tool(params, context)
            elif method == "prompts/list":
                result = await self.list_prompts(context)
            elif method == "prompts/get":
                result = await self.get_prompt(params, context)
            else:
                raise ValueError(f"Unknown method: {method}")

            response = {"jsonrpc": "2.0", "id": request_id, "result": result}
        except PermissionError as e:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32001, "message": f"Permission denied: {str(e)}"}
            }
        except ValueError as e:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": f"Invalid params: {str(e)}"}
            }
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(e)}
            }

        # Log response
        self._log_response(message, response, context)
        return response

    def _log_request(self, message: Dict[str, Any], context: UserContext):
        """Audit logging for requests."""
        self.audit_log.append({
            "type": "request",
            "timestamp": datetime.now().isoformat(),
            "user_id": context.user_id,
            "user_role": context.user_role.value,
            "method": message.get("method"),
            "request_id": message.get("id")
        })

    def _log_response(self, message: Dict[str, Any], response: Dict[str, Any], context: UserContext):
        """Audit logging for responses."""
        self.audit_log.append({
            "type": "response",
            "timestamp": datetime.now().isoformat(),
            "user_id": context.user_id,
            "request_id": message.get("id"),
            "success": "error" not in response
        })

    # ========================================================================
    # Initialization and Capability Negotiation
    # ========================================================================

    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization and capability negotiation."""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "DocumentMCPServer",
                "version": "1.0.0"
            },
            "capabilities": {
                "resources": {"listChanged": True},
                "tools": {"listChanged": True},
                "prompts": {"listChanged": True}
            }
        }

    # ========================================================================
    # Resource Provider Implementation
    # ========================================================================

    def get_accessible_documents(self, user_role: UserRole) -> List[Document]:
        """Get documents accessible to a specific user role - context-aware filtering."""
        accessible = []
        for doc in self.documents.values():
            if user_role in doc.access_roles:
                accessible.append(doc)
        return accessible

    async def list_resources(self, context: UserContext) -> Dict[str, Any]:
        """Return resources appropriate for the requesting context - discoverable API."""
        user_role = context.user_role
        resources = []
        
        for doc in self.get_accessible_documents(user_role):
            resources.append({
                "uri": f"document://{doc.id}",
                "name": doc.title,
                "description": doc.summary,
                "mimeType": "text/plain",
                "_meta": {
                    "docType": doc.doc_type.value,
                    "author": doc.author,
                    "tags": doc.tags,
                    "updatedAt": doc.updated_at.isoformat()
                }
            })
        
        return {"resources": resources}

    async def read_resource(self, params: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Read a specific resource with access control."""
        uri = params.get("uri", "")
        
        # Parse document ID from URI
        if not uri.startswith("document://"):
            raise ValueError(f"Invalid resource URI: {uri}")
        
        doc_id = uri.replace("document://", "")
        
        if doc_id not in self.documents:
            raise ValueError(f"Document not found: {doc_id}")
        
        doc = self.documents[doc_id]
        
        # Check access permissions
        if context.user_role not in doc.access_roles:
            raise PermissionError(f"Access denied to document: {doc_id}")
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": doc.content,
                    "_meta": {
                        "title": doc.title,
                        "author": doc.author,
                        "docType": doc.doc_type.value,
                        "createdAt": doc.created_at.isoformat(),
                        "updatedAt": doc.updated_at.isoformat()
                    }
                }
            ]
        }

    # ========================================================================
    # Tool Provider Implementation
    # ========================================================================

    async def list_tools(self, context: UserContext) -> Dict[str, Any]:
        """Return available tools - self-describing API."""
        return {"tools": list(self.tools.values())}

    async def call_tool(self, params: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Execute a tool with given parameters - route to specific implementation."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "search":
            return await self.search_documents(arguments, context)
        elif tool_name == "summarize":
            return await self.summarize_document(arguments, context)
        elif tool_name == "analyze":
            return await self.analyze_document(arguments, context)
        elif tool_name == "compare":
            return await self.compare_documents(arguments, context)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def search_documents(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Context-aware document search - adapts results based on user context."""
        query = args.get("query", "").lower()
        limit = args.get("limit", 10)
        doc_type_filter = args.get("doc_type")

        # Get accessible documents for user
        accessible_docs = self.get_accessible_documents(context.user_role)
        
        # Perform search with context awareness
        results = []
        for doc in accessible_docs:
            # Filter by document type if specified
            if doc_type_filter and doc.doc_type.value != doc_type_filter:
                continue
            
            # Check if query matches title, summary, content, or tags
            if (query in doc.title.lower() or 
                query in doc.summary.lower() or 
                query in doc.content.lower() or
                any(query in tag.lower() for tag in doc.tags)):
                
                # Calculate relevance score (simple implementation)
                score = 0
                if query in doc.title.lower():
                    score += 3
                if query in doc.summary.lower():
                    score += 2
                if any(query in tag.lower() for tag in doc.tags):
                    score += 2
                if query in doc.content.lower():
                    score += 1
                
                # Boost score based on user context (department relevance)
                if context.department.lower() in doc.tags:
                    score += 1
                
                results.append({
                    "id": doc.id,
                    "title": doc.title,
                    "summary": doc.summary,
                    "relevance_score": score,
                    "doc_type": doc.doc_type.value,
                    "updated_at": doc.updated_at.isoformat()
                })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        results = results[:limit]

        # Update user's recent searches for context
        context.recent_searches.append(query)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(results)} documents matching '{query}'"
                }
            ],
            "results": results,
            "_meta": {
                "query": query,
                "total_matches": len(results),
                "user_context_applied": True
            }
        }

    async def summarize_document(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Summarize a document with access control."""
        doc_id = args.get("document_id")
        max_length = args.get("max_length", 200)

        if doc_id not in self.documents:
            raise ValueError(f"Document not found: {doc_id}")
        
        doc = self.documents[doc_id]
        
        # Check access
        if context.user_role not in doc.access_roles:
            raise PermissionError(f"Access denied to document: {doc_id}")

        # Generate summary (simplified - in production would use NLP)
        summary = doc.content[:max_length]
        if len(doc.content) > max_length:
            summary += "..."

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Summary of '{doc.title}':\n{summary}"
                }
            ],
            "_meta": {
                "document_id": doc_id,
                "original_length": len(doc.content),
                "summary_length": len(summary)
            }
        }

    async def analyze_document(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Analyze a document for insights."""
        doc_id = args.get("document_id")
        analysis_type = args.get("analysis_type", "summary")

        if doc_id not in self.documents:
            raise ValueError(f"Document not found: {doc_id}")
        
        doc = self.documents[doc_id]
        
        # Check access
        if context.user_role not in doc.access_roles:
            raise PermissionError(f"Access denied to document: {doc_id}")

        # Perform analysis (simplified implementations)
        if analysis_type == "keywords":
            # Extract simple keywords from tags and title
            keywords = doc.tags + doc.title.lower().split()
            result_text = f"Keywords: {', '.join(set(keywords))}"
        elif analysis_type == "entities":
            # Simple entity extraction
            entities = {"author": doc.author, "document_type": doc.doc_type.value}
            result_text = f"Entities: {json.dumps(entities)}"
        elif analysis_type == "sentiment":
            # Simple sentiment (placeholder)
            result_text = "Sentiment: Neutral (analysis placeholder)"
        else:  # summary
            result_text = f"Summary: {doc.summary}"

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Analysis of '{doc.title}' ({analysis_type}):\n{result_text}"
                }
            ],
            "_meta": {
                "document_id": doc_id,
                "analysis_type": analysis_type
            }
        }

    async def compare_documents(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Compare two documents - demonstrates tool composability."""
        doc_id_1 = args.get("document_id_1")
        doc_id_2 = args.get("document_id_2")

        # Validate documents exist and are accessible
        for doc_id in [doc_id_1, doc_id_2]:
            if doc_id not in self.documents:
                raise ValueError(f"Document not found: {doc_id}")
            if context.user_role not in self.documents[doc_id].access_roles:
                raise PermissionError(f"Access denied to document: {doc_id}")

        doc1 = self.documents[doc_id_1]
        doc2 = self.documents[doc_id_2]

        # Compare documents
        comparison = {
            "doc1": {"id": doc1.id, "title": doc1.title, "type": doc1.doc_type.value},
            "doc2": {"id": doc2.id, "title": doc2.title, "type": doc2.doc_type.value},
            "shared_tags": list(set(doc1.tags) & set(doc2.tags)),
            "same_author": doc1.author == doc2.author,
            "same_type": doc1.doc_type == doc2.doc_type,
            "length_diff": len(doc1.content) - len(doc2.content)
        }

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Comparison of '{doc1.title}' and '{doc2.title}':\n" +
                           f"- Shared tags: {', '.join(comparison['shared_tags']) or 'None'}\n" +
                           f"- Same author: {comparison['same_author']}\n" +
                           f"- Same type: {comparison['same_type']}"
                }
            ],
            "comparison": comparison
        }

    # ========================================================================
    # Prompt Provider Implementation
    # ========================================================================

    async def list_prompts(self, context: UserContext) -> Dict[str, Any]:
        """Return available prompts."""
        return {"prompts": list(self.prompts.values())}

    async def get_prompt(self, params: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Get a specific prompt template - adaptive based on context."""
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})

        if prompt_name == "document_analysis":
            return await self._get_document_analysis_prompt(arguments, context)
        elif prompt_name == "search_assistant":
            return await self._get_search_assistant_prompt(arguments, context)
        elif prompt_name == "report_generator":
            return await self._get_report_generator_prompt(arguments, context)
        else:
            raise ValueError(f"Unknown prompt: {prompt_name}")

    async def _get_document_analysis_prompt(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Generate document analysis prompt - context-aware."""
        doc_id = args.get("document_id")
        focus_area = args.get("focus_area", "general insights")

        if doc_id and doc_id in self.documents:
            doc = self.documents[doc_id]
            doc_info = f"Document: {doc.title}\nType: {doc.doc_type.value}\nAuthor: {doc.author}"
        else:
            doc_info = "Document: [specified document]"

        # Adapt prompt based on user's role
        role_specific = ""
        if context.user_role == UserRole.MANAGER:
            role_specific = "Focus on strategic implications and actionable recommendations."
        elif context.user_role == UserRole.ADMIN:
            role_specific = "Include security and compliance considerations."

        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please analyze the following document:\n\n{doc_info}\n\n"
                               f"Focus area: {focus_area}\n\n"
                               f"Provide:\n"
                               f"1. Key themes and insights\n"
                               f"2. Important facts and figures\n"
                               f"3. Recommendations\n"
                               f"{role_specific}"
                    }
                }
            ]
        }

    async def _get_search_assistant_prompt(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Generate search assistance prompt - uses user's search history."""
        topic = args.get("topic", "")
        additional_context = args.get("context", "")

        # Include user's recent searches for context
        recent = context.recent_searches[-3:] if context.recent_searches else []
        history_hint = f"\nRecent searches: {', '.join(recent)}" if recent else ""

        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Help me find documents about: {topic}\n"
                               f"Additional context: {additional_context}\n"
                               f"User department: {context.department}{history_hint}\n\n"
                               f"Please suggest:\n"
                               f"1. Specific search queries to try\n"
                               f"2. Related topics to explore\n"
                               f"3. Document types that might be relevant"
                    }
                }
            ]
        }

    async def _get_report_generator_prompt(self, args: Dict[str, Any], context: UserContext) -> Dict[str, Any]:
        """Generate report prompt."""
        doc_ids = args.get("document_ids", [])
        report_type = args.get("report_type", "summary")

        doc_titles = []
        for doc_id in doc_ids:
            if doc_id in self.documents:
                doc_titles.append(self.documents[doc_id].title)

        return {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Generate a {report_type} report based on these documents:\n"
                               f"{chr(10).join(['- ' + t for t in doc_titles])}\n\n"
                               f"Report should be appropriate for: {context.user_role.value} role\n"
                               f"Department context: {context.department}"
                    }
                }
            ]
        }


# ============================================================================
# Authentication and Authorization Handler
# ============================================================================

class AuthorizationHandler:
    """Handles authentication and authorization for MCP server."""

    def __init__(self):
        self.api_keys: Dict[str, UserContext] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, List[float]] = {}

    def register_api_key(self, api_key: str, context: UserContext):
        """Register an API key with associated user context."""
        self.api_keys[api_key] = context

    def authenticate(self, api_key: str) -> Optional[UserContext]:
        """Authenticate request using API key."""
        return self.api_keys.get(api_key)

    def check_rate_limit(self, user_id: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check if user is within rate limits."""
        current_time = time.time()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Remove old requests outside the window
        self.rate_limits[user_id] = [
            t for t in self.rate_limits[user_id]
            if current_time - t < window_seconds
        ]
        
        # Check limit
        if len(self.rate_limits[user_id]) >= max_requests:
            return False
        
        # Record this request
        self.rate_limits[user_id].append(current_time)
        return True

    def authorize_resource_access(self, context: UserContext, doc: Document) -> bool:
        """Check if user can access a specific resource."""
        return context.user_role in doc.access_roles


# ============================================================================
# Demonstration and Testing
# ============================================================================

async def demonstrate_server():
    """Demonstrate the MCP server functionality."""
    print("🖥️  MCP Server-Side Implementation Demonstration")
    print("=" * 55)

    # Create server
    server = DocumentMCPServer()

    # Create different user contexts
    guest_context = UserContext(
        user_id="guest1",
        user_role=UserRole.GUEST,
        department="public"
    )
    
    employee_context = UserContext(
        user_id="emp123",
        user_role=UserRole.EMPLOYEE,
        department="engineering"
    )
    
    manager_context = UserContext(
        user_id="mgr456",
        user_role=UserRole.MANAGER,
        department="finance"
    )
    
    admin_context = UserContext(
        user_id="admin789",
        user_role=UserRole.ADMIN,
        department="it"
    )

    # Test 1: Initialize
    print("\n1️⃣  Server Initialization:")
    print("-" * 40)
    init_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        admin_context
    )
    print(f"Server: {init_response['result']['serverInfo']['name']}")
    print(f"Version: {init_response['result']['serverInfo']['version']}")

    # Test 2: List resources for different roles (context-aware)
    print("\n2️⃣  Context-Aware Resource Listing:")
    print("-" * 40)
    
    for ctx, name in [(guest_context, "Guest"), (employee_context, "Employee"), 
                       (manager_context, "Manager"), (admin_context, "Admin")]:
        response = await server.handle_request(
            {"jsonrpc": "2.0", "id": 2, "method": "resources/list", "params": {}},
            ctx
        )
        doc_count = len(response['result']['resources'])
        print(f"{name} can access {doc_count} documents")

    # Test 3: List tools
    print("\n3️⃣  Available Tools (Self-Describing API):")
    print("-" * 40)
    tools_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}},
        employee_context
    )
    for tool in tools_response['result']['tools']:
        print(f"  - {tool['name']}: {tool['description']}")

    # Test 4: Search with context
    print("\n4️⃣  Context-Aware Search:")
    print("-" * 40)
    search_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
            "name": "search",
            "arguments": {"query": "finance", "limit": 5}
        }},
        manager_context
    )
    print(f"Results: {search_response['result']['content'][0]['text']}")
    for r in search_response['result']['results']:
        print(f"  - {r['title']} (score: {r['relevance_score']})")

    # Test 5: Read resource with permission check
    print("\n5️⃣  Resource Access Control:")
    print("-" * 40)
    
    # Employee trying to read confidential doc (should fail)
    read_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 5, "method": "resources/read", "params": {
            "uri": "document://doc3"  # Q4 Financial Report - confidential
        }},
        employee_context
    )
    if "error" in read_response:
        print(f"Employee access to confidential doc: DENIED ✓")
    
    # Manager trying to read same doc (should succeed)
    read_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 6, "method": "resources/read", "params": {
            "uri": "document://doc3"
        }},
        manager_context
    )
    if "result" in read_response:
        print(f"Manager access to confidential doc: GRANTED ✓")

    # Test 6: Document analysis tool
    print("\n6️⃣  Document Analysis Tool:")
    print("-" * 40)
    analyze_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {
            "name": "analyze",
            "arguments": {"document_id": "doc5", "analysis_type": "keywords"}
        }},
        employee_context
    )
    print(analyze_response['result']['content'][0]['text'])

    # Test 7: Compare documents
    print("\n7️⃣  Document Comparison Tool:")
    print("-" * 40)
    compare_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {
            "name": "compare",
            "arguments": {"document_id_1": "doc2", "document_id_2": "doc6"}
        }},
        employee_context
    )
    print(compare_response['result']['content'][0]['text'])

    # Test 8: Adaptive prompts
    print("\n8️⃣  Adaptive Prompt Generation:")
    print("-" * 40)
    prompt_response = await server.handle_request(
        {"jsonrpc": "2.0", "id": 9, "method": "prompts/get", "params": {
            "name": "document_analysis",
            "arguments": {"document_id": "doc3", "focus_area": "financial trends"}
        }},
        manager_context
    )
    prompt_text = prompt_response['result']['messages'][0]['content']['text']
    print(f"Generated prompt (truncated):\n{prompt_text[:200]}...")

    # Test 9: Audit log
    print("\n9️⃣  Audit Log (Security Monitoring):")
    print("-" * 40)
    print(f"Total logged events: {len(server.audit_log)}")
    # Show last few entries
    for entry in server.audit_log[-4:]:
        print(f"  [{entry['type']}] {entry.get('method', 'response')} - User: {entry['user_id']}")

    print("\n" + "=" * 55)
    print("✅ Server demonstration complete!")


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python mcp_server_implementation.py")
        print("Demonstrates MCP server-side implementation concepts")
    else:
        await demonstrate_server()


if __name__ == "__main__":
    asyncio.run(main())
