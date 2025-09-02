#!/usr/bin/env python3
"""
MCP Task Manager Server - Chapter 4
Demonstrates MCP components and interfaces including:
- Resource providers (knowledge base)
- Tool providers (actions)
- Prompt providers (conversation starters)
- Security interfaces
- Discovery interfaces
"""

import asyncio
import json
import hashlib
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, Resource, Prompt, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, GetPromptRequest, ReadResourceRequest
)


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    priority: int = 1
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TaskManagerServer:
    """A comprehensive MCP server demonstrating resources, tools and prompts."""

    def __init__(self, name: str = "task-manager"):
        self.server = Server(name)
        self.tasks: Dict[str, Task] = {}
        self.users: Dict[str, Dict[str, Any]] = {
            "alice": {"name": "Alice Johnson", "role": "developer", "skills": ["python", "javascript"]},
            "bob": {"name": "Bob Smith", "role": "designer", "skills": ["ui", "ux", "graphics"]},
            "carol": {"name": "Carol Davis", "role": "manager", "skills": ["planning", "coordination"]}
        }
        self.prompt_templates = {
            "task_summary": "Summarize the current status of task '{task_title}' including progress and next steps.",
            "daily_standup": "Generate a daily standup report for {user_name} including completed tasks, current work, and blockers.",
            "project_overview": "Create a project overview showing all tasks, their status, and team assignments."
        }
        # Initialize with some sample data
        self._create_sample_tasks()
        # Register all the MCP interfaces
        self._register_tools()
        self._register_resources()
        self._register_prompts()

    def _create_sample_tasks(self):
        """Create some sample tasks for demonstration."""
        sample_tasks = [
            Task("1", "Implement user authentication", "Add login/logout functionality", 
                 TaskStatus.IN_PROGRESS, datetime.now() - timedelta(days=2), datetime.now(), 
                 "alice", 3, ["backend", "security"]),
            Task("2", "Design homepage layout", "Create wireframes and mockups for new homepage", 
                 TaskStatus.COMPLETED, datetime.now() - timedelta(days=5), 
                 datetime.now() - timedelta(days=1), "bob", 2, ["frontend", "design"]),
            Task("3", "Write API documentation", "Document all REST endpoints", 
                 TaskStatus.PENDING, datetime.now() - timedelta(days=1), datetime.now(), 
                 None, 1, ["documentation"]),
            Task("4", "Set up CI/CD pipeline", "Configure automated testing and deployment", 
                 TaskStatus.PENDING, datetime.now(), datetime.now(), None, 3, ["devops", "automation"])
        ]
        for task in sample_tasks:
            self.tasks[task.id] = task

    def _register_tools(self):
        """Register tool providers – these are actions the AI can perform."""
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="create_task",
                    description="Create a new task in the task management system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"},
                            "description": {"type": "string", "description": "Task description"},
                            "assigned_to": {"type": "string", "description": "Username to assign task to"},
                            "priority": {"type": "integer", "description": "Priority level (1-5)", "minimum": 1, "maximum": 5},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"}
                        },
                        "required": ["title", "description"]
                    }
                ),
                Tool(
                    name="update_task_status",
                    description="Update the status of an existing task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to update"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "failed"], "description": "New status"}
                        },
                        "required": ["task_id", "status"]
                    }
                ),
                Tool(
                    name="assign_task",
                    description="Assign a task to a team member",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "string", "description": "ID of the task to assign"},
                            "assigned_to": {"type": "string", "description": "Username to assign task to"}
                        },
                        "required": ["task_id", "assigned_to"]
                    }
                ),
                Tool(
                    name="search_tasks",
                    description="Search for tasks based on various criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for title/description"},
                            "status": {"type": "string", "description": "Filter by status"},
                            "assigned_to": {"type": "string", "description": "Filter by assignee"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"}
                        }
                    }
                ),
                Tool(
                    name="generate_report",
                    description="Generate various types of reports",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_type": {"type": "string", "enum": ["summary", "user_workload", "project_status"], "description": "Type of report"},
                            "user": {"type": "string", "description": "Username for user-specific reports"}
                        },
                        "required": ["report_type"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """Handle tool calls – this is where the actual work gets done."""
            if name == "create_task":
                return await self._create_task(arguments)
            elif name == "update_task_status":
                return await self._update_task_status(arguments)
            elif name == "assign_task":
                return await self._assign_task(arguments)
            elif name == "search_tasks":
                return await self._search_tasks(arguments)
            elif name == "generate_report":
                return await self._generate_report(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    def _register_resources(self):
        """Register resource providers – these expose data and information."""
        @self.server.list_resources()
        async def list_resources():
            return [
                Resource(uri="tasks://all", name="All Tasks", 
                        description="Complete list of all tasks in the system", 
                        mimeType="application/json"),
                Resource(uri="tasks://active", name="Active Tasks", 
                        description="Tasks that are currently in progress", 
                        mimeType="application/json"),
                Resource(uri="users://all", name="Team Members", 
                        description="List of all team members and their information", 
                        mimeType="application/json"),
                Resource(uri="analytics://task_metrics", name="Task Metrics", 
                        description="Analytics and metrics about task completion and performance", 
                        mimeType="application/json")
            ]

        @self.server.read_resource()
        async def read_resource(uri: str):
            """Provide access to various data resources."""
            if uri == "tasks://all":
                tasks_data = {}
                for task_id, task in self.tasks.items():
                    task_dict = asdict(task)
                    task_dict['status'] = task.status.value
                    task_dict['created_at'] = task.created_at.isoformat()
                    task_dict['updated_at'] = task.updated_at.isoformat()
                    tasks_data[task_id] = task_dict
                return [TextContent(type="text", text=json.dumps(tasks_data, indent=2))]
            elif uri == "tasks://active":
                active_tasks = {}
                for task_id, task in self.tasks.items():
                    if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                        task_dict = asdict(task)
                        task_dict['status'] = task.status.value
                        task_dict['created_at'] = task.created_at.isoformat()
                        task_dict['updated_at'] = task.updated_at.isoformat()
                        active_tasks[task_id] = task_dict
                return [TextContent(type="text", text=json.dumps(active_tasks, indent=2))]
            elif uri == "users://all":
                return [TextContent(type="text", text=json.dumps(self.users, indent=2))]
            elif uri == "analytics://task_metrics":
                metrics = self._calculate_task_metrics()
                return [TextContent(type="text", text=json.dumps(metrics, indent=2))]
            else:
                raise ValueError(f"Unknown resource: {uri}")

    def _register_prompts(self):
        """Register prompt providers – these expose reusable prompt templates."""
        @self.server.list_prompts()
        async def list_prompts():
            return [
                Prompt(name="task_summary", 
                      description="Generate a summary of a specific task", 
                      arguments=[{"name": "task_id", "description": "ID of the task to summarize", "required": True}]),
                Prompt(name="daily_standup", 
                      description="Generate a daily standup report for a team member", 
                      arguments=[{"name": "user_name", "description": "Username to generate report for", "required": True}]),
                Prompt(name="project_overview", 
                      description="Generate a comprehensive project overview", 
                      arguments=[])
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict):
            """Provide prompt templates with context-specific information."""
            if name == "task_summary":
                task_id = arguments.get("task_id")
                if task_id not in self.tasks:
                    raise ValueError(f"Task {task_id} not found")
                task = self.tasks[task_id]
                context = f"""
Task: {task.title}
Description: {task.description}
Status: {task.status.value}
Assigned to: {task.assigned_to or 'Unassigned'}
Priority: {task.priority}
Tags: {', '.join(task.tags)}
Created: {task.created_at.isoformat()}
Last Updated: {task.updated_at.isoformat()}
"""
                prompt = self.prompt_templates["task_summary"].format(task_title=task.title)
                return {"messages": [{"role": "user", "content": {"type": "text", "text": f"{prompt}\n\nContext:\n{context}"}}]}
            
            elif name == "daily_standup":
                user_name = arguments.get("user_name")
                if user_name not in self.users:
                    raise ValueError(f"User {user_name} not found")
                user = self.users[user_name]
                user_tasks = [t for t in self.tasks.values() if t.assigned_to == user_name]
                completed = [t for t in user_tasks if t.status == TaskStatus.COMPLETED]
                in_progress = [t for t in user_tasks if t.status == TaskStatus.IN_PROGRESS]
                context = f"""
User: {user['name']} ({user['role']})
Completed Tasks: {len(completed)}
In Progress: {len(in_progress)}
Tasks: {', '.join([t.title for t in user_tasks])}
"""
                prompt = self.prompt_templates["daily_standup"].format(user_name=user['name'])
                return {"messages": [{"role": "user", "content": {"type": "text", "text": f"{prompt}\n\nContext:\n{context}"}}]}
            
            elif name == "project_overview":
                total = len(self.tasks)
                completed = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
                in_progress = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
                pending = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
                context = f"""
Total Tasks: {total}
Completed: {completed} ({completed/total*100:.1f}%)
In Progress: {in_progress} ({in_progress/total*100:.1f}%)
Pending: {pending} ({pending/total*100:.1f}%)
Team Members: {', '.join([u['name'] for u in self.users.values()])}
"""
                prompt = self.prompt_templates["project_overview"]
                return {"messages": [{"role": "user", "content": {"type": "text", "text": f"{prompt}\n\nContext:\n{context}"}}]}
            else:
                raise ValueError(f"Unknown prompt: {name}")

    # Tool implementation methods
    async def _create_task(self, arguments: dict):
        """Create a new task."""
        task_id = str(len(self.tasks) + 1)
        task = Task(
            id=task_id,
            title=arguments["title"],
            description=arguments["description"],
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            assigned_to=arguments.get("assigned_to"),
            priority=arguments.get("priority", 1),
            tags=arguments.get("tags", [])
        )
        self.tasks[task_id] = task
        result = {"success": True, "task_id": task_id, "message": f"Task '{task.title}' created successfully"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _update_task_status(self, arguments: dict):
        """Update task status."""
        task_id = arguments["task_id"]
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        new_status = TaskStatus(arguments["status"])
        old_status = self.tasks[task_id].status
        self.tasks[task_id].status = new_status
        self.tasks[task_id].updated_at = datetime.now()
        result = {"success": True, "task_id": task_id, "old_status": old_status.value, "new_status": new_status.value}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _assign_task(self, arguments: dict):
        """Assign task to a user."""
        task_id = arguments["task_id"]
        assigned_to = arguments["assigned_to"]
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        if assigned_to not in self.users:
            raise ValueError(f"User {assigned_to} not found")
        old_assignee = self.tasks[task_id].assigned_to
        self.tasks[task_id].assigned_to = assigned_to
        self.tasks[task_id].updated_at = datetime.now()
        result = {"success": True, "task_id": task_id, "old_assignee": old_assignee, "new_assignee": assigned_to}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _search_tasks(self, arguments: dict):
        """Search for tasks based on criteria."""
        query = arguments.get("query", "").lower()
        status_filter = arguments.get("status")
        assignee_filter = arguments.get("assigned_to")
        tags_filter = arguments.get("tags", [])
        
        matching_tasks = []
        for task in self.tasks.values():
            # Text search in title and description
            if query and query not in task.title.lower() and query not in task.description.lower():
                continue
            # Status filter
            if status_filter and task.status.value != status_filter:
                continue
            # Assignee filter
            if assignee_filter and task.assigned_to != assignee_filter:
                continue
            # Tags filter
            if tags_filter and not any(tag in task.tags for tag in tags_filter):
                continue
            matching_tasks.append({
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "assigned_to": task.assigned_to,
                "priority": task.priority
            })
        
        result = {"query": arguments, "matches": len(matching_tasks), "tasks": matching_tasks}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _generate_report(self, arguments: dict):
        """Generate various types of reports."""
        report_type = arguments["report_type"]
        if report_type == "summary":
            return await self._generate_summary_report()
        elif report_type == "user_workload":
            user = arguments.get("user")
            return await self._generate_user_workload_report(user)
        elif report_type == "project_status":
            return await self._generate_project_status_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    async def _generate_summary_report(self):
        """Generate a summary report."""
        metrics = self._calculate_task_metrics()
        recent = self._get_recent_activity()
        report = {
            "report_type": "summary",
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "recent_activity": recent
        }
        return [TextContent(type="text", text=json.dumps(report, indent=2))]

    async def _generate_user_workload_report(self, user: str = None):
        """Generate user workload report."""
        performance = self._get_team_performance()
        if user and user in performance:
            report = {"report_type": "user_workload", "user": user, "data": performance[user]}
        else:
            report = {"report_type": "user_workload", "all_users": performance}
        return [TextContent(type="text", text=json.dumps(report, indent=2))]

    async def _generate_project_status_report(self):
        """Generate a comprehensive project status report."""
        metrics = self._calculate_task_metrics()
        report = {
            "report_type": "project_status",
            "generated_at": datetime.now().isoformat(),
            "overall_metrics": metrics,
            "tasks_by_priority": self._get_tasks_by_priority(),
            "team_performance": self._get_team_performance(),
            "recommendations": self._get_recommendations()
        }
        return [TextContent(type="text", text=json.dumps(report, indent=2))]

    def _calculate_task_metrics(self):
        """Calculate various task metrics."""
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return {"total_tasks": 0, "message": "No tasks in system"}
        
        status_counts = {status.value: 0 for status in TaskStatus}
        priority_sum = 0
        for task in self.tasks.values():
            status_counts[task.status.value] += 1
            priority_sum += task.priority
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": status_counts["completed"],
            "in_progress_tasks": status_counts["in_progress"],
            "pending_tasks": status_counts["pending"],
            "failed_tasks": status_counts["failed"],
            "completion_rate": status_counts["completed"] / total_tasks * 100,
            "average_priority": priority_sum / total_tasks,
            "assigned_tasks": len([t for t in self.tasks.values() if t.assigned_to]),
            "unassigned_tasks": len([t for t in self.tasks.values() if not t.assigned_to])
        }

    def _get_recent_activity(self):
        """Get recent task activity."""
        recent_tasks = sorted(self.tasks.values(), key=lambda t: t.updated_at, reverse=True)[:5]
        return [
            {"task_id": task.id, "title": task.title, "status": task.status.value, 
             "updated_at": task.updated_at.isoformat()} 
            for task in recent_tasks
        ]

    def _get_tasks_by_priority(self):
        """Group tasks by priority level."""
        priority_groups = {i: [] for i in range(1, 6)}
        for task in self.tasks.values():
            if task.priority in priority_groups:
                priority_groups[task.priority].append({
                    "id": task.id, "title": task.title, 
                    "status": task.status.value, "assigned_to": task.assigned_to
                })
        return priority_groups

    def _get_team_performance(self):
        """Calculate team performance metrics."""
        performance = {}
        for username, user_info in self.users.items():
            user_tasks = [task for task in self.tasks.values() if task.assigned_to == username]
            completed_tasks = [task for task in user_tasks if task.status == TaskStatus.COMPLETED]
            performance[username] = {
                "name": user_info["name"],
                "total_assigned": len(user_tasks),
                "completed": len(completed_tasks),
                "completion_rate": len(completed_tasks) / len(user_tasks) * 100 if user_tasks else 0,
                "average_priority": sum(t.priority for t in user_tasks) / len(user_tasks) if user_tasks else 0
            }
        return performance

    def _get_recommendations(self):
        """Generate recommendations based on current state."""
        recommendations = []
        unassigned = [t for t in self.tasks.values() if not t.assigned_to]
        if unassigned:
            recommendations.append(f"There are {len(unassigned)} unassigned tasks that need attention")
        high_priority_pending = [t for t in self.tasks.values() 
                                 if t.priority >= 3 and t.status == TaskStatus.PENDING]
        if high_priority_pending:
            recommendations.append(f"There are {len(high_priority_pending)} high-priority pending tasks")
        return recommendations

    async def run(self):
        """Run the server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


# ============================================================================
# Document Resource Provider
# ============================================================================

class DocumentResourceProvider:
    """A resource provider that exposes various document types and formats."""

    def __init__(self, server: Server):
        self.server = server
        self.documents = {
            "project_charter": {
                "title": "Project Charter",
                "content": "# Project Charter\n\nThis project aims to build a comprehensive task management system...",
                "format": "markdown",
                "last_modified": datetime.now() - timedelta(days=5)
            },
            "api_spec": {
                "title": "API Specification",
                "content": "# REST API Documentation\n\n## Endpoints\n\n### GET /tasks\nReturns all tasks...",
                "format": "markdown",
                "last_modified": datetime.now() - timedelta(days=2)
            }
        }
        self._register_resources()

    def _register_resources(self):
        @self.server.list_resources()
        async def list_resources():
            resources = []
            # Individual documents
            for doc_id, doc in self.documents.items():
                resources.append(Resource(
                    uri=f"doc://{doc_id}",
                    name=doc["title"],
                    description=f"{doc['format']} document, last modified {doc['last_modified'].strftime('%Y-%m-%d')}",
                    mimeType="text/markdown" if doc["format"] == "markdown" else "text/plain"
                ))
            # Computed resources
            resources.extend([
                Resource(uri="docs://recent", name="Recent Documents", 
                        description="Documents modified in the last week", mimeType="application/json"),
                Resource(uri="docs://search", name="Document Search", 
                        description="Search across all documents", mimeType="application/json")
            ])
            return resources

        @self.server.read_resource()
        async def read_resource(uri: str):
            if uri.startswith("doc://"):
                doc_id = uri[6:]  # remove "doc://" prefix
                if doc_id in self.documents:
                    doc = self.documents[doc_id]
                    return [TextContent(type="text", text=doc["content"])]
                else:
                    raise ValueError(f"Document {doc_id} not found")
            elif uri == "docs://recent":
                cutoff = datetime.now() - timedelta(days=7)
                recent_docs = {
                    doc_id: {"title": doc["title"], "last_modified": doc["last_modified"].isoformat()}
                    for doc_id, doc in self.documents.items() 
                    if doc["last_modified"] > cutoff
                }
                return [TextContent(type="text", text=json.dumps(recent_docs, indent=2))]
            elif uri.startswith("docs://search"):
                query = "api"  # In a real implementation, this would come from URI parameters
                matching_docs = {
                    doc_id: {"title": doc["title"]}
                    for doc_id, doc in self.documents.items() 
                    if query.lower() in doc["content"].lower() or query.lower() in doc["title"].lower()
                }
                return [TextContent(type="text", text=json.dumps(matching_docs, indent=2))]
            else:
                raise ValueError(f"Unknown resource: {uri}")


# ============================================================================
# Email Tool Provider
# ============================================================================

class EmailToolProvider:
    """Tool provider for email operations."""

    def __init__(self, server: Server):
        self.server = server
        self.sent_emails = []  # Store sent emails for demonstration
        self.scheduled_emails = []
        self.email_templates = {}
        self._register_tools()

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="send_email",
                    description="Send an email to one or more recipients",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "array", "items": {"type": "string"}, "description": "Recipients"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                            "priority": {"type": "string", "enum": ["low", "normal", "high"], "description": "Priority"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="schedule_email",
                    description="Schedule an email to be sent at a specific time",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "array", "items": {"type": "string"}},
                            "subject": {"type": "string"},
                            "body": {"type": "string"},
                            "send_at": {"type": "string", "description": "ISO datetime to send"}
                        },
                        "required": ["to", "subject", "body", "send_at"]
                    }
                ),
                Tool(
                    name="create_email_template",
                    description="Create a reusable email template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Template name"},
                            "subject": {"type": "string", "description": "Subject template"},
                            "body": {"type": "string", "description": "Body template with {placeholders}"}
                        },
                        "required": ["name", "subject", "body"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "send_email":
                return await self._send_email(arguments)
            elif name == "schedule_email":
                return await self._schedule_email(arguments)
            elif name == "create_email_template":
                return await self._create_template(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _send_email(self, args):
        """Send an email immediately."""
        try:
            # Validate email addresses
            for email in args["to"]:
                if "@" not in email:
                    raise ValueError(f"Invalid email address: {email}")
            
            # Simulate sending email
            message_id = hashlib.md5(f"{args['to']}{args['subject']}{datetime.now()}".encode()).hexdigest()[:12]
            self.sent_emails.append({
                "message_id": message_id,
                "to": args["to"],
                "subject": args["subject"],
                "sent_at": datetime.now().isoformat()
            })
            
            result = {
                "success": True, 
                "message_id": message_id, 
                "sent_to": args["to"], 
                "sent_at": datetime.now().isoformat()
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            result = {"success": False, "error": str(e)}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _schedule_email(self, args):
        """Schedule an email for later."""
        schedule_id = hashlib.md5(f"{args['to']}{args['send_at']}".encode()).hexdigest()[:12]
        self.scheduled_emails.append({
            "schedule_id": schedule_id,
            "to": args["to"],
            "subject": args["subject"],
            "send_at": args["send_at"]
        })
        result = {"success": True, "schedule_id": schedule_id, "scheduled_for": args["send_at"]}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _create_template(self, args):
        """Create a reusable email template."""
        self.email_templates[args["name"]] = {
            "subject": args["subject"],
            "body": args["body"],
            "created_at": datetime.now().isoformat()
        }
        result = {"success": True, "template_name": args["name"], "message": "Template created successfully"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


# ============================================================================
# Secure MCP Server
# ============================================================================

class SecureMCPServer:
    """An MCP server with comprehensive security features."""

    def __init__(self, name: str, api_key: str):
        self.server = Server(name)
        self.api_key = api_key
        self.authorized_clients = {}
        self.audit_log = []
        self.rate_limits = {}

    async def _authenticate_request(self, request) -> bool:
        """Authenticate incoming requests."""
        auth_header = request.get("auth")
        if not auth_header:
            return False
        # Simple API key check
        return auth_header == self.api_key

    async def _check_rate_limit(self, request) -> bool:
        """Check if the request exceeds rate limits."""
        client_id = request.get("client_id", "unknown")
        current_time = time.time()
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = []
        # Remove old requests (older than 1 minute)
        self.rate_limits[client_id] = [
            req_time for req_time in self.rate_limits[client_id] 
            if current_time - req_time < 60
        ]
        # Check if under limit (max 100 requests per minute)
        if len(self.rate_limits[client_id]) >= 100:
            return False
        # Add current request timestamp
        self.rate_limits[client_id].append(current_time)
        return True

    async def _log_request(self, request):
        """Log incoming requests for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "method": request.get("method"),
            "client_id": request.get("client_id", "unknown"),
            "request_id": request.get("id")
        }
        self.audit_log.append(log_entry)

    async def _log_response(self, request, response):
        """Log responses for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "response",
            "request_id": request.get("id"),
            "success": not response.get("error"),
            "response_size": len(str(response))
        }
        self.audit_log.append(log_entry)

    def get_audit_log(self) -> List[Dict]:
        """Get the audit log for security monitoring."""
        return self.audit_log.copy()


# ============================================================================
# MCP Discovery Service
# ============================================================================

class MCPDiscoveryService:
    """A service for discovering available MCP servers and their capabilities."""

    def __init__(self):
        self.registered_servers = {}
        self.server = Server("mcp-discovery")
        self._setup_discovery_interface()

    def _setup_discovery_interface(self):
        """Set up the discovery interface."""
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="register_server",
                    description="Register an MCP server with the discovery service",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Server name"},
                            "description": {"type": "string", "description": "Server description"},
                            "endpoint": {"type": "string", "description": "Server endpoint URL"},
                            "capabilities": {"type": "array", "items": {"type": "string"}, "description": "List of capabilities"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for discovery"}
                        },
                        "required": ["name", "description", "endpoint", "capabilities"]
                    }
                ),
                Tool(
                    name="discover_servers",
                    description="Discover servers based on capabilities or tags",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "capabilities": {"type": "array", "items": {"type": "string"}, "description": "Required capabilities"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter tags"}
                        }
                    }
                ),
                Tool(
                    name="get_server_info",
                    description="Get detailed information about a specific server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_name": {"type": "string", "description": "Name of the server"}
                        },
                        "required": ["server_name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "register_server":
                return await self._register_server(arguments)
            elif name == "discover_servers":
                return await self._discover_servers(arguments)
            elif name == "get_server_info":
                return await self._get_server_info(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _register_server(self, args):
        """Register a new server."""
        server_info = {
            "name": args["name"],
            "description": args["description"],
            "endpoint": args["endpoint"],
            "capabilities": args["capabilities"],
            "tags": args.get("tags", []),
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        self.registered_servers[args["name"]] = server_info
        result = {"success": True, "message": f"Server '{args['name']}' registered successfully"}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _discover_servers(self, args):
        """Discover servers based on criteria."""
        required_capabilities = args.get("capabilities", [])
        required_tags = args.get("tags", [])
        
        matching_servers = []
        for server_name, server_info in self.registered_servers.items():
            # Check capabilities
            if required_capabilities:
                if not all(cap in server_info["capabilities"] for cap in required_capabilities):
                    continue
            # Check tags
            if required_tags:
                if not any(tag in server_info["tags"] for tag in required_tags):
                    continue
            matching_servers.append(server_info)
        
        result = {"query": args, "matches": len(matching_servers), "servers": matching_servers}
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _get_server_info(self, args):
        """Get detailed information about a server."""
        server_name = args["server_name"]
        if server_name not in self.registered_servers:
            raise ValueError(f"Server '{server_name}' not found")
        server_info = self.registered_servers[server_name]
        return [TextContent(type="text", text=json.dumps(server_info, indent=2))]

    async def run(self):
        """Run the discovery service."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


# ============================================================================
# Main Entry Point and Testing
# ============================================================================

async def test_task_manager():
    """Test the task manager functionality locally without MCP transport."""
    print("=" * 60)
    print("Testing MCP Task Manager Server Components")
    print("=" * 60)
    
    # Create server instance
    task_server = TaskManagerServer()
    
    # Test 1: Show registered tools info
    print("\n1. Registered Tools:")
    print("-" * 40)
    tool_names = ["create_task", "update_task_status", "assign_task", "search_tasks", "generate_report"]
    for name in tool_names:
        print(f"  - {name}")
    
    # Test 2: Show registered resources info
    print("\n2. Registered Resources:")
    print("-" * 40)
    resource_uris = ["tasks://all", "tasks://active", "users://all", "analytics://task_metrics"]
    for uri in resource_uris:
        print(f"  - {uri}")
    
    # Test 3: Show registered prompts info
    print("\n3. Registered Prompts:")
    print("-" * 40)
    prompt_names = ["task_summary", "daily_standup", "project_overview"]
    for name in prompt_names:
        print(f"  - {name}")
    
    # Test 4: Create a new task
    print("\n4. Creating a New Task:")
    print("-" * 40)
    result = await task_server._create_task({
        "title": "Write unit tests",
        "description": "Add comprehensive unit tests for the authentication module",
        "assigned_to": "alice",
        "priority": 3,
        "tags": ["testing", "backend"]
    })
    print(f"  Result: {result[0].text}")
    
    # Test 5: Search for tasks
    print("\n5. Searching for Tasks:")
    print("-" * 40)
    result = await task_server._search_tasks({
        "query": "authentication",
        "status": None,
        "assigned_to": None
    })
    print(f"  Result: {result[0].text}")
    
    # Test 6: Show all tasks
    print("\n6. All Tasks in System:")
    print("-" * 40)
    for task_id, task in task_server.tasks.items():
        print(f"    - Task {task_id}: {task.title} ({task.status.value})")
    
    # Test 7: Get task metrics
    print("\n7. Task Metrics:")
    print("-" * 40)
    metrics = task_server._calculate_task_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Test 8: Generate project status report
    print("\n8. Generating Project Status Report:")
    print("-" * 40)
    result = await task_server._generate_report({"report_type": "project_status"})
    report = json.loads(result[0].text)
    print(f"  Report Type: {report['report_type']}")
    print(f"  Generated At: {report['generated_at']}")
    print(f"  Completion Rate: {report['overall_metrics']['completion_rate']:.1f}%")
    
    # Test 9: Team Performance
    print("\n9. Team Performance:")
    print("-" * 40)
    performance = task_server._get_team_performance()
    for user, stats in performance.items():
        print(f"  {stats['name']}: {stats['completed']}/{stats['total_assigned']} tasks completed")
    
    # Test 10: Update task status
    print("\n10. Updating Task Status:")
    print("-" * 40)
    result = await task_server._update_task_status({
        "task_id": "3",
        "status": "in_progress"
    })
    print(f"  Result: {result[0].text}")
    
    # Test 11: Assign task
    print("\n11. Assigning Task:")
    print("-" * 40)
    result = await task_server._assign_task({
        "task_id": "4",
        "assigned_to": "carol"
    })
    print(f"  Result: {result[0].text}")
    
    # Test 12: Generate summary report
    print("\n12. Summary Report:")
    print("-" * 40)
    result = await task_server._generate_summary_report()
    report = json.loads(result[0].text)
    print(f"  Total Tasks: {report['metrics']['total_tasks']}")
    print(f"  Completed: {report['metrics']['completed_tasks']}")
    print(f"  In Progress: {report['metrics']['in_progress_tasks']}")
    print(f"  Pending: {report['metrics']['pending_tasks']}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)


async def main():
    """Main entry point - runs the server or tests based on arguments."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run tests
        await test_task_manager()
    else:
        # Run the server
        print("Starting MCP Task Manager Server...")
        server = TaskManagerServer()
        await server.run()


if __name__ == "__main__":
    asyncio.run(main())
