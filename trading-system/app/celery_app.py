from celery import Celery
from .core.engine import TradingEngine
import os

celery = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

engine = TradingEngine()

@celery.task(bind=True)
def execute_async_order(self, symbol: str, quantity: float, price: float):
    """Execute order asynchronously"""
    try:
        result = engine.execute_order(symbol, quantity, price)
        return {'status': 'success', 'order_id': result}
    except Exception as e:
        self.retry(exc=e, countdown=60)
