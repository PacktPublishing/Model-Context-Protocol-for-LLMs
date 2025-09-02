class DummyMCPServer:
    """Expose simple tools via list_tools() and call_tool()."""

    def __init__(self):
        self.tools = {
            "search": self.search,
            "analyze": self.analyze,
        }

    def list_tools(self):
        # Return metadata for each tool
        return [
            {"name": "search", "description": "Search documents for a query"},
            {"name": "analyze", "description": "Analyze text for sentiment"},
        ]

    def call_tool(self, name: str, args: dict):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name](**args)

    def search(self, query: str) -> str:
        # Return hard-coded documents containing the query
        documents = [
            "Stanford study: Remote work improves productivity by 13%.",
            "MIT and Microsoft report: company-wide remote work reduces "
            "cross-team collaboration.",
        ]
        matches = [doc for doc in documents if query.lower() in doc.lower()]
        return "\n".join(matches) if matches else "No documents found."

    def analyze(self, data: str) -> str:
        # Count positive and negative words in the data
        positive = data.lower().count("improves")
        negative = data.lower().count("reduces")
        return (
            f"Analysis summary: {positive} positive signal(s), "
            f"{negative} negative signal(s)."
        )


class MCPClient:
    """Discover tools on initialization and forward calls to the server."""

    def __init__(self, server: DummyMCPServer):
        self.server = server
        self.tools = {
            tool["name"]: tool for tool in server.list_tools()
        }

    def call_tool(self, name: str, args: dict) -> str:
        return self.server.call_tool(name, args)


class ResearchAgent:
    def __init__(self, client: MCPClient):
        self.client = client

    def research(self, query: str) -> str:
        print(f"ResearchAgent: searching for '{query}' via MCP...")
        results = self.client.call_tool("search", {"query": query})
        print(f"ResearchAgent: found documents:\n{results}\n")
        return results

class AnalysisAgent:
    def __init__(self, client: MCPClient):
        self.client = client

    def analyze(self, data: str) -> str:
        print("AnalysisAgent: analyzing data via MCP...")
        summary = self.client.call_tool("analyze", {"data": data})
        print(f"AnalysisAgent: {summary}\n")
        return summary

def simulate_conversation():
    server = DummyMCPServer()
    client = MCPClient(server)
    research_agent = ResearchAgent(client)
    analysis_agent = AnalysisAgent(client)
    query = "remote work"
    docs = research_agent.research(query)
    analysis_agent.analyze(docs)

if __name__ == "__main__":
    simulate_conversation()
