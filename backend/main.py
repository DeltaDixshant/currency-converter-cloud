from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Travel Currency & Cost Planner API",
    description="A scalable currency conversion microservice built with FastAPI for cloud deployment",
    version="2.0.0",
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

# Simple in-memory cache (in production, use Redis)
cache: Dict[str, Dict] = {}
CACHE_DURATION = timedelta(minutes=5)

def get_cached_rate(from_curr: str, to_curr: str) -> Optional[float]:
    """Check if we have a cached exchange rate"""
    cache_key = f"{from_curr}_{to_curr}"
    
    if cache_key in cache:
        cached_data = cache[cache_key]
        if datetime.utcnow() < cached_data["expires_at"]:
            logger.info(f"Cache HIT for {cache_key}")
            return cached_data["rate"]
        else:
            logger.info(f"Cache EXPIRED for {cache_key}")
            del cache[cache_key]
    
    logger.info(f"Cache MISS for {cache_key}")
    return None

def set_cached_rate(from_curr: str, to_curr: str, rate: float):
    """Cache an exchange rate"""
    cache_key = f"{from_curr}_{to_curr}"
    cache[cache_key] = {
        "rate": rate,
        "expires_at": datetime.utcnow() + CACHE_DURATION
    }
    logger.info(f"Cached rate for {cache_key}: {rate}")


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
    endpoints: List[str]

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


# ==================== MULTI-CURRENCY MODELS ====================

class MultiConversionRequest(BaseModel):
    """Request model for multi-currency comparison"""
    base_currency: str = Field(
        ..., 
        min_length=3, 
        max_length=3,
        description="Base currency code",
        example="USD"
    )
    amount: float = Field(
        ..., 
        gt=0,
        description="Amount to convert",
        example=1000
    )
    target_currencies: List[str] = Field(
        ...,
        description="List of currencies to compare",
        example=["EUR", "GBP", "INR", "JPY", "AUD"]
    )

class CurrencyComparison(BaseModel):
    """Individual currency comparison result"""
    currency: str
    converted_amount: float
    exchange_rate: float
    rank: int

class MultiConversionResponse(BaseModel):
    """Response model for multi-currency comparison"""
    base_currency: str
    base_amount: float
    comparisons: List[CurrencyComparison]
    best_value: str
    total_currencies_compared: int
    timestamp: str

    # ==================== CRYPTOCURRENCY MODELS ====================

class CryptoPrices(BaseModel):
    """Current cryptocurrency prices"""
    symbol: str
    usd: float
    eur: float
    gbp: float

class CryptoResponse(BaseModel):
    """Response with multiple crypto prices"""
    bitcoin: CryptoPrices
    ethereum: CryptoPrices
    tether: CryptoPrices
    timestamp: str
    source: str = "CoinGecko"

class CryptoConversionResponse(BaseModel):
    """Crypto conversion result"""
    from_currency: str
    to_crypto: str
    fiat_amount: float
    crypto_amount: float
    rate: float
    timestamp: str
    source: str = "CoinGecko"


# ==================== ENDPOINTS ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API welcome message"""
    return {
        "message": "🌍 Smart Travel Currency & Cost Planner API",
        "tagline": "Beyond Simple Currency Conversion!",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "author": "Dixshant Valecha",
        "project": "NCI MSc Cloud Computing - Scalable Cloud Programming",
        
        "unique_features": [
            "💱 Real-time currency conversion (160+ currencies)",
            "🔄 Multi-currency comparison (find best rates)",
            "₿ Cryptocurrency support (BTC, ETH, USDT)",
            "📊 Caching for performance",
            "🌤️ Integrated weather data (coming soon)",
            "💰 Cost of living comparisons (coming soon)"
        ],
        
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "info": "/info",
            "single_conversion": "POST /convert",
            "multi_currency_compare": "POST /convert/compare",
            "crypto_prices": "GET /crypto/prices",
            "crypto_conversion": "POST /convert/crypto",
            "supported_currencies": "GET /currencies"
        },
        
        "differentiators": [
            "✅ Multi-currency comparison (unique!)",
            "✅ Travel planning focus (unique!)",
            "✅ Microservices integration ready"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return HealthResponse(
        status="healthy",
        service="currency-converter-api",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0"
    )


@app.get("/info", response_model=APIInfo, tags=["Information"])
async def api_info():
    """Get detailed API information and available endpoints"""
    return APIInfo(
        name="Smart Travel Currency & Cost Planner API",
        description="Microservice-based currency conversion with real-time exchange rates and travel planning features",
        version="2.0.0",
        endpoints=[
            "GET  /          - Root endpoint",
            "GET  /health    - Health check",
            "GET  /info      - API information",
            "GET  /docs      - Interactive API documentation (Swagger UI)",
            "GET  /redoc     - Alternative API documentation",
            "POST /convert   - Single currency conversion",
            "POST /convert/compare - Multi-currency comparison",
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
    
    if not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="API key not configured. Please set EXCHANGE_RATE_API_KEY environment variable."
        )
    
    from_curr = request.from_currency.upper()
    to_curr = request.to_currency.upper()
    
    logger.info(f"Conversion request: {from_curr} → {to_curr}, Amount: {request.amount}")
    
    try:
        # Check cache first
        cached_rate = get_cached_rate(from_curr, to_curr)
        
        if cached_rate:
            converted_amount = request.amount * cached_rate
            
            return ConversionResponse(
                from_currency=from_curr,
                to_currency=to_curr,
                amount=request.amount,
                converted_amount=round(converted_amount, 2),
                exchange_rate=round(cached_rate, 6),
                timestamp=datetime.utcnow().isoformat(),
                source="ExchangeRate-API (cached)"
            )
        
        # Cache miss - call external API
        url = f"{BASE_URL}/{API_KEY}/pair/{from_curr}/{to_curr}/{request.amount}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
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
        
        conversion_rate = data.get("conversion_rate")
        conversion_result = data.get("conversion_result")
        
        # Cache the rate
        set_cached_rate(from_curr, to_curr, conversion_rate)
        
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
        logger.error(f"Conversion error: {e}")
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
        
        supported_codes = data.get("supported_codes", [])
        
        currencies = {
            "total": len(supported_codes),
            "currencies": [
                {
                    "code": code[0],
                    "name": code[1]
                }
                for code in supported_codes[:20]
            ],
            "note": f"Showing 20 of {len(supported_codes)} total currencies. Full list available via API."
        }
        
        return currencies
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503, 
            detail="External API unavailable."
        )


@app.post("/convert/compare", response_model=MultiConversionResponse, tags=["Currency Conversion"])
async def compare_currencies(request: MultiConversionRequest):
    """
    Compare conversion rates across multiple currencies
    
    **Use Case:** Find which currency gives you the best value for your money
    
    Example: Convert $1000 to EUR, GBP, INR, JPY, AUD and see which gives most value
    
    - **base_currency**: Your starting currency (e.g., USD)
    - **amount**: Amount you want to convert
    - **target_currencies**: List of currencies to compare
    
    Returns ranked list from best to worst exchange rate
    """
    
    if not API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="API key not configured"
        )
    
    base_curr = request.base_currency.upper()
    comparisons = []
    
    logger.info(f"Multi-currency comparison: {base_curr} {request.amount} → {request.target_currencies}")
    
    # Convert to each target currency
    for target_curr in request.target_currencies:
        target_curr = target_curr.upper()
        
        try:
            # Check cache first
            cached_rate = get_cached_rate(base_curr, target_curr)
            
            if not cached_rate:
                # Fetch from API
                url = f"{BASE_URL}/{API_KEY}/pair/{base_curr}/{target_curr}"
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get("result") == "success":
                        cached_rate = data.get("conversion_rate")
                        set_cached_rate(base_curr, target_curr, cached_rate)
                        logger.info(f"Fetched rate for {base_curr}/{target_curr}: {cached_rate}")
            
            if cached_rate:
                converted = request.amount * cached_rate
                comparisons.append({
                    "currency": target_curr,
                    "converted_amount": round(converted, 2),
                    "exchange_rate": round(cached_rate, 6)
                })
        
        except Exception as e:
            logger.error(f"Error converting {base_curr} to {target_curr}: {e}")
            continue
    
    if not comparisons:
        raise HTTPException(
            status_code=400,
            detail="Could not convert to any of the target currencies"
        )
    
    # Sort by converted amount (descending = best value first)
    comparisons.sort(key=lambda x: x["converted_amount"], reverse=True)
    
    # Add ranking
    ranked_comparisons = []
    for idx, comp in enumerate(comparisons, 1):
        ranked_comparisons.append(
            CurrencyComparison(
                currency=comp["currency"],
                converted_amount=comp["converted_amount"],
                exchange_rate=comp["exchange_rate"],
                rank=idx
            )
        )
    
    # Determine best value
    best = ranked_comparisons[0] if ranked_comparisons else None
    best_value = f"{best.currency} ({best.converted_amount})" if best else "N/A"
    
    logger.info(f"Comparison complete. Best value: {best_value}")
    
    return MultiConversionResponse(
        base_currency=base_curr,
        base_amount=request.amount,
        comparisons=ranked_comparisons,
        best_value=best_value,
        total_currencies_compared=len(ranked_comparisons),
        timestamp=datetime.utcnow().isoformat()
    )
# ==================== CRYPTOCURRENCY ENDPOINTS ====================

@app.get("/crypto/prices", response_model=CryptoResponse, tags=["Cryptocurrency"])
async def get_crypto_prices():
    """
    Get current cryptocurrency prices in USD, EUR, and GBP
    
    **Supported Cryptocurrencies:**
    - Bitcoin (BTC)
    - Ethereum (ETH)
    - Tether (USDT)
    
    **No API key required** - uses CoinGecko free tier
    
    Returns real-time prices across major fiat currencies
    """
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd,eur,gbp"
        
        logger.info("Fetching crypto prices from CoinGecko")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
        logger.info(f"Crypto prices fetched: BTC=${data['bitcoin']['usd']}")
        
        return CryptoResponse(
            bitcoin=CryptoPrices(
                symbol="BTC",
                usd=data["bitcoin"]["usd"],
                eur=data["bitcoin"]["eur"],
                gbp=data["bitcoin"]["gbp"]
            ),
            ethereum=CryptoPrices(
                symbol="ETH",
                usd=data["ethereum"]["usd"],
                eur=data["ethereum"]["eur"],
                gbp=data["ethereum"]["gbp"]
            ),
            tether=CryptoPrices(
                symbol="USDT",
                usd=data["tether"]["usd"],
                eur=data["tether"]["eur"],
                gbp=data["tether"]["gbp"]
            ),
            timestamp=datetime.utcnow().isoformat(),
            source="CoinGecko"
        )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="CoinGecko API timeout. Please try again."
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"CoinGecko API unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Crypto price fetch error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch crypto prices: {str(e)}"
        )


@app.post("/convert/crypto", response_model=CryptoConversionResponse, tags=["Cryptocurrency"])
async def convert_to_crypto(
    from_currency: str = "USD",
    to_crypto: str = "BTC",
    amount: float = 1000
):
    """
    Convert fiat currency to cryptocurrency
    
    **Supported Fiat Currencies:** USD, EUR, GBP
    
    **Supported Cryptocurrencies:**
    - BTC (Bitcoin)
    - ETH (Ethereum)
    - USDT (Tether)
    
    **Example:** How much Bitcoin can I buy with $1000?
    
    - **from_currency**: Fiat currency (USD, EUR, GBP)
    - **to_crypto**: Cryptocurrency (BTC, ETH, USDT)
    - **amount**: Amount of fiat currency to convert
    
    Returns the equivalent cryptocurrency amount at current market rates
    """
    
    # Map crypto symbols to CoinGecko IDs
    crypto_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether"
    }
    
    to_crypto_upper = to_crypto.upper()
    from_currency_upper = from_currency.upper()
    
    if to_crypto_upper not in crypto_map:
        raise HTTPException(
            status_code=400,
            detail=f"Cryptocurrency '{to_crypto}' not supported. Use: BTC, ETH, or USDT"
        )
    
    if from_currency_upper not in ["USD", "EUR", "GBP"]:
        raise HTTPException(
            status_code=400,
            detail=f"Fiat currency '{from_currency}' not supported. Use: USD, EUR, or GBP"
        )
    
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )
    
    crypto_id = crypto_map[to_crypto_upper]
    currency_lower = from_currency_upper.lower()
    
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency_lower}"
        
        logger.info(f"Converting {amount} {from_currency_upper} to {to_crypto_upper}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        
        # Price of 1 crypto in fiat currency
        crypto_price = data[crypto_id][currency_lower]
        
        # How much crypto can you buy
        crypto_amount = amount / crypto_price
        
        logger.info(f"Conversion: {amount} {from_currency_upper} = {crypto_amount:.8f} {to_crypto_upper}")
        
        return CryptoConversionResponse(
            from_currency=from_currency_upper,
            to_crypto=to_crypto_upper,
            fiat_amount=amount,
            crypto_amount=round(crypto_amount, 8),
            rate=round(crypto_price, 2),
            timestamp=datetime.utcnow().isoformat(),
            source="CoinGecko"
        )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="CoinGecko API timeout. Please try again."
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"CoinGecko API unavailable: {str(e)}"
        )
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid response from CoinGecko: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Crypto conversion error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Crypto conversion failed: {str(e)}"
        )



# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Runs when the API starts"""
    print("=" * 60)
    print("🚀 Smart Travel Currency & Cost Planner API Started!")
    print("👨‍💻 Developer: Dixshant Valecha")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("💱 Convert Currency: POST http://localhost:8000/convert")
    print("🔄 Multi-Compare: POST http://localhost:8000/convert/compare")
    print("=" * 60)
    
    if not API_KEY:
        print("⚠️  WARNING: EXCHANGE_RATE_API_KEY not set in .env file!")
    else:
        print(f"✅ Exchange Rate API Key: Configured ({API_KEY[:8]}...)")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the API shuts down"""
    print("👋 Currency Converter API Shutting Down...")