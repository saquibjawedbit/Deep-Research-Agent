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
    SourceValidationList,
    InsightList,
    DocumentList,
    MethodologyReviewList,
    CrossReferenceList,
    EvidenceRatingList,
    CitationReport,
    Analysis,
    QualityReport,
    RefinementReport,
    ResearchPlan,
    ParallelResearchPathList,
    VisualizationList,
    IterativeRefinementDecision,
    EnhancedDeepResearchReport
)

# Import knowledge manager
from .utils.knowledge_manager import ResearchKnowledgeManager


@CrewBase
class LatestAiDevelopment():
    """Deep Research Crew - Phase 1 MVP"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        """Initialize the crew with knowledge management."""
        self.knowledge_manager = ResearchKnowledgeManager()

    @agent
    def research_lead(self) -> Agent:
        """Research orchestrator and synthesis lead."""
        return Agent(
            config=self.agents_config['research_lead'],
            verbose=True,
            allow_delegation=False  # No delegation needed in sequential process
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


    @agent
    def query_expansion_specialist(self) -> Agent:
        """Research planning and query expansion expert."""
        return Agent(
            config=self.agents_config['query_expansion_specialist'],
            verbose=True
        )

    @agent
    def web_search_specialist(self) -> Agent:
        """Real-time web search and information discovery specialist."""
        return Agent(
            config=self.agents_config['web_search_specialist'],
            tools=[
                SerperSearchTool(),
                WebScraperTool(),
                EnhancedFirecrawlTool()
            ],
            verbose=True
        )

    @agent
    def synthesis_expert(self) -> Agent:
        """Multi-perspective synthesis and integration specialist."""
        return Agent(
            config=self.agents_config['synthesis_expert'],
            verbose=True
        )

    @agent
    def visualization_specialist(self) -> Agent:
        """Data visualization and presentation expert."""
        return Agent(
            config=self.agents_config['visualization_specialist'],
            verbose=True
        )

    @task
    def query_expansion_task(self) -> Task:
        """Transform user query into multi-step research plan."""
        return Task(
            config=self.tasks_config['query_expansion_task'],
            context=[]
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
    def parallel_research_task(self) -> Task:
        """Execute parallel research across multiple subtopics."""
        return Task(
            config=self.tasks_config['parallel_research_task'],
            async_execution=True,
            context=[]
        )

    @task
    def perspective_synthesis_task(self) -> Task:
        """Synthesize findings from parallel research paths."""
        return Task(
            config=self.tasks_config['perspective_synthesis_task'],
            context=[]
        )

    @task
    def iterative_deepening_task(self) -> Task:
        """Evaluate completeness and decide whether to continue research."""
        return Task(
            config=self.tasks_config['iterative_deepening_task'],
            context=[]
        )

    @task
    def visualization_generation_task(self) -> Task:
        """Generate visualizations for key findings."""
        return Task(
            config=self.tasks_config['visualization_generation_task'],
            context=[]
        )

    @task
    def report_generation_task(self) -> Task:
        """Generate final research report."""
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_file='research_report.md',
            context=[]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Deep Research Crew with Gemini Deep Research capabilities"""
        # Use all agents including research_lead for sequential process
        all_agents = [
            self.research_lead(),
            self.literature_miner(),
            self.senior_analyst(),
            self.report_composer(),
            self.data_validator(),
            self.cross_reference_specialist(),
            self.methodology_critic(),
            self.citation_expert(),
            self.evidence_evaluator(),
            self.query_expansion_specialist(),
            self.web_search_specialist(),
            self.synthesis_expert(),
            self.visualization_specialist()
        ]
        
        # Get knowledge sources from previous research sessions
        knowledge_sources = self.knowledge_manager.get_all_knowledge_sources()
        
        return Crew(
            agents=all_agents,
            tasks=self.tasks,
            process=Process.sequential,  # Changed to sequential for better reliability with local LLM
            verbose=True,
            memory=False,  # Disabled to avoid OpenAI API requirement with local LLM
            knowledge_sources=knowledge_sources  # Add persistent knowledge
        )

    def research_crew(self) -> Crew:
        """Creates the Enhanced Research Phase Crew with parallel execution"""
        return Crew(
            tasks=[
                self.query_expansion_task(),  # NEW: Multi-step planning
                self.discovery_task(),
                self.source_validation_task(),
                self.parallel_research_task(),  # NEW: Parallel research paths
                self.literature_mining_task(),
                self.source_verification_task(),
                self.claim_extraction_task(),
                self.perspective_synthesis_task(),  # NEW: Synthesize parallel findings
                self.methodology_review_task(),
                self.cross_reference_task(),
                self.evidence_evaluation_task(),
                self.citation_validation_task(),
                self.deep_analysis_task(),
                self.quality_assurance_task(),
                self.iterative_deepening_task()  # NEW: Decide if more research needed
            ],
            process=Process.hierarchical,
            manager_agent=self.research_lead(),
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
        """Creates the Enhanced Reporting Phase Crew with visualizations"""
        return Crew(
            tasks=[
                self.visualization_generation_task(),  # NEW: Generate visualizations
                self.report_generation_task()
            ],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
