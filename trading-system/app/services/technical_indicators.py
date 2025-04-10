import pandas as pd
import numpy as np
import talib
from typing import Dict, List

class TechnicalIndicatorService:
    def __init__(self):
        self.indicators = {
            'MA': self.calculate_moving_averages,
            'RSI': self.calculate_rsi,
            'MACD': self.calculate_macd,
            'Bollinger': self.calculate_bollinger_bands,
            'Stochastic': self.calculate_stochastic,
            'Fibonacci': self.calculate_fibonacci,
            'Ichimoku': self.calculate_ichimoku,
            'Volume': self.calculate_volume_indicators
        }

    def calculate_all_indicators(self, ohlc_data: pd.DataFrame) -> Dict:
        """حساب جميع المؤشرات الفنية"""
        results = {}
        for name, func in self.indicators.items():
            results[name] = func(ohlc_data)
        return results

    def calculate_moving_averages(self, data: pd.DataFrame) -> Dict:
        """حساب المتوسطات المتحركة"""
        return {
            'SMA_50': talib.SMA(data['close'], timeperiod=50),
            'SMA_200': talib.SMA(data['close'], timeperiod=200),
            'EMA_20': talib.EMA(data['close'], timeperiod=20),
            'EMA_50': talib.EMA(data['close'], timeperiod=50)
        }

    def calculate_rsi(self, data: pd.DataFrame) -> pd.Series:
        """حساب مؤشر القوة النسبية"""
        return talib.RSI(data['close'], timeperiod=14)

    def calculate_macd(self, data: pd.DataFrame) -> Dict:
        """حساب مؤشر الماكد"""
        macd, signal, _ = talib.MACD(data['close'], 
                                   fastperiod=12, 
                                   slowperiod=26, 
                                   signalperiod=9)
        return {'MACD': macd, 'Signal': signal}

    def calculate_bollinger_bands(self, data: pd.DataFrame) -> Dict:
        """حساب بولنجر باندز"""
        upper, middle, lower = talib.BBANDS(data['close'], 
                                          timeperiod=20,
                                          nbdevup=2, 
                                          nbdevdn=2)
        return {'Upper': upper, 'Middle': middle, 'Lower': lower}

    def calculate_stochastic(self, data: pd.DataFrame) -> Dict:
        """حساب ستوكاستيك"""
        slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'],
                                  fastk_period=14, slowk_period=3,
                                  slowd_period=3)
        return {'Stochastic_K': slowk, 'Stochastic_D': slowd}

    def calculate_fibonacci(self, data: pd.DataFrame) -> Dict:
        """حساب مستويات فيبوناتشي"""
        max_price = data['high'].max()
        min_price = data['low'].min()
        diff = max_price - min_price
        return {
            '23.6%': max_price - diff * 0.236,
            '38.2%': max_price - diff * 0.382,
            '50%': max_price - diff * 0.5,
            '61.8%': max_price - diff * 0.618
        }

    def calculate_ichimoku(self, data: pd.DataFrame) -> Dict:
        """حساب إيشيموكو"""
        high = data['high']
        low = data['low']
        tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2
        kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        senkou_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)
        return {
            'Tenkan': tenkan,
            'Kijun': kijun,
            'Senkou_A': senkou_a,
            'Senkou_B': senkou_b
        }

    def calculate_volume_indicators(self, data: pd.DataFrame) -> Dict:
        """حساب مؤشرات الحجم"""
        return {
            'OBV': talib.OBV(data['close'], data['volume']),
            'Volume_MA': talib.SMA(data['volume'], timeperiod=20)
        }

    # المؤشرات المتقدمة
    def calculate_elliott_wave(self, data: pd.DataFrame) -> Dict:
        """تحليل موجة إليوت"""
        closes = data['close'].values
        waves = []
        for i in range(2, len(closes)-2):
            if closes[i] > closes[i-1] > closes[i-2] and closes[i] > closes[i+1] > closes[i+2]:
                waves.append({'type': 'peak', 'index': i, 'price': closes[i]})
            elif closes[i] < closes[i-1] < closes[i-2] and closes[i] < closes[i+1] < closes[i+2]:
                waves.append({'type': 'trough', 'index': i, 'price': closes[i]})
        return {'waves': waves}

    def detect_candle_patterns(self, data: pd.DataFrame) -> List[str]:
        """كشف أنماط الشموع اليابانية"""
        patterns = []
        open_prices = data['open'].values
        high_prices = data['high'].values
        low_prices = data['low'].values
        close_prices = data['close'].values
        
        # نمط الشهاب (Shooting Star)
        for i in range(1, len(data)):
            body = abs(open_prices[i] - close_prices[i])
            lower_wick = min(open_prices[i], close_prices[i]) - low_prices[i]
            upper_wick = high_prices[i] - max(open_prices[i], close_prices[i])
            
            if upper_wick > body * 2 and lower_wick < body * 0.5:
                patterns.append(f'Shooting Star at index {i}')
                
        # نمط المطرقة (Hammer)
        for i in range(1, len(data)):
            body = abs(open_prices[i] - close_prices[i])
            lower_wick = min(open_prices[i], close_prices[i]) - low_prices[i]
            upper_wick = high_prices[i] - max(open_prices[i], close_prices[i])
            
            if lower_wick > body * 2 and upper_wick < body * 0.5:
                patterns.append(f'Hammer at index {i}')
                
        return patterns

    def advanced_fibonacci(self, data: pd.DataFrame) -> Dict:
        """مستويات فيبوناتشي المتقدمة"""
        pivot_high = data['high'].rolling(5).max().dropna()
        pivot_low = data['low'].rolling(5).min().dropna()
        
        levels = {}
        for i in range(1, len(pivot_high)):
            diff = pivot_high[i] - pivot_low[i]
            levels[f'Wave_{i}'] = {
                '0%': pivot_low[i],
                '23.6%': pivot_low[i] + diff * 0.236,
                '38.2%': pivot_low[i] + diff * 0.382,
                '50%': pivot_low[i] + diff * 0.5,
                '61.8%': pivot_low[i] + diff * 0.618,
                '100%': pivot_high[i]
            }
        return levels

    # تحسينات الأداء
    def calculate_parallel(self, data: pd.DataFrame) -> Dict:
        """حساب المؤشرات بشكل متوازي"""
        import concurrent.futures
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_indicator = {
                executor.submit(indicator, data): name 
                for name, indicator in self.indicators.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_indicator):
                name = future_to_indicator[future]
                results[name] = future.result()
                
        return results

    # نظام التخزين المؤقت
    _cache = {}
    
    def cached_calculation(self, data: pd.DataFrame) -> Dict:
        """حساب مع التخزين المؤقت"""
        cache_key = hash(tuple(data['close'].values))
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        results = self.calculate_all_indicators(data)
        self._cache[cache_key] = results
        return results

    # نظام التنبيهات
    def check_alert_levels(self, data: pd.DataFrame, levels: Dict) -> List[str]:
        """الكشف عن اختراق المستويات"""
        alerts = []
        current_close = data['close'].iloc[-1]
        
        for level_name, level_value in levels.items():
            if current_close >= level_value * 0.99 and current_close <= level_value * 1.01:
                alerts.append(f'Price approaching {level_name} level: {level_value}')
                
        return alerts
