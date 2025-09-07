from fastapi import APIRouter
from app.api.endpoints import portfolio, trading, strategies, market_data

api_router = APIRouter()

api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
