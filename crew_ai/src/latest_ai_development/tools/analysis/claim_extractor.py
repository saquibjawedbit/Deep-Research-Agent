"""Claim extraction tool for identifying factual claims in text."""

from typing import Any, Dict, Type, List, Optional
from pydantic import BaseModel, Field
import re
from datetime import datetime

from ..base import BaseResearchTool, ResearchToolInput
from ...models.claim import Claim, ClaimType, Provenance


class ClaimExtractorInput(ResearchToolInput):
    """Input schema for claim extractor tool."""
    text: str = Field(description="Text to extract claims from")
    source_id: str = Field(description="ID of source document")
    source_type: str = Field(default="text", description="Type of source")
    source_url: Optional[str] = Field(default=None, description="URL of source")
    max_claims: int = Field(default=20, description="Maximum number of claims to extract")


class ClaimExtractorTool(BaseResearchTool):
    """
    Tool for extracting factual claims from text.
    
    Identifies:
    - Numerical claims (X% improvement, Y accuracy, etc.)
    - Comparative claims (better than, faster than, etc.)
    - Experimental results
    - Theoretical assertions
    """
    
    name: str = "claim_extractor"
    description: str = "Extract factual claims from text with provenance tracking"
    args_schema: Type[BaseModel] = ClaimExtractorInput
    
    def execute(
        self,
        text: str,
        source_id: str,
        source_type: str = "text",
        source_url: Optional[str] = None,
        max_claims: int = 20
    ) -> Dict[str, Any]:
        """
        Extract claims from text.
        
        Args:
            text: Text to extract claims from
            source_id: ID of source document
            source_type: Type of source
            source_url: URL of source
            max_claims: Maximum number of claims to extract
            
        Returns:
            Dictionary containing extracted claims
        """
        claims = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        for i, sentence in enumerate(sentences):
            # Check if sentence contains a claim
            claim_type = self._identify_claim_type(sentence)
            
            if claim_type:
                # Extract entities and metrics
                entities = self._extract_entities(sentence)
                metrics = self._extract_metrics(sentence)
                
                # Create provenance
                provenance = Provenance(
                    source_id=source_id,
                    source_type=source_type,
                    source_url=source_url,
                    paragraph=i // 5,  # Approximate paragraph number
                    line_range=(i, i)
                )
                
                # Create claim
                claim = Claim(
                    claim_id=f"{source_id}_claim_{len(claims)+1}",
                    text=sentence.strip(),
                    claim_type=claim_type,
                    provenance=provenance,
                    entities=entities,
                    metrics=metrics,
                    context=self._get_context(sentences, i)
                )
                
                claims.append(claim)
                
                if len(claims) >= max_claims:
                    break
        
        return {
            "claims": [claim.model_dump() for claim in claims],
            "num_claims": len(claims),
            "num_sentences_analyzed": len(sentences)
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _identify_claim_type(self, sentence: str) -> Optional[ClaimType]:
        """Identify if sentence contains a claim and its type."""
        sentence_lower = sentence.lower()
        
        # Numerical claim patterns
        numerical_patterns = [
            r'\d+\.?\d*\s*%',  # Percentages
            r'\d+\.?\d*\s*(?:times|fold)',  # Multipliers
            r'accuracy|precision|recall|f1|score|error|rate',  # Metrics
            r'improved?|increased?|decreased?|reduced?|better|worse'
        ]
        
        if any(re.search(pattern, sentence_lower) for pattern in numerical_patterns):
            if re.search(r'\d+\.?\d*\s*%', sentence):
                return ClaimType.NUMERICAL
        
        # Comparative claim patterns
        comparative_patterns = [
            r'better than|worse than|faster than|slower than',
            r'outperform|surpass|exceed',
            r'compared to|in comparison|versus|vs\.'
        ]
        
        if any(re.search(pattern, sentence_lower) for pattern in comparative_patterns):
            return ClaimType.COMPARATIVE
        
        # Experimental claim patterns
        experimental_patterns = [
            r'we (?:found|observed|discovered|showed|demonstrated)',
            r'results? (?:show|indicate|suggest|reveal)',
            r'experiment|evaluation|test|benchmark'
        ]
        
        if any(re.search(pattern, sentence_lower) for pattern in experimental_patterns):
            return ClaimType.EXPERIMENTAL
        
        # Theoretical claim patterns
        theoretical_patterns = [
            r'we (?:propose|introduce|present|define)',
            r'theorem|lemma|proposition|hypothesis',
            r'can be shown|it follows that|therefore'
        ]
        
        if any(re.search(pattern, sentence_lower) for pattern in theoretical_patterns):
            return ClaimType.THEORETICAL
        
        return None
    
    def _extract_entities(self, sentence: str) -> List[str]:
        """Extract named entities from sentence."""
        entities = []
        
        # Simple entity extraction (capitalized words/phrases)
        # In production, use spaCy or similar NER
        capitalized_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.finditer(capitalized_pattern, sentence)
        
        for match in matches:
            entity = match.group(0)
            # Filter out sentence-starting words
            if entity not in ['The', 'This', 'That', 'These', 'Those', 'We', 'Our']:
                entities.append(entity)
        
        return list(set(entities))[:10]  # Limit and deduplicate
    
    def _extract_metrics(self, sentence: str) -> Dict[str, Any]:
        """Extract numerical metrics from sentence."""
        metrics = {}
        
        # Extract percentages
        percentage_pattern = r'(\d+\.?\d*)\s*%'
        percentages = re.findall(percentage_pattern, sentence)
        if percentages:
            metrics['percentages'] = [float(p) for p in percentages]
        
        # Extract accuracy/precision/recall values
        metric_pattern = r'(?:accuracy|precision|recall|f1|error|rate)[\s:=]+(\d+\.?\d*)'
        metric_matches = re.finditer(metric_pattern, sentence, re.IGNORECASE)
        for match in metric_matches:
            metric_name = match.group(0).split()[0].lower()
            metric_value = float(match.group(1))
            metrics[metric_name] = metric_value
        
        return metrics
    
    def _get_context(self, sentences: List[str], index: int, window: int = 1) -> str:
        """Get surrounding context for a sentence."""
        start = max(0, index - window)
        end = min(len(sentences), index + window + 1)
        
        context_sentences = sentences[start:end]
        return ' '.join(context_sentences)
