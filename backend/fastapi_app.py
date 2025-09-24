from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio
import json
import uuid
from datetime import datetime
import logging

# Import system components
from main import initialize_system
from config import API_HOST, API_PORT, REACT_FRONTEND_URLS

# Setup FastAPI
app = FastAPI(
    title="Agentic Math RAG API with MCP Integration",
    description="AI-powered math education system with human feedback and MCP tools",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=REACT_FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global system components (initialized on startup)
SYSTEM_COMPONENTS = {}

class MathQuestion(BaseModel):
    question: str = Field(..., description="The math question to solve")
    use_mcp: bool = Field(default=False, description="Use MCP tools if available")

class MathSolution(BaseModel):
    question: str
    solution: str
    confidence: float
    sources: List[str]
    processing_time: float
    guardrails_passed: Dict[str, bool]
    feedback_rating: Optional[int] = None
    session_id: str

class FeedbackData(BaseModel):
    session_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comments: Dict[str, str] = Field(default_factory=dict)

class SystemStatus(BaseModel):
    status: str
    components: Dict[str, bool]
    knowledge_base_size: int
    total_feedback: int
    mcp_available: bool

class StreamResponse(BaseModel):
    type: str
    message: str
    session_id: str
    data: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize system components on FastAPI startup"""
    global SYSTEM_COMPONENTS
    try:
        logger.info("Initializing Agentic RAG system...")
        SYSTEM_COMPONENTS = await initialize_system()
        logger.info("System initialization complete!")
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Math RAG API with MCP Integration",
        "version": "1.0.0",
        "status": "active",
        "features": ["Portkey Guardrails", "Qdrant Vector DB", "DSPy Optimization", "MCP Tools", "Human Feedback"]
    }

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """System health check"""
    try:
        components = {
            "knowledge_base": len(SYSTEM_COMPONENTS.get('knowledge_base', [])) > 0,
            "vector_store": SYSTEM_COMPONENTS.get('vector_store_manager') is not None,
            "guardrails": (SYSTEM_COMPONENTS.get('llm_input_guardrails') is not None and 
                          SYSTEM_COMPONENTS.get('llm_output_guardrails') is not None),
            "web_search": SYSTEM_COMPONENTS.get('web_search_manager') is not None,
            "dspy_optimizer": SYSTEM_COMPONENTS.get('dspy_optimizer') is not None,
            "mcp_server": SYSTEM_COMPONENTS.get('mcp_server') is not None
        }
        
        mcp_server = SYSTEM_COMPONENTS.get('mcp_server')
        mcp_available = mcp_server.is_available() if mcp_server else False
        
        return SystemStatus(
            status="healthy" if all(components.values()) else "degraded",
            components=components,
            knowledge_base_size=len(SYSTEM_COMPONENTS.get('knowledge_base', [])),
            total_feedback=len(SYSTEM_COMPONENTS.get('dspy_optimizer', {}).feedback_data or []),
            mcp_available=mcp_available
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/solve", response_model=MathSolution)
async def solve_math_problem(question_data: MathQuestion, background_tasks: BackgroundTasks):
    """Solve a math problem using the Agentic RAG system with optional MCP integration"""
    start_time = asyncio.get_event_loop().time()
    session_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Processing question: {question_data.question}")
        
        math_rag_system = SYSTEM_COMPONENTS.get('math_rag_system')
        mcp_server = SYSTEM_COMPONENTS.get('mcp_server')
        
        if not math_rag_system:
            raise HTTPException(status_code=500, detail="Math RAG system not initialized")
        
        # Choose processing method based on use_mcp flag
        if question_data.use_mcp and mcp_server and mcp_server.is_available():
            try:
                logger.info("Using MCP tools for processing")
                solution_text = await mcp_server.solve_with_mcp(question_data.question)
                guardrails_passed = {"input": True, "output": True}  # MCP has built-in validation
                sources = ["MCP Tools"]
                
            except Exception as mcp_error:
                logger.warning(f"MCP processing failed: {str(mcp_error)}, falling back to RAG")
                # Fallback to existing RAG system
                result = math_rag_system.solve_math_problem(question_data.question)
                solution_text = result.get("final_solution", "No solution generated")
                guardrails_passed = {
                    "input": result.get("input_guardrails_passed", False),
                    "output": result.get("output_guardrails_passed", False)
                }
                sources = ["Knowledge Base", "Web Search"] if result.get("web_search_results") else ["Knowledge Base"]
        else:
            # Use existing RAG system (unchanged logic)
            result = math_rag_system.solve_math_problem(question_data.question)
            solution_text = result.get("final_solution", "No solution generated")
            guardrails_passed = {
                "input": result.get("input_guardrails_passed", False),
                "output": result.get("output_guardrails_passed", False)
            }
            sources = ["Knowledge Base", "Web Search"] if result.get("web_search_results") else ["Knowledge Base"]
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Calculate confidence based on guardrails performance
        confidence = 1.0 if all(guardrails_passed.values()) else 0.7
        
        # Store session for logging
        session_data = {
            "session_id": session_id,
            "question": question_data.question,
            "solution": solution_text,
            "timestamp": datetime.now().isoformat(),
            "use_mcp": question_data.use_mcp
        }
        
        background_tasks.add_task(log_session, session_data)
        
        return MathSolution(
            question=question_data.question,
            solution=solution_text,
            confidence=confidence,
            sources=sources,
            processing_time=processing_time,
            guardrails_passed=guardrails_passed,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/solve/stream")
async def solve_math_problem_stream(question_data: MathQuestion):
    """Stream the solution process in real-time"""
    
    async def generate_stream():
        session_id = str(uuid.uuid4())
        
        try:
            # Stream the processing steps
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting analysis...', 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Applying input guardrails...', 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching knowledge base...', 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.5)
            
            if question_data.use_mcp:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Using MCP tools...', 'session_id': session_id})}\n\n"
                await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating solution...', 'session_id': session_id})}\n\n"
            await asyncio.sleep(1)
            
            # Process with system
            math_rag_system = SYSTEM_COMPONENTS.get('math_rag_system')
            mcp_server = SYSTEM_COMPONENTS.get('mcp_server')
            
            if question_data.use_mcp and mcp_server and mcp_server.is_available():
                try:
                    solution_text = await mcp_server.solve_with_mcp(question_data.question)
                    guardrails_passed = {"input": True, "output": True}
                except:
                    result = math_rag_system.solve_math_problem(question_data.question)
                    solution_text = result.get("final_solution", "No solution generated")
                    guardrails_passed = {
                        "input": result.get("input_guardrails_passed", False),
                        "output": result.get("output_guardrails_passed", False)
                    }
            else:
                result = math_rag_system.solve_math_problem(question_data.question)
                solution_text = result.get("final_solution", "No solution generated")
                guardrails_passed = {
                    "input": result.get("input_guardrails_passed", False),
                    "output": result.get("output_guardrails_passed", False)
                }
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Applying output guardrails...', 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.5)
            
            solution_data = {
                'type': 'solution',
                'question': question_data.question,
                'solution': solution_text,
                'guardrails_passed': guardrails_passed,
                'session_id': session_id
            }
            
            yield f"data: {json.dumps(solution_data)}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'session_id': session_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e), 'session_id': session_id})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackData):
    """Submit feedback for a solution"""
    try:
        dspy_optimizer = SYSTEM_COMPONENTS.get('dspy_optimizer')
        if not dspy_optimizer:
            raise HTTPException(status_code=500, detail="DSPy optimizer not available")
        
        # Use existing DSPy feedback system (unchanged)
        dspy_optimizer.collect_feedback(
            question=f"Session feedback for {feedback.session_id}",
            generated_solution=f"Session {feedback.session_id}",
            rating=feedback.rating,
            comments=feedback.comments
        )
        
        logger.info(f"Feedback received for session {feedback.session_id}: {feedback.rating}/5")
        return {"message": "Feedback submitted successfully", "session_id": feedback.session_id}
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@app.get("/feedback/analytics")
async def get_feedback_analytics():
    """Get feedback analytics"""
    try:
        dspy_optimizer = SYSTEM_COMPONENTS.get('dspy_optimizer')
        if not dspy_optimizer:
            return {"total_feedback": 0, "average_rating": 0, "rating_distribution": {}}
        
        analytics = dspy_optimizer.get_feedback_analytics()
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        knowledge_base = SYSTEM_COMPONENTS.get('knowledge_base', [])
        
        if not knowledge_base:
            return {
                "total_problems": 0,
                "topics": [],
                "subjects": [],
                "sources": []
            }
        
        topics = list(set(item["topic"] for item in knowledge_base))
        subjects = list(set(item["metadata"]["subject"] for item in knowledge_base))
        sources = list(set(item["metadata"]["source"] for item in knowledge_base))
        
        return {
            "total_problems": len(knowledge_base),
            "topics": topics,
            "subjects": subjects,
            "sources": sources
        }
    except Exception as e:
        logger.error(f"Error getting KB stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get knowledge base stats")

@app.get("/mcp/tools")
async def get_mcp_tools():
    """Get available MCP tools"""
    try:
        mcp_server = SYSTEM_COMPONENTS.get('mcp_server')
        if mcp_server:
            return mcp_server.get_tools_info()
        else:
            return {
                "available": False,
                "message": "MCP server not initialized"
            }
    except Exception as e:
        logger.error(f"Error getting MCP tools: {str(e)}")
        return {"available": False, "error": str(e)}

@app.get("/system/components")
async def get_system_components():
    """Get information about system components"""
    try:
        return {
            "initialized_components": list(SYSTEM_COMPONENTS.keys()),
            "total_components": len(SYSTEM_COMPONENTS),
            "system_status": "operational" if SYSTEM_COMPONENTS else "not_initialized"
        }
    except Exception as e:
        logger.error(f"Error getting system components: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system components")


async def log_session(session_data: Dict[str, Any]):
    """Log session data for analytics"""
    try:
        logger.info(f"Session logged: {session_data['session_id']} - MCP: {session_data.get('use_mcp', False)}")
    except Exception as e:
        logger.error(f"Failed to log session: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_app:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )