# Simplified RAG system that does not rely on any external MCP libraries.
# In this example we simulate MCP servers by storing data in in‑memory dictionaries.

class MCPRAGSystem:
    """A simple RAG system using local data sources to simulate MCP retrieval."""

    def __init__(self):
        self.data_sources = {}

    def add_data_source(self, source_name: str, documents: dict) -> None:
        """Add a data source with a mapping of URI to text content."""
        self.data_sources[source_name] = documents

    def retrieve_information(self, query: str, max_results: int = 5):
        """Retrieve relevant information from local data sources."""
        query_words = set(query.lower().split())
        results = []
        for source_name, docs in self.data_sources.items():
            for uri, content in docs.items():
                content_words = set(content.lower().split())
                # Simple Jaccard similarity
                intersection = query_words & content_words
                union = query_words | content_words
                score = len(intersection) / len(union) if union else 0.0
                if score > 0:
                    results.append({
                        'source': source_name,
                        'uri': uri,
                        'content': content[:200],  # truncate for display
                        'relevance_score': score
                    })
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:max_results]

    def generate_response(self, query: str, retrieved_info: list) -> str:
        """Generate a simple response using retrieved information."""
        if not retrieved_info:
            return "I couldn't find relevant information."
        context = "\n\n".join(
            [f"Source: {info['source']}\nContent: {info['content']}" for info in retrieved_info]
        )
        return (
            f"Based on the available information:\n\n{context}\n\n"
            f"Summary: The query '{query}' is related to {len(retrieved_info)} document(s) from the connected data sources."
        )


# Example usage
if __name__ == "__main__":
    rag = MCPRAGSystem()
    # Add two simple data sources to simulate MCP servers
    rag.add_data_source('server1', {
        'doc1': 'Retrieval augmented generation enhances language models by retrieving relevant documents and augmenting generation with factual information.',
        'doc2': 'Model Context Protocol provides standardized access to external data sources and tools.'
    })
    rag.add_data_source('server2', {
        'doc3': 'MCP enables AI systems to connect to databases, APIs, and other tools using a unified JSON-RPC interface.'
    })
    query = 'What does MCP do in RAG systems?'
    retrieved = rag.retrieve_information(query)
    print('Retrieved information:', retrieved)
    print('Generated response:', rag.generate_response(query, retrieved))
