# Model Context Protocol for LLMs

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Code samples and examples for the book **"Model Context Protocol for LLMs"**, published by Packt.

## Overview

This repository contains working code examples that accompany each chapter of the book. The examples demonstrate the Model Context Protocol (MCP) - a standardized protocol for enabling AI systems to communicate with external tools, resources, and services.

## Prerequisites

- Python 3.10+
- pip (Python package manager)

## Installation

```bash
# Clone the repository
git clone https://github.com/PacktPublishing/Model-Context-Protocol-for-LLMs.git
cd Model-Context-Protocol-for-LLMs

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install mcp
```

## Chapter Contents

### [Chapter 1: Introduction to Model Context Protocol](chapter-01/)
Basic MCP server implementation examples demonstrating core concepts.
- `hello_server.py` - Official MCP server using the mcp library
- `test_client.py` - Test client for the hello server

### [Chapter 2: Theoretical Foundations of Multi-Agent Systems](chapter-02/)
Multi-agent system examples demonstrating agent coordination and communication.
- `smart_home_agents.py` - Multiple specialized agents in a smart home environment

### [Chapter 4: MCP Components and Interfaces](chapter-04/)
Comprehensive examples of MCP's core components: resource providers, tool providers, and prompt providers.
- `task_manager_server.py` - Full-featured task management MCP server with:
  - Resource providers (tasks, users, analytics)
  - Tool providers (create, update, search, report)
  - Prompt providers (summaries, standups, overviews)
  - Security interfaces (authentication, rate limiting)
  - Discovery interfaces

### [Chapter 5: MCP Architecture Overview](chapter-05/)
Examples demonstrating MCP's architecture including client-server interactions and JSON-RPC communication.
- `mcp_architecture.py` - Architecture demonstration with:
  - SimpleMCPServer and SimpleMCPClient
  - JSON-RPC message format examples
  - Security concepts (authentication, audit logging)

### [Chapter 6: Server-Side Implementation](chapter-06/)
Comprehensive server-side implementation with context-aware providers and security.
- `mcp_server_implementation.py` - Document MCP server with:
  - Context-aware resource filtering by user role
  - Role-based access control (Guest, Employee, Manager, Admin)
  - Intelligent search with relevance scoring
  - Adaptive prompt generation
  - Audit logging

### [Chapter 7: Client-Side Integration](chapter-07/)
Client-side integration examples including workflow orchestration and framework integration.
- `mcp_client_integration.py` - MCP client with:
  - Capability discovery across multiple servers
  - Goal-based workflow planning and execution
  - Context management (distributed system memory)
  - Security with permission delegation
  - LangChain and AutoGen integration patterns

### [Chapter 9: MCP Performance Optimization](chapter-09/)
Progress notifications, predictive caching, and sequential vs parallel execution patterns.
- `performance_optimization.py` - Performance optimization techniques for MCP systems

### [Chapter 10: MCP and Multi-Agent Systems](chapter-10/)
MCP integration with multi-agent frameworks using an AutoGen-inspired pattern.
- `multi_agent_mcp.py` - Multi-agent coordination through MCP

### [Chapter 11: MCP for Retrieval-Augmented Generation](chapter-11/)
Simplified RAG system using MCP-style data sources.
- `mcp_rag_system.py` - RAG pipeline with MCP resource integration

### [Chapter 13: Integrating MCP with AutoGen](chapter-13/)
MCP tool wrapping for AutoGen-style multi-agent systems.
- `autogen_mcp_integration.py` - AutoGen agents using MCP tools

### [Chapter 14: MCP for Enterprise Knowledge Management](chapter-14/)
MCP resource provider for enterprise document management.
- `enterprise_document_store.py` - Enterprise document store with access control

### [Chapter 15: MCP for Personalization and Recommendation Systems](chapter-15/)
MCP components for personalization and recommendation systems.
- `personalization_server.py` - User profiling and content recommendation

### [Chapter 16: Multimodal Applications](chapter-16/)
Multimodal content analysis (images, text, audio) through a unified MCP interface.
- `multimodal_analyzer.py` - Unified multimodal content analyzer

### [Chapter 17: Evaluation Methodologies](chapter-17/)
Comprehensive evaluation framework covering discovery, performance, reliability, and UX.
- `mcp_evaluation_framework.py` - Multi-dimensional MCP evaluation suite

### [Chapter 18: Performance Benchmarks and Testing](chapter-18/)
Benchmarking suite measuring discovery, coordination, scalability, and end-to-end scenarios with SQLite storage.
- `mcp_benchmarks.py` - Benchmark suite with historical result tracking

### [Chapter 19: Optimization Strategies](chapter-19/)
Context-aware caching, load balancing, DAG orchestration, and performance monitoring.
- `mcp_optimization_strategies.py` - Four optimization strategies with interactive demos

### [Chapter 20: Future Directions](chapter-20/)
Forward-looking MCP framework for capability composition, multi-agent collaboration, and emergent behaviors.
- `future_mcp_framework.py` - Next-generation MCP patterns and architectures

## Running the Examples

Each chapter directory contains a README with specific instructions. Generally:

```bash
# Navigate to chapter directory
cd chapter-04

# Run the example (most support --test or --help flags)
python task_manager_server.py --test
```

## Quick Start

```bash
# Chapter 1 - Hello MCP
python chapter-01/hello_server.py

# Chapter 4 - MCP Components
python chapter-04/task_manager_server.py --test

# Chapter 5 - Architecture
python chapter-05/mcp_architecture.py --all

# Chapter 6 - Server Implementation
python chapter-06/mcp_server_implementation.py

# Chapter 7 - Client Integration
python chapter-07/mcp_client_integration.py

# Chapter 9 - Performance Optimization
python chapter-09/performance_optimization.py

# Chapter 10 - Multi-Agent Systems
python chapter-10/multi_agent_mcp.py

# Chapter 11 - RAG with MCP
python chapter-11/mcp_rag_system.py

# Chapter 13 - AutoGen Integration
python chapter-13/autogen_mcp_integration.py

# Chapter 14 - Enterprise Knowledge
python chapter-14/enterprise_document_store.py

# Chapter 15 - Personalization
python chapter-15/personalization_server.py

# Chapter 16 - Multimodal Applications
python chapter-16/multimodal_analyzer.py

# Chapter 17 - Evaluation
python chapter-17/mcp_evaluation_framework.py

# Chapter 18 - Benchmarks
python chapter-18/mcp_benchmarks.py

# Chapter 19 - Optimization
python chapter-19/mcp_optimization_strategies.py

# Chapter 20 - Future Directions
python chapter-20/future_mcp_framework.py
```

## Key Concepts Covered

| Chapter | Key Topics |
|---------|------------|
| 1 | MCP basics, server structure, tools and resources |
| 2 | Multi-agent systems, coordination, emergent behaviors |
| 4 | Resource/Tool/Prompt providers, security, discovery |
| 5 | Client-server architecture, JSON-RPC, capability negotiation |
| 6 | Context-aware servers, RBAC, audit logging |
| 7 | Client orchestration, workflows, framework integration |
| 9 | Progress notifications, predictive caching, parallel execution |
| 10 | Multi-agent coordination, capability-based routing |
| 11 | Retrieval-augmented generation, document chunking, relevance scoring |
| 12 | LangChain tool wrapping, MCP-backed memory, research workflows |
| 13 | AutoGen integration, multi-agent MCP tool sharing |
| 14 | Enterprise document management, access control, metadata |
| 15 | User profiling, content recommendation, personalization |
| 16 | Multimodal analysis, image/text/audio processing |
| 17 | Evaluation frameworks, discovery/performance/reliability metrics |
| 18 | Benchmarking, latency percentiles, SQLite result persistence |
| 19 | Caching, load balancing, DAG orchestration, regression detection |
| 20 | Capability composition, emergent behaviors, future MCP patterns |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Published by Packt Publishing
