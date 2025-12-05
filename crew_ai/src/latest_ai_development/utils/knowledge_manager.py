"""
Knowledge Manager for Deep Research Agent

This module provides utilities for managing research knowledge across sessions,
enabling context persistence and cross-query learning.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource


class ResearchKnowledgeManager:
    """Manages knowledge persistence for research sessions."""
    
    def __init__(self, knowledge_dir: str = "knowledge"):
        """
        Initialize the knowledge manager.
        
        Args:
            knowledge_dir: Directory to store knowledge files
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        (self.knowledge_dir / "research_sessions").mkdir(exist_ok=True)
        (self.knowledge_dir / "domain_knowledge").mkdir(exist_ok=True)
        
    def save_research_session(
        self,
        query: str,
        findings: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Save research findings from a session.
        
        Args:
            query: The research query
            findings: The research findings/report
            session_id: Optional session identifier
            
        Returns:
            Path to the saved file
        """
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        filename = f"session_{session_id}.txt"
        filepath = self.knowledge_dir / "research_sessions" / filename
        
        content = f"""
Research Query: {query}
Date: {datetime.now().isoformat()}
Session ID: {session_id}

{'='*80}
FINDINGS
{'='*80}

{findings}
"""
        
        filepath.write_text(content)
        return str(filepath)
    
    def get_all_knowledge_sources(self) -> List[TextFileKnowledgeSource]:
        """
        Get all knowledge sources from the knowledge directory.
        
        Returns:
            List of TextFileKnowledgeSource objects
        """
        knowledge_sources = []
        
        # Get all text files from research sessions
        session_files = list((self.knowledge_dir / "research_sessions").glob("*.txt"))
        
        # Get all text files from domain knowledge
        domain_files = list((self.knowledge_dir / "domain_knowledge").glob("*.txt"))
        
        all_files = session_files + domain_files
        
        if all_files:
            # Create relative paths from knowledge directory
            relative_paths = [
                str(f.relative_to(self.knowledge_dir)) for f in all_files
            ]
            
            knowledge_sources.append(
                TextFileKnowledgeSource(file_paths=relative_paths)
            )
            
        return knowledge_sources
    
    def add_domain_knowledge(self, topic: str, content: str) -> str:
        """
        Add domain-specific knowledge.
        
        Args:
            topic: Topic name (used for filename)
            content: Knowledge content
            
        Returns:
            Path to the saved file
        """
        # Sanitize topic for filename
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_topic = safe_topic.replace(' ', '_').lower()
        
        filename = f"{safe_topic}.txt"
        filepath = self.knowledge_dir / "domain_knowledge" / filename
        
        filepath.write_text(content)
        return str(filepath)
    
    def create_session_knowledge_source(self, findings: str) -> StringKnowledgeSource:
        """
        Create a knowledge source from current session findings.
        
        Args:
            findings: Current research findings
            
        Returns:
            StringKnowledgeSource with the findings
        """
        return StringKnowledgeSource(
            content=findings,
            metadata={"type": "current_session", "timestamp": datetime.now().isoformat()}
        )
    
    def get_knowledge_stats(self) -> dict:
        """Get statistics about stored knowledge."""
        session_files = list((self.knowledge_dir / "research_sessions").glob("*.txt"))
        domain_files = list((self.knowledge_dir / "domain_knowledge").glob("*.txt"))
        
        return {
            "total_sessions": len(session_files),
            "domain_knowledge_files": len(domain_files),
            "total_knowledge_files": len(session_files) + len(domain_files),
            "storage_path": str(self.knowledge_dir.absolute())
        }
