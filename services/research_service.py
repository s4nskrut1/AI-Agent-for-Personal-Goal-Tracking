"""
Optional Web Research Service for GoalMate via Tavily API.
Used selectively when current web information (courses, roadmaps, project ideas) genuinely adds value.
Never invoked for basic internal goal operations.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("GoalMate.Research")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()


def search_web_resources(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Executes a web search via Tavily API if configured.
    Returns structured results: [{'title': ..., 'url': ..., 'content': ...}].
    If Tavily key is missing, provides curated high-quality educational suggestions.
    """
    if not TAVILY_API_KEY or TAVILY_API_KEY.startswith("YOUR_"):
        logger.info("Tavily API key not set. Using curated educational recommendations.")
        return {
            "source": "curated",
            "query": query,
            "results": [
                {
                    "title": "Official Python Tutorial & Documentation",
                    "url": "https://docs.python.org/3/tutorial/",
                    "snippet": "Comprehensive, canonical guide to Python 3 fundamentals, data structures, OOP, and standard libraries."
                },
                {
                    "title": "FreeCodeCamp: Python for Beginners",
                    "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
                    "snippet": "Interactive curriculum with hands-on projects, exercises, and certification."
                },
                {
                    "title": "Real Python Tutorials & Practical Guides",
                    "url": "https://realpython.com/",
                    "snippet": "High-quality, industry-standard tutorials covering Python syntax, API creation with FastAPI, and OOP design."
                }
            ]
        }

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_domains=["docs.python.org", "realpython.com", "github.com", "freecodecamp.org", "coursera.org", "medium.com"]
        )
        formatted = []
        for item in response.get("results", []):
            formatted.append({
                "title": item.get("title", "Resource"),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:280]
            })
        return {
            "source": "tavily_live",
            "query": query,
            "results": formatted
        }
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}. Falling back to curated resources.")
        return {
            "source": "fallback",
            "error": str(e),
            "results": [
                {
                    "title": "Official Python Tutorial",
                    "url": "https://docs.python.org/3/tutorial/",
                    "snippet": "Canonical guide covering Python fundamentals, data structures, and best practices."
                }
            ]
        }


# Convenience alias
search_resources = search_web_resources
