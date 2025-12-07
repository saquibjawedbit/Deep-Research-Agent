from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# Import custom tools - only what's needed
from .tools.ingestion.web_scraper import WebScraperTool
from .tools.ingestion.advanced_search import SerperSearchTool
from .tools.ingestion.firecrawl_scraper import EnhancedFirecrawlTool

# Import knowledge manager
from .utils.knowledge_manager import ResearchKnowledgeManager


@CrewBase
class LatestAiDevelopment():
    """Streamlined Deep Research Crew - Optimized for 5-10 min execution"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        """Initialize the crew with knowledge management."""
        self.knowledge_manager = ResearchKnowledgeManager()

    @agent
    def research_planner(self) -> Agent:
        """Research strategy architect."""
        return Agent(
            config=self.agents_config['research_planner'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def web_researcher(self) -> Agent:
        """Rapid information gatherer from web sources."""
        return Agent(
            config=self.agents_config['web_researcher'],
            tools=[
                SerperSearchTool(),
                WebScraperTool(),
                EnhancedFirecrawlTool()
            ],
            verbose=True
        )

    @agent
    def insight_analyst(self) -> Agent:
        """Fast synthesis specialist."""
        return Agent(
            config=self.agents_config['insight_analyst'],
            verbose=True
        )

    @agent
    def report_writer(self) -> Agent:
        """Concise research communicator."""
        return Agent(
            config=self.agents_config['report_writer'],
            verbose=True
        )

    @task
    def research_planning_task(self) -> Task:
        """Create focused research strategy."""
        return Task(
            config=self.tasks_config['research_planning_task']
        )

    @task
    def information_gathering_task(self) -> Task:
        """Rapid web research and information extraction."""
        return Task(
            config=self.tasks_config['information_gathering_task'],
            context=[self.research_planning_task()]
        )

    @task
    def analysis_task(self) -> Task:
        """Fast analysis and synthesis of gathered information."""
        return Task(
            config=self.tasks_config['analysis_task'],
            context=[self.research_planning_task(), self.information_gathering_task()]
        )

    @task
    def report_generation_task(self) -> Task:
        """Generate final research report."""
        return Task(
            config=self.tasks_config['report_generation_task'],
            output_file='research_report.md',
            context=[self.research_planning_task(), self.information_gathering_task(), self.analysis_task()]
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Streamlined Deep Research Crew - 5-10 min execution"""
        # Only 4 agents for fast execution
        streamlined_agents = [
            self.research_planner(),
            self.web_researcher(),
            self.insight_analyst(),
            self.report_writer()
        ]
        
        # Only 4 tasks in linear workflow
        streamlined_tasks = [
            self.research_planning_task(),
            self.information_gathering_task(),
            self.analysis_task(),
            self.report_generation_task()
        ]
        
        # Get knowledge sources from previous research sessions (optional)
        knowledge_sources = self.knowledge_manager.get_all_knowledge_sources()
        
        return Crew(
            agents=streamlined_agents,
            tasks=streamlined_tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disabled to prevent context overflow
            knowledge_sources=knowledge_sources if knowledge_sources else None
        )
