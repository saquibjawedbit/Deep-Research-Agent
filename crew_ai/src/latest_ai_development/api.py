from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
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

@app.post("/api/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """
    Run the Deep Research Crew for a given query.
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
