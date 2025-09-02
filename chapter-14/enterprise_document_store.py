class DocumentStore:
    """Simple document store that mimics an MCP resource provider."""
    def __init__(self) -> None:
        # In a real system this data would come from SharePoint, Confluence, databases, etc.
        self.documents = [
            {
                "title": "Employee Handbook",
                "content": "Complete guide to company policies and procedures...",
                "department": "HR",
                "author": "HR Team",
                "created_date": "2024-01-15",
                "classification": "internal",
                "tags": ["policies", "procedures", "hr"],
            },
            {
                "title": "Q4 Financial Report",
                "content": "Quarterly financial analysis and projections...",
                "department": "Finance",
                "author": "CFO",
                "created_date": "2024-01-10",
                "classification": "confidential",
                "tags": ["finance", "quarterly", "analysis"],
            },
            {
                "title": "Product Roadmap 2024",
                "content": "Strategic product development plans for 2024...",
                "department": "Product",
                "author": "Product Manager",
                "created_date": "2024-01-05",
                "classification": "internal",
                "tags": ["product", "roadmap", "strategy"],
            },
            {
                "title": "Security Guidelines",
                "content": "Information security policies and best practices...",
                "department": "IT",
                "author": "CISO",
                "created_date": "2024-01-20",
                "classification": "internal",
                "tags": ["security", "policies", "it"],
            },
            {
                "title": "Customer Success Stories",
                "content": "Case studies and testimonials from key customers...",
                "department": "Marketing",
                "author": "Marketing Team",
                "created_date": "2024-01-12",
                "classification": "public",
                "tags": ["marketing", "customers", "success"],
            },
        ]

    def list_resources(self) -> list:
        """Return a list of document metadata similar to an MCP `resources/list` response."""
        resources = []
        for idx, doc in enumerate(self.documents):
            resources.append({
                "uri": f"doc://{idx}",
                "name": doc["title"],
                "description": f"{doc['classification'].title()} document from {doc['department']} by {doc['author']}"
            })
        return resources

    def search_documents(self, query: str, department: str | None = None, classification: str | None = None) -> list:
        """Return documents whose title, content or tags match a query with optional filters."""
        query_lower = query.lower()
        results = []
        for idx, doc in enumerate(self.documents):
            if (query_lower in doc["title"].lower() or
                query_lower in doc["content"].lower() or
                any(query_lower in tag for tag in doc["tags"])):
                if department and doc["department"] != department:
                    continue
                if classification and doc["classification"] != classification:
                    continue
                results.append({
                    "title": doc["title"],
                    "department": doc["department"],
                    "author": doc["author"],
                    "classification": doc["classification"],
                    "preview": doc["content"][:100],
                    "uri": f"doc://{idx}"
                })
        return results

    def get_summary(self) -> str:
        """Return summary statistics about the document store."""
        total_docs = len(self.documents)
        from collections import Counter
        dept_counts = Counter(doc["department"] for doc in self.documents)
        class_counts = Counter(doc["classification"] for doc in self.documents)
        summary = (
            "Enterprise Document Store Summary\n"
            "===============================\n\n"
            f"Total Documents: {total_docs}\n"
            f"Departments: {len(dept_counts)}\n"
            f"Classifications: {len(class_counts)}\n\n"
            "Documents by Department:\n"
        )
        for dept, count in dept_counts.items():
            summary += f"  • {dept}: {count} documents\n"
        summary += "\nDocuments by Classification:\n"
        for classif, count in class_counts.items():
            summary += f"  • {classif}: {count} documents\n"
        return summary


# Demonstration
if __name__ == "__main__":
    store = DocumentStore()
    
    # List available document resources
    resources = store.list_resources()
    print(f"Found {len(resources)} document resources:")
    for res in resources[:3]:
        print(f"  • {res['name']} ({res['uri']})")

    # Search for a keyword
    results = store.search_documents("security")
    print("\nSearch results for 'security':")
    if results:
        for res in results:
            print(f"• {res['title']}\n  Department: {res['department']} | Author: {res['author']} | Classification: {res['classification']}\n  Preview: {res['preview']}...\n  URI: {res['uri']}\n")
    else:
        print("No documents found for this query.\n")

    # Print summary statistics
    print(store.get_summary())
