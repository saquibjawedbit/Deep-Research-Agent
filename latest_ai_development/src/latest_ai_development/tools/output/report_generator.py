"""Report generation tool for creating research reports."""

from typing import Any, Dict, Type, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import json

from ..base import BaseResearchTool, ResearchToolInput
from ...models.claim import Claim
from ...models.document import Document
from ...models.research import ResearchResult


class ReportGeneratorInput(ResearchToolInput):
    """Input schema for report generator tool."""
    research_result: Dict[str, Any] = Field(description="Research result data")
    output_path: str = Field(default="research_report.md", description="Output file path")
    include_provenance: bool = Field(default=True, description="Include provenance information")


class ReportGeneratorTool(BaseResearchTool):
    """
    Tool for generating research reports in Markdown format.
    
    Generates:
    - Executive summary
    - Claim-by-claim analysis
    - Confidence scores and evidence
    - Provenance links
    - Key findings
    """
    
    name: str = "report_generator"
    description: str = "Generate comprehensive research reports with claims, evidence, and provenance"
    args_schema: Type[BaseModel] = ReportGeneratorInput
    
    def execute(
        self,
        research_result: Dict[str, Any],
        output_path: str = "research_report.md",
        include_provenance: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a research report.
        
        Args:
            research_result: Research result data
            output_path: Output file path
            include_provenance: Include provenance information
            
        Returns:
            Dictionary containing report metadata
        """
        # Parse research result
        result = ResearchResult(**research_result)
        
        # Generate report content
        report = self._generate_report(result, include_provenance)
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report)
        
        return {
            "report_path": str(output_file.absolute()),
            "report_size_bytes": len(report),
            "num_claims_reported": len(result.claims),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_report(self, result: ResearchResult, include_provenance: bool) -> str:
        """Generate report content."""
        lines = []
        
        # Title
        lines.append(f"# Deep Research Report: {result.query_text}")
        lines.append("")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        if result.executive_summary:
            lines.append(result.executive_summary)
        else:
            lines.append(f"This report analyzes **{result.total_documents_processed}** documents "
                        f"and extracts **{result.total_claims_extracted}** claims related to: *{result.query_text}*")
        lines.append("")
        
        # Statistics
        lines.append("### Research Statistics")
        lines.append("")
        lines.append(f"- **Documents Found**: {result.total_documents_found}")
        lines.append(f"- **Documents Processed**: {result.total_documents_processed}")
        lines.append(f"- **Claims Extracted**: {result.total_claims_extracted}")
        lines.append(f"- **Verified Claims**: {result.verified_claims}")
        lines.append(f"- **Contradicted Claims**: {result.contradicted_claims}")
        lines.append("")
        
        # Key Findings
        if result.key_findings:
            lines.append("### Key Findings")
            lines.append("")
            for i, finding in enumerate(result.key_findings, 1):
                lines.append(f"{i}. {finding}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # Claims Analysis
        lines.append("## Claims Analysis")
        lines.append("")
        
        # Group claims by confidence
        verified_claims = [c for c in result.claims if c.confidence.value == "verified"]
        partial_claims = [c for c in result.claims if c.confidence.value == "partially_verified"]
        contradicted_claims = [c for c in result.claims if c.confidence.value == "contradicted"]
        unknown_claims = [c for c in result.claims if c.confidence.value == "unknown"]
        
        # Verified claims
        if verified_claims:
            lines.append("### ✅ Verified Claims")
            lines.append("")
            for claim in verified_claims:
                lines.extend(self._format_claim(claim, include_provenance))
            lines.append("")
        
        # Partially verified claims
        if partial_claims:
            lines.append("### ⚠️ Partially Verified Claims")
            lines.append("")
            for claim in partial_claims:
                lines.extend(self._format_claim(claim, include_provenance))
            lines.append("")
        
        # Contradicted claims
        if contradicted_claims:
            lines.append("### ❌ Contradicted Claims")
            lines.append("")
            for claim in contradicted_claims:
                lines.extend(self._format_claim(claim, include_provenance))
            lines.append("")
        
        # Unknown claims
        if unknown_claims:
            lines.append("### ❓ Unverified Claims")
            lines.append("")
            for claim in unknown_claims:
                lines.extend(self._format_claim(claim, include_provenance))
            lines.append("")
        
        # Documents
        lines.append("---")
        lines.append("")
        lines.append("## Source Documents")
        lines.append("")
        for i, doc in enumerate(result.documents[:20], 1):  # Limit to 20
            lines.append(f"### {i}. {doc.title}")
            lines.append("")
            if doc.authors:
                lines.append(f"**Authors**: {', '.join(doc.authors)}")
            if doc.url:
                lines.append(f"**URL**: {doc.url}")
            if doc.abstract:
                lines.append(f"**Abstract**: {doc.abstract[:300]}...")
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by Deep Research Crew*")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _format_claim(self, claim: Claim, include_provenance: bool) -> List[str]:
        """Format a single claim for the report."""
        lines = []
        
        lines.append(f"#### {claim.claim_id}")
        lines.append("")
        lines.append(f"> {claim.text}")
        lines.append("")
        
        # Metadata
        lines.append(f"**Type**: {claim.claim_type.value}")
        lines.append(f"**Confidence**: {claim.confidence.value}")
        
        if claim.entities:
            lines.append(f"**Entities**: {', '.join(claim.entities)}")
        
        if claim.metrics:
            metrics_str = ', '.join(f"{k}: {v}" for k, v in claim.metrics.items())
            lines.append(f"**Metrics**: {metrics_str}")
        
        lines.append("")
        
        # Evidence
        if claim.evidence:
            lines.append("**Evidence**:")
            lines.append("")
            for i, evidence in enumerate(claim.evidence[:3], 1):  # Limit to 3
                support_icon = "✓" if evidence.supports_claim else "✗"
                lines.append(f"{i}. {support_icon} {evidence.text[:150]}...")
                if evidence.provenance.source_url:
                    lines.append(f"   - Source: {evidence.provenance.source_url}")
            lines.append("")
        
        # Provenance
        if include_provenance:
            prov = claim.provenance
            lines.append("**Provenance**:")
            lines.append(f"- Source: {prov.source_id} ({prov.source_type})")
            if prov.source_url:
                lines.append(f"- URL: {prov.source_url}")
            if prov.page_number:
                lines.append(f"- Page: {prov.page_number}")
            if prov.section:
                lines.append(f"- Section: {prov.section}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return lines
