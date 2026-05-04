import os
from typing import List, Dict, Any
from tavily import TavilyClient

def web_search(query: str, api_key: str = None) -> List[Dict[str, Any]]:
    """
    Performs a web search using Tavily.
    """
    if not api_key:
        api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        return [{"title": "Error", "content": "No Tavily API key provided.", "url": ""}]
    
    try:
        tavily = TavilyClient(api_key=api_key)
        # We use search depth "advanced" for better research insights
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "Search Failed", "content": str(e), "url": ""}]

def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Formats search results into a readable markdown string.
    """
    if not results:
        return "No results found."
    
    formatted = ""
    for idx, res in enumerate(results, 1):
        formatted += f"### {idx}. {res.get('title')}\n"
        formatted += f"Source: {res.get('url')}\n\n"
        formatted += f"{res.get('content')}\n\n"
        formatted += "---\n\n"
    return formatted
