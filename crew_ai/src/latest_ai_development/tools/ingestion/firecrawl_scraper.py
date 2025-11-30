"""Firecrawl-based web scraper with fallback to basic scraper."""

from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, Field
import os

from ..base import BaseResearchTool, ResearchToolInput
from .web_scraper import WebScraperTool

# Try to import Firecrawl tool, but don't fail if not available
try:
    from crewai_tools import FirecrawlScrapeWebsiteTool
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    FirecrawlScrapeWebsiteTool = None


class FirecrawlScraperInput(ResearchToolInput):
    """Input schema for Firecrawl scraper tool."""
    url: str = Field(description="URL to scrape")
    page_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional page options for scraping"
    )
    extract_links: bool = Field(default=True, description="Whether to extract links")


class EnhancedFirecrawlTool(BaseResearchTool):
    """
    Enhanced web scraper using Firecrawl API with fallback to basic scraper.
    
    Features:
    - Converts complex websites to clean Markdown
    - Handles JavaScript-heavy sites
    - Better content extraction than basic HTML parsing
    - Automatic fallback to WebScraperTool if Firecrawl unavailable
    - Configurable scraping options
    """
    
    name: str = "firecrawl_scraper"
    description: str = "Scrape websites and convert to clean Markdown using Firecrawl API (falls back to basic scraper if unavailable)"
    args_schema: Type[BaseModel] = FirecrawlScraperInput
    
    def __init__(self, **kwargs):
        """Initialize the Firecrawl scraper with fallback."""
        super().__init__(**kwargs)
        
        self._use_firecrawl = False
        self._firecrawl_tool = None
        self._fallback_tool = None
        
        # Check if Firecrawl is available and configured
        api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if FIRECRAWL_AVAILABLE and api_key:
            try:
                # Initialize Firecrawl tool
                self._firecrawl_tool = FirecrawlScrapeWebsiteTool(api_key=api_key)
                self._use_firecrawl = True
                print("✓ Firecrawl scraper initialized successfully")
            except Exception as e:
                print(f"⚠ Firecrawl initialization failed: {e}")
                print("  Falling back to basic web scraper")
                self._use_firecrawl = False
        else:
            if not FIRECRAWL_AVAILABLE:
                print("⚠ Firecrawl not available in crewai_tools")
            elif not api_key:
                print("⚠ FIRECRAWL_API_KEY not found in environment")
            print("  Using basic web scraper as fallback")
        
        # Initialize fallback tool
        if not self._use_firecrawl:
            self._fallback_tool = WebScraperTool()
    
    def execute(
        self,
        url: str,
        page_options: Optional[Dict[str, Any]] = None,
        extract_links: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape a website using Firecrawl or fallback scraper.
        
        Args:
            url: URL to scrape
            page_options: Additional options for Firecrawl (ignored for fallback)
            extract_links: Whether to extract links from the page
            
        Returns:
            Dictionary containing scraped content and metadata
        """
        if page_options is None:
            page_options = {}
        
        try:
            if self._use_firecrawl:
                # Use Firecrawl for scraping
                result = self._scrape_with_firecrawl(url, page_options)
            else:
                # Use fallback scraper
                result = self._scrape_with_fallback(url, extract_links)
            
            return {
                **result,
                "scraper_used": "firecrawl" if self._use_firecrawl else "fallback",
                "status": "success"
            }
            
        except Exception as e:
            # If Firecrawl fails, try fallback
            if self._use_firecrawl and self._fallback_tool is None:
                self._fallback_tool = WebScraperTool()
            
            if self._fallback_tool:
                try:
                    result = self._scrape_with_fallback(url, extract_links)
                    return {
                        **result,
                        "scraper_used": "fallback_after_error",
                        "status": "success",
                        "warning": f"Firecrawl failed, used fallback: {str(e)}"
                    }
                except Exception as fallback_error:
                    return {
                        "url": url,
                        "error": str(fallback_error),
                        "status": "error",
                        "message": f"Both scrapers failed. Firecrawl: {str(e)}, Fallback: {str(fallback_error)}"
                    }
            else:
                return {
                    "url": url,
                    "error": str(e),
                    "status": "error",
                    "message": f"Scraping failed: {str(e)}"
                }
    
    def _scrape_with_firecrawl(
        self,
        url: str,
        page_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Scrape using Firecrawl API.
        
        Args:
            url: URL to scrape
            page_options: Firecrawl page options
            
        Returns:
            Scraped content in Markdown format
        """
        # Firecrawl returns Markdown content
        markdown_content = self._firecrawl_tool.run(url=url)
        
        return {
            "url": url,
            "content": markdown_content,
            "format": "markdown",
            "page_options": page_options
        }
    
    def _scrape_with_fallback(
        self,
        url: str,
        extract_links: bool
    ) -> Dict[str, Any]:
        """
        Scrape using fallback WebScraperTool.
        
        Args:
            url: URL to scrape
            extract_links: Whether to extract links
            
        Returns:
            Scraped content from fallback tool
        """
        result = self._fallback_tool.execute(
            url=url,
            extract_links=extract_links,
            clean_html=True
        )
        
        # Convert to consistent format
        return {
            "url": url,
            "content": result.get("document", {}).get("full_text", ""),
            "format": "text",
            "document": result.get("document"),
            "links": result.get("links", []),
            "metadata": result.get("metadata", {})
        }
    
    def _run(self, url: str) -> str:
        """
        CrewAI tool interface - simplified run method.
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped content as string
        """
        result = self.execute(url=url)
        if result["status"] == "success":
            return result.get("content", "")
        else:
            return f"Scraping error: {result.get('message', 'Unknown error')}"


def create_firecrawl_tool(api_key: Optional[str] = None) -> EnhancedFirecrawlTool:
    """
    Factory function to create a Firecrawl scraper tool.
    
    Args:
        api_key: Optional Firecrawl API key (will use env var if not provided)
        
    Returns:
        Configured EnhancedFirecrawlTool instance
    """
    if api_key:
        os.environ["FIRECRAWL_API_KEY"] = api_key
    
    return EnhancedFirecrawlTool()
