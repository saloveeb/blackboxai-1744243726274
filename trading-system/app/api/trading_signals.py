from fastapi import APIRouter, Depends
from ..services.exchange import ExchangeService
from ..services.sentiment import SentimentAnalyzer
from ..core.trading_engine import TradingEngine
from ..schemas import TradingSignal

router = APIRouter()
engine = TradingEngine()

@router.post("/signals")
async def create_signal(signal: TradingSignal):
    """Process new trading signal"""
    return engine.process_signal(signal.dict())

@router.get("/risk")
async def get_risk_report():
    """Get current portfolio risk assessment"""
    return engine.get_risk_report()

@router.get("/sentiment/{symbol}")
async def get_symbol_sentiment(symbol: str):
    """Get market sentiment for symbol"""
    return SentimentAnalyzer().analyze_market_sentiment(symbol)

@router.get("/exchanges")
async def list_exchanges():
    """List available exchanges"""
    return ExchangeService().list_connected_exchanges()
