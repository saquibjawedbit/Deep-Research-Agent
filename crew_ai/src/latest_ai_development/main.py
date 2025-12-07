#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from latest_ai_development.crew import LatestAiDevelopment

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the Deep Research Crew with enhanced quality control.
    """
    # Enhanced research parameters
    inputs = {
        # Core research parameters
        'query': 'efficacy of transformer models for natural language processing',
        'start_date': '2020-01-01',
        'end_date': str(datetime.now().year) + '-12-31',
        'sources': 'papers, web',
        'max_docs': 15,
        
        # Quality control parameters
        'depth_level': 3,  # 1-5 scale: 1=basic, 3=standard, 5=exhaustive
        'quality_threshold': 0.7,  # 0.0-1.0: minimum source credibility score
        'enable_fact_checking': True,  # Enable cross-reference validation
        'enable_iterative_refinement': True,  # Enable multi-pass research
        'max_iterations': 2,  # Maximum refinement iterations
        'min_sources_per_claim': 2,  # Minimum sources to validate a claim
    }

    try:
        crew_instance = LatestAiDevelopment()
        
        # Execute streamlined research workflow
        print("\n Starting Deep Research...")
        research_crew = crew_instance.crew()
        research_result = research_crew.kickoff(inputs=inputs)

        return research_result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")



def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        LatestAiDevelopment().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LatestAiDevelopment().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        LatestAiDevelopment().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = LatestAiDevelopment().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")

def run_server():
    """
    Run the FastAPI backend server.
    """
    import uvicorn
    import os
    
    # Change to src directory to ensure proper module imports
    src_dir = os.path.join(os.path.dirname(__file__), '..')
    os.chdir(src_dir)
    
    uvicorn.run(
        "latest_ai_development.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    run()
