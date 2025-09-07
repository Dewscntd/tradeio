"""Market data endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models.trading import MarketData
from app.core.database import get_db


router = APIRouter()


@router.get("/{symbol}")
async def get_market_data(
    symbol: str,
    exchange: str,
    timeframe: str = "1h",
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Return recent market data for a symbol.

    Data is returned in chronological order.
    """

    query = (
        db.query(MarketData)
        .filter(MarketData.symbol == symbol, MarketData.timeframe == timeframe)
        .order_by(MarketData.timestamp.desc())
        .limit(limit)
    )

    rows: List[MarketData] = query.all()
    # Reverse to chronological order
    rows.reverse()
    return [
        {
            "symbol": row.symbol,
            "timestamp": row.timestamp,
            "open": row.open_price,
            "high": row.high_price,
            "low": row.low_price,
            "close": row.close_price,
            "volume": row.volume,
        }
        for row in rows
    ]
