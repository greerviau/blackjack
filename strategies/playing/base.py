"""
Base class for playing strategies.

Determines hit/stand/double/split decisions independent of betting.
"""

from abc import ABC, abstractmethod


class PlayingStrategy(ABC):
    """Abstract base for playing strategies."""

    @abstractmethod
    def decide_action(self, hand, dealer_upcard_value: int, valid_actions: list) -> str:
        """
        Decide what action to take.

        Args:
            hand: The current hand
            dealer_upcard_value: Dealer's visible card value
            valid_actions: List of valid actions (e.g., ["hit", "stand", "double"])

        Returns:
            Action string: "hit", "stand", "double", or "split"
        """
        pass
