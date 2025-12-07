"""Advanced search tools using SerperDev API for web search."""

from typing import  Optional
from pydantic import Field
import os
import requests
from crewai.tools import BaseTool

from ..base import ResearchToolInput


class AdvancedSearchInput(ResearchToolInput):
    """Input schema for advanced search tool."""
    query: str = Field(description="Search query to execute")
    num_results: int = Field(default=10, description="Number of results to return")
    search_type: str = Field(default="search", description="Type of search: search, news, images")


class SerperSearchTool(BaseTool):
    """
    Direct implementation of Serper search with better error handling.
    
    Features:
    - Web search using SerperDev API
    - Configurable result count
    - Multiple search types (web, news, images)
    - Automatic API key detection from environment
    - Direct API calls for reliability
    """
    
    name: str = "serper_search"
    description: str = "Search the web using SerperDev API to find relevant URLs and information. Returns search results with titles, links, and snippets."
    
    def _run(self, query: str, num_results: int = 10) -> str:
        """
        Execute a web search using Serper API.
        
        Args:
            query: Search query to execute
            num_results: Number of results to return (default: 10)
            
        Returns:
            Formatted string with search results
        """
        # Get API key from environment
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY not found in environment variables. Get your API key from https://serper.dev"
        
        try:
            # Make direct API call to Serper
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": num_results
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            results = []
            if "organic" in data:
                for idx, result in enumerate(data["organic"][:num_results], 1):
                    title = result.get("title", "No title")
                    link = result.get("link", "No link")
                    snippet = result.get("snippet", "No description")
                    results.append(f"{idx}. {title}\n   URL: {link}\n   {snippet}\n")
            
            if not results:
                return f"No results found for query: {query}"
            
            output = f"Search results for '{query}':\n\n"
            output += "\n".join(results)
            return output
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Serper API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus: {e.response.status_code}"
                try:
                    error_msg += f"\nResponse: {e.response.json()}"
                except:
                    error_msg += f"\nResponse: {e.response.text}"
            return error_msg
        except Exception as e:
            return f"Search error: {str(e)}"
            return error_msg
        except Exception as e:
            return f"Search error: {str(e)}"


def create_search_tool(api_key: Optional[str] = None) -> SerperSearchTool:
    """
    Factory function to create a search tool.
    
    Args:
        api_key: Optional API key (will use env var if not provided)
        
    Returns:
        Configured SerperSearchTool instance
    """
    if api_key:
        os.environ["SERPER_API_KEY"] = api_key
    
    return SerperSearchTool()
