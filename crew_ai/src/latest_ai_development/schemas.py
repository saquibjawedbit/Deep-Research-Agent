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

# New schemas for Gemini Deep Research capabilities

class ResearchSubtopic(BaseModel):
    """Individual subtopic in a research plan"""
    title: str
    description: str
    search_queries: List[str] = Field(..., description="Specific search queries for this subtopic")
    priority: int = Field(..., ge=1, le=5, description="Priority level 1-5")
    estimated_sources: int = Field(..., description="Estimated number of sources needed")

class ResearchPlan(BaseModel):
    """Multi-step research plan generated from user query"""
    original_query: str
    research_objective: str
    subtopics: List[ResearchSubtopic]
    search_strategies: List[str] = Field(..., description="Overall search strategies to employ")
    success_criteria: List[str] = Field(..., description="Criteria to determine research completeness")
    estimated_duration_minutes: int = Field(..., description="Estimated time to complete research")

class ParallelResearchPath(BaseModel):
    """Results from a single parallel research path"""
    path_id: str
    subtopic: str
    sources_found: int
    key_insights: List[str]
    documents: List[Document]
    completion_status: str = Field(..., description="completed, partial, or failed")

class ParallelResearchPathList(BaseModel):
    items: List[ParallelResearchPath]

class Visualization(BaseModel):
    """Metadata and data for a visualization"""
    viz_id: str
    viz_type: str = Field(..., description="chart, graph, network, mindmap, table")
    title: str
    description: str
    data: dict = Field(..., description="Structured data for the visualization")
    file_path: Optional[str] = Field(None, description="Path to generated image file")

class VisualizationList(BaseModel):
    items: List[Visualization]

class IterativeRefinementDecision(BaseModel):
    """Decision on whether to continue research or complete"""
    should_continue: bool
    reason: str
    identified_gaps: List[str]
    additional_queries: List[str] = Field(default_factory=list)
    current_quality_score: float = Field(..., ge=0, le=1)

class EnhancedDeepResearchReport(BaseModel):
    """Enhanced report with visualizations and multi-page structure"""
    title: str
    executive_summary: str
    table_of_contents: List[str]
    research_plan_summary: str
    key_findings: List[Insight]
    detailed_analysis: str
    methodology_audit: str
    visualizations: List[Visualization]
    sources_bibliography: List[Document]
    quality_metrics: dict = Field(..., description="Quality scores and metrics")
    final_conclusion: str
    appendices: Optional[dict] = Field(None, description="Additional supporting materials")
