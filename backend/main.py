from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = os.getenv("EXCHANGE_RATE_BASE_URL", "https://v6.exchangerate-api.com/v6")


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

class ConversionRequest(BaseModel):
    """Request model for currency conversion"""
    from_currency: str = Field(
        ..., 
        min_length=3, 
        max_length=3,
        description="Source currency code (e.g., USD, EUR, GBP)",
        example="USD"
    )
    to_currency: str = Field(
        ..., 
        min_length=3, 
        max_length=3,
        description="Target currency code (e.g., EUR, GBP, INR)",
        example="EUR"
    )
    amount: float = Field(
        ..., 
        gt=0,
        description="Amount to convert (must be positive)",
        example=100.0
    )

class ConversionResponse(BaseModel):
    """Response model for currency conversion"""
    from_currency: str
    to_currency: str
    amount: float
    converted_amount: float
    exchange_rate: float
    timestamp: str
    source: str = "ExchangeRate-API"


# ==================== ENDPOINTS ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API welcome message"""
    return {
        "message": "🌍 Currency Converter API - NCI Cloud Computing Project",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "author": "Dixshant Valecha",
        "docs": "/docs",
        "health": "/health",
        "convert": "/convert"
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return HealthResponse(
        status="healthy",
        service="currency-converter-api",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/info", response_model=APIInfo, tags=["Information"])
async def api_info():
    """Get detailed API information and available endpoints"""
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
            "POST /convert   - Currency conversion with real-time rates",
            "GET  /currencies - List all supported currencies"
        ]
    )


@app.post("/convert", response_model=ConversionResponse, tags=["Currency Conversion"])
async def convert_currency(request: ConversionRequest):
    """
    Convert currency from one type to another using real-time exchange rates
    
    - **from_currency**: 3-letter currency code (e.g., USD)
    - **to_currency**: 3-letter currency code (e.g., EUR)
    - **amount**: Amount to convert (must be positive)
    
    Returns the converted amount with the current exchange rate.
    """
    
    # Validate API key exists
    if not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="API key not configured. Please set EXCHANGE_RATE_API_KEY environment variable."
        )
    
    # Convert to uppercase for consistency
    from_curr = request.from_currency.upper()
    to_curr = request.to_currency.upper()
    
    try:
        # Call external Exchange Rate API
        url = f"{BASE_URL}/{API_KEY}/pair/{from_curr}/{to_curr}/{request.amount}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
        # Check if API call was successful
        if data.get("result") != "success":
            error_type = data.get("error-type", "unknown_error")
            
            if error_type == "unsupported-code":
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid currency code. '{from_curr}' or '{to_curr}' is not supported."
                )
            elif error_type == "invalid-key":
                raise HTTPException(
                    status_code=500, 
                    detail="Invalid API key configuration."
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Currency conversion failed: {error_type}"
                )
        
        # Extract conversion data
        conversion_rate = data.get("conversion_rate")
        conversion_result = data.get("conversion_result")
        
        return ConversionResponse(
            from_currency=from_curr,
            to_currency=to_curr,
            amount=request.amount,
            converted_amount=round(conversion_result, 2),
            exchange_rate=round(conversion_rate, 6),
            timestamp=datetime.utcnow().isoformat(),
            source="ExchangeRate-API"
        )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="External API timeout. Please try again."
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"External API unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/currencies", tags=["Currency Conversion"])
async def get_supported_currencies():
    """
    Get list of all supported currency codes
    
    Returns a list of all available 3-letter currency codes that can be used for conversion.
    """
    
    if not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="API key not configured."
        )
    
    try:
        url = f"{BASE_URL}/{API_KEY}/codes"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
        if data.get("result") != "success":
            raise HTTPException(
                status_code=500, 
                detail="Failed to fetch currency codes."
            )
        
        # Extract currency codes and names
        supported_codes = data.get("supported_codes", [])
        
        currencies = {
            "total": len(supported_codes),
            "currencies": [
                {
                    "code": code[0],
                    "name": code[1]
                }
                for code in supported_codes[:20]  # Show first 20 as example
            ],
            "note": f"Showing 20 of {len(supported_codes)} total currencies. Full list available via API."
        }
        
        return currencies
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503, 
            detail="External API unavailable."
        )


# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Runs when the API starts"""
    print("=" * 60)
    print("🚀 Currency Converter API Started!")
    print("👨‍💻 Developer: Dixshant Valecha")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("💱 Convert Currency: POST http://localhost:8000/convert")
    print("=" * 60)
    
    # Validate API key on startup
    if not API_KEY:
        print("⚠️  WARNING: EXCHANGE_RATE_API_KEY not set in .env file!")
    else:
        print(f"✅ Exchange Rate API Key: Configured ({API_KEY[:8]}...)")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the API shuts down"""
    print("👋 Currency Converter API Shutting Down...")