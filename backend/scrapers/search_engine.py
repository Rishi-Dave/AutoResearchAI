"""
Integrates with SerpAPI to search the web.
This is our starting point for finding information
"""

import os
from serpapi import Client
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SearchEngine:
    """
    Wrapper for search engine API
    We use SerpAPI because it handles:
    - Rate limiting
    - Proxy Rotation
    - Result parsing
    """

    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_KEY not found")
        self.client = Client(api_key=self.api_key)
        

    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search for a query and return structued results

        Args:
            query: Search term
            num_results: Number of results to return

        Returns:
            List of search results with title, link, snippet
        """

        params = {
            "q": query,
            "num": num_results,
            "engine": "google"
        }

        results = self.client.search(params)

        parsed_results = []
        for result in results.get("organic_results", []):
            parsed_results.append({
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
                "date_retrieved": datetime.now().isoformat()
            })

        return parsed_results