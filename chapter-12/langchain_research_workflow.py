# Pseudocode for the research assistant workflow
query = "impact of microplastics on marine life"

# Step 1: Document retrieval
docs = doc_loader.load_documents()                 # from MCP document servers
retrieved = rag_system.search(query)              # top documents via TF–IDF

# Step 2: Summarisation via MCP tool
summaries = []
for doc in retrieved:
    summary = langchain_agent.run_tool("summarize", {"text": doc.text})
    summaries.append(summary)

# Step 3: Context storage (memory)
memory_server.write_resource("history", {"sender": "assistant", "text": "Summary of documents..."})

# Step 4: User-facing response
answer = langchain_agent.run_tool("generate_report", {"summaries": summaries})
print(answer)
