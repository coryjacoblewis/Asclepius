"""
Asclepius API Interface
-----------------------
To Run: uvicorn app:app --reload
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from main import HealthAIGateway
from dotenv import load_dotenv
import logging

# Load env vars immediately
load_dotenv()

# Configure logging centrally
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AsclepiusAPI")

gateway = None

# MODERN PATTERN: Lifespan Context Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    global gateway
    try:
        logger.info("Booting Asclepius Gateway...")
        gateway = HealthAIGateway()
        yield
    except Exception as e:
        logger.critical(f"Critical Startup Error: {e}")
        # In production, you might want to stop the app here
        yield
    finally:
        # Shutdown logic (cleanup)
        logger.info("Shutting down Gateway...")

app = FastAPI(title="Asclepius: Clinical Guardrails API", lifespan=lifespan)

class EvaluationRequest(BaseModel):
    # SECURITY: Add limits to prevent DOS attacks
    query: str = Field(..., max_length=1000)
    context: str = Field(..., max_length=10000)
    response: str = Field(..., max_length=5000)

@app.post("/evaluate")
async def evaluate_health_ai(request: EvaluationRequest):
    if not gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")
    
    return gateway.process_transaction(
        request.query, 
        request.context, 
        request.response
    )

@app.get("/health")
async def health_check():
    return {"status": "operational", "version": "1.0.0"}