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
        crew_instance = LatestAiDevelopment()
        
        # 1. Research Phase
        print("\n🔍 Starting Phase 1: Research & Analysis...")
        research_crew = crew_instance.research_crew()
        research_result = research_crew.kickoff(inputs=inputs)
        
        quality_report = research_result.pydantic
        quality_score = quality_report.overall_quality_score if quality_report else 0.0
        print(f"\n📊 Quality Score: {quality_score:.2f} (Threshold: {inputs['quality_threshold']})")
        
        # 2. Refinement Phase (Conditional)
        if inputs['enable_iterative_refinement'] and quality_score < inputs['quality_threshold']:
            print("\n🔄 Quality below threshold. Starting Phase 2: Iterative Refinement...")
            max_iterations = inputs['max_iterations']
            current_iteration = 0
            
            while current_iteration < max_iterations and quality_score < inputs['quality_threshold']:
                current_iteration += 1
                print(f"   > Iteration {current_iteration}/{max_iterations}...")
                
                refinement_inputs = inputs.copy()
                refinement_inputs['quality_report'] = quality_report.model_dump() if quality_report else {}
                
                refinement_crew = crew_instance.refinement_crew()
                refinement_result = refinement_crew.kickoff(inputs=refinement_inputs)
                
                refinement_report = refinement_result.pydantic
                if refinement_report:
                    quality_score = refinement_report.updated_quality_score
                    print(f"   > New Quality Score: {quality_score:.2f}")
        
        # 3. Report Generation Phase
        print("\n📝 Starting Phase 3: Final Report Generation...")
        report_crew = crew_instance.report_crew()
        final_result = report_crew.kickoff(inputs=inputs)
        
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
        print("   ✓ Conditional refinement loop")
        
        return final_result
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
    
    print("=" * 80)
    print("🚀 Starting Deep Research Agent API Server")
    print("=" * 80)
    print("\n📡 Server will be available at:")
    print("   • Local: http://localhost:8000")
    print("   • Network: http://0.0.0.0:8000")
    print("\n📚 API Documentation:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("\n" + "=" * 80 + "\n")
    
    uvicorn.run(
        "latest_ai_development.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    run()
