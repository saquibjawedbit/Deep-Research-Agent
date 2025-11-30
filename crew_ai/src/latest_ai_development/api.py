from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import os
import json
import asyncio
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from latest_ai_development.crew import LatestAiDevelopment

# Load environment variables
load_dotenv()

app = FastAPI(title="Deep Research Crew API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str
    start_date: Optional[str] = "2020-01-01"
    end_date: Optional[str] = None
    sources: Optional[str] = "papers, web"
    max_docs: Optional[int] = 10
    
    # Quality control parameters
    depth_level: Optional[int] = 3
    quality_threshold: Optional[float] = 0.7
    enable_fact_checking: Optional[bool] = True
    enable_iterative_refinement: Optional[bool] = True
    max_iterations: Optional[int] = 2
    min_sources_per_claim: Optional[int] = 2

class ResearchResponse(BaseModel):
    status: str
    result: str
    report_path: str

# Global status queue for streaming
status_queue = asyncio.Queue()

async def status_event_generator() -> AsyncGenerator[str, None]:
    """Generate SSE events from status updates."""
    while True:
        try:
            # Wait for status update with timeout
            status = await asyncio.wait_for(status_queue.get(), timeout=30.0)
            
            # If we get a "done" signal, send it and break
            if status.get("type") == "done":
                yield f"data: {json.dumps(status)}\n\n"
                break
                
            # Send the status update as SSE
            yield f"data: {json.dumps(status)}\n\n"
            
        except asyncio.TimeoutError:
            # Send keepalive ping
            yield f": keepalive\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            break

@app.get("/api/research/stream")
async def stream_research(
    query: str,
    start_date: Optional[str] = "2020-01-01",
    end_date: Optional[str] = None,
    sources: Optional[str] = "papers, web",
    max_docs: Optional[int] = 5,
    depth_level: Optional[int] = 3,
    quality_threshold: Optional[float] = 0.7,
    enable_fact_checking: Optional[bool] = True,
    enable_iterative_refinement: Optional[bool] = True,
    max_iterations: Optional[int] = 2,
    min_sources_per_claim: Optional[int] = 2
):
    """
    Stream research progress with real-time status updates.
    """
    if not end_date:
        end_date = f"{datetime.now().year}-12-31"

    inputs = {
        'query': query,
        'start_date': start_date,
        'end_date': end_date,
        'sources': sources,
        'max_docs': max_docs,
        'depth_level': depth_level,
        'quality_threshold': quality_threshold,
        'enable_fact_checking': enable_fact_checking,
        'enable_iterative_refinement': enable_iterative_refinement,
        'max_iterations': max_iterations,
        'min_sources_per_claim': min_sources_per_claim
    }

    async def run_crew_with_status():
        """Run crew and emit real-time status updates from actual agent activities."""
        from latest_ai_development.streaming_callback import StreamingCallbackHandler, create_step_callback, create_task_callback
        
        try:
            # Send initial status
            await status_queue.put({
                "type": "started",
                "message": "Initializing Deep Research Crew with 9 agents and 12 tasks...",
                "agent": "System"
            })
            
            # Create streaming callback handler
            callback_handler = StreamingCallbackHandler(status_queue)
            
            # Initialize crew
            await asyncio.sleep(0.5)
            await status_queue.put({
                "type": "system",
                "message": "Loading specialized agents: Research Lead, Literature Miner, Senior Analyst, Report Composer, Data Validator, Cross-Reference Specialist, Methodology Critic, Citation Expert, Evidence Evaluator",
                "agent": "System"
            })
            
            # Get the crew instance
            loop = asyncio.get_event_loop()
            crew_instance = LatestAiDevelopment()
            
            # Add step callbacks to all agents
            step_cb = create_step_callback(callback_handler)
            task_cb = create_task_callback(callback_handler)
            
            # Notify about quality control settings
            await status_queue.put({
                "type": "system",
                "message": f"Quality Control: Depth Level {inputs.get('depth_level', 3)}/5, Quality Threshold {inputs.get('quality_threshold', 0.7)}, Fact Checking {'Enabled' if inputs.get('enable_fact_checking') else 'Disabled'}",
                "agent": "System"
            })
            
            await asyncio.sleep(0.5)
            
            # Map task names to agent names for better status messages
            task_agent_map = {
                "discovery_task": "Principal Investigator",
                "source_validation_task": "Data Validator",
                "literature_mining_task": "Literature Miner",
                "claim_extraction_task": "Literature Miner",
                "methodology_review_task": "Methodology Critic",
                "cross_reference_task": "Cross-Reference Specialist",
                "evidence_evaluation_task": "Evidence Evaluator",
                "citation_validation_task": "Citation Expert",
                "deep_analysis_task": "Senior Analyst",
                "quality_assurance_task": "Data Validator",
                "iterative_refinement_task": "Principal Investigator",
                "report_generation_task": "Report Composer"
            }
            
            # Create a custom callback to track task progress
            task_count = 0
            total_tasks = 12
            
            async def task_progress_callback(task_output):
                nonlocal task_count
                task_count += 1
                await callback_handler.on_task_complete(task_output)
                await status_queue.put({
                    "type": "progress",
                    "message": f"Progress: {task_count}/{total_tasks} tasks completed",
                    "progress": int((task_count / total_tasks) * 100)
                })
            
            # Build crew with callbacks
            crew = crew_instance.crew()
            
            # Create a synchronous wrapper for the async callback
            # CrewAI calls callbacks synchronously, so we need to schedule the coroutine properly
            def sync_callback_wrapper(output):
                """Synchronous wrapper that schedules the async callback in the event loop."""
                try:
                    # Schedule the coroutine in the running event loop
                    asyncio.run_coroutine_threadsafe(task_progress_callback(output), loop)
                except Exception as e:
                    print(f"Error in callback: {e}")
            
            # Manually add callbacks to tasks (CrewAI will use these)
            for task in crew.tasks:
                task.callback = sync_callback_wrapper
            
            # Run the crew in executor to avoid blocking
            await status_queue.put({
                "type": "execution_started",
                "message": "Beginning deep research execution...",
                "agent": "System"
            })
            
            # Execute crew
            result = await loop.run_in_executor(None, lambda: crew.kickoff(inputs=inputs))
            
            # Send completion status
            await status_queue.put({
                "type": "completed",
                "message": "Deep research complete! Generated comprehensive report with quality metrics.",
                "result": str(result),
                "agent": "System"
            })
            
            # Signal done
            await status_queue.put({"type": "done"})
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            await status_queue.put({
                "type": "error",
                "message": f"{str(e)}",
                "details": error_details
            })
            await status_queue.put({"type": "done"})

    
    # Start crew execution in background
    asyncio.create_task(run_crew_with_status())
    
    # Return SSE stream
    return StreamingResponse(
        status_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/api/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """
    Run the Deep Research Crew for a given query (non-streaming).
    """
    if not request.end_date:
        request.end_date = f"{datetime.now().year}-12-31"

    inputs = {
        'query': request.query,
        'start_date': request.start_date,
        'end_date': request.end_date,
        'sources': request.sources,
        'max_docs': request.max_docs,
        'depth_level': request.depth_level,
        'quality_threshold': request.quality_threshold,
        'enable_fact_checking': request.enable_fact_checking,
        'enable_iterative_refinement': request.enable_iterative_refinement,
        'max_iterations': request.max_iterations,
        'min_sources_per_claim': request.min_sources_per_claim
    }

    try:
        # Initialize and run the crew
        crew = LatestAiDevelopment().crew()
        result = crew.kickoff(inputs=inputs)
        
        return ResearchResponse(
            status="success",
            result=str(result),
            report_path="research_report.md"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
