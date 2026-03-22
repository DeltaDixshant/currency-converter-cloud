from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
import logging
from enum import Enum

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CryptoFiat Bridge API",
    description="Seamless conversion between traditional and digital currencies",
    version="3.0.0",
    contact={
        "name": "Dixshant Valecha",
        "url": "https://github.com/DeltaDixshant/currency-converter-cloud"
    },
    license_info={"name": "MIT"}
)

from fastapi.middleware.cors import CORSMiddleware

# ✅ FIX 1: allow_credentials must be False when allow_origins=["*"]
# Having both True causes duplicate Access-Control-Allow-Origin headers → CORS error in browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # ← FIXED (was True)
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
BASE_URL = os.getenv("EXCHANGE_RATE_BASE_URL", "https://v6.exchangerate-api.com/v6")

cache: Dict[str, Dict] = {}
CACHE_DURATION = timedelta(minutes=5)


def get_cached_rate(from_curr: str, to_curr: str) -> Optional[float]:
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
    cache_key = f"{from_curr}_{to_curr}"
    cache[cache_key] = {
        "rate": rate,
        "expires_at": datetime.utcnow() + CACHE_DURATION
    }
    logger.info(f"Cached rate for {cache_key}: {rate}")


# ==================== CRYPTO MAPPINGS ====================

CRYPTO_ID_MAP = {
    "BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether",
    "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
    "SOL": "solana", "DOT": "polkadot", "DOGE": "dogecoin",
    "MATIC": "matic-network", "LINK": "chainlink", "LTC": "litecoin",
    "BCH": "bitcoin-cash", "AVAX": "avalanche-2", "SHIB": "shiba-inu",
    "UNI": "uniswap", "ATOM": "cosmos", "TON": "the-open-network",
    "TRX": "tron", "DAI": "dai"
}

# ✅ FIX 2: CoinCap fallback IDs (used when CoinGecko returns 429)
COINCAP_ID_MAP = {
    "BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether",
    "BNB": "binance-coin", "XRP": "xrp", "ADA": "cardano",
    "SOL": "solana", "DOT": "polkadot", "DOGE": "dogecoin",
    "MATIC": "polygon", "LINK": "chainlink", "LTC": "litecoin",
    "BCH": "bitcoin-cash", "AVAX": "avalanche", "SHIB": "shiba-inu",
    "UNI": "uniswap", "ATOM": "cosmos", "TON": "the-open-network",
    "TRX": "tron", "DAI": "multi-collateral-dai"
}

CRYPTO_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "USDT": "Tether",
    "BNB": "Binance Coin", "XRP": "Ripple", "ADA": "Cardano",
    "SOL": "Solana", "DOT": "Polkadot", "DOGE": "Dogecoin",
    "MATIC": "Polygon", "LINK": "Chainlink", "LTC": "Litecoin",
    "BCH": "Bitcoin Cash", "AVAX": "Avalanche", "SHIB": "Shiba Inu",
    "UNI": "Uniswap", "ATOM": "Cosmos", "TON": "Toncoin",
    "TRX": "TRON", "DAI": "Dai"
}


def get_crypto_id(symbol: str) -> str:
    symbol_upper = symbol.upper()
    if symbol_upper in CRYPTO_ID_MAP:
        return CRYPTO_ID_MAP[symbol_upper]
    raise HTTPException(
        status_code=400,
        detail=f"Cryptocurrency '{symbol}' not supported. Supported: {', '.join(CRYPTO_ID_MAP.keys())}"
    )


# ✅ FIX 3: fetch_crypto_prices now falls back to CoinCap on 429
async def fetch_crypto_price_usd(symbol: str) -> float:
    """
    Get USD price for a single crypto symbol.
    Tries CoinGecko first; falls back to CoinCap if rate-limited (429).
    """
    symbol = symbol.upper()

    # ── Try CoinGecko ──────────────────────────────────────────────────
    coingecko_id = CRYPTO_ID_MAP.get(symbol)
    if coingecko_id:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": coingecko_id, "vs_currencies": "usd"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if coingecko_id in data:
                        price = float(data[coingecko_id]["usd"])
                        logger.info(f"CoinGecko ✓ {symbol}: ${price}")
                        return price
                elif resp.status_code == 429:
                    logger.warning(f"CoinGecko rate-limited for {symbol}, switching to CoinCap")
                else:
                    logger.warning(f"CoinGecko returned {resp.status_code} for {symbol}")
        except Exception as e:
            logger.warning(f"CoinGecko failed for {symbol}: {e}")

    # ── Fallback: CoinCap ──────────────────────────────────────────────
    coincap_id = COINCAP_ID_MAP.get(symbol)
    if coincap_id:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"https://api.coincap.io/v2/assets/{coincap_id}")
                if resp.status_code == 200:
                    data = resp.json()
                    price = float(data["data"]["priceUsd"])
                    logger.info(f"CoinCap fallback ✓ {symbol}: ${price}")
                    return price
        except Exception as e:
            logger.warning(f"CoinCap fallback failed for {symbol}: {e}")

    raise HTTPException(
        status_code=503,
        detail=f"Price unavailable for {symbol}. Both CoinGecko and CoinCap failed. Try again in a moment."
    )


async def fetch_crypto_prices(crypto_ids: List[str], vs_currencies: List[str]) -> Dict:
    """
    Fetch prices for multiple cryptos. Falls back to CoinCap per-symbol on 429.
    Returns dict keyed by CoinGecko ID: { "bitcoin": { "usd": 83000, ... }, ... }
    """
    ids_str = ",".join(crypto_ids)
    currencies_str = ",".join(vs_currencies)

    # ── Try CoinGecko bulk fetch ───────────────────────────────────────
    try:
        url = (
            f"https://api.coingecko.com/api/v3/simple/price"
            f"?ids={ids_str}&vs_currencies={currencies_str}"
            f"&include_24hr_change=true&include_market_cap=true&include_24hr_vol=true"
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                logger.info(f"CoinGecko bulk fetch ✓ for: {ids_str}")
                return response.json()
            elif response.status_code == 429:
                logger.warning("CoinGecko bulk rate-limited, falling back to CoinCap per symbol")
            else:
                logger.warning(f"CoinGecko bulk returned {response.status_code}")
    except Exception as e:
        logger.warning(f"CoinGecko bulk fetch failed: {e}")

    # ── Fallback: CoinCap per symbol ───────────────────────────────────
    # Reverse-map CoinGecko IDs back to symbols so we can look up CoinCap IDs
    reverse_map = {v: k for k, v in CRYPTO_ID_MAP.items()}
    result = {}

    for cg_id in crypto_ids:
        symbol = reverse_map.get(cg_id)
        if not symbol:
            continue
        coincap_id = COINCAP_ID_MAP.get(symbol)
        if not coincap_id:
            continue
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"https://api.coincap.io/v2/assets/{coincap_id}")
                if resp.status_code == 200:
                    data = resp.json()["data"]
                    usd_price = float(data["priceUsd"])
                    result[cg_id] = {
                        "usd": usd_price,
                        "usd_24h_change": float(data.get("changePercent24Hr") or 0),
                        "usd_market_cap": float(data.get("marketCapUsd") or 0),
                        "usd_24h_vol": float(data.get("volumeUsd24Hr") or 0),
                    }
                    logger.info(f"CoinCap fallback ✓ {symbol}: ${usd_price}")
        except Exception as e:
            logger.warning(f"CoinCap fallback failed for {symbol}: {e}")

    if not result:
        raise HTTPException(status_code=503, detail="Both CoinGecko and CoinCap are unavailable. Try again shortly.")

    return result


async def fetch_detailed_crypto_data(crypto_id: str) -> Dict:
    """Fetch detailed data for a single cryptocurrency from CoinGecko."""
    url = (
        f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
        f"?localization=false&tickers=false&community_data=false&developer_data=false"
    )
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        if response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="CoinGecko rate limit reached. Please wait 60 seconds and try again."
            )
        response.raise_for_status()
        return response.json()


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
    from_currency: str = Field(..., min_length=3, max_length=3, example="USD")
    to_currency: str = Field(..., min_length=3, max_length=3, example="EUR")
    amount: float = Field(..., gt=0, example=100.0)

class ConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    amount: float
    converted_amount: float
    exchange_rate: float
    timestamp: str
    source: str = "ExchangeRate-API"

class MultiConversionRequest(BaseModel):
    base_currency: str = Field(..., min_length=3, max_length=3, example="USD")
    amount: float = Field(..., gt=0, example=1000)
    target_currencies: List[str] = Field(..., example=["EUR", "GBP", "INR", "JPY", "AUD"])

class CurrencyComparison(BaseModel):
    currency: str
    converted_amount: float
    exchange_rate: float
    rank: int

class MultiConversionResponse(BaseModel):
    base_currency: str
    base_amount: float
    comparisons: List[CurrencyComparison]
    best_value: str
    total_currencies_compared: int
    timestamp: str

class CryptoListResponse(BaseModel):
    total_cryptos: int
    currencies: List[Dict[str, str]]
    supported_fiats: List[str]
    timestamp: str

class CryptoToCryptoRequest(BaseModel):
    from_crypto: str = Field(..., example="BTC")
    to_crypto: str = Field(..., example="ETH")
    amount: float = Field(..., gt=0, example=0.5)

class CryptoToCryptoResponse(BaseModel):
    from_crypto: str
    to_crypto: str
    from_amount: float
    to_amount: float
    exchange_rate: float
    usd_value: float
    timestamp: str
    source: str = "CoinGecko/CoinCap"

class CryptoToFiatRequest(BaseModel):
    from_crypto: str = Field(..., example="BTC")
    to_currency: str = Field(..., example="USD")
    crypto_amount: float = Field(..., gt=0, example=0.5)

class CryptoToFiatResponse(BaseModel):
    from_crypto: str
    to_currency: str
    crypto_amount: float
    fiat_amount: float
    rate: float
    timestamp: str
    source: str = "CoinGecko/CoinCap"

class FiatToCryptoRequest(BaseModel):
    from_currency: str = Field(..., example="USD")
    to_crypto: str = Field(..., example="BTC")
    fiat_amount: float = Field(..., gt=0, example=1000)

class FiatToCryptoResponse(BaseModel):
    from_currency: str
    to_crypto: str
    fiat_amount: float
    crypto_amount: float
    rate: float
    timestamp: str
    source: str = "CoinGecko/CoinCap"

class CryptoPrices(BaseModel):
    symbol: str
    usd: float
    eur: float
    gbp: float

class CryptoResponse(BaseModel):
    bitcoin: CryptoPrices
    ethereum: CryptoPrices
    tether: CryptoPrices
    timestamp: str
    source: str = "CoinGecko"

class CryptoConversionResponse(BaseModel):
    from_currency: str
    to_crypto: str
    fiat_amount: float
    crypto_amount: float
    rate: float
    timestamp: str
    source: str = "CoinGecko/CoinCap"


# ==================== MAZZ PARTNER API PROXY ====================

MAZZ_API_BASE = "https://itafimfx0h.execute-api.us-east-1.amazonaws.com"

class PhoneFormatRequest(BaseModel):
    number: str = Field(..., example="+353833456789")
    locale: Optional[str] = Field(None, example="IE")

class DateFormatRequest(BaseModel):
    date: str = Field(..., example="2026-03-22")
    locale: Optional[str] = Field(None, example="IE")
    format: Optional[str] = Field(None, example="DD/MM/YYYY")

@app.post("/proxy/format/phone", tags=["Partner - Locale Formatter"])
async def proxy_format_phone(request: PhoneFormatRequest):
    """Proxy → Mazz Locale Formatter: Format a phone number (national, international, E.164)"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(
                f"{MAZZ_API_BASE}/format/phone",
                json=request.dict(exclude_none=True),
                headers={"Content-Type": "application/json"},
            )
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Mazz phone proxy error: {e}")
            raise HTTPException(status_code=502, detail=f"Partner API unreachable: {str(e)}")

@app.post("/proxy/format/date", tags=["Partner - Locale Formatter"])
async def proxy_format_date(request: DateFormatRequest):
    """Proxy → Mazz Locale Formatter: Format a date for a given locale/format"""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(
                f"{MAZZ_API_BASE}/format/date",
                json=request.dict(exclude_none=True),
                headers={"Content-Type": "application/json"},
            )
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Mazz date proxy error: {e}")
            raise HTTPException(status_code=502, detail=f"Partner API unreachable: {str(e)}")


# ==================== ROOT & HEALTH ====================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "₿ CryptoFiat Bridge API",
        "tagline": "Seamless Conversion Between Traditional & Digital Currencies",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "author": "Dixshant Valecha",
        "project": "NCI MSc Cloud Computing - Scalable Cloud Programming",
        "core_features": [
            "💱 Traditional currency conversion (160+ currencies)",
            "₿ Cryptocurrency prices (20+ cryptos)",
            "🔄 Crypto-to-crypto conversion (BTC→ETH, etc.)",
            "💰 Crypto-to-fiat conversion (BTC→USD, etc.)",
            "💵 Fiat-to-crypto conversion (USD→BTC, etc.)",
            "📊 Detailed crypto market data",
            "📈 Multi-currency comparison",
            "⚡ High-performance caching",
            "🔁 CoinCap fallback (no downtime on rate limits)"
        ],
        "supported_cryptocurrencies": list(CRYPTO_ID_MAP.keys()),
        "supported_fiats": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "INR"],
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "crypto_list": "GET /crypto/list",
            "crypto_prices": "GET /crypto/prices",
            "crypto_prices_multi": "GET /crypto/prices/multi",
            "crypto_details": "GET /crypto/details/{symbol}",
            "fiat_to_crypto": "POST /convert/crypto",
            "crypto_to_fiat": "POST /crypto/to-fiat",
            "crypto_to_crypto": "POST /crypto/convert",
            "traditional_convert": "POST /convert",
            "multi_compare": "POST /convert/compare",
            "currencies": "GET /currencies",
            "proxy_phone": "POST /proxy/format/phone",
            "proxy_date": "POST /proxy/format/date"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    return HealthResponse(
        status="healthy",
        service="cryptofiat-bridge-api",
        timestamp=datetime.utcnow().isoformat(),
        version="3.0.0"
    )


@app.get("/info", response_model=APIInfo, tags=["Information"])
async def api_info():
    return APIInfo(
        name="CryptoFiat Bridge API",
        description="Bidirectional conversion between traditional and digital currencies with real-time market data",
        version="3.0.0",
        endpoints=[
            "GET  /           - Root",
            "GET  /health     - Health check",
            "GET  /info       - API information",
            "GET  /docs       - Swagger UI",
            "POST /convert    - Fiat to fiat conversion",
            "POST /convert/compare - Multi-currency comparison",
            "GET  /currencies - List supported fiat currencies",
            "GET  /crypto/list - List supported cryptocurrencies",
            "GET  /crypto/prices - Basic crypto prices",
            "GET  /crypto/prices/multi - Multiple crypto prices",
            "GET  /crypto/details/{symbol} - Detailed crypto info",
            "POST /convert/crypto - Fiat to crypto",
            "POST /crypto/to-fiat - Crypto to fiat",
            "POST /crypto/convert - Crypto to crypto",
            "POST /proxy/format/phone - Partner: phone formatter",
            "POST /proxy/format/date  - Partner: date formatter",
        ]
    )


# ==================== FIAT ENDPOINTS ====================

@app.post("/convert", response_model=ConversionResponse, tags=["Currency Conversion"])
async def convert_currency(request: ConversionRequest):
    """Convert fiat currency using real-time exchange rates"""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured.")
    from_curr = request.from_currency.upper()
    to_curr = request.to_currency.upper()
    logger.info(f"Fiat conversion: {from_curr} → {to_curr}, amount: {request.amount}")
    try:
        cached_rate = get_cached_rate(from_curr, to_curr)
        if cached_rate:
            return ConversionResponse(
                from_currency=from_curr, to_currency=to_curr, amount=request.amount,
                converted_amount=round(request.amount * cached_rate, 2),
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
                raise HTTPException(status_code=400, detail=f"Invalid currency: '{from_curr}' or '{to_curr}'")
            raise HTTPException(status_code=400, detail=f"Conversion failed: {error_type}")
        set_cached_rate(from_curr, to_curr, data["conversion_rate"])
        return ConversionResponse(
            from_currency=from_curr, to_currency=to_curr, amount=request.amount,
            converted_amount=round(data["conversion_result"], 2),
            exchange_rate=round(data["conversion_rate"], 6),
            timestamp=datetime.utcnow().isoformat()
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="External API timeout.")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"External API error: {str(e)}")


@app.get("/currencies", tags=["Currency Conversion"])
async def get_supported_currencies():
    """Get list of all supported fiat currency codes"""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured.")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/{API_KEY}/codes")
            response.raise_for_status()
            data = response.json()
        if data.get("result") != "success":
            raise HTTPException(status_code=500, detail="Failed to fetch currency codes.")
        supported_codes = data.get("supported_codes", [])
        return {
            "total": len(supported_codes),
            "currencies": [{"code": c[0], "name": c[1]} for c in supported_codes[:20]],
            "note": f"Showing 20 of {len(supported_codes)} currencies."
        }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail="External API unavailable.")


@app.post("/convert/compare", response_model=MultiConversionResponse, tags=["Currency Conversion"])
async def compare_currencies(request: MultiConversionRequest):
    """Compare conversion rates across multiple fiat currencies"""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured.")
    base_curr = request.base_currency.upper()
    comparisons = []
    for target_curr in request.target_currencies:
        target_curr = target_curr.upper()
        try:
            rate = get_cached_rate(base_curr, target_curr)
            if not rate:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{BASE_URL}/{API_KEY}/pair/{base_curr}/{target_curr}")
                    response.raise_for_status()
                    data = response.json()
                    if data.get("result") == "success":
                        rate = data["conversion_rate"]
                        set_cached_rate(base_curr, target_curr, rate)
            if rate:
                comparisons.append({
                    "currency": target_curr,
                    "converted_amount": round(request.amount * rate, 2),
                    "exchange_rate": round(rate, 6)
                })
        except Exception as e:
            logger.error(f"Error converting {base_curr} to {target_curr}: {e}")
            continue
    if not comparisons:
        raise HTTPException(status_code=400, detail="Could not convert to any target currencies.")
    comparisons.sort(key=lambda x: x["converted_amount"], reverse=True)
    ranked = [
        CurrencyComparison(currency=c["currency"], converted_amount=c["converted_amount"],
                           exchange_rate=c["exchange_rate"], rank=i + 1)
        for i, c in enumerate(comparisons)
    ]
    best = ranked[0]
    return MultiConversionResponse(
        base_currency=base_curr, base_amount=request.amount, comparisons=ranked,
        best_value=f"{best.currency} ({best.converted_amount})",
        total_currencies_compared=len(ranked),
        timestamp=datetime.utcnow().isoformat()
    )


# ==================== CRYPTO ENDPOINTS ====================

@app.get("/crypto/list", response_model=CryptoListResponse, tags=["Cryptocurrency"])
async def list_cryptocurrencies():
    """Get list of all 20 supported cryptocurrencies"""
    currencies = [
        {"symbol": symbol, "name": CRYPTO_NAMES[symbol], "id": CRYPTO_ID_MAP[symbol]}
        for symbol in CRYPTO_ID_MAP
    ]
    return CryptoListResponse(
        total_cryptos=len(currencies),
        currencies=currencies,
        supported_fiats=["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "INR"],
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/crypto/prices", tags=["Cryptocurrency"])
async def get_crypto_prices():
    """Get BTC, ETH, USDT prices in USD/EUR/GBP (with CoinCap fallback)"""
    try:
        data = await fetch_crypto_prices(
            ["bitcoin", "ethereum", "tether"], ["usd", "eur", "gbp"]
        )
        def safe(coin, currency):
            return data.get(coin, {}).get(currency, 0)
        return CryptoResponse(
            bitcoin=CryptoPrices(symbol="BTC", usd=safe("bitcoin","usd"), eur=safe("bitcoin","eur"), gbp=safe("bitcoin","gbp")),
            ethereum=CryptoPrices(symbol="ETH", usd=safe("ethereum","usd"), eur=safe("ethereum","eur"), gbp=safe("ethereum","gbp")),
            tether=CryptoPrices(symbol="USDT", usd=safe("tether","usd"), eur=safe("tether","eur"), gbp=safe("tether","gbp")),
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/crypto/prices/multi", tags=["Cryptocurrency"])
async def get_multiple_crypto_prices(
    symbols: str = "BTC,ETH,USDT,ADA,SOL",
    vs_currency: str = "usd"
):
    """Get prices for multiple cryptocurrencies (with CoinCap fallback)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        crypto_ids = [get_crypto_id(s) for s in symbol_list]
        data = await fetch_crypto_prices(crypto_ids, [vs_currency.lower()])
        result = {}
        for symbol, crypto_id in zip(symbol_list, crypto_ids):
            if crypto_id in data:
                cd = data[crypto_id]
                result[symbol] = {
                    "price": cd.get(vs_currency.lower()),
                    "market_cap": cd.get(f"{vs_currency.lower()}_market_cap"),
                    "24h_volume": cd.get(f"{vs_currency.lower()}_24h_vol"),
                    "24h_change": cd.get(f"{vs_currency.lower()}_24h_change"),
                }
        return {"data": result, "vs_currency": vs_currency.upper(),
                "timestamp": datetime.utcnow().isoformat(), "source": "CoinGecko/CoinCap"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert/crypto", response_model=FiatToCryptoResponse, tags=["Cryptocurrency"])
async def convert_fiat_to_crypto(request: FiatToCryptoRequest):
    """
    Convert fiat currency to any of the 20 supported cryptocurrencies.
    Uses CoinCap as fallback if CoinGecko is rate-limited.
    """
    from_curr = request.from_currency.upper()
    to_crypto = request.to_crypto.upper()

    # Get USD price of the target crypto
    usd_price = await fetch_crypto_price_usd(to_crypto)

    # If from_currency is not USD, convert fiat → USD first
    if from_curr == "USD":
        usd_amount = request.fiat_amount
    else:
        if not API_KEY:
            raise HTTPException(status_code=500, detail="API key not configured for fiat conversion.")
        try:
            cached = get_cached_rate(from_curr, "USD")
            if cached:
                usd_amount = request.fiat_amount * cached
            else:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(f"{BASE_URL}/{API_KEY}/pair/{from_curr}/USD")
                    resp.raise_for_status()
                    d = resp.json()
                    rate = d.get("conversion_rate", 1)
                    set_cached_rate(from_curr, "USD", rate)
                    usd_amount = request.fiat_amount * rate
        except Exception:
            usd_amount = request.fiat_amount  # fallback: assume 1:1

    crypto_amount = usd_amount / usd_price
    logger.info(f"Fiat→Crypto: {request.fiat_amount} {from_curr} = {crypto_amount:.8f} {to_crypto}")

    return FiatToCryptoResponse(
        from_currency=from_curr,
        to_crypto=to_crypto,
        fiat_amount=request.fiat_amount,
        crypto_amount=round(crypto_amount, 8),
        rate=round(usd_price, 2),
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/crypto/to-fiat", response_model=CryptoToFiatResponse, tags=["Cryptocurrency"])
async def convert_crypto_to_fiat(request: CryptoToFiatRequest):
    """
    Convert cryptocurrency to fiat currency.
    Supports all 20 cryptos and USD/EUR/GBP/JPY/AUD/CAD/CHF/INR.
    Uses CoinCap as fallback if CoinGecko is rate-limited.
    """
    from_crypto = request.from_crypto.upper()
    to_curr = request.to_currency.upper()

    supported_fiats = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "INR"]
    if to_curr not in supported_fiats:
        raise HTTPException(status_code=400, detail=f"Fiat '{to_curr}' not supported. Use: {supported_fiats}")

    usd_price = await fetch_crypto_price_usd(from_crypto)
    usd_value = request.crypto_amount * usd_price

    # Convert USD → target fiat if needed
    if to_curr == "USD":
        fiat_amount = usd_value
        rate = usd_price
    else:
        if not API_KEY:
            fiat_amount = usd_value
            rate = usd_price
        else:
            try:
                fiat_rate = get_cached_rate("USD", to_curr)
                if not fiat_rate:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get(f"{BASE_URL}/{API_KEY}/pair/USD/{to_curr}")
                        resp.raise_for_status()
                        d = resp.json()
                        fiat_rate = d.get("conversion_rate", 1)
                        set_cached_rate("USD", to_curr, fiat_rate)
                fiat_amount = usd_value * fiat_rate
                rate = usd_price * fiat_rate
            except Exception:
                fiat_amount = usd_value
                rate = usd_price

    logger.info(f"Crypto→Fiat: {request.crypto_amount} {from_crypto} = {fiat_amount:.2f} {to_curr}")

    return CryptoToFiatResponse(
        from_crypto=from_crypto,
        to_currency=to_curr,
        crypto_amount=request.crypto_amount,
        fiat_amount=round(fiat_amount, 2),
        rate=round(rate, 4),
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/crypto/convert", response_model=CryptoToCryptoResponse, tags=["Cryptocurrency"])
async def convert_crypto_to_crypto(request: CryptoToCryptoRequest):
    """
    Convert one cryptocurrency to another.
    Uses CoinCap as fallback if CoinGecko is rate-limited.
    """
    from_crypto = request.from_crypto.upper()
    to_crypto = request.to_crypto.upper()

    from_usd = await fetch_crypto_price_usd(from_crypto)
    to_usd = await fetch_crypto_price_usd(to_crypto)

    usd_value = request.amount * from_usd
    to_amount = usd_value / to_usd
    exchange_rate = from_usd / to_usd

    logger.info(f"Crypto→Crypto: {request.amount} {from_crypto} = {to_amount:.8f} {to_crypto}")

    return CryptoToCryptoResponse(
        from_crypto=from_crypto,
        to_crypto=to_crypto,
        from_amount=request.amount,
        to_amount=round(to_amount, 8),
        exchange_rate=round(exchange_rate, 8),
        usd_value=round(usd_value, 2),
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/crypto/details/{symbol}", tags=["Cryptocurrency"])
async def get_crypto_details(symbol: str):
    """Get detailed market information for a cryptocurrency"""
    try:
        crypto_id = get_crypto_id(symbol)
        data = await fetch_detailed_crypto_data(crypto_id)
        market_data = data.get("market_data", {})
        return {
            "symbol": symbol.upper(),
            "name": data.get("name"),
            "description": (data.get("description", {}).get("en", "")[:200] + "...") if data.get("description", {}).get("en") else None,
            "current_price": {
                "usd": market_data.get("current_price", {}).get("usd"),
                "eur": market_data.get("current_price", {}).get("eur"),
                "gbp": market_data.get("current_price", {}).get("gbp"),
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
            "ath": {"usd": market_data.get("ath", {}).get("usd"), "date": market_data.get("ath_date", {}).get("usd")},
            "atl": {"usd": market_data.get("atl", {}).get("usd"), "date": market_data.get("atl_date", {}).get("usd")},
            "last_updated": data.get("last_updated"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching crypto details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("₿  CryptoFiat Bridge API v3.0 Started!")
    print("👨‍💻 Developer: Dixshant Valecha")
    print("📚 Docs:   http://localhost:8000/docs")
    print("🏥 Health: http://localhost:8000/health")
    print("🔁 Fallback: CoinCap (auto on CoinGecko 429)")
    print("=" * 60)
    if not API_KEY:
        print("⚠️  WARNING: EXCHANGE_RATE_API_KEY not set!")
    else:
        print(f"✅ Exchange Rate API Key: configured ({API_KEY[:8]}...)")
    print(f"✅ Supported Cryptos: {len(CRYPTO_ID_MAP)}")


@app.on_event("shutdown")
async def shutdown_event():
    print("👋 CryptoFiat Bridge API shutting down...")