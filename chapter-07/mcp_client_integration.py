#!/usr/bin/env python3
"""
Client-Side Integration - Chapter 7
Demonstrates MCP client-side integration concepts including:
- Role of the MCP client (discovery, context management, orchestration)
- Integrating with AI models and frameworks
- Managing context retrieval
- Orchestrating tool execution
- Handling security on the client side
- Session and state management
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# Data Structures for Workflows
# ============================================================================

@dataclass
class WorkflowStep:
    """Data structure representing a step in a workflow."""
    server_id: str
    tool_name: str
    args: tuple
    id: str = field(default="")
    
    def __post_init__(self):
        if not self.id:
            self.id = f"{self.server_id}_{self.tool_name}"


@dataclass
class Workflow:
    """Encapsulates an ordered list of workflow steps."""
    steps: List[WorkflowStep]
    goal: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Dummy Server Implementation (for demonstration)
# ============================================================================

class DummyServer:
    """A simple server implementation exposing tools for demonstration."""
    
    def __init__(self, server_id: str, tools: Dict[str, Callable]):
        self.server_id = server_id
        self.tools = tools
        self.capabilities_cache: Optional[List[Dict[str, Any]]] = None
    
    async def discover_capabilities(self) -> List[Dict[str, Any]]:
        """
        Discover available tools - in a real MCP server this would return 
        structured tool schemas with descriptions and parameter definitions.
        """
        if self.capabilities_cache is None:
            self.capabilities_cache = [
                {
                    "name": name,
                    "description": f"Tool: {name}",
                    "type": "tool"
                }
                for name in self.tools.keys()
            ]
        return self.capabilities_cache
    
    async def call_tool(self, tool_name: str, *args) -> Any:
        """Dispatch to the appropriate tool function."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        func = self.tools[tool_name]
        return func(*args)
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources (simplified)."""
        return [{"uri": f"{self.server_id}://data", "name": f"{self.server_id} data"}]


# ============================================================================
# Context Manager - State Coordination
# ============================================================================

class ContextManager:
    """
    Manages context across multiple servers and operations.
    The context manager is the memory of the distributed system.
    """
    
    def __init__(self):
        self.store: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
    
    def update(self, key: str, value: Any):
        """Update a context value and record in history."""
        self.store[key] = value
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "update",
            "key": key,
            "value_type": type(value).__name__
        })
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.store.get(key, default)
    
    def get_current(self) -> Dict[str, Any]:
        """Get the current context state."""
        return dict(self.store)
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preferences that influence context selection."""
        self.user_preferences[key] = value
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get recent context history for debugging."""
        return self.history[-n:]
    
    def clear(self):
        """Clear the context (but preserve history)."""
        self.store.clear()


# ============================================================================
# Workflow Orchestrator - Intelligent Orchestration
# ============================================================================

class WorkflowOrchestrator:
    """
    Orchestrates tool execution with intelligent planning and adaptation.
    Handles dependency management, adaptive workflows, and error recovery.
    """
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
    
    async def plan_workflow(self, goal: str, context: Dict[str, Any], 
                           available_tools: Dict[str, List[str]]) -> Workflow:
        """
        Parse a goal description and generate workflow steps.
        This is a simplified planner - in production, this would use
        more sophisticated NLP or AI-based planning.
        """
        steps: List[WorkflowStep] = []
        goal_lower = goal.lower()
        
        # Math operations
        if 'sum' in goal_lower or 'add' in goal_lower:
            numbers = context.get('numbers', (2, 3))
            steps.append(WorkflowStep('math', 'add', numbers))
        
        if 'multiply' in goal_lower or 'product' in goal_lower:
            numbers = context.get('numbers', (4, 5))
            steps.append(WorkflowStep('math', 'multiply', numbers))
        
        if 'subtract' in goal_lower or 'difference' in goal_lower:
            numbers = context.get('numbers', (10, 3))
            steps.append(WorkflowStep('math', 'subtract', numbers))
        
        if 'divide' in goal_lower or 'quotient' in goal_lower:
            numbers = context.get('numbers', (20, 4))
            steps.append(WorkflowStep('math', 'divide', numbers))
        
        # Text operations
        if 'uppercase' in goal_lower or 'upper' in goal_lower:
            text = context.get('text', 'hello world')
            steps.append(WorkflowStep('text', 'uppercase', (text,)))
        
        if 'lowercase' in goal_lower or 'lower' in goal_lower:
            text = context.get('text', 'HELLO WORLD')
            steps.append(WorkflowStep('text', 'lowercase', (text,)))
        
        if 'reverse' in goal_lower:
            text = context.get('text', 'hello')
            steps.append(WorkflowStep('text', 'reverse', (text,)))
        
        if 'length' in goal_lower or 'count' in goal_lower:
            text = context.get('text', 'hello world')
            steps.append(WorkflowStep('text', 'length', (text,)))
        
        # Data operations
        if 'fetch' in goal_lower or 'retrieve' in goal_lower or 'get data' in goal_lower:
            query = context.get('query', 'default')
            steps.append(WorkflowStep('data', 'fetch', (query,)))
        
        if 'analyze' in goal_lower or 'analysis' in goal_lower:
            data = context.get('data', [1, 2, 3, 4, 5])
            steps.append(WorkflowStep('data', 'analyze', (data,)))
        
        return Workflow(steps=steps, goal=goal)
    
    async def execute_workflow(self, workflow: Workflow, 
                               servers: Dict[str, DummyServer],
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute each step in sequence and update the context.
        Implements error handling and recovery strategies.
        """
        results: List[Dict[str, Any]] = []
        
        for i, step in enumerate(workflow.steps):
            execution_record = {
                "step_id": step.id,
                "step_index": i,
                "server_id": step.server_id,
                "tool_name": step.tool_name,
                "args": step.args,
                "status": TaskStatus.RUNNING.value,
                "started_at": datetime.now().isoformat()
            }
            
            try:
                if step.server_id not in servers:
                    raise ValueError(f"Server not found: {step.server_id}")
                
                server = servers[step.server_id]
                result = await server.call_tool(step.tool_name, *step.args)
                
                # Store result in context for downstream use
                context[f"{step.tool_name}_result"] = result
                
                execution_record["status"] = TaskStatus.COMPLETED.value
                execution_record["result"] = result
                execution_record["completed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                execution_record["status"] = TaskStatus.FAILED.value
                execution_record["error"] = str(e)
                execution_record["completed_at"] = datetime.now().isoformat()
                
                # Simple retry logic could be added here
                # For now, we continue with other steps
            
            results.append(execution_record)
            self.execution_history.append(execution_record)
        
        return results
    
    async def execute_parallel(self, workflow: Workflow,
                               servers: Dict[str, DummyServer],
                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute independent steps in parallel for efficiency."""
        tasks = []
        
        for step in workflow.steps:
            async def execute_step(s):
                if s.server_id in servers:
                    return await servers[s.server_id].call_tool(s.tool_name, *s.args)
                return None
            tasks.append(execute_step(step))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            {
                "step_id": step.id,
                "result": result if not isinstance(result, Exception) else None,
                "error": str(result) if isinstance(result, Exception) else None,
                "status": TaskStatus.FAILED.value if isinstance(result, Exception) else TaskStatus.COMPLETED.value
            }
            for step, result in zip(workflow.steps, results)
        ]


# ============================================================================
# Security Handler - Client-Side Security
# ============================================================================

class SecurityHandler:
    """
    Handles client-side security including credential management,
    permission delegation, and data protection.
    """
    
    def __init__(self):
        self.credentials: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, List[str]] = {}
        self.audit_log: List[Dict[str, Any]] = []
    
    def register_server_credentials(self, server_id: str, credentials: Dict[str, Any]):
        """Register credentials for a specific server."""
        # In production, credentials should be encrypted
        self.credentials[server_id] = credentials
    
    def get_credentials(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get credentials for a server."""
        return self.credentials.get(server_id)
    
    def set_permissions(self, user_id: str, allowed_operations: List[str]):
        """Set allowed operations for a user."""
        self.permissions[user_id] = allowed_operations
    
    def check_permission(self, user_id: str, operation: str) -> bool:
        """Check if a user has permission for an operation."""
        user_perms = self.permissions.get(user_id, [])
        if operation in user_perms or "*" in user_perms:
            return True
        # Check for wildcard patterns like "text:*"
        server_id = operation.split(":")[0] if ":" in operation else ""
        wildcard = f"{server_id}:*"
        return wildcard in user_perms
    
    def log_access(self, user_id: str, operation: str, server_id: str, success: bool):
        """Log access for audit purposes."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "operation": operation,
            "server_id": server_id,
            "success": success
        })
    
    def get_audit_log(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit log, optionally filtered by user."""
        if user_id:
            return [e for e in self.audit_log if e["user_id"] == user_id]
        return self.audit_log


# ============================================================================
# MCP Client - The Main Integration Layer
# ============================================================================

class MCPClient:
    """
    The MCP client ties everything together - it's the orchestration layer
    that discovers, manages, and invokes server capabilities on behalf of AI systems.
    """
    
    def __init__(self, client_id: str = "mcp-client"):
        self.client_id = client_id
        self.servers: Dict[str, DummyServer] = {}
        self.context = ContextManager()
        self.orchestrator = WorkflowOrchestrator()
        self.security = SecurityHandler()
        self.capabilities_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.session_start = datetime.now()
    
    async def connect_server(self, server_id: str, server: DummyServer) -> Dict[str, Any]:
        """
        Connect to an MCP server and discover its capabilities.
        This is an ongoing conversation - capabilities can change over time.
        """
        # Discover capabilities
        capabilities = await server.discover_capabilities()
        
        # Cache capabilities
        self.capabilities_cache[server_id] = capabilities
        
        # Register server
        self.servers[server_id] = server
        
        return {
            "server_id": server_id,
            "capabilities_count": len(capabilities),
            "capabilities": [c["name"] for c in capabilities]
        }
    
    async def disconnect_server(self, server_id: str) -> bool:
        """Disconnect from a server."""
        if server_id in self.servers:
            del self.servers[server_id]
            if server_id in self.capabilities_cache:
                del self.capabilities_cache[server_id]
            return True
        return False
    
    async def refresh_capabilities(self, server_id: str) -> List[Dict[str, Any]]:
        """Refresh capabilities for a specific server."""
        if server_id not in self.servers:
            raise ValueError(f"Server not connected: {server_id}")
        
        capabilities = await self.servers[server_id].discover_capabilities()
        self.capabilities_cache[server_id] = capabilities
        return capabilities
    
    def get_all_capabilities(self) -> Dict[str, List[str]]:
        """Get all available capabilities across all connected servers."""
        return {
            server_id: [c["name"] for c in caps]
            for server_id, caps in self.capabilities_cache.items()
        }
    
    async def execute_goal(self, goal_description: str, 
                          user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a goal by planning and running a workflow.
        This is where the client acts as the conductor of distributed capabilities.
        """
        # Update context with user-provided values
        if user_context:
            for key, value in user_context.items():
                self.context.update(key, value)
        
        # Get available tools for planning
        available_tools = self.get_all_capabilities()
        
        # Plan the workflow
        workflow = await self.orchestrator.plan_workflow(
            goal_description,
            self.context.get_current(),
            available_tools
        )
        
        # Execute the workflow
        results = await self.orchestrator.execute_workflow(
            workflow,
            self.servers,
            self.context.store
        )
        
        return {
            "goal": goal_description,
            "workflow_steps": len(workflow.steps),
            "results": results,
            "context_state": self.context.get_current()
        }
    
    async def call_tool_directly(self, server_id: str, tool_name: str, 
                                 *args, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Call a specific tool directly (bypassing workflow planning).
        Useful for simple, single-tool operations.
        """
        # Security check
        operation = f"{server_id}:{tool_name}"
        if not self.security.check_permission(user_id, operation):
            self.security.log_access(user_id, operation, server_id, False)
            raise PermissionError(f"User {user_id} not authorized for {operation}")
        
        if server_id not in self.servers:
            raise ValueError(f"Server not connected: {server_id}")
        
        try:
            result = await self.servers[server_id].call_tool(tool_name, *args)
            self.security.log_access(user_id, operation, server_id, True)
            
            # Update context
            self.context.update(f"{tool_name}_result", result)
            
            return {
                "server_id": server_id,
                "tool_name": tool_name,
                "args": args,
                "result": result,
                "success": True
            }
        except Exception as e:
            self.security.log_access(user_id, operation, server_id, False)
            return {
                "server_id": server_id,
                "tool_name": tool_name,
                "args": args,
                "error": str(e),
                "success": False
            }
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current client session."""
        return {
            "client_id": self.client_id,
            "session_start": self.session_start.isoformat(),
            "connected_servers": list(self.servers.keys()),
            "context_keys": list(self.context.store.keys()),
            "execution_history_count": len(self.orchestrator.execution_history)
        }


# ============================================================================
# Framework Integration Examples
# ============================================================================

class LangChainIntegration:
    """
    Example of how MCP tools can be exposed as LangChain-compatible tools.
    In production, you would use the langchain-mcp-adapters package.
    """
    
    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client
    
    def get_langchain_tools(self) -> List[Dict[str, Any]]:
        """
        Convert MCP capabilities to LangChain tool format.
        This is a simplified example - the real adapter handles more complexity.
        """
        tools = []
        for server_id, capabilities in self.client.capabilities_cache.items():
            for cap in capabilities:
                tools.append({
                    "name": f"{server_id}_{cap['name']}",
                    "description": cap.get("description", f"Tool from {server_id}"),
                    "server_id": server_id,
                    "mcp_tool_name": cap["name"]
                })
        return tools
    
    async def invoke_tool(self, tool_name: str, *args) -> Any:
        """Invoke a tool through the MCP client."""
        # Parse server_id and actual tool name
        parts = tool_name.split("_", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid tool name format: {tool_name}")
        
        server_id, mcp_tool_name = parts
        result = await self.client.call_tool_directly(server_id, mcp_tool_name, *args)
        return result


class AutoGenIntegration:
    """
    Example of how MCP can be integrated with AutoGen multi-agent systems.
    Each agent can be connected to different MCP servers.
    """
    
    def __init__(self):
        self.agent_clients: Dict[str, MCPClient] = {}
    
    def register_agent(self, agent_id: str, client: MCPClient):
        """Register an MCP client for a specific agent."""
        self.agent_clients[agent_id] = client
    
    def get_agent_capabilities(self, agent_id: str) -> Dict[str, List[str]]:
        """Get capabilities available to a specific agent."""
        if agent_id not in self.agent_clients:
            return {}
        return self.agent_clients[agent_id].get_all_capabilities()
    
    async def agent_execute(self, agent_id: str, goal: str) -> Dict[str, Any]:
        """Execute a goal for a specific agent."""
        if agent_id not in self.agent_clients:
            raise ValueError(f"Agent not registered: {agent_id}")
        return await self.agent_clients[agent_id].execute_goal(goal)


# ============================================================================
# Demonstration
# ============================================================================

async def demo():
    """Demonstrate MCP client functionality."""
    print("🧠 MCP Client-Side Integration Demonstration")
    print("=" * 55)
    
    # Create dummy servers with different capabilities
    math_server = DummyServer('math', {
        'add': lambda a, b: a + b,
        'subtract': lambda a, b: a - b,
        'multiply': lambda a, b: a * b,
        'divide': lambda a, b: a / b if b != 0 else "Error: Division by zero"
    })
    
    text_server = DummyServer('text', {
        'uppercase': lambda s: s.upper(),
        'lowercase': lambda s: s.lower(),
        'reverse': lambda s: s[::-1],
        'length': lambda s: len(s)
    })
    
    data_server = DummyServer('data', {
        'fetch': lambda query: f"Data for query: {query}",
        'analyze': lambda data: {
            'count': len(data),
            'sum': sum(data) if isinstance(data, list) else 0,
            'avg': sum(data) / len(data) if isinstance(data, list) and len(data) > 0 else 0
        }
    })
    
    # Create MCP client
    client = MCPClient("demo-client")
    
    # Test 1: Connect to servers
    print("\n1️⃣  Connecting to Servers (Capability Discovery):")
    print("-" * 45)
    
    for name, server in [("math", math_server), ("text", text_server), ("data", data_server)]:
        result = await client.connect_server(name, server)
        print(f"  {name}: {result['capabilities']}")
    
    # Test 2: View all capabilities
    print("\n2️⃣  All Available Capabilities:")
    print("-" * 45)
    all_caps = client.get_all_capabilities()
    for server_id, tools in all_caps.items():
        print(f"  {server_id}: {', '.join(tools)}")
    
    # Test 3: Execute goals through workflow planning
    print("\n3️⃣  Goal-Based Execution (Intelligent Orchestration):")
    print("-" * 45)
    
    # Simple math goal
    result = await client.execute_goal("Compute the sum of two numbers", {"numbers": (10, 5)})
    print(f"  Goal: 'sum of two numbers'")
    print(f"  Result: {result['results'][0]['result'] if result['results'] else 'No result'}")
    
    # Multiple operations
    result = await client.execute_goal("Find sum and multiply numbers", {"numbers": (3, 4)})
    print(f"  Goal: 'sum and multiply'")
    print(f"  Steps executed: {result['workflow_steps']}")
    for r in result['results']:
        print(f"    - {r['tool_name']}: {r['result']}")
    
    # Test 4: Text operations
    print("\n4️⃣  Text Processing Workflow:")
    print("-" * 45)
    result = await client.execute_goal(
        "Convert to uppercase and get length",
        {"text": "hello mcp client"}
    )
    for r in result['results']:
        print(f"  {r['tool_name']}: {r['result']}")
    
    # Test 5: Context management
    print("\n5️⃣  Context State (Memory of Distributed System):")
    print("-" * 45)
    context_state = client.context.get_current()
    for key, value in context_state.items():
        print(f"  {key}: {value}")
    
    # Test 6: Security - Permission delegation
    print("\n6️⃣  Security - Permission Management:")
    print("-" * 45)
    
    # Set up permissions
    client.security.set_permissions("user123", ["math:add", "math:multiply", "text:*"])
    client.security.set_permissions("guest", ["math:add"])
    
    # Test permission check
    print(f"  user123 can use math:add? {client.security.check_permission('user123', 'math:add')}")
    print(f"  user123 can use text:uppercase? {client.security.check_permission('user123', 'text:uppercase')}")
    print(f"  guest can use math:multiply? {client.security.check_permission('guest', 'math:multiply')}")
    
    # Test 7: Direct tool call with security
    print("\n7️⃣  Direct Tool Call with Security:")
    print("-" * 45)
    
    result = await client.call_tool_directly("math", "add", 100, 50, user_id="user123")
    print(f"  math:add(100, 50) = {result['result']}")
    
    # Test 8: Session info
    print("\n8️⃣  Session Information:")
    print("-" * 45)
    session = client.get_session_info()
    print(f"  Client ID: {session['client_id']}")
    print(f"  Connected servers: {session['connected_servers']}")
    print(f"  Context keys: {session['context_keys']}")
    print(f"  Execution history: {session['execution_history_count']} operations")
    
    # Test 9: Audit log
    print("\n9️⃣  Security Audit Log:")
    print("-" * 45)
    for entry in client.security.get_audit_log():
        status = "✓" if entry['success'] else "✗"
        print(f"  [{status}] {entry['user_id']} -> {entry['operation']}")
    
    # Test 10: Framework integration example
    print("\n🔟 Framework Integration (LangChain-style):")
    print("-" * 45)
    langchain_adapter = LangChainIntegration(client)
    lc_tools = langchain_adapter.get_langchain_tools()
    print(f"  Exposed as LangChain tools: {len(lc_tools)}")
    for tool in lc_tools[:3]:
        print(f"    - {tool['name']}")
    
    print("\n" + "=" * 55)
    print("✅ Client demonstration complete!")


async def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python mcp_client_integration.py")
        print("Demonstrates MCP client-side integration concepts")
    else:
        await demo()


if __name__ == "__main__":
    asyncio.run(main())
