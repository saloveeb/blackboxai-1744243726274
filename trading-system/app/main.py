from fastapi import FastAPI, Depends
from pathlib import Path
import uvicorn
from .api import trading, auth, strategies, trading_signals
from .core.engine import TradingEngine
from .api.auth import oauth2_scheme
from .services import ExchangeService, SentimentAnalyzer, RiskManager

app = FastAPI(
    title="نظام التداول الآلي",
    description="نظام متكامل للتداول الآلي بالذكاء الاصطناعي",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Include all API routers with authentication
app.include_router(auth.router, prefix="/api/v1")
app.include_router(trading.router, prefix="/api/v1", dependencies=[Depends(oauth2_scheme)])
app.include_router(strategies.router, prefix="/api/v1", dependencies=[Depends(oauth2_scheme)])
app.include_router(trading_signals.router, prefix="/api/v1", dependencies=[Depends(oauth2_scheme)])

# Initialize services
engine = TradingEngine()
exchange_service = ExchangeService()
sentiment_analyzer = SentimentAnalyzer()
risk_manager = RiskManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await exchange_service.initialize()
    await sentiment_analyzer.initialize()
    risk_manager.initialize()
    engine.initialize()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
