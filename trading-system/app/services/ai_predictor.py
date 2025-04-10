import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Attention
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import pandas as pd
from typing import Tuple

class AITradingPredictor:
    def __init__(self):
        self.model = self.build_model()
        
    def build_model(self) -> Sequential:
        """بناء نموذج LSTM مع انتباه للتنبؤ الدقيق بالأسعار"""
        model = Sequential([
            LSTM(256, return_sequences=True, input_shape=(60, 5)),
            Dropout(0.4),
            Attention(use_scale=True),
            LSTM(128, return_sequences=True),
            Dropout(0.3),
            LSTM(64),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='linear')
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001),
                    loss='huber_loss',
                    metrics=['mae', 'mse'])
        return model
        
    def train(self, data: pd.DataFrame, epochs: int = 100) -> dict:
        """تدريب النموذج مع إيقاف مبكر وحفظ أفضل نموذج"""
        X, y = self.prepare_data(data)
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
            ModelCheckpoint('best_model.h5', save_best_only=True)
        ]
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=64,
            validation_split=0.2,
            callbacks=callbacks,
            verbose=1
        )
        return history.history
        
    def predict(self, data: pd.DataFrame, lookahead: int = 3) -> Dict:
        """تنبؤ متعدد الخطوات مع فترات زمنية مختلفة"""
        predictions = {}
        X, _ = self.prepare_data(data)
        
        # التنبؤ للفترات القادمة
        current_input = X[-1:]
        for i in range(1, lookahead + 1):
            pred = self.model.predict(current_input)[0][0]
            predictions[f'day_{i}'] = pred
            
            # تحديث المدخلات للتنبؤ التالي
            new_input = np.roll(current_input, -1, axis=1)
            new_input[0, -1, 0] = pred  # تحديث سعر الإغلاق المتوقع
            current_input = new_input
            
        return predictions
        
    def evaluate_model(self, test_data: pd.DataFrame) -> Dict:
        """تقييم أداء النموذج على بيانات الاختبار"""
        X_test, y_test = self.prepare_data(test_data)
        predictions = self.model.predict(X_test)
        
        # حساب مقاييس الأداء
        mae = np.mean(np.abs(predictions - y_test))
        mse = np.mean((predictions - y_test)**2)
        accuracy = np.mean(np.sign(predictions[1:] - predictions[:-1]) == 
                         np.sign(y_test[1:] - y_test[:-1])) * 100
        
        return {
            'MAE': mae,
            'MSE': mse,
            'Direction_Accuracy': f'{accuracy:.2f}%',
            'Sharpe_Ratio': self.calculate_sharpe(predictions, y_test)
        }

    def calculate_sharpe(self, preds: np.array, actuals: np.array) -> float:
        """حساب نسبة شارب للتنبؤات"""
        returns = preds[1:] - actuals[:-1]
        return np.mean(returns) / np.std(returns) * np.sqrt(252)

    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.array, np.array]:
        """تحضير البيانات للتدريب مع ميزات إضافية"""
        features = pd.DataFrame()
        features['close'] = data['close']
        features['returns'] = data['close'].pct_change()
        features['volume'] = data['volume'] / data['volume'].max()
        features['sentiment'] = data.get('sentiment', 0)
        
        scaled_data = self.scale_data(features.values)
        X, y = [], []
        
        for i in range(60, len(scaled_data)):
            X.append(scaled_data[i-60:i])
            y.append(scaled_data[i])
            
        return np.array(X), np.array(y)
        
    def scale_data(self, data: np.array) -> np.array:
        """تسوية البيانات بين 0 و1"""
        return (data - np.min(data)) / (np.max(data) - np.min(data))
