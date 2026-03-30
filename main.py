from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from query_agent import get_agent, QueryAgent
from models import QueryResponse, ErrorResponse
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GenAI Query Agent API",
    description="AI-powered MongoDB Query Agent for ERP Systems",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request Models ====================
class QueryRequest(BaseModel):
    query: str
    debug: bool = False

class BatchQueryRequest(BaseModel):
    queries: List[str]

# ==================== Utility ====================
def get_query_agent() -> QueryAgent:
    """Dependency injection for query agent"""
    return get_agent()

# ==================== Health Check ====================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "GenAI Query Agent is running"
    }

# ==================== Main Query Endpoint ====================
@app.post("/query", response_model=dict)
async def process_query(
    request: QueryRequest,
    agent: QueryAgent = Depends(get_query_agent)
):
    
    try:
        print("Processing the query and getting result")
        result = agent.process_question(request.query)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": result.get("error"),
                    "question": request.query
                }
            )
        
        response = {
            "success": True,
            "query": request.query,
            "collection": result.get("collection"),
            "result_count": result.get("result_count", 0),
            "data": result.get("results", []),
            "response_text": result.get("response_text", "")
        }
        
        if request.debug:
            response["generated_query"] = result.get("generated_query")
        
        return response
    
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "question": request.query
            }
        )
        
@app.post("/agent-query", response_model=dict)
async def agent_query(
    request: QueryRequest,
    agent: QueryAgent = Depends(get_query_agent)
):
    try:
        print("Processing agent-based query")

        # ✅ Call agent (NOT llm_provider)
        result = agent.process_question(request.query)

        return result

    except Exception as e:
        logger.exception(f"Agent error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e),
                "query": request.query
            }
        )

# ==================== Batch Query Endpoint ====================
@app.post("/batch-query")
async def batch_process_queries(
    request: BatchQueryRequest,
    agent: QueryAgent = Depends(get_query_agent)
):
    """
    Process multiple natural language questions at once.
    
    Example:
    {
        "queries": [
            "List all students in class 6",
            "Show attendance for today"
        ]
    }
    """
    try:
        results = agent.process_batch_questions(request.queries)
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        return {
            "success": len(successful) > 0,
            "total_queries": len(request.queries),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }
    
    except Exception as e:
        logger.exception(f"Error in batch processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(e)
            }
        )

# ==================== Help/Info Endpoints ====================
@app.get("/queries/examples")
async def get_example_queries():
    """Get example queries organized by complexity level"""
    return {
        "level_1_basic": [
            "List all students in class 6",
            "Show the attendance of John Doe for January 15",
            "List all teachers in the system",
            "Show all assignments created today"
        ],
        "level_2_filtering": [
            "Show students who were absent yesterday",
            "List assignments due this week",
            "Show students belonging to section A of class 6",
            "Show all exams scheduled this month"
        ],
        "level_3_aggregation": [
            "Count how many students were absent today",
            "Show the number of assignments submitted per class",
            "Find the class with the highest number of absent students today"
        ],
        "level_4_multi_collection": [
            "Show students who have not submitted an assignment",
            "List teachers and the classes they teach",
            "Show attendance percentage of each student"
        ],
        "level_5_analytical": [
            "Show the top 5 students with the highest attendance percentage"
        ]
    }

@app.get("/info")
async def get_info():
    """Get API and system information"""
    return {
        "name": "GenAI Query Agent API",
        "version": "1.0.0",
        "llm_provider": "Configured - Check environment",
        "endpoints": {
            "health": "/health (GET)",
            "query": "/query (POST)",
            "batch_query": "/batch-query (POST)",
            "examples": "/queries/examples (GET)",
            "docs": "/docs (GET)"
        },
        "documentation": "Visit /docs for interactive Swagger UI"
    }

# ==================== Error Handlers ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "success": False,
        "error": str(exc),
        "type": exc.__class__.__name__
    }

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info" if not settings.DEBUG else "debug"
    )
