from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.trading import Portfolio, Position, Trade
from app.core.database import get_db
from typing import List
import json

router = APIRouter()

@router.get("/summary")
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get portfolio summary with current positions and P&L"""
    portfolio = db.query(Portfolio).first()
    if not portfolio:
        # Create default portfolio
        portfolio = Portfolio(name="Main Portfolio", cash_balance=100000.0)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    positions = db.query(Position).filter(Position.portfolio_id == portfolio.id).all()
    
    total_market_value = sum(pos.market_value for pos in positions)
    total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
    
    return {
        "portfolio_id": portfolio.id,
        "total_value": portfolio.cash_balance + total_market_value,
        "cash_balance": portfolio.cash_balance,
        "market_value": total_market_value,
        "unrealized_pnl": total_unrealized_pnl,
        "positions_count": len(positions),
        "updated_at": portfolio.updated_at
    }

@router.get("/positions")
async def get_positions(db: Session = Depends(get_db)):
    """Get all current positions"""
    positions = db.query(Position).all()
    return [
        {
            "id": pos.id,
            "symbol": pos.symbol,
            "exchange": pos.exchange,
            "quantity": pos.quantity,
            "avg_price": pos.avg_price,
            "current_price": pos.current_price,
            "market_value": pos.market_value,
            "unrealized_pnl": pos.unrealized_pnl,
            "pnl_percentage": (pos.unrealized_pnl / (pos.avg_price * pos.quantity)) * 100 if pos.quantity > 0 else 0
        }
        for pos in positions
    ]

@router.get("/trades")
async def get_trades(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent trades"""
    trades = db.query(Trade).order_by(Trade.executed_at.desc()).limit(limit).all()
    return [
        {
            "id": trade.id,
            "symbol": trade.symbol,
            "exchange": trade.exchange,
            "side": trade.side,
            "quantity": trade.quantity,
            "price": trade.price,
            "commission": trade.commission,
            "strategy": trade.strategy,
            "executed_at": trade.executed_at
        }
        for trade in trades
    ]
