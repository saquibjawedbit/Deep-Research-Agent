from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# Import custom tools
from .tools.ingestion.pdf_parser import PDFParserTool
from .tools.ingestion.web_scraper import WebScraperTool
from .tools.ingestion.advanced_search import SerperSearchTool
from .tools.ingestion.firecrawl_scraper import EnhancedFirecrawlTool
from .tools.ingestion.youtube_search import EnhancedYouTubeSearchTool
from .tools.analysis.claim_extractor import ClaimExtractorTool
from .tools.output.report_generator import ReportGeneratorTool

# Import knowledge sources
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

# Import Pydantic models
from .schemas import (
    SourceValidation,
    SourceValidationList,
    Insight,
    InsightList,
    Document,
    DocumentList,
    MethodologyReview,
    MethodologyReviewList,
    CrossReference,
    CrossReferenceList,
    EvidenceRating,
    EvidenceRatingList,
    CitationReport,
    Analysis,
    QualityReport,
    RefinementReport,
    DeepResearchReport
)


@CrewBase
class LatestAiDevelopment():
    """Deep Research Crew - Phase 1 MVP"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def research_lead(self) -> Agent:
        """Research orchestrator and synthesis lead."""
        return Agent(
            config=self.agents_config['research_lead'],
            tools=[SerperSearchTool()],  # Add search capability
            verbose=True,
            allow_delegation=False
        )

    @agent
    def literature_miner(self) -> Agent:
        """Literature mining and document analysis specialist."""
        return Agent(
            config=self.agents_config['literature_miner'],
            tools=[
                SerperSearchTool(),  # Added search capability
                PDFParserTool(),
                WebScraperTool(),
                EnhancedFirecrawlTool(),  # Advanced web scraping with fallback
                EnhancedYouTubeSearchTool(),  # YouTube video search
                ClaimExtractorTool()
            ],
            verbose=True
        )

    @agent
    def senior_analyst(self) -> Agent:
        """Senior data analyst and strategist."""
        return Agent(
            config=self.agents_config['senior_analyst'],
            verbose=True
        )

    @agent
    def report_composer(self) -> Agent:
        """Research report and documentation specialist."""
        return Agent(
            config=self.agents_config['report_composer'],
            tools=[ReportGeneratorTool()],
            verbose=True
        )

    @agent
    def data_validator(self) -> Agent:
        """Data quality assurance and source credibility specialist."""
        return Agent(
            config=self.agents_config['data_validator'],
            verbose=True
        )

    @agent
    def cross_reference_specialist(self) -> Agent:
        """Cross-verification and fact-checking expert."""
        return Agent(
            config=self.agents_config['cross_reference_specialist'],
            verbose=True
        )

    @agent
    def methodology_critic(self) -> Agent:
        """Research methodology evaluator."""
        return Agent(
            config=self.agents_config['methodology_critic'],
            verbose=True
        )

    @agent
    def citation_expert(self) -> Agent:
        """Citation and provenance specialist."""
        return Agent(
            config=self.agents_config['citation_expert'],
            verbose=True
        )

    @agent
    def evidence_evaluator(self) -> Agent:
        """Evidence strength and reliability assessor."""
        return Agent(
            config=self.agents_config['evidence_evaluator'],
            verbose=True
        )


    @task
    def discovery_task(self) -> Task:
        """Initial query understanding and research planning."""
        return Task(
            config=self.tasks_config['discovery_task'],
            context=[]
        )

    @task
    def source_validation_task(self) -> Task:
        """Validate source credibility before processing."""
        return Task(
            config=self.tasks_config['source_validation_task'],
            output_pydantic=SourceValidationList,
            context=[]
        )

    @task
    def literature_mining_task(self) -> Task:
        """Document extraction and parsing."""
        return Task(
            config=self.tasks_config['literature_mining_task'],
            output_pydantic=DocumentList,
            async_execution=True,
            context=[]
        )

    @task
    def source_verification_task(self) -> Task:
        """Verify and cross-reference gathered data."""
        return Task(
            config=self.tasks_config['source_verification_task'],
            context=[]
        )

    @task
    def claim_extraction_task(self) -> Task:
        """Extract claims from documents."""
        return Task(
            config=self.tasks_config['claim_extraction_task'],
            output_pydantic=InsightList,
            context=[]
        )

    @task
    def methodology_review_task(self) -> Task:
        """Critically evaluate research methodologies."""
        return Task(
            config=self.tasks_config['methodology_review_task'],
            output_pydantic=MethodologyReviewList,
            context=[]
        )

    @task
    def cross_reference_task(self) -> Task:
        """Cross-verify claims across multiple sources."""
        return Task(
            config=self.tasks_config['cross_reference_task'],
            output_pydantic=CrossReferenceList,
            context=[]
        )

    @task
    def evidence_evaluation_task(self) -> Task:
        """Rate evidence strength and reliability."""
        return Task(
            config=self.tasks_config['evidence_evaluation_task'],
            output_pydantic=EvidenceRatingList,
            context=[]
        )

    @task
    def citation_validation_task(self) -> Task:
        """Validate citations and build citation network."""
        return Task(
            config=self.tasks_config['citation_validation_task'],
            output_pydantic=CitationReport,
            context=[]
        )

    @task
    def deep_analysis_task(self) -> Task:
        """Analyze insights and synthesize findings."""
        return Task(
            config=self.tasks_config['deep_analysis_task'],
            output_pydantic=Analysis,
            context=[]
        )

    @task
    def quality_assurance_task(self) -> Task:
        """Perform final quality check before report generation."""
        return Task(
            config=self.tasks_config['quality_assurance_task'],
            output_pydantic=QualityReport,
            context=[]
        )

    @task
    def iterative_refinement_task(self) -> Task:
        """Conduct targeted additional research if gaps identified."""
        return Task(
            config=self.tasks_config['iterative_refinement_task'],
            output_pydantic=RefinementReport,
            context=[]
        )

    @task
    def report_generation_task(self) -> Task:
        """Generate final research report."""
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_pydantic=DeepResearchReport,
            output_file='research_report.md',
            context=[]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Deep Research Crew (Full Pipeline)"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            }
        )

    def research_crew(self) -> Crew:
        """Creates the Research Phase Crew"""
        return Crew(
            tasks=[
                self.discovery_task(),
                self.source_validation_task(),
                self.literature_mining_task(),
                self.source_verification_task(),
                self.claim_extraction_task(),
                self.methodology_review_task(),
                self.cross_reference_task(),
                self.evidence_evaluation_task(),
                self.citation_validation_task(),
                self.deep_analysis_task(),
                self.quality_assurance_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True
        )

    def refinement_crew(self) -> Crew:
        """Creates the Refinement Phase Crew"""
        return Crew(
            tasks=[self.iterative_refinement_task()],
            process=Process.sequential,
            verbose=True,
            memory=True
        )

    def report_crew(self) -> Crew:
        """Creates the Reporting Phase Crew"""
        return Crew(
            tasks=[self.report_generation_task()],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
