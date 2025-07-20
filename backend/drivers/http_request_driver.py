"""
HTTP Request Driver for Automation Engine
Handles web scraping, API calls, and data fetching
"""

import requests
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)

class HTTPRequestDriver:
    """Driver for making HTTP requests and processing web data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request with given parameters"""
        
        url = params.get('url')
        method = params.get('method', 'GET').upper()
        headers = params.get('headers', {})
        data = params.get('data')
        json_data = params.get('json')
        timeout = params.get('timeout', 30)
        extract_type = params.get('extract_type', 'text')  # text, json, html, title
        
        if not url:
            return {
                "success": False,
                "error": "URL parameter is required"
            }
        
        try:
            logger.info(f"🌐 Making {method} request to {url}")
            
            # Merge custom headers
            request_headers = {**self.session.headers, **headers}
            
            # Make the request
            if method == 'GET':
                response = self.session.get(url, headers=request_headers, timeout=timeout)
            elif method == 'POST':
                if json_data:
                    response = self.session.post(url, json=json_data, headers=request_headers, timeout=timeout)
                else:
                    response = self.session.post(url, data=data, headers=request_headers, timeout=timeout)
            elif method == 'PUT':
                if json_data:
                    response = self.session.put(url, json=json_data, headers=request_headers, timeout=timeout)
                else:
                    response = self.session.put(url, data=data, headers=request_headers, timeout=timeout)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=request_headers, timeout=timeout)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}"
                }
            
            # Check response status
            response.raise_for_status()
            
            # Extract data based on type
            extracted_data = self._extract_data(response, extract_type)
            
            result = {
                "success": True,
                "status_code": response.status_code,
                "url": url,
                "method": method,
                "data": extracted_data,
                "output": extracted_data,  # For compatibility with workflow templates
                "headers": dict(response.headers),
                "size": len(response.content)
            }
            
            logger.info(f"✅ HTTP request successful: {response.status_code}")
            return result
            
        except requests.exceptions.Timeout:
            error = f"Request timeout after {timeout} seconds"
            logger.error(f"❌ {error}")
            return {"success": False, "error": error}
            
        except requests.exceptions.ConnectionError:
            error = "Connection error - could not reach the server"
            logger.error(f"❌ {error}")
            return {"success": False, "error": error}
            
        except requests.exceptions.HTTPError as e:
            error = f"HTTP error {response.status_code}: {str(e)}"
            logger.error(f"❌ {error}")
            return {"success": False, "error": error, "status_code": response.status_code}
            
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(f"❌ {error}")
            return {"success": False, "error": error}
    
    def _extract_data(self, response: requests.Response, extract_type: str) -> Any:
        """Extract data from response based on type"""
        
        try:
            if extract_type == 'json':
                return response.json()
            
            elif extract_type == 'text':
                return response.text
            
            elif extract_type == 'html':
                soup = BeautifulSoup(response.text, 'html.parser')
                return {
                    "title": soup.title.string if soup.title else "",
                    "text": soup.get_text().strip(),
                    "html": response.text
                }
            
            elif extract_type == 'title':
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.title.string if soup.title else ""
            
            elif extract_type == 'links':
                soup = BeautifulSoup(response.text, 'html.parser')
                links = []
                for link in soup.find_all('a', href=True):
                    links.append({
                        "text": link.get_text().strip(),
                        "href": link['href']
                    })
                return links
            
            elif extract_type == 'images':
                soup = BeautifulSoup(response.text, 'html.parser')
                images = []
                for img in soup.find_all('img', src=True):
                    images.append({
                        "alt": img.get('alt', ''),
                        "src": img['src']
                    })
                return images
            
            elif extract_type == 'auto':
                # Auto-detect content type
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/json' in content_type:
                    return response.json()
                elif 'text/html' in content_type:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return {
                        "title": soup.title.string if soup.title else "",
                        "text": soup.get_text().strip()[:1000],  # First 1000 chars
                        "full_text": soup.get_text().strip()
                    }
                else:
                    return response.text
            
            else:
                return response.text
                
        except Exception as e:
            logger.warning(f"⚠️ Data extraction failed: {e}")
            return response.text

# Global driver instance
http_driver = HTTPRequestDriver()

def execute_http_request(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute HTTP request - convenience function"""
    return http_driver.execute(params)

if __name__ == "__main__":
    # Test the HTTP driver
    print("🧪 Testing HTTP Request Driver")
    
    # Test 1: JSON API
    result1 = http_driver.execute({
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "method": "GET",
        "extract_type": "json"
    })
    print(f"Test 1 - JSON API: {result1.get('success')}")
    if result1.get('success'):
        print(f"Data: {result1['data']}")
    
    # Test 2: HTML website
    result2 = http_driver.execute({
        "url": "https://httpbin.org/html",
        "method": "GET", 
        "extract_type": "html"
    })
    print(f"Test 2 - HTML: {result2.get('success')}")
    if result2.get('success'):
        print(f"Title: {result2['data'].get('title', 'No title')}")
    
    print("HTTP Driver tests completed!")
