from typing import Dict, Optional
import numpy as np
from .ai_predictor import AITradingPredictor
from .risk import RiskManager

class AIStrategyEngine:
    def __init__(self):
        self.predictor = AITradingPredictor()
        self.risk_manager = RiskManager()
        
    def generate_signal(self, symbol: str, market_data: Dict) -> Dict:
        """توليد إشارة تداول ذكية"""
        # 1. التنبؤ بالسعر المستقبلي
        prediction = self.predictor.predict(market_data)
        
        # 2. تحليل المخاطر
        risk_assessment = self.risk_manager.assess_trade_risk(symbol, prediction)
        
        # 3. تحديد الإشارة المثلى
        if prediction > market_data['current_price'] * 1.02 and risk_assessment['score'] < 0.3:
            return {
                'action': 'buy',
                'confidence': min(prediction - market_data['current_price'], 0.95),
                'target_price': prediction,
                'stop_loss': market_data['current_price'] * 0.98
            }
        elif prediction < market_data['current_price'] * 0.98 and risk_assessment['score'] < 0.3:
            return {
                'action': 'sell',
                'confidence': min(market_data['current_price'] - prediction, 0.95),
                'target_price': prediction,
                'stop_loss': market_data['current_price'] * 1.02
            }
        return {'action': 'hold', 'confidence': 0}

    def optimize_portfolio(self, portfolio: Dict) -> Dict:
        """تحسين المحفظة باستخدام خوارزميات التعلم المعزز"""
        # تنفيذ خوارزميات تحسين المحفظة
        optimized = {}
        total_value = sum(asset['value'] for asset in portfolio.values())
        
        for symbol, asset in portfolio.items():
            signal = self.generate_signal(symbol, asset['market_data'])
            if signal['action'] != 'hold':
                optimized[symbol] = {
                    'action': signal['action'],
                    'amount': asset['value'] * signal['confidence'] / total_value,
                    'target': signal['target_price'],
                    'stop_loss': signal['stop_loss']
                }
        return optimized
