from abc import ABC, abstractmethod
from typing import Dict


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_signal(self, symbol: str, data) -> Dict:
        """Generate a trading signal for a symbol."""
        raise NotImplementedError
