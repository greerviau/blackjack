"""
Pseudo Card Counting System.

Instead of counting every individual card, this system tracks the average
composition of cards visible in each round. It maintains a round-based count
that indicates whether recent rounds have shown favorable or unfavorable cards.
"""

from .base import CountingSystem


class PseudoCounter(CountingSystem):
    """
    Pseudo card counting system that tracks round-level card composition.

    Instead of counting each card individually, this system:
    1. Accumulates cards visible during a round
    2. At round end, calculates if the round was "good" (lots of low cards)
       or "bad" (lots of high cards)
    3. Maintains a rolling history of recent rounds
    4. Uses this history to adjust betting

    This is simpler than traditional counting and focuses on patterns
    over recent rounds rather than precise running counts.
    """

    def __init__(self, n_decks: int):
        """
        Initialize the pseudo counter.

        Args:
            lookback_rounds: Number of recent rounds to track (default: 5)
        """
        super().__init__(n_decks)
        # Track cards in the current round
        self.current_round_cards = []

    def reset(self) -> None:
        """Reset for a new shoe."""
        super().reset()
        self.current_round_cards = []

    def count_card(self, card) -> None:
        """
        Accumulate cards seen in the current round.

        Args:
            card: The card that was revealed
        """
        self.current_round_cards.append(card)
        self.cards_seen += 1

    def end_round(self) -> None:
        """
        Process the round's accumulated cards and update the pseudo count.

        The count is scaled by the ratio of low to high cards seen.
        If 3x as many low cards came out as high cards, that's more
        valuable than just 1 more low card vs high cards.
        """
        if not self.current_round_cards:
            return

        low = sum(1 for c in self.current_round_cards if 2 <= c.value < 7)  # 2-6
        high = sum(
            1 for c in self.current_round_cards if c.value >= 10 or c.value == 1
        )  # 10-A

        if low > high:
            if high == 0:
                self.running_count += low // 2
            else:
                self.running_count += low // high
        elif high > low:
            if low == 0:
                self.running_count -= high // 2
            else:
                self.running_count -= high // low

        # Clear for next round
        self.current_round_cards = []

    def get_true_count(self) -> int:
        """
        Get the pseudo count adjusted for deck penetration.

        The pseudo count represents the cumulative effect of recent rounds.
        A positive count means recent rounds showed more low cards (good).
        A negative count means recent rounds showed more high cards (bad).

        Returns:
            Adjusted pseudo count as a float
        """
        # Calculate how many decks remain
        total_cards = self.n_decks * 52
        cards_remaining = total_cards - self.cards_seen
        decks_remaining = max(cards_remaining / 52, 0.5)  # Minimum 0.5 decks

        return int(self.running_count / decks_remaining)
