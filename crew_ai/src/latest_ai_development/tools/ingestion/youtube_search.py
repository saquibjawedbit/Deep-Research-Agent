"""YouTube video search and transcript extraction tool."""

from typing import Any, Dict, Type, Optional, List
from pydantic import BaseModel, Field
import os

from ..base import BaseResearchTool, ResearchToolInput

# Try to import YouTube tools
try:
    from crewai_tools import YoutubeVideoSearchTool
    YOUTUBE_TOOL_AVAILABLE = True
except ImportError:
    YOUTUBE_TOOL_AVAILABLE = False
    YoutubeVideoSearchTool = None


class YouTubeSearchInput(ResearchToolInput):
    """Input schema for YouTube search tool."""
    query: str = Field(description="Search query for YouTube videos")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class EnhancedYouTubeSearchTool(BaseResearchTool):
    """
    Enhanced YouTube search tool for finding and analyzing video content.
    
    Features:
    - Search within video transcripts and captions
    - Extract video metadata (title, description, channel)
    - Retrieve video transcripts when available
    - Handle videos without transcripts gracefully
    - Filter and rank results by relevance
    """
    
    name: str = "youtube_search"
    description: str = "Search YouTube videos and extract transcripts/captions for research purposes"
    args_schema: Type[BaseModel] = YouTubeSearchInput
    
    def __init__(self, **kwargs):
        """Initialize the YouTube search tool."""
        super().__init__(**kwargs)
        
        self._youtube_tool = None
        self._tool_available = False
        
        if YOUTUBE_TOOL_AVAILABLE:
            try:
                # Initialize YouTube search tool
                self._youtube_tool = YoutubeVideoSearchTool()
                self._tool_available = True
                print("✓ YouTube search tool initialized successfully")
            except Exception as e:
                print(f"⚠ YouTube tool initialization failed: {e}")
                self._tool_available = False
        else:
            print("⚠ YoutubeVideoSearchTool not available in crewai_tools")
            print("  Install with: pip install crewai[tools]")
    
    def execute(
        self,
        query: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search YouTube videos and extract relevant content.
        
        Args:
            query: Search query for videos
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing video results with transcripts and metadata
        """
        if not self._tool_available:
            return {
                "query": query,
                "results": [],
                "status": "error",
                "message": "YouTube search tool not available. Install crewai[tools]."
            }
        
        try:
            # Execute YouTube search
            search_results = self._youtube_tool.run(search_query=query)
            
            # The tool returns a string with video information
            # In a production environment, you might want to parse this more thoroughly
            return {
                "query": query,
                "results": search_results,
                "max_results": max_results,
                "status": "success",
                "source_type": "youtube"
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "status": "error",
                "message": f"YouTube search failed: {str(e)}"
            }
    
    def _run(self, query: str) -> str:
        """
        CrewAI tool interface - simplified run method.
        
        Args:
            query: Search query
            
        Returns:
            Video search results as string
        """
        result = self.execute(query=query)
        if result["status"] == "success":
            return str(result["results"])
        else:
            return f"YouTube search error: {result.get('message', 'Unknown error')}"
    
    def search_and_extract_transcripts(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search videos and extract transcripts.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of video data with transcripts
        """
        result = self.execute(query=query, max_results=max_results)
        
        if result["status"] == "success":
            # Parse and structure the results
            # This is a simplified version - you might want to enhance parsing
            return [{
                "query": query,
                "content": result["results"],
                "source": "youtube",
                "status": "success"
            }]
        else:
            return []


def create_youtube_tool() -> EnhancedYouTubeSearchTool:
    """
    Factory function to create a YouTube search tool.
    
    Returns:
        Configured EnhancedYouTubeSearchTool instance
    """
    return EnhancedYouTubeSearchTool()
