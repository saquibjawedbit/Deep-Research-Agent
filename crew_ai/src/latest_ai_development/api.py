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
    max_docs: Optional[int] = 5
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
        'max_docs': max_docs
    }

    async def run_crew_with_status():
        """Run crew and emit status updates."""
        try:
            # Send initial status
            await status_queue.put({
                "type": "started",
                "message": "Initializing Deep Research Agent...",
                "agent": "System"
            })
            
            # Simulate status updates (in real implementation, these would come from crew callbacks)
            await asyncio.sleep(1)
            await status_queue.put({
                "type": "agent_started",
                "message": "Research Lead is planning the research strategy...",
                "agent": "Principal Investigator"
            })
            
            await asyncio.sleep(2)
            await status_queue.put({
                "type": "thinking",
                "message": "Breaking down research questions...",
                "agent": "Principal Investigator"
            })
            
            # Run the actual crew in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            crew = LatestAiDevelopment().crew()
            
            await status_queue.put({
                "type": "task_started",
                "message": "Compiling sources and documents...",
                "agent": "Source Compiler"
            })
            
            result = await loop.run_in_executor(None, lambda: crew.kickoff(inputs=inputs))
            
            # Send completion status
            await status_queue.put({
                "type": "completed",
                "message": "Research complete!",
                "result": str(result)
            })
            
            # Signal done
            await status_queue.put({"type": "done"})
            
        except Exception as e:
            await status_queue.put({
                "type": "error",
                "message": str(e)
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
        'max_docs': request.max_docs
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
