import ccxt
from typing import Dict, List
from ..database import Exchange, SessionLocal

class ExchangeService:
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.db = SessionLocal()
        
    def connect_exchange(self, exchange_id: int) -> bool:
        """Connect to an exchange using stored credentials"""
        exchange = self.db.query(Exchange).get(exchange_id)
        if not exchange or not exchange.enabled:
            return False
            
        exchange_class = getattr(ccxt, exchange.name.lower())
        self.exchanges[exchange.name] = exchange_class({
            'apiKey': exchange.api_key,
            'secret': exchange.secret,
            'enableRateLimit': True
        })
        return True
        
    def get_balances(self, exchange_name: str) -> Dict:
        """Get account balances from exchange"""
        if exchange_name not in self.exchanges:
            if not self.connect_exchange_by_name(exchange_name):
                raise ValueError(f"Exchange {exchange_name} not configured")
        return self.exchanges[exchange_name].fetch_balance()
        
    def execute_trade(self, exchange_name: str, symbol: str, 
                    side: str, amount: float, price: float = None):
        """Execute trade on specified exchange"""
        if exchange_name not in self.exchanges:
            if not self.connect_exchange_by_name(exchange_name):
                raise ValueError(f"Exchange {exchange_name} not configured")
                
        exchange = self.exchanges[exchange_name]
        if price:
            return exchange.create_limit_order(symbol, side, amount, price)
        return exchange.create_market_order(symbol, side, amount)
        
    def connect_exchange_by_name(self, name: str) -> bool:
        """Connect to exchange by name"""
        exchange = self.db.query(Exchange).filter_by(name=name).first()
        if exchange:
            return self.connect_exchange(exchange.id)
        return False
