"""Simple MCP‑based document loader and retrieval example.

This example demonstrates how an MCP client could treat MCP servers as document
stores for retrieval‑augmented generation. We implement a minimal in‑memory
server and loader, then build a tiny RAG system using scikit‑learn's TF–IDF
vectorizer to search documents. This avoids external dependencies on the
`langchain` or `mcp` Python packages while still illustrating the core
concepts.
"""

from dataclasses import dataclass
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

@dataclass
class Document:
    """Represents a document with text and associated metadata."""
    text: str
    metadata: Dict[str, str]

class DummyMCPServer:
    """A simple in‑memory MCP server that exposes documents as resources."""
    def __init__(self, resources: Dict[str, str]):
        self.resources = resources

    def list_resources(self) -> List[str]:
        return list(self.resources.keys())

    def read_resource(self, name: str) -> str:
        return self.resources[name]
