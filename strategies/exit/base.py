"""
Base class for exit strategies.
"""

from abc import ABC, abstractmethod


class ExitStrategy(ABC):
    """Abstract base class for all exit strategies."""

    def __init__(self, starting_bankroll: float):
        self.starting_bankroll = float(starting_bankroll)

    @abstractmethod
    def should_exit(self, bankroll: float) -> bool:
        """
        Determine if to exit or not

        Returns:
            boolean on whether to exit or not
        """
        pass
