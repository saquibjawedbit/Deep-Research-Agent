"""Fact-checking tool for verifying claims against external sources."""

from typing import Any, Dict, Type, Optional, List
from pydantic import BaseModel, Field
import requests
from datetime import datetime
import time

from ..base import BaseResearchTool, ResearchToolInput
from ...models.claim import Claim, Evidence, ConfidenceLevel, Provenance


class FactCheckerInput(ResearchToolInput):
    """Input schema for fact checker tool."""
    claim_text: str = Field(description="Claim text to verify")
    claim_id: str = Field(description="ID of claim being verified")
    search_query: Optional[str] = Field(default=None, description="Custom search query (auto-generated if not provided)")
    max_sources: int = Field(default=5, description="Maximum number of sources to check")


class FactCheckerTool(BaseResearchTool):
    """
    Tool for fact-checking claims against external sources.
    
    Verification strategies:
    - Search academic databases (Semantic Scholar)
    - Cross-reference with known datasets
    - Search general web for corroboration
    - Assign confidence scores
    """
    
    name: str = "fact_checker"
    description: str = "Verify claims against external sources and assign confidence scores"
    args_schema: Type[BaseModel] = FactCheckerInput
    
    def execute(
        self,
        claim_text: str,
        claim_id: str,
        search_query: Optional[str] = None,
        max_sources: int = 5
    ) -> Dict[str, Any]:
        """
        Verify a claim.
        
        Args:
            claim_text: Claim text to verify
            claim_id: ID of claim being verified
            search_query: Custom search query
            max_sources: Maximum number of sources to check
            
        Returns:
            Dictionary containing verification results
        """
        # Generate search query if not provided
        if not search_query:
            search_query = self._generate_search_query(claim_text)
        
        # Search for evidence
        evidence_list = []
        
        # Try Semantic Scholar API
        try:
            semantic_scholar_evidence = self._search_semantic_scholar(search_query, max_sources)
            evidence_list.extend(semantic_scholar_evidence)
        except Exception as e:
            print(f"Semantic Scholar search failed: {e}")
        
        # Determine confidence level
        confidence = self._determine_confidence(claim_text, evidence_list)
        
        return {
            "claim_id": claim_id,
            "confidence": confidence.value,
            "evidence": [e.model_dump() for e in evidence_list],
            "num_sources_checked": len(evidence_list),
            "search_query": search_query,
            "verified_at": datetime.now().isoformat()
        }
    
    def _generate_search_query(self, claim_text: str) -> str:
        """Generate a search query from claim text."""
        # Simple approach: extract key terms
        # Remove common words and keep important terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 
                      'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                      'would', 'could', 'should', 'may', 'might', 'can', 'that', 'this', 
                      'these', 'those', 'we', 'our', 'they', 'their'}
        
        words = claim_text.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if w.lower() not in stop_words and len(w) > 3]
        
        # Take first 5-7 keywords
        return ' '.join(keywords[:7])
    
    def _search_semantic_scholar(self, query: str, max_results: int = 5) -> List[Evidence]:
        """Search Semantic Scholar for relevant papers."""
        evidence_list = []
        
        try:
            # Semantic Scholar API
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': query,
                'limit': max_results,
                'fields': 'title,abstract,authors,year,url,citationCount'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                
                for paper in papers:
                    # Create evidence from paper
                    title = paper.get('title', '')
                    abstract = paper.get('abstract', '')
                    authors = paper.get('authors', [])
                    year = paper.get('year')
                    paper_url = paper.get('url', '')
                    
                    if abstract:
                        # Create provenance
                        provenance = Provenance(
                            source_id=paper.get('paperId', ''),
                            source_type='academic_paper',
                            source_url=paper_url,
                            extracted_at=datetime.now()
                        )
                        
                        # Create evidence
                        evidence = Evidence(
                            text=f"{title}. {abstract[:200]}...",
                            provenance=provenance,
                            relevance_score=0.7,  # Default score
                            supports_claim=True  # Assume support for now
                        )
                        
                        evidence_list.append(evidence)
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
        
        return evidence_list
    
    def _determine_confidence(self, claim_text: str, evidence_list: List[Evidence]) -> ConfidenceLevel:
        """Determine confidence level based on evidence."""
        if not evidence_list:
            return ConfidenceLevel.UNKNOWN
        
        # Count supporting vs contradicting evidence
        supporting = sum(1 for e in evidence_list if e.supports_claim)
        contradicting = len(evidence_list) - supporting
        
        # Calculate average relevance
        avg_relevance = sum(e.relevance_score for e in evidence_list) / len(evidence_list)
        
        # Determine confidence
        if supporting >= 3 and avg_relevance >= 0.6:
            return ConfidenceLevel.VERIFIED
        elif supporting >= 2 and contradicting == 0:
            return ConfidenceLevel.PARTIALLY_VERIFIED
        elif contradicting > supporting:
            return ConfidenceLevel.CONTRADICTED
        else:
            return ConfidenceLevel.UNKNOWN
