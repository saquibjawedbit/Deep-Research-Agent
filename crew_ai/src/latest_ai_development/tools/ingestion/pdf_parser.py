"""PDF parsing tool for extracting structured content from academic papers."""

from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, Field
import pymupdf
import re
from pathlib import Path

from ..base import BaseResearchTool, ResearchToolInput
from ...models.document import Document, Section, Citation


class PDFParserInput(ResearchToolInput):
    """Input schema for PDF parser tool."""
    pdf_path: str = Field(description="Path to PDF file or URL")
    extract_citations: bool = Field(default=True, description="Whether to extract citations")
    extract_tables: bool = Field(default=False, description="Whether to extract tables")


class PDFParserTool(BaseResearchTool):
    """
    Tool for parsing PDF documents and extracting structured content.
    
    Extracts:
    - Title, authors, abstract
    - Sections (Introduction, Methods, Results, etc.)
    - Citations and references
    - Datasets and code links mentioned
    """
    
    name: str = "pdf_parser"
    description: str = "Parse PDF documents and extract structured content including sections, citations, and metadata"
    args_schema: Type[BaseModel] = PDFParserInput
    
    def execute(self, pdf_path: str, extract_citations: bool = True, extract_tables: bool = False) -> Dict[str, Any]:
        """
        Parse a PDF document.
        
        Args:
            pdf_path: Path to PDF file or URL
            extract_citations: Whether to extract citations
            extract_tables: Whether to extract tables
            
        Returns:
            Dictionary containing parsed document data
        """
        # Handle URL
        if pdf_path.startswith('http://') or pdf_path.startswith('https://'):
            import requests
            import tempfile
            import os
            
            response = requests.get(pdf_path, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code != 200:
                return {"error": f"Failed to download PDF from {pdf_path}, status code: {response.status_code}"}
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(response.content)
                temp_pdf_path = temp_pdf.name
            
            try:
                doc = pymupdf.open(temp_pdf_path)
            except Exception as e:
                os.unlink(temp_pdf_path)
                return {"error": f"Failed to open PDF: {str(e)}"}
        else:
            # Local file
            if not os.path.exists(pdf_path):
                 return {"error": f"File not found: {pdf_path}"}
            doc = pymupdf.open(pdf_path)
        
        # Extract metadata
        metadata = doc.metadata
        title = metadata.get('title', self._extract_title_from_first_page(doc))
        authors = self._extract_authors(doc)
        
        # Extract text and sections
        full_text = ""
        sections = []
        current_section = None
        
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            full_text += text + "\n"
            
            # Simple section detection based on common headers
            section_headers = self._detect_section_headers(text)
            for header in section_headers:
                if current_section:
                    sections.append(current_section)
                
                current_section = Section(
                    section_id=f"sec_{len(sections)+1}",
                    title=header,
                    content="",
                    section_type=self._classify_section(header),
                    page_start=page_num,
                    page_end=page_num
                )
            
            if current_section:
                current_section.content += text + "\n"
                current_section.page_end = page_num
        
        if current_section:
            sections.append(current_section)
        
        # Extract abstract
        abstract = self._extract_abstract(full_text)
        
        # Extract citations if requested
        citations = []
        if extract_citations:
            citations = self._extract_citations(full_text)
        
        # Extract datasets and code links
        datasets = self._extract_datasets(full_text)
        code_links = self._extract_code_links(full_text)
        
        # Create document object
        document = Document(
            document_id=f"doc_{Path(pdf_path).stem}",
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            full_text=full_text,
            source_type="pdf",
            url=pdf_path if pdf_path.startswith('http') else None,
            citations=citations,
            datasets_mentioned=datasets,
            code_links=code_links
        )
        
        num_pages = len(doc)
        doc.close()
        
        # Clean up temp file if it exists
        if 'temp_pdf_path' in locals() and temp_pdf_path and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
        
        return {
            "document": document.model_dump(),
            "num_pages": num_pages,
            "num_sections": len(sections),
            "num_citations": len(citations)
        }
    
    def _extract_title_from_first_page(self, doc: pymupdf.Document) -> str:
        """Extract title from first page (usually largest font)."""
        if len(doc) == 0:
            return "Unknown Title"
        
        first_page = doc[0]
        text = first_page.get_text()
        lines = text.split('\n')
        
        # Return first non-empty line as title
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                return line
        
        return "Unknown Title"
    
    def _extract_authors(self, doc: pymupdf.Document) -> list[str]:
        """Extract authors from PDF metadata or first page."""
        metadata = doc.metadata
        author = metadata.get('author', '')
        
        if author:
            # Split by common delimiters
            authors = re.split(r'[,;]|\band\b', author)
            return [a.strip() for a in authors if a.strip()]
        
        return []
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract section from text."""
        # Look for abstract section
        abstract_pattern = r'(?i)abstract\s*[:\n]+(.*?)(?=\n\s*\n|\n[A-Z][a-z]+:|\nIntroduction|\n1\.)'
        match = re.search(abstract_pattern, text, re.DOTALL)
        
        if match:
            abstract = match.group(1).strip()
            # Clean up
            abstract = re.sub(r'\s+', ' ', abstract)
            return abstract
        
        return None
    
    def _detect_section_headers(self, text: str) -> list[str]:
        """Detect section headers in text."""
        headers = []
        
        # Common section patterns
        patterns = [
            r'^(\d+\.?\s+[A-Z][A-Za-z\s]+)$',  # Numbered sections
            r'^([A-Z][A-Z\s]+)$',  # ALL CAPS headers
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$'  # Title Case headers
        ]
        
        for line in text.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if re.match(pattern, line) and len(line) < 100:
                    # Check if it's a known section type
                    if any(keyword in line.lower() for keyword in 
                           ['abstract', 'introduction', 'method', 'result', 'discussion', 
                            'conclusion', 'reference', 'acknowledgment', 'appendix']):
                        headers.append(line)
                        break
        
        return headers
    
    def _classify_section(self, header: str) -> Optional[str]:
        """Classify section type based on header."""
        header_lower = header.lower()
        
        if 'abstract' in header_lower:
            return 'abstract'
        elif 'introduction' in header_lower:
            return 'introduction'
        elif 'method' in header_lower or 'approach' in header_lower:
            return 'methods'
        elif 'result' in header_lower or 'finding' in header_lower:
            return 'results'
        elif 'discussion' in header_lower:
            return 'discussion'
        elif 'conclusion' in header_lower:
            return 'conclusion'
        elif 'reference' in header_lower or 'bibliograph' in header_lower:
            return 'references'
        elif 'related work' in header_lower:
            return 'related_work'
        
        return None
    
    def _extract_citations(self, text: str) -> list[Citation]:
        """Extract citations from text."""
        citations = []
        
        # Simple citation pattern (Author et al., Year)
        citation_pattern = r'([A-Z][a-z]+(?:\s+et\s+al\.)?),?\s+(\d{4})'
        matches = re.finditer(citation_pattern, text)
        
        seen = set()
        for i, match in enumerate(matches):
            author = match.group(1)
            year = int(match.group(2))
            citation_text = match.group(0)
            
            # Avoid duplicates
            key = f"{author}_{year}"
            if key not in seen:
                seen.add(key)
                citations.append(Citation(
                    citation_id=f"cite_{i+1}",
                    authors=[author],
                    year=year,
                    citation_text=citation_text
                ))
        
        return citations[:50]  # Limit to 50 citations
    
    def _extract_datasets(self, text: str) -> list[str]:
        """Extract dataset names mentioned in text."""
        datasets = []
        
        # Common dataset patterns
        dataset_keywords = [
            'ImageNet', 'COCO', 'MNIST', 'CIFAR', 'SQuAD', 'GLUE', 'SuperGLUE',
            'WikiText', 'Penn Treebank', 'MS MARCO', 'Natural Questions'
        ]
        
        for keyword in dataset_keywords:
            if keyword in text:
                datasets.append(keyword)
        
        # Pattern for "X dataset"
        dataset_pattern = r'([A-Z][A-Za-z0-9]+)\s+dataset'
        matches = re.finditer(dataset_pattern, text)
        for match in matches:
            dataset_name = match.group(1)
            if dataset_name not in datasets:
                datasets.append(dataset_name)
        
        return list(set(datasets))[:20]  # Limit and deduplicate
    
    def _extract_code_links(self, text: str) -> list[str]:
        """Extract code repository links from text."""
        links = []
        
        # GitHub/GitLab patterns
        url_pattern = r'https?://(?:github\.com|gitlab\.com)/[\w\-]+/[\w\-]+'
        matches = re.finditer(url_pattern, text)
        
        for match in matches:
            url = match.group(0)
            if url not in links:
                links.append(url)
        
        return links
