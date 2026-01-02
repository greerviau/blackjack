"""
Hi-Lo Card Counting System.

The most popular and effective card counting system.
"""

from .base import CountingSystem


class HiLoCounter(CountingSystem):
    """
    Hi-Lo card counting system.

    Count values:
    - 2-6: +1 (low cards favor dealer)
    - 7-9: 0 (neutral)
    - 10-A: -1 (high cards favor player)
    """

    def count_card(self, card) -> None:
        """Update the Hi-Lo count based on the card."""
        value = card.value

        if 2 <= value <= 6:
            self.running_count += 1
        elif value >= 10 or value == 1:  # 10, J, Q, K, A
            self.running_count -= 1
        # 7, 8, 9 are neutral (0)

        self.cards_seen += 1

    def get_true_count(self) -> int:
        """
        Calculate true count by dividing running count by remaining decks.

        Returns:
            True count as a float
        """
        # Calculate how many decks remain
        total_cards = self.n_decks * 52
        cards_remaining = total_cards - self.cards_seen
        decks_remaining = max(cards_remaining / 52, 0.5)  # Minimum 0.5 decks

        return int(self.running_count / decks_remaining)
