import json
from datetime import datetime

class PersonalizationServer:
    """A minimal personalization system demonstrating MCP-like operations."""
    def __init__(self):
        # Sample user profiles. In practice these would come from MCP `resources/read`.
        self.user_profiles = {
            "user_001": {"interests": ["technology", "ai", "programming"], "experience_level": "advanced"},
            "user_002": {"interests": ["business", "marketing", "strategy"], "experience_level": "intermediate"},
            "user_003": {"interests": ["design", "creativity", "art"], "experience_level": "beginner"},
        }
        # Recent user actions (timestamped). A real system would record many more actions.
        self.behaviour_history = [
            ("user_001", "view", "article_001", {"device": "mobile", "time_of_day": "morning"}),
            ("user_001", "like", "article_002", {"device": "desktop", "time_of_day": "afternoon"}),
            ("user_002", "view", "article_003", {"device": "desktop", "time_of_day": "morning"}),
            ("user_003", "view", "article_004", {"device": "mobile", "time_of_day": "evening"}),
        ]
        # Content catalog with popularity scores and tags.
        self.content_items = {
            "article_001": {"title": "Introduction to Machine Learning", "category": "technology", "tags": ["ml", "ai", "beginner"], "popularity": 0.8},
            "article_002": {"title": "Advanced Neural Networks", "category": "technology", "tags": ["ml", "ai", "advanced"], "popularity": 0.6},
            "article_003": {"title": "Marketing Strategy Guide", "category": "business", "tags": ["marketing", "strategy"], "popularity": 0.7},
            "article_004": {"title": "Design Thinking Principles", "category": "design", "tags": ["design", "creativity"], "popularity": 0.9},
            "article_005": {"title": "Python Programming Basics", "category": "technology", "tags": ["programming", "python", "beginner"], "popularity": 0.85},
        }

    def list_resources(self):
        """Return URIs and descriptions of available resources."""
        return [
            {"uri": "profile://user_profiles", "name": "User Profiles", "description": "User preference and demographic data"},
            {"uri": "behavior://user_behavior", "name": "User Behavior Data", "description": "Recent user interactions"},
            {"uri": "content://content_items", "name": "Content Catalog", "description": "Articles and their metadata"},
        ]

    def read_resource(self, uri: str) -> str:
        """Return the JSON representation of a resource."""
        if uri == "profile://user_profiles":
            return json.dumps(self.user_profiles, indent=2)
        elif uri == "behavior://user_behavior":
            return json.dumps([
                {"user_id": user_id, "action": action, "item_id": item_id, "context": context}
                for (user_id, action, item_id, context) in self.behaviour_history
            ], indent=2)
        elif uri == "content://content_items":
            return json.dumps(self.content_items, indent=2)
        else:
            raise ValueError(f"Unknown resource URI: {uri}")

    def get_recommendations(self, user_id: str, context: dict | None = None, limit: int = 3) -> str:
        """Compute simple relevance scores and return a formatted list."""
        context = context or {}
        profile = self.user_profiles.get(user_id)
        if not profile:
            return f"User {user_id} not found"

        interests = [i.lower() for i in profile.get("interests", [])]
        level = profile.get("experience_level", "beginner").lower()
        # Items the user has already interacted with
        viewed = {item_id for (uid, _, item_id, _) in self.behaviour_history if uid == user_id}
        scores = []
        for item_id, meta in self.content_items.items():
            if item_id in viewed:
                continue
            score = 0.0
            # Match user interests to item tags
            tag_matches = sum(1 for interest in interests if any(interest in tag.lower() for tag in meta["tags"]))
            score += 0.4 * tag_matches
            # Experience level match
            if level in meta["tags"]:
                score += 0.3
            # Popularity boost
            score += 0.2 * meta["popularity"]
            # Context boost
            if context.get("time_of_day") == "morning" and "beginner" in meta["tags"]:
                score += 0.1
            scores.append((score, item_id))
        # Sort and build output
        scores.sort(reverse=True, key=lambda x: x[0])
        top = scores[:limit]
        if not top:
            return f"No new recommendations for {user_id}"
        lines = [f"Personalized recommendations for {user_id}:"]
        for idx, (score, item_id) in enumerate(top, 1):
            meta = self.content_items[item_id]
            lines.append(f"{idx}. {meta['title']} (Score: {score:.2f})")
        # Explanation of factors
        lines.append("")
        lines.append("Based on:")
        lines.append(f"- Interests: {', '.join(profile['interests'])}")
        lines.append(f"- Experience level: {profile['experience_level']}")
        lines.append(f"- Recent actions: {sum(1 for (uid, _, _, _) in self.behaviour_history if uid == user_id)}")
        if context:
            lines.append(f"- Context: {context}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Demonstrate the personalization server
    server = PersonalizationServer()
    # List available resources
    print("Resources:")
    for res in server.list_resources():
        print(f"- {res['uri']}: {res['description']}")
    # Read content catalog
    print("\nContent catalog:")
    print(server.read_resource("content://content_items"))
    # Get recommendations for a user with morning context
    print("\nRecommendations:")
    print(server.get_recommendations("user_001", context={"time_of_day": "morning"}, limit=3))
