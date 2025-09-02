class MemoryMCPServer:
    """Minimal in-memory MCP server for conversation history."""
    def __init__(self):
        self.messages = []  # list of {'sender': ..., 'text': ...}

    def list_resources(self):
        return ['history']

    def read_resource(self, name):
        return '\n'.join(f"{m['sender']}: {m['text']}" for m in self.messages)

    def write_resource(self, name, message):
        self.messages.append(message)

# In LangChain, you'd implement a Memory class that calls read_resource() and write_resource()
# on the MCP server to persist context across interactions.
