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
    
    print("=" * 80)
    print("DEEP RESEARCH CREW - Enhanced with Quality Control")
    print("=" * 80)
    print(f"\n📋 Research Query: {inputs['query']}")
    print(f"📅 Date Range: {inputs['start_date']} to {inputs['end_date']}")
    print(f"📚 Sources: {inputs['sources']}")
    print(f"📊 Max Documents: {inputs['max_docs']}")
    print(f"\n🎯 Quality Control Settings:")
    print(f"   • Depth Level: {inputs['depth_level']}/5")
    print(f"   • Quality Threshold: {inputs['quality_threshold']}")
    print(f"   • Fact Checking: {'✓ Enabled' if inputs['enable_fact_checking'] else '✗ Disabled'}")
    print(f"   • Iterative Refinement: {'✓ Enabled' if inputs['enable_iterative_refinement'] else '✗ Disabled'}")
    print(f"   • Min Sources per Claim: {inputs['min_sources_per_claim']}")
    print("\n" + "=" * 80 + "\n")

    try:
        result = LatestAiDevelopment().crew().kickoff(inputs=inputs)
        
        print("\n" + "=" * 80)
        print("✅ RESEARCH COMPLETE")
        print("=" * 80)
        print(f"\n📄 Report saved to: research_report.md")
        print("\n📊 Enhanced Features Applied:")
        print("   ✓ Source credibility validation")
        print("   ✓ Cross-reference fact checking")
        print("   ✓ Methodology critique")
        print("   ✓ Evidence strength rating")
        print("   ✓ Citation validation")
        print("   ✓ Quality assurance review")
        print("\n💡 Check the report for:")
        print("   • Evidence quality ratings")
        print("   • Source credibility scores")
        print("   • Methodology assessments")
        print("   • Cross-referenced claims")
        print("   • Citation network")
        
        return result
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

if __name__ == "__main__":
    run()
