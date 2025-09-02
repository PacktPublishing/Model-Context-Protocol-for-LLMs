# Chapter 14: MCP for Enterprise Knowledge Management

Example demonstrating an MCP resource provider for enterprise document management.

## Code Examples

### `enterprise_document_store.py` - Enterprise Document Store
A document management system implementing MCP resource provider patterns for enterprise knowledge.

```bash
python enterprise_document_store.py
```

## Features Demonstrated

### DocumentStore (MCP Resource Provider)
- `list_resources()` - MCP-style resource listing with metadata
- `search_documents()` - Keyword search with department and classification filters
- `get_summary()` - Aggregate statistics about the document store

### Enterprise Document Types
- Internal documents (Employee Handbook, Product Roadmap, Security Guidelines)
- Confidential documents (Q4 Financial Report)
- Public documents (Customer Success Stories)

### Search and Filtering
- Full-text search across title, content, and tags
- Department filtering (HR, Finance, Product, IT, Marketing)
- Classification filtering (public, internal, confidential)

## Expected Output
```
Found 5 document resources:
  • Employee Handbook (doc://0)
  • Q4 Financial Report (doc://1)
  • Product Roadmap 2024 (doc://2)

Search results for 'security':
• Security Guidelines
  Department: IT | Author: CISO | Classification: internal
  ...

Enterprise Document Store Summary
===============================
Total Documents: 5
...
```

## Key Concepts
- MCP resource providers for enterprise data
- Document classification and access control
- Search and metadata patterns
