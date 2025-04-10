from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime
from ..core.engine import TradingEngine

router = APIRouter(tags=["trading"])
engine = TradingEngine()

class OrderCreate(BaseModel):
    symbol: str
    quantity: float
    price: float
    order_type: Optional[str] = "market"

class Order(OrderCreate):
    order_id: str
    timestamp: datetime
    status: str

@router.post("/orders/", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    """Execute a trade order with validation"""
    try:
        # Validate order parameters
        if order.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if order.price <= 0:
            raise ValueError("Price must be positive")
        if len(order.symbol) > 10:
            raise ValueError("Symbol too long")
            
        result = engine.execute_order(
            symbol=order.symbol,
            quantity=order.quantity,
            price=order.price
        )
        return {
            "status": "success",
            "order_id": result,
            "symbol": order.symbol,
            "executed_quantity": order.quantity
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/positions/")
async def get_positions():
    """Get current positions"""
    return engine.get_positions()

@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    order = engine.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an order"""
    if not engine.cancel_order(order_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return {
        "status": "success",
        "message": f"Order {order_id} cancelled"
    }

@router.get("/orders/")
async def get_order_history():
    """Get complete order history"""
    return engine.get_order_history()
