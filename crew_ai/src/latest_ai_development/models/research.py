"""Models for research queries and results."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .claim import Claim
from .document import Document


class ResearchQuery(BaseModel):
    """A research query submitted to the Deep Research Crew."""
    query_id: str = Field(description="Unique identifier for this query")
    query_text: str = Field(description="The research question or topic")
    
    # Query parameters
    start_date: Optional[datetime] = Field(default=None, description="Start date for source filtering")
    end_date: Optional[datetime] = Field(default=None, description="End date for source filtering")
    sources: List[str] = Field(
        default_factory=lambda: ["papers", "web"],
        description="Source types to search (papers, youtube, x, reddit, news, web)"
    )
    max_docs: int = Field(default=50, description="Maximum number of documents to process")
    reproduce: bool = Field(default=False, description="Whether to attempt reproduction of claims")
    
    # Metadata
    submitted_at: datetime = Field(default_factory=datetime.now, description="When query was submitted")
    submitted_by: Optional[str] = Field(default=None, description="User who submitted query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "query_001",
                "query_text": "efficacy of transformer models for NLP tasks",
                "start_date": "2020-01-01",
                "end_date": "2024-12-31",
                "sources": ["papers", "web"],
                "max_docs": 100,
                "reproduce": True
            }
        }


class ResearchResult(BaseModel):
    """Results from a research query."""
    query_id: str = Field(description="ID of the query this result is for")
    query_text: str = Field(description="The original query text")
    
    # Results
    documents: List[Document] = Field(default_factory=list, description="Documents found and processed")
    claims: List[Claim] = Field(default_factory=list, description="Claims extracted from documents")
    
    # Summary statistics
    total_documents_found: int = Field(description="Total documents found")
    total_documents_processed: int = Field(description="Total documents processed")
    total_claims_extracted: int = Field(description="Total claims extracted")
    verified_claims: int = Field(default=0, description="Number of verified claims")
    contradicted_claims: int = Field(default=0, description="Number of contradicted claims")
    
    # Executive summary
    executive_summary: Optional[str] = Field(default=None, description="High-level summary of findings")
    key_findings: List[str] = Field(default_factory=list, description="Key findings from research")
    
    # Output artifacts
    report_path: Optional[str] = Field(default=None, description="Path to generated report")
    notebook_path: Optional[str] = Field(default=None, description="Path to reproducible notebook")
    provenance_graph_path: Optional[str] = Field(default=None, description="Path to provenance graph")
    
    # Metadata
    started_at: datetime = Field(default_factory=datetime.now, description="When research started")
    completed_at: Optional[datetime] = Field(default=None, description="When research completed")
    processing_time_seconds: Optional[float] = Field(default=None, description="Total processing time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "query_001",
                "query_text": "efficacy of transformer models",
                "total_documents_found": 100,
                "total_documents_processed": 50,
                "total_claims_extracted": 25,
                "verified_claims": 18,
                "contradicted_claims": 2,
                "executive_summary": "Transformer models show significant improvements...",
                "key_findings": [
                    "30% average improvement over previous architectures",
                    "Best performance on translation tasks"
                ]
            }
        }
