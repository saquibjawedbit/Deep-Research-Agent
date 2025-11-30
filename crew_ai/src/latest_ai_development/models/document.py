"""Models for documents, sections, and citations."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class Citation(BaseModel):
    """A citation to another work."""
    citation_id: str = Field(description="Unique identifier for this citation")
    title: Optional[str] = Field(default=None, description="Title of cited work")
    authors: List[str] = Field(default_factory=list, description="Authors of cited work")
    year: Optional[int] = Field(default=None, description="Publication year")
    venue: Optional[str] = Field(default=None, description="Publication venue (journal, conference, etc.)")
    doi: Optional[str] = Field(default=None, description="DOI if available")
    url: Optional[str] = Field(default=None, description="URL if available")
    citation_text: str = Field(description="Raw citation text as it appears in source")
    
    class Config:
        json_schema_extra = {
            "example": {
                "citation_id": "cite_001",
                "title": "Attention Is All You Need",
                "authors": ["Vaswani, A.", "Shazeer, N."],
                "year": 2017,
                "venue": "NeurIPS",
                "citation_text": "Vaswani et al., 2017"
            }
        }


class Section(BaseModel):
    """A section within a document."""
    section_id: str = Field(description="Unique identifier for this section")
    title: str = Field(description="Section title")
    content: str = Field(description="Section text content")
    section_type: Optional[str] = Field(default=None, description="Type (abstract, introduction, methods, etc.)")
    page_start: Optional[int] = Field(default=None, description="Starting page number")
    page_end: Optional[int] = Field(default=None, description="Ending page number")
    subsections: List['Section'] = Field(default_factory=list, description="Nested subsections")
    
    class Config:
        json_schema_extra = {
            "example": {
                "section_id": "sec_001",
                "title": "Methods",
                "content": "We trained a transformer model...",
                "section_type": "methods",
                "page_start": 3,
                "page_end": 5
            }
        }


class Document(BaseModel):
    """A research document (paper, article, etc.)."""
    document_id: str = Field(description="Unique identifier for this document")
    title: str = Field(description="Document title")
    authors: List[str] = Field(default_factory=list, description="Document authors")
    
    # Content
    abstract: Optional[str] = Field(default=None, description="Abstract text")
    sections: List[Section] = Field(default_factory=list, description="Document sections")
    full_text: Optional[str] = Field(default=None, description="Full document text")
    
    # Metadata
    publication_date: Optional[datetime] = Field(default=None, description="Publication date")
    venue: Optional[str] = Field(default=None, description="Publication venue")
    doi: Optional[str] = Field(default=None, description="DOI")
    url: Optional[str] = Field(default=None, description="URL")
    source_type: str = Field(description="Source type (pdf, html, etc.)")
    
    # References
    citations: List[Citation] = Field(default_factory=list, description="Citations in this document")
    references: List[str] = Field(default_factory=list, description="Reference list")
    
    # Extracted information
    datasets_mentioned: List[str] = Field(default_factory=list, description="Datasets mentioned")
    code_links: List[str] = Field(default_factory=list, description="Links to code repositories")
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.now, description="When this was processed")
    processing_version: str = Field(default="1.0.0", description="Version of processing pipeline")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_001",
                "title": "Advances in Transformer Models",
                "authors": ["Smith, J.", "Doe, A."],
                "abstract": "We present a novel approach...",
                "source_type": "pdf",
                "datasets_mentioned": ["ImageNet", "COCO"],
                "code_links": ["https://github.com/example/repo"]
            }
        }
