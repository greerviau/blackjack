"""
Loss streak counting system - tracks consecutive losses.
"""

from typing import TYPE_CHECKING

from .base import CountingSystem

if TYPE_CHECKING:
    from core import GameResult


class LossStreakCounter(CountingSystem):
    """Tracks consecutive losses to adjust betting (e.g., Martingale)."""

    def __init__(self, n_decks: int):
        super().__init__(n_decks)
        self.loss_streak = 0

    def reset(self):
        super().reset()
        self.loss_streak = 0

    def end_hand(self, result: "GameResult") -> None:
        """Update loss streak based on hand result."""
        if result.is_win:
            self.loss_streak = 0
        elif result.is_loss:
            self.loss_streak += 1

    def get_true_count(self) -> int:
        """Return the current loss streak."""
        return self.loss_streak
