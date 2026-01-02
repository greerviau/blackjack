"""
Card counting systems for blackjack.

Tracks cards to determine when the deck is favorable.
"""

from .base import ExitStrategy
from .double import DoubleExitStrategy
from .peak import PeakExitStrategy
from .profit_lock import ProfitLockExitStrategy
from .win_loss_stop import WinLossStopExitStrategy

__all__ = [
    "ExitStrategy",
    "DoubleExitStrategy",
    "PeakExitStrategy",
    "WinLossStopExitStrategy",
    "ProfitLockExitStrategy",
]
