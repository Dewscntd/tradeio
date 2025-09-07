import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from app.strategies.base_strategy import BaseStrategy
import logging

logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    """Simple momentum strategy using moving averages"""

    def __init__(
        self,
        short_window: int = 10,
        long_window: int = 30,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
    ):
        super().__init__("Momentum Strategy")
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Moving averages
        df["sma_short"] = df["close"].rolling(window=self.short_window).mean()
        df["sma_long"] = df["close"].rolling(window=self.long_window).mean()

        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Volume moving average
        df["volume_ma"] = df["volume"].rolling(window=20).mean()

        return df

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Dict:
        """Generate trading signal for a symbol"""
        if len(df) < self.long_window:
            return {"signal": "HOLD", "strength": 0.0, "reason": "Insufficient data"}

        df = self.calculate_indicators(df)
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signal = "HOLD"
        strength = 0.0
        reason = ""

        # Check for bullish momentum
        if (
            latest["sma_short"] > latest["sma_long"]
            and prev["sma_short"] <= prev["sma_long"]
            and latest["rsi"] < self.rsi_overbought
            and latest["volume"] > latest["volume_ma"] * 1.2
        ):
            signal = "BUY"
            strength = min(
                0.8,
                (latest["rsi"] - self.rsi_oversold)
                / (self.rsi_overbought - self.rsi_oversold),
            )
            reason = "Bullish crossover with volume confirmation"

        # Check for bearish momentum
        elif (
            latest["sma_short"] < latest["sma_long"]
            and prev["sma_short"] >= prev["sma_long"]
            and latest["rsi"] > self.rsi_oversold
        ):
            signal = "SELL"
            strength = min(
                0.8,
                (self.rsi_overbought - latest["rsi"])
                / (self.rsi_overbought - self.rsi_oversold),
            )
            reason = "Bearish crossover"

        return {
            "symbol": symbol,
            "signal": signal,
            "strength": strength,
            "reason": reason,
            "indicators": {
                "sma_short": latest["sma_short"],
                "sma_long": latest["sma_long"],
                "rsi": latest["rsi"],
                "volume_ratio": latest["volume"] / latest["volume_ma"],
            },
        }


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using Bollinger Bands"""

    def __init__(self, bb_period: int = 20, bb_std: float = 2.0, rsi_period: int = 14):
        super().__init__("Mean Reversion Strategy")
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and RSI"""
        # Bollinger Bands
        df["bb_middle"] = df["close"].rolling(window=self.bb_period).mean()
        bb_std = df["close"].rolling(window=self.bb_period).std()
        df["bb_upper"] = df["bb_middle"] + (bb_std * self.bb_std)
        df["bb_lower"] = df["bb_middle"] - (bb_std * self.bb_std)

        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Bollinger Band position
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

        return df

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Dict:
        """Generate mean reversion signal"""
        if len(df) < self.bb_period:
            return {"signal": "HOLD", "strength": 0.0, "reason": "Insufficient data"}

        df = self.calculate_indicators(df)
        latest = df.iloc[-1]

        signal = "HOLD"
        strength = 0.0
        reason = ""

        # Oversold condition
        if (
            latest["close"] <= latest["bb_lower"]
            and latest["rsi"] <= 30
            and latest["bb_position"] <= 0.1
        ):
            signal = "BUY"
            strength = min(
                0.9,
                (30 - latest["rsi"]) / 30 + (0.1 - latest["bb_position"]),
            )
            reason = "Oversold - below lower Bollinger Band"

        # Overbought condition
        elif (
            latest["close"] >= latest["bb_upper"]
            and latest["rsi"] >= 70
            and latest["bb_position"] >= 0.9
        ):
            signal = "SELL"
            strength = min(
                0.9,
                (latest["rsi"] - 70) / 30 + (latest["bb_position"] - 0.9),
            )
            reason = "Overbought - above upper Bollinger Band"

        return {
            "symbol": symbol,
            "signal": signal,
            "strength": strength,
            "reason": reason,
            "indicators": {
                "bb_position": latest["bb_position"],
                "rsi": latest["rsi"],
                "close": latest["close"],
                "bb_upper": latest["bb_upper"],
                "bb_lower": latest["bb_lower"],
            },
        }
