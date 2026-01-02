from abc import abstractmethod
from typing import TYPE_CHECKING

from .hand import Hand

if TYPE_CHECKING:
    from .game import Blackjack, GameResult


class Player:
    def __init__(self, bankroll: float):
        self.original_bankroll = float(bankroll)
        self.bankroll = float(bankroll)
        self.hands = []
        self.current_hand_idx = 0

    @property
    def current_hand(self) -> Hand:
        return self.hands[self.current_hand_idx]

    @property
    def has_next_hand(self) -> bool:
        return self.current_hand_idx + 1 < len(self.hands)

    def next_hand(self) -> None:
        self.current_hand_idx += 1

    def join_game(self, game: "Blackjack"):
        self.game = game

    def reset(self) -> None:
        pass

    def new_hand(self, bet: float) -> None:
        self.hands = [Hand(bet)]
        self.current_hand_idx = 0

    @abstractmethod
    def end_hand(self, result: "GameResult") -> None:
        pass

    @abstractmethod
    def end_round(self, **kwargs) -> None:
        pass

    @abstractmethod
    def decide_bet(self) -> float:
        """Decide how much to bet before the hand is dealt.

        Returns:
            The bet amount
        """
        pass

    @abstractmethod
    def decide_action(self, valid_actions: list[str]) -> str:
        """Decide what action to take for the current hand.

        Returns:
            One of: "hit", "stand", "double", "split"
        """
        pass

    @abstractmethod
    def should_continue_playing(self) -> bool:
        """Decide whether to continue playing another round.

        Returns:
            True to continue, False to quit
        """
        pass
