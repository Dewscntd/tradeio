"""Endpoints for managing trading strategies."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.trading import Strategy


router = APIRouter()


@router.get("/")
async def list_strategies(db: Session = Depends(get_db)):
    """List all strategies."""
    strategies = db.query(Strategy).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "is_active": s.is_active,
            "parameters": s.parameters,
            "performance_metrics": s.performance_metrics,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in strategies
    ]


@router.post("/")
async def create_strategy(
    name: str,
    description: str = "",
    parameters: str = "{}",
    db: Session = Depends(get_db),
):
    """Create a new strategy."""

    strategy = Strategy(
        name=name,
        description=description,
        parameters=parameters,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return {"id": strategy.id}


@router.patch("/{strategy_id}")
async def update_strategy(strategy_id: int, is_active: bool, db: Session = Depends(get_db)):
    """Activate or deactivate a strategy."""

    strategy = db.query(Strategy).get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.is_active = is_active
    db.commit()
    db.refresh(strategy)
    return {"id": strategy.id, "is_active": strategy.is_active}


@router.put("/{strategy_id}")
async def edit_strategy(
    strategy_id: int,
    name: str,
    description: str,
    parameters: str,
    db: Session = Depends(get_db),
):
    """Update strategy details."""

    strategy = db.query(Strategy).get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    strategy.name = name
    strategy.description = description
    strategy.parameters = parameters
    db.commit()
    db.refresh(strategy)
    return {"id": strategy.id}


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Delete a strategy."""

    strategy = db.query(Strategy).get(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    db.delete(strategy)
    db.commit()
    return {"status": "deleted"}
