from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import httpx

app = FastAPI(
    title="Currency Converter API",
    description="A scalable currency conversion microservice built with FastAPI for cloud deployment",
    version="1.0.0",
    contact={
        "name": "Dixshant Valecha",
        "url": "https://github.com/DeltaDixshant/currency-converter-cloud"
    },
    license_info={
        "name": "MIT"
    }
)

# CORS middleware (needed for React frontend later)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== DATA MODELS ====================

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    version: str

class APIInfo(BaseModel):
    name: str
    description: str
    version: str
    endpoints: list[str]


# ==================== ENDPOINTS ====================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "🌍 Currency Converter API - NCI Cloud Computing Project",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "author": "Dixshant Valecha",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    return HealthResponse(
        status="healthy",
        service="currency-converter-api",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/info", response_model=APIInfo, tags=["Information"])
async def api_info():
    """
    Get detailed API information and available endpoints
    """
    return APIInfo(
        name="Currency Converter API",
        description="Microservice-based currency conversion with real-time exchange rates",
        version="1.0.0",
        endpoints=[
            "GET  /          - Root endpoint",
            "GET  /health    - Health check",
            "GET  /info      - API information",
            "GET  /docs      - Interactive API documentation (Swagger UI)",
            "GET  /redoc     - Alternative API documentation",
            "POST /convert   - Currency conversion (Week 2)"
        ]
    )


# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """
    Runs when the API starts
    """
    print("=" * 50)
    print("🚀 Currency Converter API Started!")
    print("👨‍💻 Developer: Dixshant Valecha")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the API shuts down
    """
    print("👋 Currency Converter API Shutting Down...")