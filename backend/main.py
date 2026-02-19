from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
import logging
from enum import Enum

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== CHANGE 1: Updated App Metadata ====================
app = FastAPI(
    title="CryptoFiat Bridge API",  # ✏️ CHANGED: New name
    description="Seamless conversion between traditional and digital currencies",  # ✏️ CHANGED
    version="3.0.0",  # ✏️ CHANGED: Version bump
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


# ==================== CHANGE 2: NEW CRYPTO MAPPING ====================
# ✨ NEW: Comprehensive crypto symbol to CoinGecko ID mapping
CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "SOL": "solana",
    "DOT": "polkadot",
    "DOGE": "dogecoin",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "AVAX": "avalanche-2",
    "SHIB": "shiba-inu",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "TON": "the-open-network",
    "TRX": "tron",
    "DAI": "dai"
}

# ✨ NEW: Helper function to get crypto ID
def get_crypto_id(symbol: str) -> str:
    """Convert symbol to CoinGecko ID"""
    symbol_upper = symbol.upper()
    if symbol_upper in CRYPTO_ID_MAP:
        return CRYPTO_ID_MAP[symbol_upper]
    raise HTTPException(
        status_code=400,
        detail=f"Cryptocurrency '{symbol}' not supported. Use: {', '.join(CRYPTO_ID_MAP.keys())}"
    )

# ✨ NEW: Helper function to fetch crypto prices
async def fetch_crypto_prices(crypto_ids: List[str], vs_currencies: List[str]) -> Dict:
    """Fetch prices for multiple cryptos"""
    ids_str = ",".join(crypto_ids)
    currencies_str = ",".join(vs_currencies)
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies={currencies_str}&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# ✨ NEW: Helper function for detailed crypto data
async def fetch_detailed_crypto_data(crypto_id: str) -> Dict:
    """Fetch detailed data for a single cryptocurrency"""
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}?localization=false&tickers=false&community_data=false&developer_data=false"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


# ==================== DATA MODELS (Existing) ====================

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


# ==================== MULTI-CURRENCY MODELS (Existing) ====================

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


# ==================== CHANGE 3: ENHANCED CRYPTO MODELS ====================

# ✨ NEW: Enum for supported cryptos
class CryptoSymbol(str, Enum):
    """Supported cryptocurrencies"""
    BTC = "bitcoin"
    ETH = "ethereum"
    USDT = "tether"
    BNB = "binancecoin"
    XRP = "ripple"
    ADA = "cardano"
    SOL = "solana"
    DOT = "polkadot"
    DOGE = "dogecoin"
    MATIC = "matic-network"
    LINK = "chainlink"
    LTC = "litecoin"
    BCH = "bitcoin-cash"
    AVAX = "avalanche-2"
    SHIB = "shiba-inu"
    UNI = "uniswap"
    ATOM = "cosmos"
    TON = "the-open-network"
    TRX = "tron"
    DAI = "dai"

# ✨ NEW: Enum for fiat currencies
class FiatCurrency(str, Enum):
    """Supported fiat currencies"""
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    JPY = "jpy"
    AUD = "aud"
    CAD = "cad"
    CHF = "chf"
    INR = "inr"

# ✨ NEW: Model for crypto list response
class CryptoListResponse(BaseModel):
    """List of supported cryptocurrencies"""
    total_cryptos: int
    currencies: List[Dict[str, str]]
    supported_fiats: List[str]
    timestamp: str

# ✨ NEW: Crypto-to-Crypto conversion models
class CryptoToCryptoRequest(BaseModel):
    """Request for crypto-to-crypto conversion"""
    from_crypto: str = Field(..., example="BTC", description="Source cryptocurrency (e.g., BTC, ETH)")
    to_crypto: str = Field(..., example="ETH", description="Target cryptocurrency (e.g., ETH, USDT)")
    amount: float = Field(..., gt=0, example=0.5, description="Amount of source crypto")

class CryptoToCryptoResponse(BaseModel):
    """Response for crypto-to-crypto conversion"""
    from_crypto: str
    to_crypto: str
    from_amount: float
    to_amount: float
    exchange_rate: float
    usd_value: float
    timestamp: str
    source: str = "CoinGecko"

# ✨ NEW: Crypto-to-Fiat conversion models
class CryptoToFiatRequest(BaseModel):
    """Request for crypto-to-fiat conversion"""
    crypto: str = Field(..., example="BTC", description="Cryptocurrency symbol (e.g., BTC)")
    fiat: str = Field(..., example="USD", description="Fiat currency (e.g., USD, EUR)")
    amount: float = Field(..., gt=0, example=0.5, description="Amount of cryptocurrency")

class CryptoToFiatResponse(BaseModel):
    """Response for crypto-to-fiat conversion"""
    crypto: str
    fiat: str
    crypto_amount: float
    fiat_amount: float
    rate: float
    timestamp: str
    source: str = "CoinGecko"

# Existing crypto models (keeping for compatibility)
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


# ==================== CHANGE 4: UPDATED ROOT ENDPOINT ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API welcome message"""
    return {
        "message": "₿ CryptoFiat Bridge API",  # ✏️ CHANGED: New name
        "tagline": "Seamless Conversion Between Traditional & Digital Currencies",  # ✏️ CHANGED
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",  # ✏️ CHANGED
        "author": "Dixshant Valecha",
        "project": "NCI MSc Cloud Computing - Scalable Cloud Programming",
        
        # ✏️ CHANGED: Updated feature list
        "core_features": [
            "💱 Traditional currency conversion (160+ currencies)",
            "₿ Cryptocurrency prices (20+ cryptos)",
            "🔄 Crypto-to-crypto conversion (BTC→ETH, etc.)",
            "💰 Crypto-to-fiat conversion (BTC→USD, etc.)",
            "💵 Fiat-to-crypto conversion (USD→BTC, etc.)",
            "📊 Detailed crypto market data",
            "📈 Multi-currency comparison",
            "⚡ High-performance caching"
        ],
        
        # ✨ NEW: List all supported cryptos
        "supported_cryptocurrencies": [
            "BTC", "ETH", "USDT", "BNB", "XRP", "ADA", "SOL", "DOT", 
            "DOGE", "MATIC", "LINK", "LTC", "BCH", "AVAX", "SHIB", 
            "UNI", "ATOM", "TON", "TRX", "DAI"
        ],
        
        # ✨ NEW: List supported fiats
        "supported_fiats": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "INR"],
        
        # ✏️ CHANGED: Updated endpoints
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "info": "/info",
            
            "crypto_list": "GET /crypto/list",
            "crypto_prices_basic": "GET /crypto/prices",
            "crypto_prices_multi": "GET /crypto/prices/multi",
            "crypto_details": "GET /crypto/details/{symbol}",
            
            "fiat_to_crypto": "POST /convert/crypto",
            "crypto_to_fiat": "POST /crypto/to-fiat",
            "crypto_to_crypto": "POST /crypto/convert",
            
            "traditional_convert": "POST /convert",
            "multi_compare": "POST /convert/compare",
            "currencies": "GET /currencies"
        },
        
        # ✨ NEW: Use cases
        "use_cases": [
            "🏦 Investment planning - Calculate crypto portfolio value",
            "💸 Trading - Quick crypto-to-crypto conversions",
            "🌍 International - Convert between any currency",
            "📊 Market analysis - Track prices and trends",
            "🎓 Education - Learn crypto market dynamics"
        ],
        
        # ✏️ CHANGED: Updated USPs
        "unique_selling_points": [
            "✅ 20+ cryptocurrencies supported",
            "✅ Bidirectional conversions (fiat↔crypto, crypto↔crypto)",
            "✅ Real-time market data",
            "✅ Detailed crypto information",
            "✅ Production-ready API design"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return HealthResponse(
        status="healthy",
        service="cryptofiat-bridge-api",  # ✏️ CHANGED: New service name
        timestamp=datetime.utcnow().isoformat(),
        version="3.0.0"  # ✏️ CHANGED
    )


# ✏️ CHANGED: Updated info endpoint
@app.get("/info", response_model=APIInfo, tags=["Information"])
async def api_info():
    """Get detailed API information and available endpoints"""
    return APIInfo(
        name="CryptoFiat Bridge API",
        description="Bidirectional conversion between traditional and digital currencies with real-time market data",
        version="3.0.0",
        endpoints=[
            "GET  /          - Root endpoint",
            "GET  /health    - Health check",
            "GET  /info      - API information",
            "GET  /docs      - Interactive API documentation (Swagger UI)",
            "GET  /redoc     - Alternative API documentation",
            
            "POST /convert   - Single currency conversion",
            "POST /convert/compare - Multi-currency comparison",
            "GET  /currencies - List all supported fiat currencies",
            
            "GET  /crypto/list - List all supported cryptocurrencies",
            "GET  /crypto/prices - Basic crypto prices (BTC, ETH, USDT)",
            "GET  /crypto/prices/multi - Multiple crypto prices",
            "GET  /crypto/details/{symbol} - Detailed crypto information",
            
            "POST /convert/crypto - Fiat to crypto conversion",
            "POST /crypto/to-fiat - Crypto to fiat conversion",
            "POST /crypto/convert - Crypto to crypto conversion"
        ]
    )


# ==================== EXISTING ENDPOINTS (Unchanged) ====================

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
    
    for target_curr in request.target_currencies:
        target_curr = target_curr.upper()
        
        try:
            cached_rate = get_cached_rate(base_curr, target_curr)
            
            if not cached_rate:
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
    
    comparisons.sort(key=lambda x: x["converted_amount"], reverse=True)
    
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


# ==================== CHANGE 5: NEW CRYPTO ENDPOINTS ====================

# ✨ NEW: List all supported cryptocurrencies
@app.get("/crypto/list", response_model=CryptoListResponse, tags=["Cryptocurrency"])
async def list_cryptocurrencies():
    """
    Get list of all supported cryptocurrencies
    
    Returns comprehensive list of supported cryptocurrencies and fiat currencies
    """
    
    currencies = [
        {"symbol": symbol, "name": name, "id": CRYPTO_ID_MAP[symbol]}
        for symbol, name in [
            ("BTC", "Bitcoin"),
            ("ETH", "Ethereum"),
            ("USDT", "Tether"),
            ("BNB", "Binance Coin"),
            ("XRP", "Ripple"),
            ("ADA", "Cardano"),
            ("SOL", "Solana"),
            ("DOT", "Polkadot"),
            ("DOGE", "Dogecoin"),
            ("MATIC", "Polygon"),
            ("LINK", "Chainlink"),
            ("LTC", "Litecoin"),
            ("BCH", "Bitcoin Cash"),
            ("AVAX", "Avalanche"),
            ("SHIB", "Shiba Inu"),
            ("UNI", "Uniswap"),
            ("ATOM", "Cosmos"),
            ("TON", "Toncoin"),
            ("TRX", "TRON"),
            ("DAI", "Dai")
        ]
    ]
    
    return CryptoListResponse(
        total_cryptos=len(currencies),
        currencies=currencies,
        supported_fiats=["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "INR"],
        timestamp=datetime.utcnow().isoformat()
    )


# ✨ NEW: Get multiple crypto prices
@app.get("/crypto/prices/multi", tags=["Cryptocurrency"])
async def get_multiple_crypto_prices(
    symbols: str = "BTC,ETH,USDT,ADA,SOL",
    vs_currency: str = "usd"
):
    """
    Get current prices for multiple cryptocurrencies
    
    - **symbols**: Comma-separated crypto symbols (e.g., "BTC,ETH,USDT")
    - **vs_currency**: Fiat currency (usd, eur, gbp, etc.)
    
    Example: /crypto/prices/multi?symbols=BTC,ETH,SOL&vs_currency=usd
    """
    
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        crypto_ids = [get_crypto_id(symbol) for symbol in symbol_list]
        
        data = await fetch_crypto_prices(crypto_ids, [vs_currency.lower()])
        
        result = {}
        for symbol, crypto_id in zip(symbol_list, crypto_ids):
            if crypto_id in data:
                crypto_data = data[crypto_id]
                result[symbol] = {
                    "price": crypto_data.get(vs_currency.lower()),
                    "market_cap": crypto_data.get(f"{vs_currency.lower()}_market_cap"),
                    "24h_volume": crypto_data.get(f"{vs_currency.lower()}_24h_vol"),
                    "24h_change": crypto_data.get(f"{vs_currency.lower()}_24h_change")
                }
        
        return {
            "data": result,
            "vs_currency": vs_currency.upper(),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "CoinGecko"
        }
    
    except Exception as e:
        logger.error(f"Error fetching multiple crypto prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✨ NEW: Crypto-to-Crypto conversion
@app.post("/crypto/convert", response_model=CryptoToCryptoResponse, tags=["Cryptocurrency"])
async def convert_crypto_to_crypto(request: CryptoToCryptoRequest):
    """
    Convert one cryptocurrency to another
    
    **Example:** How much ETH can I get for 0.5 BTC?
    
    - **from_crypto**: Source cryptocurrency (BTC, ETH, etc.)
    - **to_crypto**: Target cryptocurrency (ETH, USDT, etc.)
    - **amount**: Amount of source crypto
    
    Returns equivalent amount in target cryptocurrency
    """
    
    try:
        from_id = get_crypto_id(request.from_crypto)
        to_id = get_crypto_id(request.to_crypto)
        
        crypto_ids = [from_id, to_id]
        data = await fetch_crypto_prices(crypto_ids, ["usd"])
        
        from_price_usd = data[from_id]["usd"]
        to_price_usd = data[to_id]["usd"]
        
        usd_value = request.amount * from_price_usd
        to_amount = usd_value / to_price_usd
        exchange_rate = from_price_usd / to_price_usd
        
        logger.info(f"Crypto conversion: {request.amount} {request.from_crypto} = {to_amount} {request.to_crypto}")
        
        return CryptoToCryptoResponse(
            from_crypto=request.from_crypto.upper(),
            to_crypto=request.to_crypto.upper(),
            from_amount=request.amount,
            to_amount=round(to_amount, 8),
            exchange_rate=round(exchange_rate, 8),
            usd_value=round(usd_value, 2),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Crypto-to-crypto conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✨ NEW: Crypto-to-Fiat conversion
@app.post("/crypto/to-fiat", response_model=CryptoToFiatResponse, tags=["Cryptocurrency"])
async def convert_crypto_to_fiat(request: CryptoToFiatRequest):
    """
    Convert cryptocurrency to fiat currency
    
    **Example:** I have 0.5 BTC, how much USD is that?
    
    - **crypto**: Cryptocurrency symbol (BTC, ETH, etc.)
    - **fiat**: Fiat currency (USD, EUR, GBP, etc.)
    - **amount**: Amount of cryptocurrency
    
    Returns equivalent amount in fiat currency
    """
    
    try:
        crypto_id = get_crypto_id(request.crypto)
        fiat_lower = request.fiat.lower()
        
        if fiat_lower not in ["usd", "eur", "gbp", "jpy", "aud", "cad", "chf", "inr"]:
            raise HTTPException(
                status_code=400,
                detail=f"Fiat currency '{request.fiat}' not supported"
            )
        
        data = await fetch_crypto_prices([crypto_id], [fiat_lower])
        
        crypto_price = data[crypto_id][fiat_lower]
        fiat_amount = request.amount * crypto_price
        
        logger.info(f"Crypto to fiat: {request.amount} {request.crypto} = {fiat_amount} {request.fiat}")
        
        return CryptoToFiatResponse(
            crypto=request.crypto.upper(),
            fiat=request.fiat.upper(),
            crypto_amount=request.amount,
            fiat_amount=round(fiat_amount, 2),
            rate=round(crypto_price, 2),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Crypto to fiat conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ✨ NEW: Detailed crypto information
@app.get("/crypto/details/{symbol}", tags=["Cryptocurrency"])
async def get_crypto_details(symbol: str):
    """
    Get detailed information about a cryptocurrency
    
    **Example:** /crypto/details/BTC
    
    Returns comprehensive data including:
    - Current price, market cap, volume
    - 24h price change
    - All-time high/low
    - Circulating/total/max supply
    - Market rank
    """
    
    try:
        crypto_id = get_crypto_id(symbol)
        data = await fetch_detailed_crypto_data(crypto_id)
        
        market_data = data.get("market_data", {})
        
        return {
            "symbol": symbol.upper(),
            "name": data.get("name"),
            "description": data.get("description", {}).get("en", "")[:200] + "..." if data.get("description") else None,
            "current_price": {
                "usd": market_data.get("current_price", {}).get("usd"),
                "eur": market_data.get("current_price", {}).get("eur"),
                "gbp": market_data.get("current_price", {}).get("gbp")
            },
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "market_cap_rank": data.get("market_cap_rank"),
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "price_change_24h": market_data.get("price_change_24h"),
            "price_change_percentage_24h": market_data.get("price_change_percentage_24h"),
            "price_change_percentage_7d": market_data.get("price_change_percentage_7d"),
            "price_change_percentage_30d": market_data.get("price_change_percentage_30d"),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "max_supply": market_data.get("max_supply"),
            "ath": {
                "usd": market_data.get("ath", {}).get("usd"),
                "date": market_data.get("ath_date", {}).get("usd")
            },
            "atl": {
                "usd": market_data.get("atl", {}).get("usd"),
                "date": market_data.get("atl_date", {}).get("usd")
            },
            "last_updated": data.get("last_updated"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching crypto details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EXISTING CRYPTO ENDPOINTS ====================

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
        
        crypto_price = data[crypto_id][currency_lower]
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


# ==================== CHANGE 6: UPDATED STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Runs when the API starts"""
    print("=" * 60)
    print("₿ CryptoFiat Bridge API Started!")  # ✏️ CHANGED
    print("👨‍💻 Developer: Dixshant Valecha")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("💱 Fiat Convert: POST http://localhost:8000/convert")
    print("₿ Crypto Prices: GET http://localhost:8000/crypto/prices")  # ✏️ CHANGED
    print("🔄 Crypto Convert: POST http://localhost:8000/crypto/convert")  # ✨ NEW
    print("=" * 60)
    
    if not API_KEY:
        print("⚠️  WARNING: EXCHANGE_RATE_API_KEY not set in .env file!")
    else:
        print(f"✅ Exchange Rate API Key: Configured ({API_KEY[:8]}...)")
    
    print(f"✅ Supported Cryptos: {len(CRYPTO_ID_MAP)} currencies")  # ✨ NEW


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the API shuts down"""
    print("👋 CryptoFiat Bridge API Shutting Down...")  # ✏️ CHANGED