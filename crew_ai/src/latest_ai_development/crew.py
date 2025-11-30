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
        )

    @task
    def source_validation_task(self) -> Task:
        """Validate source credibility before processing."""
        return Task(
            config=self.tasks_config['source_validation_task'],
        )

    @task
    def literature_mining_task(self) -> Task:
        """Document extraction and parsing."""
        return Task(
            config=self.tasks_config['literature_mining_task'],
        )

    @task
    def claim_extraction_task(self) -> Task:
        """Extract claims from documents."""
        return Task(
            config=self.tasks_config['claim_extraction_task'],
        )

    @task
    def methodology_review_task(self) -> Task:
        """Critically evaluate research methodologies."""
        return Task(
            config=self.tasks_config['methodology_review_task'],
        )

    @task
    def cross_reference_task(self) -> Task:
        """Cross-verify claims across multiple sources."""
        return Task(
            config=self.tasks_config['cross_reference_task'],
        )

    @task
    def evidence_evaluation_task(self) -> Task:
        """Rate evidence strength and reliability."""
        return Task(
            config=self.tasks_config['evidence_evaluation_task'],
        )

    @task
    def citation_validation_task(self) -> Task:
        """Validate citations and build citation network."""
        return Task(
            config=self.tasks_config['citation_validation_task'],
        )

    @task
    def deep_analysis_task(self) -> Task:
        """Analyze insights and synthesize findings."""
        return Task(
            config=self.tasks_config['deep_analysis_task'],
        )

    @task
    def quality_assurance_task(self) -> Task:
        """Perform final quality check before report generation."""
        return Task(
            config=self.tasks_config['quality_assurance_task'],
        )

    @task
    def iterative_refinement_task(self) -> Task:
        """Conduct targeted additional research if gaps identified."""
        return Task(
            config=self.tasks_config['iterative_refinement_task'],
        )

    @task
    def report_generation_task(self) -> Task:
        """Generate final research report."""
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_file='research_report.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Deep Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            # Knowledge Sources Configuration
            knowledge_sources=[
                TextFileKnowledgeSource(
                    file_paths=["data/user_preference.txt"]
                )
            ],
            embedder={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            }
        )
