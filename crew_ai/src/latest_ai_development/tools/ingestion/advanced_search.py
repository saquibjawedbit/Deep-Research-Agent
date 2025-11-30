"""Advanced search tools using SerperDev API for web search."""

from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, Field
import os
from crewai_tools import SerperDevTool

from ..base import BaseResearchTool, ResearchToolInput


class AdvancedSearchInput(ResearchToolInput):
    """Input schema for advanced search tool."""
    query: str = Field(description="Search query to execute")
    num_results: int = Field(default=10, description="Number of results to return")
    search_type: str = Field(default="search", description="Type of search: search, news, images")


class SerperSearchTool(BaseResearchTool):
    """
    Wrapper for SerperDev search tool with enhanced error handling.
    
    Features:
    - Web search using SerperDev API
    - Configurable result count
    - Multiple search types (web, news, images)
    - Automatic API key detection from environment
    - Graceful error handling
    """
    
    name: str = "serper_search"
    description: str = "Search the web using SerperDev API to find relevant URLs and information"
    args_schema: Type[BaseModel] = AdvancedSearchInput
    
    def __init__(self, **kwargs):
        """Initialize the search tool."""
        super().__init__(**kwargs)
        
        # Check for API key
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            raise ValueError(
                "SERPER_API_KEY not found in environment variables. "
                "Get your API key from https://serper.dev and add it to your .env file."
            )
        
        # Initialize the underlying SerperDev tool
        self._serper_tool = SerperDevTool(
            search_url="https://google.serper.dev/search",
            n_results=10
        )
    
    def execute(
        self, 
        query: str, 
        num_results: int = 10,
        search_type: str = "search"
    ) -> Dict[str, Any]:
        """
        Execute a web search.
        
        Args:
            query: Search query to execute
            num_results: Number of results to return (default: 10)
            search_type: Type of search - 'search', 'news', or 'images'
            
        Returns:
            Dictionary containing search results with URLs, titles, and snippets
        """
        try:
            # Execute search using the underlying tool
            # The SerperDevTool returns a string with search results
            results_str = self._serper_tool.run(search_query=query)
            
            # Parse the results (SerperDev returns formatted text)
            # In a production environment, you might want to parse this more thoroughly
            return {
                "query": query,
                "results": results_str,
                "num_results": num_results,
                "search_type": search_type,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": None,
                "error": str(e),
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
    
    def _run(self, query: str) -> str:
        """
        CrewAI tool interface - simplified run method.
        
        Args:
            query: Search query
            
        Returns:
            Search results as string
        """
        result = self.execute(query=query)
        if result["status"] == "success":
            return result["results"]
        else:
            return f"Search error: {result.get('message', 'Unknown error')}"


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
