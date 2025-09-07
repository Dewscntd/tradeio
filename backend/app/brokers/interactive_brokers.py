from ib_insync import IB, Stock, MarketOrder, LimitOrder, util
import asyncio
from typing import Optional, List, Dict
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class InteractiveBrokersClient:
    def __init__(self):
        self.ib = IB()
        self.connected = False

    async def connect(self):
        """Connect to Interactive Brokers TWS/Gateway"""
        try:
            await self.ib.connectAsync(
                host=settings.IB_HOST,
                port=settings.IB_PORT,
                clientId=settings.IB_CLIENT_ID
            )
            self.connected = True
            logger.info("Connected to Interactive Brokers")

            # Set up event handlers
            self.ib.orderStatusEvent += self.on_order_status
            self.ib.execDetailsEvent += self.on_execution

        except Exception as e:
            logger.error(f"Failed to connect to IB: {e}")
            self.connected = False

    async def disconnect(self):
        """Disconnect from Interactive Brokers"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False

    async def get_account_summary(self) -> Dict:
        """Get account summary information"""
        if not self.connected:
            await self.connect()

        account_values = self.ib.accountSummary()
        summary = {}

        for item in account_values:
            summary[item.tag] = {
                'value': item.value,
                'currency': item.currency
            }

        return summary

    async def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.connected:
            await self.connect()

        positions = self.ib.positions()
        return [
            {
                'symbol': pos.contract.symbol,
                'exchange': pos.contract.exchange,
                'quantity': pos.position,
                'avg_cost': pos.avgCost,
                'market_value': pos.marketValue,
                'unrealized_pnl': pos.unrealizedPNL
            }
            for pos in positions if pos.position != 0
        ]

    async def place_order(self, symbol: str, exchange: str, action: str,
                         quantity: float, order_type: str = 'MKT',
                         limit_price: Optional[float] = None) -> Optional[str]:
        """Place a trading order"""
        if not self.connected:
            await self.connect()

        try:
            # Create contract
            if exchange == "TASE":
                contract = Stock(symbol, "TASE", "ILS")
            else:
                contract = Stock(symbol, "SMART", "USD")

            # Create order
            if order_type == 'MKT':
                order = MarketOrder(action, quantity)
            elif order_type == 'LMT' and limit_price:
                order = LimitOrder(action, quantity, limit_price)
            else:
                raise ValueError("Invalid order type or missing limit price")

            # Place order
            trade = self.ib.placeOrder(contract, order)
            logger.info(f"Placed order: {symbol} {action} {quantity}")

            return trade.order.orderId

        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return None

    async def get_market_data(self, symbol: str, exchange: str) -> Optional[Dict]:
        """Get real-time market data for a symbol"""
        if not self.connected:
            await self.connect()

        try:
            if exchange == "TASE":
                contract = Stock(symbol, "TASE", "ILS")
            else:
                contract = Stock(symbol, "SMART", "USD")

            self.ib.qualifyContracts(contract)
            ticker = self.ib.reqMktData(contract)

            # Wait for data
            await asyncio.sleep(1)

            return {
                'symbol': symbol,
                'bid': ticker.bid,
                'ask': ticker.ask,
                'last': ticker.last,
                'volume': ticker.volume,
                'timestamp': util.df([ticker])['time'].iloc[0] if len(util.df([ticker])) > 0 else None
            }

        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            return None

    def on_order_status(self, trade):
        """Handle order status updates"""
        logger.info(f"Order status update: {trade.order.orderId} - {trade.orderStatus.status}")

    def on_execution(self, trade, fill):
        """Handle trade executions"""
        logger.info(
            f"Trade executed: {fill.contract.symbol} {fill.execution.side} {fill.execution.shares} @ {fill.execution.price}"
        )


# Global IB client instance
ib_client = InteractiveBrokersClient()
