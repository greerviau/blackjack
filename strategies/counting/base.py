"""
Base class for card counting systems.

Counting systems track cards that have been played and maintain
a count that can be used by betting strategies.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import GameResult


class CountingSystem(ABC):
    """Abstract base class for all counting systems."""

    def __init__(self, n_decks: int):
        self.n_decks = n_decks
        self.cards_seen = 0
        self.running_count = 0

    def reset(self) -> None:
        """Reset the count for a new shoe."""
        self.cards_seen = 0
        self.running_count = 0

    def count_card(self, card) -> None:
        """
        Update the count based on a card that was revealed.

        Args:
            card: The card that was revealed
        """
        pass

    def end_round(self) -> None:
        """Called at the end of a round."""
        pass

    def end_hand(self, result: "GameResult") -> None:
        """Called at the end of a hand."""
        pass

    def get_running_count(self) -> int:
        """Get the running count."""
        return self.running_count

    @abstractmethod
    def get_true_count(self) -> int:
        """Get the true count (adjusted for remaining decks)."""
        pass
