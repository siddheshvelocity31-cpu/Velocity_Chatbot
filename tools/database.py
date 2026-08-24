"""Knowledge base and mock database lookup tool for the Gemini Chatbot."""

from typing import Dict, Any, List, Optional

MOCK_KNOWLEDGE_BASE = [
    {
        "id": "KB-101",
        "category": "return_policy",
        "title": "30-Day Return & Refund Policy",
        "content": "Customers can return items within 30 days of delivery. Items must be in original condition with tags attached. Refunds are processed within 3-5 business days.",
        "tags": ["returns", "refunds", "policy", "warranty"]
    },
    {
        "id": "KB-102",
        "category": "shipping",
        "title": "Shipping Rates & Delivery Times",
        "content": "Standard shipping takes 3-5 business days ($4.99 or free on orders over $50). Express shipping takes 1-2 business days ($14.99). International shipping takes 7-14 business days.",
        "tags": ["shipping", "delivery", "rates", "express", "international"]
    },
    {
        "id": "KB-103",
        "category": "products",
        "title": "QuantumPro Ultra Laptop Specs",
        "content": "The QuantumPro Ultra features a 14-inch OLED display, 32GB RAM, 1TB NVMe SSD, M4 processor, 18-hour battery life, and weights 1.2 kg. Price: $1,499.",
        "tags": ["laptop", "quantumpro", "hardware", "specs", "price"]
    },
    {
        "id": "KB-104",
        "category": "products",
        "title": "AeroBuds Pro Wireless Earbuds",
        "content": "AeroBuds Pro feature Active Noise Cancellation (ANC), Transparency Mode, 28 hours total playback with charging case, and IPX5 water resistance. Price: $129.",
        "tags": ["audio", "earbuds", "headphones", "anc", "price"]
    },
    {
        "id": "KB-105",
        "category": "support",
        "title": "Customer Support Operating Hours",
        "content": "Live chat and phone support are available Monday through Friday from 9:00 AM to 8:00 PM EST. Weekend email support response time is within 12 hours.",
        "tags": ["hours", "contact", "support", "email", "phone"]
    }
]


def search_knowledge_base(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Search company knowledge base, product information, and policies.

    Args:
        query: Keywords to search for (e.g. 'return policy', 'laptop price', 'shipping cost').
        category: Optional category filter ('return_policy', 'shipping', 'products', 'support').

    Returns:
        A dictionary containing matched knowledge base articles and summaries.
    """
    query_terms = query.lower().split()
    matched_articles: List[Dict[str, Any]] = []

    for article in MOCK_KNOWLEDGE_BASE:
        if category and category.lower() != "all" and article["category"].lower() != category.lower():
            continue

        title_lower = article["title"].lower()
        content_lower = article["content"].lower()
        tags_lower = [t.lower() for t in article["tags"]]

        score = 0
        for term in query_terms:
            if term in title_lower:
                score += 3
            if any(term in tag for tag in tags_lower):
                score += 2
            if term in content_lower:
                score += 1

        if score > 0:
            matched_articles.append({
                "id": article["id"],
                "category": article["category"],
                "title": article["title"],
                "content": article["content"],
                "relevance_score": score
            })

    matched_articles.sort(key=lambda x: x["relevance_score"], reverse=True)

    return {
        "status": "success",
        "query": query,
        "results_count": len(matched_articles),
        "articles": matched_articles[:3]
    }
