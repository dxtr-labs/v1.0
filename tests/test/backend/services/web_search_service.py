#!/usr/bin/env python3
"""
🌐 Web Search Service for AI Agents
Provides comprehensive web search capabilities across multiple sources
"""

import os
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus
import json
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    """
    Comprehensive web search service that searches across:
    - Google Search API
    - Reddit API
    - LinkedIn (via web scraping)
    - News sources
    - General web sources
    """
    
    def __init__(self):
        # API Keys (add these to .env.local)
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        
        # Search sources configuration
        self.search_sources = {
            "google": True,
            "reddit": True, 
            "linkedin": True,
            "news": True,
            "general_web": True
        }
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds between requests
        
    async def search_comprehensive(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Perform comprehensive web search across all available sources
        
        Args:
            query: Search query (e.g., "investors interested in ramen bowl companies")
            max_results: Maximum results per source
            
        Returns:
            Dictionary with search results from all sources
        """
        logger.info(f"🔍 Starting comprehensive web search for: '{query}'")
        
        # Sanitize and prepare query
        clean_query = self._sanitize_query(query)
        
        # Prepare search tasks
        search_tasks = []
        
        # Google Search
        if self.search_sources["google"] and self.google_api_key:
            search_tasks.append(self._search_google(clean_query, max_results))
        
        # Reddit Search
        if self.search_sources["reddit"]:
            search_tasks.append(self._search_reddit(clean_query, max_results))
            
        # LinkedIn Search (web scraping)
        if self.search_sources["linkedin"]:
            search_tasks.append(self._search_linkedin(clean_query, max_results))
            
        # News Search
        if self.search_sources["news"]:
            search_tasks.append(self._search_news(clean_query, max_results))
            
        # General Web Search
        if self.search_sources["general_web"]:
            search_tasks.append(self._search_general_web(clean_query, max_results))
        
        # Execute all searches concurrently
        try:
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Compile results
            compiled_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "sources": {},
                "summary": {
                    "total_results": 0,
                    "sources_searched": 0,
                    "sources_successful": 0
                }
            }
            
            source_names = ["google", "reddit", "linkedin", "news", "general_web"]
            
            for i, result in enumerate(results):
                source_name = source_names[i] if i < len(source_names) else f"source_{i}"
                compiled_results["sources"][source_name] = result if not isinstance(result, Exception) else {"error": str(result)}
                
                if not isinstance(result, Exception) and result.get("results"):
                    compiled_results["summary"]["total_results"] += len(result["results"])
                    compiled_results["summary"]["sources_successful"] += 1
                
                compiled_results["summary"]["sources_searched"] += 1
            
            # Generate AI-friendly summary
            compiled_results["ai_summary"] = self._generate_ai_summary(compiled_results)
            
            logger.info(f"✅ Web search completed: {compiled_results['summary']['total_results']} total results")
            return compiled_results
            
        except Exception as e:
            logger.error(f"❌ Web search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _search_google(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search using Google Custom Search API"""
        if not self.google_api_key or not self.google_search_engine_id:
            return {"error": "Google Search API not configured"}
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_search_engine_id,
                "q": query,
                "num": min(max_results, 10)  # Google API max is 10
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get("items", []):
                            results.append({
                                "title": item.get("title"),
                                "url": item.get("link"),
                                "snippet": item.get("snippet"),
                                "source": "Google"
                            })
                        
                        return {
                            "source": "google",
                            "results": results,
                            "total_found": data.get("searchInformation", {}).get("totalResults", "0")
                        }
                    else:
                        return {"error": f"Google Search API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {"error": str(e)}
    
    async def _search_reddit(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Reddit using their API"""
        try:
            # Use Reddit's public search API (no auth required for basic search)
            url = "https://www.reddit.com/search.json"
            params = {
                "q": query,
                "limit": min(max_results, 25),  # Reddit API max is 25
                "sort": "relevance",
                "type": "link"
            }
            
            headers = {
                "User-Agent": "WebSearchBot/1.0"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for post in data.get("data", {}).get("children", []):
                            post_data = post.get("data", {})
                            results.append({
                                "title": post_data.get("title"),
                                "url": f"https://reddit.com{post_data.get('permalink')}",
                                "snippet": post_data.get("selftext", "")[:200],
                                "subreddit": post_data.get("subreddit"),
                                "score": post_data.get("score", 0),
                                "source": "Reddit"
                            })
                        
                        return {
                            "source": "reddit",
                            "results": results,
                            "total_found": len(results)
                        }
                    else:
                        return {"error": f"Reddit API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
            return {"error": str(e)}
    
    async def _search_linkedin(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search LinkedIn using web scraping approach"""
        try:
            # LinkedIn search via DuckDuckGo (to avoid LinkedIn's anti-bot measures)
            search_query = f"site:linkedin.com {query}"
            return await self._search_duckduckgo(search_query, max_results, source_name="LinkedIn")
            
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
            return {"error": str(e)}
    
    async def _search_news(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search news sources"""
        try:
            # Search news sites via DuckDuckGo
            news_sites = "site:techcrunch.com OR site:reuters.com OR site:bloomberg.com OR site:cnbc.com"
            search_query = f"({news_sites}) {query}"
            return await self._search_duckduckgo(search_query, max_results, source_name="News")
            
        except Exception as e:
            logger.error(f"News search error: {e}")
            return {"error": str(e)}
    
    async def _search_general_web(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search general web using DuckDuckGo"""
        return await self._search_duckduckgo(query, max_results, source_name="General Web")
    
    async def _search_duckduckgo(self, query: str, max_results: int, source_name: str = "DuckDuckGo") -> Dict[str, Any]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        
                        # Get related topics
                        for topic in data.get("RelatedTopics", [])[:max_results]:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append({
                                    "title": topic.get("Text", "").split(" - ")[0],
                                    "url": topic.get("FirstURL", ""),
                                    "snippet": topic.get("Text", ""),
                                    "source": source_name
                                })
                        
                        # If no related topics, try abstract
                        if not results and data.get("Abstract"):
                            results.append({
                                "title": data.get("Heading", query),
                                "url": data.get("AbstractURL", ""),
                                "snippet": data.get("Abstract", ""),
                                "source": source_name
                            })
                        
                        return {
                            "source": source_name.lower().replace(" ", "_"),
                            "results": results,
                            "total_found": len(results)
                        }
                    else:
                        return {"error": f"DuckDuckGo API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return {"error": str(e)}
    
    def _sanitize_query(self, query: str) -> str:
        """Clean and prepare search query"""
        # Remove special characters that might break APIs
        query = re.sub(r'[^\w\s\-\+\(\)\"\':]', ' ', query)
        # Normalize whitespace
        query = ' '.join(query.split())
        return query.strip()
    
    def _generate_ai_summary(self, search_results: Dict[str, Any]) -> str:
        """Generate AI-friendly summary of search results"""
        summary_parts = []
        
        summary_parts.append(f"Search completed for '{search_results['query']}'")
        summary_parts.append(f"Found {search_results['summary']['total_results']} total results across {search_results['summary']['sources_successful']} sources")
        
        # Summarize by source
        for source_name, source_data in search_results["sources"].items():
            if isinstance(source_data, dict) and source_data.get("results"):
                count = len(source_data["results"])
                summary_parts.append(f"• {source_name.title()}: {count} results")
        
        return ". ".join(summary_parts) + "."

# Global instance
web_search_service = WebSearchService()


# Example usage and testing
async def test_web_search():
    """Test the web search functionality"""
    query = "investors interested in ramen bowl companies"
    results = await web_search_service.search_comprehensive(query, max_results=5)
    
    print("🔍 Web Search Results:")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(test_web_search())
