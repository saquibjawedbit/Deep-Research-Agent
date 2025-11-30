"""Models for claims, evidence, and provenance tracking."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ClaimType(str, Enum):
    """Types of claims that can be extracted."""
    EXPERIMENTAL = "experimental"
    THEORETICAL = "theoretical"
    COMPARATIVE = "comparative"
    NUMERICAL = "numerical"
    QUALITATIVE = "qualitative"


class ConfidenceLevel(str, Enum):
    """Confidence levels for claim verification."""
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class Provenance(BaseModel):
    """Provenance information for a claim or evidence."""
    source_id: str = Field(description="Unique identifier for the source document")
    source_type: str = Field(description="Type of source (pdf, web, video, etc.)")
    source_url: Optional[str] = Field(default=None, description="URL of the source if available")
    page_number: Optional[int] = Field(default=None, description="Page number in document")
    section: Optional[str] = Field(default=None, description="Section name (e.g., 'Methods', 'Results')")
    paragraph: Optional[int] = Field(default=None, description="Paragraph number in section")
    timestamp: Optional[str] = Field(default=None, description="Timestamp for video sources")
    line_range: Optional[tuple[int, int]] = Field(default=None, description="Line range in source")
    extracted_at: datetime = Field(default_factory=datetime.now, description="When this was extracted")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "paper_123",
                "source_type": "pdf",
                "source_url": "https://arxiv.org/pdf/2301.12345.pdf",
                "page_number": 5,
                "section": "Results",
                "paragraph": 2
            }
        }


class Evidence(BaseModel):
    """Evidence supporting or contradicting a claim."""
    text: str = Field(description="The evidence text")
    provenance: Provenance = Field(description="Where this evidence came from")
    relevance_score: float = Field(ge=0.0, le=1.0, description="How relevant this evidence is (0-1)")
    supports_claim: bool = Field(description="Whether this evidence supports the claim")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The model achieved 95% accuracy on the test set.",
                "provenance": {
                    "source_id": "paper_123",
                    "source_type": "pdf",
                    "page_number": 5
                },
                "relevance_score": 0.9,
                "supports_claim": True
            }
        }


class Claim(BaseModel):
    """A factual claim extracted from research materials."""
    claim_id: str = Field(description="Unique identifier for this claim")
    text: str = Field(description="The claim text")
    claim_type: ClaimType = Field(description="Type of claim")
    provenance: Provenance = Field(description="Where this claim came from")
    
    # Extracted details
    entities: List[str] = Field(default_factory=list, description="Named entities mentioned in the claim")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Numerical metrics mentioned")
    context: Optional[str] = Field(default=None, description="Surrounding context for the claim")
    
    # Verification
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.UNKNOWN, description="Verification confidence")
    evidence: List[Evidence] = Field(default_factory=list, description="Supporting or contradicting evidence")
    verification_notes: Optional[str] = Field(default=None, description="Notes from verification process")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="When this claim was extracted")
    verified_at: Optional[datetime] = Field(default=None, description="When this claim was verified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "claim_001",
                "text": "Transformer models reduce error by 30% on dataset Y",
                "claim_type": "numerical",
                "provenance": {
                    "source_id": "paper_123",
                    "source_type": "pdf",
                    "page_number": 3
                },
                "entities": ["Transformer models", "dataset Y"],
                "metrics": {"error_reduction": 0.30},
                "confidence": "verified"
            }
        }
