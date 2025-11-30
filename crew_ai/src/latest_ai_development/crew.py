from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# Import custom tools
from .tools.ingestion.pdf_parser import PDFParserTool
from .tools.ingestion.web_scraper import WebScraperTool
from .tools.analysis.claim_extractor import ClaimExtractorTool
from .tools.analysis.fact_checker import FactCheckerTool
from .tools.output.report_generator import ReportGeneratorTool


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
            verbose=True,
            allow_delegation=False
        )

    @agent
    def literature_miner(self) -> Agent:
        """Literature mining and document analysis specialist."""
        return Agent(
            config=self.agents_config['literature_miner'],
            tools=[PDFParserTool(), WebScraperTool(), ClaimExtractorTool()],
            verbose=True
        )

    @agent
    def claim_verifier(self) -> Agent:
        """Fact-checking and claim verification specialist."""
        return Agent(
            config=self.agents_config['claim_verifier'],
            tools=[FactCheckerTool()],
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

    @task
    def discovery_task(self) -> Task:
        """Initial query understanding and research planning."""
        return Task(
            config=self.tasks_config['discovery_task'],
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
    def fact_checking_task(self) -> Task:
        """Verify claims against external sources."""
        return Task(
            config=self.tasks_config['fact_checking_task'],
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
        )
