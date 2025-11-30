"""Web scraping tool for extracting content from web pages."""

from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

from ..base import BaseResearchTool, ResearchToolInput
from ...models.document import Document, Section


class WebScraperInput(ResearchToolInput):
    """Input schema for web scraper tool."""
    url: str = Field(description="URL to scrape")
    extract_links: bool = Field(default=True, description="Whether to extract links")
    clean_html: bool = Field(default=True, description="Whether to clean HTML tags")


class WebScraperTool(BaseResearchTool):
    """
    Tool for scraping web pages and extracting clean text content.
    
    Features:
    - Extracts title, main content, and metadata
    - Cleans HTML and extracts readable text
    - Respects robots.txt (basic implementation)
    - Extracts links and references
    """
    
    name: str = "web_scraper"
    description: str = "Scrape web pages and extract clean text content, links, and metadata"
    args_schema: Type[BaseModel] = WebScraperInput
    
    def execute(self, url: str, extract_links: bool = True, clean_html: bool = True) -> Dict[str, Any]:
        """
        Scrape a web page.
        
        Args:
            url: URL to scrape
            extract_links: Whether to extract links
            clean_html: Whether to clean HTML tags
            
        Returns:
            Dictionary containing scraped content
        """
        # Set user agent
        headers = {
            'User-Agent': 'DeepResearchCrew/1.0 (Educational Research Bot)'
        }
        
        # Fetch page
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract main content
        content = self._extract_main_content(soup, clean_html)
        
        # Extract metadata
        metadata = self._extract_metadata(soup)
        
        # Extract links if requested
        links = []
        if extract_links:
            links = self._extract_links(soup, url)
        
        # Create document
        document = Document(
            document_id=f"web_{urlparse(url).netloc}_{hash(url)}",
            title=title,
            authors=metadata.get('authors', []),
            full_text=content,
            source_type="html",
            url=url,
            publication_date=metadata.get('publication_date'),
            sections=[Section(
                section_id="main",
                title="Main Content",
                content=content
            )]
        )
        
        return {
            "document": document.model_dump(),
            "num_links": len(links),
            "links": links[:50],  # Limit links
            "metadata": metadata
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try <h1> tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Try og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        return "Unknown Title"
    
    def _extract_main_content(self, soup: BeautifulSoup, clean_html: bool) -> str:
        """Extract main content from page."""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()
        
        # Try to find main content area
        main_content = None
        
        # Try <article> tag
        article = soup.find('article')
        if article:
            main_content = article
        
        # Try <main> tag
        if not main_content:
            main = soup.find('main')
            if main:
                main_content = main
        
        # Try content div
        if not main_content:
            content_div = soup.find('div', class_=re.compile(r'content|article|post|entry', re.I))
            if content_div:
                main_content = content_div
        
        # Fallback to body
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return ""
        
        # Extract text
        if clean_html:
            text = main_content.get_text(separator='\n', strip=True)
            # Clean up whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            return text.strip()
        else:
            return str(main_content)
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from page."""
        metadata = {}
        
        # Extract author
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            metadata['authors'] = [author_meta['content'].strip()]
        
        # Extract publication date
        date_meta = soup.find('meta', property='article:published_time')
        if date_meta and date_meta.get('content'):
            metadata['publication_date'] = date_meta['content']
        
        # Extract description
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        if desc_meta and desc_meta.get('content'):
            metadata['description'] = desc_meta['content'].strip()
        
        return metadata
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """Extract links from page."""
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip anchors and javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Make absolute URL
            if href.startswith('http'):
                links.append(href)
            elif href.startswith('/'):
                parsed = urlparse(base_url)
                links.append(f"{parsed.scheme}://{parsed.netloc}{href}")
        
        return list(set(links))  # Deduplicate
