import numpy as np
from typing import Dict, List
from ..database import SessionLocal, Position, Exchange

class RiskManager:
    def __init__(self):
        self.db = SessionLocal()
        
    def calculate_portfolio_risk(self) -> Dict:
        """Calculate comprehensive portfolio risk metrics"""
        positions = self.db.query(Position).filter_by(open=True).all()
        risk_report = {
            'total_value': 0.0,
            'var_95': 0.0,
            'max_drawdown': 0.0,
            'position_risks': []
        }
        
        for position in positions:
            position_risk = self._calculate_position_risk(position)
            risk_report['position_risks'].append(position_risk)
            risk_report['total_value'] += position_risk['current_value']
            
        # Calculate portfolio-level metrics
        risk_report['var_95'] = self._calculate_portfolio_var(risk_report['position_risks'])
        risk_report['max_drawdown'] = max(p['drawdown'] for p in risk_report['position_risks'])
        
        return risk_report
        
    def _calculate_position_risk(self, position: Position) -> Dict:
        """Calculate risk metrics for single position"""
        current_value = position.quantity * position.current_price
        entry_value = position.quantity * position.entry_price
        drawdown = (entry_value - current_value) / entry_value if entry_value else 0
        
        return {
            'symbol': position.symbol,
            'current_value': current_value,
            'entry_value': entry_value,
            'pnl': current_value - entry_value,
            'drawdown': drawdown,
            'liquidation_risk': self._calculate_liquidation_risk(position)
        }
        
    def _calculate_liquidation_risk(self, position: Position) -> float:
        """Calculate liquidation risk based on exchange rules"""
        exchange = self.db.query(Exchange).get(position.exchange_id)
        if not exchange:
            return 0.0
            
        # Implementation would use exchange-specific margin requirements
        return 0.0  # Placeholder
        
    def _calculate_portfolio_var(self, positions: List[Dict]) -> float:
        """Calculate Value at Risk for portfolio"""
        # This would use historical simulation or parametric method
        return sum(p['current_value'] * 0.05 for p in positions)  # Simple 5% VaR
        
    def check_position_limits(self, symbol: str, amount: float) -> bool:
        """Check if new position exceeds risk limits"""
        portfolio = self.calculate_portfolio_risk()
        position_values = [p['current_value'] for p in portfolio['position_risks']]
        avg_position = np.mean(position_values) if position_values else 0
        return amount <= avg_position * 2  # Don't exceed 2x average position size
