from pathlib import Path
import logging
from typing import Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import SessionLocal, Order as DBOrder, Position as DBPosition, init_db

class TradingEngine:
    def __init__(self):
        # Windows-compatible paths
        self.log_path = Path("C:/trading_logs/engine.log")
        self.log_path.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=str(self.log_path),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize database
        init_db()
        self.db = SessionLocal()
        self._load_initial_state()

    def _load_initial_state(self):
        """Load positions and order count from database"""
        positions = self.db.query(DBPosition).all()
        self.positions = {p.symbol: p.quantity for p in positions}
        
        last_order = self.db.query(DBOrder).order_by(DBOrder.id.desc()).first()
        self.order_count = last_order.id if last_order else 0

    def execute_order(self, symbol: str, quantity: float, price: float) -> str:
        """Execute a trading order with full tracking"""
        order_id = f"ORD-{self.order_count}"
        self.order_count += 1
        
        # Update position
        if symbol not in self.positions:
            self.positions[symbol] = 0.0
            position = DBPosition(symbol=symbol, quantity=quantity)
            self.db.add(position)
        else:
            self.positions[symbol] += quantity
            position = self.db.query(DBPosition).filter_by(symbol=symbol).first()
            position.quantity = self.positions[symbol]
        
        # Create order record
        order = DBOrder(
            order_id=order_id,
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type="market",
            status="filled",
            timestamp=datetime.now()
        )
        self.db.add(order)
        self.db.commit()
        
        logging.info(f"Executed order {order_id}: {quantity} {symbol} @ {price}")
        return order_id

    def get_positions(self) -> Dict[str, float]:
        """Get current positions"""
        return self.positions

    def get_order(self, order_id: str) -> Dict:
        """Get order details by ID"""
        order = self.db.query(DBOrder).filter_by(order_id=order_id).first()
        if not order:
            return {}
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "quantity": order.quantity,
            "price": order.price,
            "order_type": order.order_type,
            "status": order.status,
            "timestamp": order.timestamp
        }

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        order = self.db.query(DBOrder).filter_by(order_id=order_id).first()
        if not order:
            return False
            
        order.status = "cancelled"
        self.db.commit()
        logging.info(f"Cancelled order {order_id}")
        return True

    def get_order_history(self) -> List[Dict]:
        """Get complete order history"""
        orders = self.db.query(DBOrder).order_by(DBOrder.timestamp.desc()).all()
        return [{
            "order_id": o.order_id,
            "symbol": o.symbol,
            "quantity": o.quantity,
            "price": o.price,
            "status": o.status,
            "timestamp": o.timestamp
        } for o in orders]

    def __del__(self):
        """Clean up database session"""
        self.db.close()
