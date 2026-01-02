"""
Win streak counting system - tracks consecutive wins.
"""

from typing import TYPE_CHECKING

from .base import CountingSystem

if TYPE_CHECKING:
    from core import GameResult


class WinStreakCounter(CountingSystem):
    """Tracks consecutive wins to adjust betting."""

    def __init__(self, n_decks: int):
        super().__init__(n_decks)
        self.win_streak = 0

    def reset(self):
        super().reset()
        self.win_streak = 0

    def end_hand(self, result: "GameResult") -> None:
        """Update win streak based on hand result."""
        if result.is_win:
            self.win_streak += 1
        elif result.is_loss:
            self.win_streak = 0

    def get_true_count(self) -> int:
        """Return the current win streak."""
        return self.win_streak
