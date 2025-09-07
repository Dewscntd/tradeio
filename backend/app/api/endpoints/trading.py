"""Trading-related endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.brokers.interactive_brokers import ib_client
from app.core.database import get_db
from app.models.trading import Trade


router = APIRouter()


@router.get("/health")
async def trading_health():
    return {"status": "ok"}


class OrderRequest(BaseModel):
    symbol: str
    exchange: str
    side: str  # BUY or SELL
    quantity: float
    order_type: str = "MKT"
    limit_price: float | None = None
    strategy: str | None = None


@router.post("/order")
async def place_order(order: OrderRequest, db: Session = Depends(get_db)):
    """Place an order via Interactive Brokers and record it."""

    order_id = await ib_client.place_order(
        order.symbol,
        order.exchange,
        order.side,
        order.quantity,
        order.order_type,
        order.limit_price,
    )

    if order_id is None:
        raise HTTPException(status_code=400, detail="Order placement failed")

    trade = Trade(
        portfolio_id=1,  # default portfolio
        symbol=order.symbol,
        exchange=order.exchange,
        side=order.side,
        quantity=order.quantity,
        price=order.limit_price or 0.0,
        strategy=order.strategy or "",
        executed_at=datetime.utcnow(),
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    return {"order_id": order_id, "trade_id": trade.id}
