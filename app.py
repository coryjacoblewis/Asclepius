"""
Asclepius API Interface
-----------------------
To Run: uvicorn app:app --reload
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import HealthAIGateway

app = FastAPI(title="Asclepius: Clinical Guardrails API")

# Global variable to hold the gateway instance
gateway = None

@app.on_event("startup")
async def startup_event():
    """
    Initialize the gateway when the server starts.
    """
    global gateway
    try:
        gateway = HealthAIGateway()
    except Exception as e:
        print(f"Critical Startup Error: {e}")

# Define the expected JSON input format
class EvaluationRequest(BaseModel):
    query: str
    context: str
    response: str

@app.post("/evaluate")
async def evaluate_health_ai(request: EvaluationRequest):
    """
    Ingestion Endpoint: Receives a transaction and returns a safety score.
    """
    if not gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")
    
    # Pass data to the Orchestrator
    result = gateway.process_transaction(
        request.query, 
        request.context, 
        request.response
    )
    
    return result

@app.get("/health")
async def health_check():
    return {"status": "operational", "version": "1.0.0"}