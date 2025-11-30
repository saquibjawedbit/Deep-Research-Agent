from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class SourceValidation(BaseModel):
    source_id: str
    url: str
    credibility_score: float = Field(..., ge=0, le=1)
    is_valid: bool
    reason: str

class SourceValidationList(BaseModel):
    items: List[SourceValidation]

class Insight(BaseModel):
    content: str
    source_url: str
    insight_type: str = Field(..., description="Empirical, Theoretical, or Methodological")
    confidence_score: float

class InsightList(BaseModel):
    items: List[Insight]

class Document(BaseModel):
    title: str
    url: str
    content: str
    summary: str
    authors: List[str]
    publication_date: str
    source_reliability: float

class DocumentList(BaseModel):
    items: List[Document]

class MethodologyReview(BaseModel):
    source_id: str
    methodology_type: str
    strengths: List[str]
    limitations: List[str]
    rigor_score: float = Field(..., ge=0, le=1)

class MethodologyReviewList(BaseModel):
    items: List[MethodologyReview]

class CrossReference(BaseModel):
    claim: str
    supporting_sources: List[str]
    contradicting_sources: List[str]
    consensus_score: float = Field(..., ge=0, le=1)

class CrossReferenceList(BaseModel):
    items: List[CrossReference]

class EvidenceRating(BaseModel):
    claim: str
    evidence_type: str
    strength_score: float = Field(..., ge=0, le=1)
    rationale: str

class EvidenceRatingList(BaseModel):
    items: List[EvidenceRating]

class CitationReport(BaseModel):
    total_citations: int
    accuracy_score: float
    flagged_citations: List[str]

class Analysis(BaseModel):
    key_findings: List[str]
    trends: List[str]
    gaps: List[str]
    overall_quality_score: float

class QualityReport(BaseModel):
    overall_quality_score: float = Field(..., ge=0, le=1)
    issues: List[str]
    recommendations: List[str]
    pass_review: bool

class RefinementReport(BaseModel):
    iteration: int
    actions_taken: List[str]
    new_findings: List[str]
    updated_quality_score: float

class DeepResearchReport(BaseModel):
    executive_summary: str
    key_findings: List[Insight]
    methodology_audit: str
    final_conclusion: str
