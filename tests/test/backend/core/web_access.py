# backend/core/web_access.py
# Web access module for AI to search internet and make HTTP requests

import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import quote
import re

logger = logging.getLogger(__name__)

class WebAccessEngine:
    """Enhanced web access engine for AI internet capabilities"""
    
    def __init__(self):
        self.session = None
        self.search_apis = {
            "duckduckgo": "https://api.duckduckgo.com/",
            "wikipedia": "https://en.wikipedia.org/api/rest_v1/page/summary/",
            "news": "https://newsapi.org/v2/everything"
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            logger.info(f"🔍 Searching web for: {query}")
            
            # Use DuckDuckGo Instant Answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(self.search_apis["duckduckgo"], params=params) as response:
                data = await response.json()
                
                results = {
                    "query": query,
                    "abstract": data.get("Abstract", ""),
                    "abstract_text": data.get("AbstractText", ""),
                    "definition": data.get("Definition", ""),
                    "answer": data.get("Answer", ""),
                    "related_topics": []
                }
                
                # Add related topics
                for topic in data.get("RelatedTopics", [])[:num_results]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results["related_topics"].append({
                            "text": topic["Text"],
                            "url": topic.get("FirstURL", "")
                        })
                
                logger.info(f"✅ Found {len(results['related_topics'])} web results")
                return results
                
        except Exception as e:
            logger.error(f"❌ Web search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "abstract": f"Search failed for '{query}': {str(e)}"
            }
    
    async def get_wikipedia_summary(self, topic: str) -> Dict[str, Any]:
        """Get Wikipedia summary for a topic"""
        try:
            logger.info(f"📚 Getting Wikipedia summary for: {topic}")
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Clean topic for URL
            clean_topic = quote(topic.replace(" ", "_"))
            url = f"{self.search_apis['wikipedia']}{clean_topic}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {
                        "title": data.get("title", topic),
                        "summary": data.get("extract", ""),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", "") if data.get("thumbnail") else "",
                        "source": "Wikipedia"
                    }
                    
                    logger.info(f"✅ Wikipedia summary retrieved for {topic}")
                    return result
                else:
                    return {
                        "title": topic,
                        "summary": f"Wikipedia article not found for '{topic}'",
                        "error": f"HTTP {response.status}",
                        "source": "Wikipedia"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Wikipedia search failed: {e}")
            return {
                "title": topic,
                "summary": f"Failed to retrieve Wikipedia information for '{topic}': {str(e)}",
                "error": str(e),
                "source": "Wikipedia"
            }
    
    async def make_http_request(self, url: str, method: str = "GET", data: dict = None, headers: dict = None) -> Dict[str, Any]:
        """Make HTTP request to any URL"""
        try:
            logger.info(f"🌐 Making {method} request to: {url}")
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            default_headers = {
                "User-Agent": "AI-Assistant/1.0 (Web Access Engine)"
            }
            if headers:
                default_headers.update(headers)
            
            kwargs = {
                "headers": default_headers,
                "timeout": aiohttp.ClientTimeout(total=10)
            }
            
            if data and method.upper() in ["POST", "PUT", "PATCH"]:
                kwargs["json"] = data
            
            async with self.session.request(method.upper(), url, **kwargs) as response:
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    content = await response.json()
                else:
                    content = await response.text()
                
                result = {
                    "url": url,
                    "method": method.upper(),
                    "status": response.status,
                    "headers": dict(response.headers),
                    "content": content,
                    "content_type": content_type,
                    "success": 200 <= response.status < 300
                }
                
                logger.info(f"✅ HTTP request completed: {response.status}")
                return result
                
        except Exception as e:
            logger.error(f"❌ HTTP request failed: {e}")
            return {
                "url": url,
                "method": method.upper(),
                "error": str(e),
                "success": False
            }
    
    async def get_current_news(self, topic: str = None, num_articles: int = 5) -> Dict[str, Any]:
        """Get current news (simulated for demo - would need API key for real NewsAPI)"""
        try:
            logger.info(f"📰 Getting current news about: {topic or 'general'}")
            
            # For demo purposes, return structured news data
            # In production, you'd use a real news API with API key
            news_data = {
                "query": topic or "general news",
                "articles": [
                    {
                        "title": f"Latest developments in {topic or 'technology'}",
                        "description": f"Recent updates and trends in {topic or 'the tech industry'}",
                        "source": "Tech News Daily",
                        "published_at": "2025-07-13T05:00:00Z",
                        "url": "https://example-news.com/article1"
                    },
                    {
                        "title": f"Market analysis: {topic or 'Global markets'} outlook",
                        "description": f"Expert analysis on {topic or 'current market conditions'}",
                        "source": "Financial Times",
                        "published_at": "2025-07-13T04:30:00Z",
                        "url": "https://example-news.com/article2"
                    }
                ],
                "total_results": num_articles,
                "note": "Demo news data - integrate with real news API for live results"
            }
            
            logger.info(f"✅ Retrieved {len(news_data['articles'])} news articles")
            return news_data
            
        except Exception as e:
            logger.error(f"❌ News retrieval failed: {e}")
            return {
                "query": topic or "general",
                "error": str(e),
                "articles": []
            }

# Singleton instance
web_access_engine = WebAccessEngine()

async def search_internet(query: str) -> Dict[str, Any]:
    """Convenience function for internet search"""
    async with WebAccessEngine() as engine:
        return await engine.search_web(query)

async def get_wikipedia_info(topic: str) -> Dict[str, Any]:
    """Convenience function for Wikipedia lookup"""
    async with WebAccessEngine() as engine:
        return await engine.get_wikipedia_summary(topic)

async def make_web_request(url: str, method: str = "GET", data: dict = None) -> Dict[str, Any]:
    """Convenience function for HTTP requests"""
    async with WebAccessEngine() as engine:
        return await engine.make_http_request(url, method, data)
