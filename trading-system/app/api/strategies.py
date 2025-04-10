from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from datetime import datetime
from ..core.engine import TradingEngine
from ..database import SessionLocal, Strategy as DBStrategy
from ..api.auth import oauth2_scheme

router = APIRouter(tags=["strategies"])
engine = TradingEngine()

class StrategyCreate(BaseModel):
    name: str
    symbol: str
    type: str
    timeframe: str
    risk: float
    parameters: dict
    active: bool

class Strategy(StrategyCreate):
    id: int
    created_at: datetime
    updated_at: datetime

@router.post("/strategies/", response_model=Strategy)
async def create_strategy(strategy: StrategyCreate, token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    try:
        db_strategy = DBStrategy(**strategy.dict())
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        return db_strategy
    finally:
        db.close()

@router.get("/strategies/", response_model=List[Strategy])
async def get_strategies(token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    try:
        return db.query(DBStrategy).all()
    finally:
        db.close()

@router.delete("/strategies/{strategy_id}")
async def delete_strategy(strategy_id: int, token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    try:
        strategy = db.query(DBStrategy).filter(DBStrategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        db.delete(strategy)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()
