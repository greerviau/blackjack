"""
Composable strategy that combines playing, counting, and betting components.

This allows users to mix and match different strategies:
- Playing strategy (how to play hands)
- Counting system (card counting)
- Betting strategy (bet sizing)
"""

from typing import TYPE_CHECKING, Optional

from core import Player

if TYPE_CHECKING:
    from core import GameResult

from .bet_spread import BetSpread
from .counting import CountingSystem
from .exit import ExitStrategy
from .playing import PlayingStrategy


class ComposableStrategy(Player):
    """
    A strategy that composes three independent components:
    1. PlayingStrategy - decides how to play hands (hit/stand/double/split)
    2. CountingSystem - tracks cards for counting (optional)
    3. BetSpread - decides bet sizes
    """

    def __init__(
        self,
        bankroll: float,
        playing_strategy: PlayingStrategy,
        counting_system: CountingSystem,
        bet_spread: Optional[BetSpread] = None,
        exit_strategy: Optional[ExitStrategy] = None,
        min_bet: int = 10,
        max_bet: int = 1000,
    ):
        """
        Initialize the composable strategy.

        Args:
            playing_strategy: How to play hands (defaults to BasicPlayingStrategy)
            counting_system: How to count cards (defaults to NoCounter)
            betting_strategy: How to size bets (defaults to FlatBetting)
            min_bet: Minimum bet amount
            max_bet: Maximum bet amount
            exit_miltiplier: A multiplication of the bankroll to exit the game
        """
        super().__init__(bankroll)
        # Use defaults if not provided
        self.playing = playing_strategy
        self.counting = counting_system
        self.bet_spread = bet_spread or BetSpread({}, min_bet, min_bet)  # Flat betting
        self.exit_strategy = exit_strategy

        self.min_bet = min_bet
        self.max_bet = max_bet

    def reset(self):
        super().reset()
        self.counting.reset()

    def end_hand(self, result: "GameResult") -> None:
        self.counting.end_hand(result)

    def end_round(self, **kwargs) -> None:
        self.counting.end_round()

    def decide_bet(self) -> float:
        """
        Get the bet amount for the next hand.

        Passes the true count to the betting strategy if it's available.
        """
        # Get true count from counting system
        true_count = self.counting.get_true_count()

        # Get bet from betting strategy (passing true count as context)
        bet = self.bet_spread.get_bet(value=true_count)

        # Ensure bet doesn't exceed bankroll
        bet = min(bet, self.bankroll)

        # Ensure bet doesn't exceed table max
        bet = max(self.game.table_min, min(bet, self.game.table_max))

        return bet

    def decide_action(self, valid_actions: list[str]) -> str:
        """
        Decide what action to take using the playing strategy.

        Returns:
            Action string: "hit", "stand", "double", or "split"
        """
        if len(valid_actions) == 1:
            return valid_actions[0]

        # Get dealer upcard value
        dealer_upcard = self.game.dealer_up_card

        return self.playing.decide_action(
            self.current_hand,
            dealer_upcard.value,
            valid_actions,
        )

    def should_continue_playing(self) -> bool:
        """Continue playing if we have money and haven't hit our exit condition."""
        if self.bankroll <= self.game.table_min:
            return False
        if self.exit_strategy is None:
            return True
        return not self.exit_strategy.should_exit(self.bankroll)
