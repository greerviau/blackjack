"""
Predefined strategy combinations for simulation.
"""

from .bet_spread import BetSpread
from .composable_strategy import ComposableStrategy
from .counting import (
    HiLoCounter,
    LossStreakCounter,
    NoCounter,
    PseudoCounter,
    WinStreakCounter,
)
from .exit import (
    DoubleExitStrategy,
    PeakExitStrategy,
    ProfitLockExitStrategy,
    WinLossStopExitStrategy,
)
from .playing import BasicPlayingStrategy

# Base strategy names (without exit strategies)
BASE_STRATEGIES = [
    "Basic + Flat",
    "Basic + Martingale",
    "Basic + Win 1-2-4",
    "Basic + Hi-Lo + Linear",
    "Basic + Hi-Lo + MinMax",
    "Basic + Pseudo + Linear",
    "Basic + Pseudo + MinMax",
]

# Exit strategy suffixes
# Peak: 10% trailing stop, activates at 50% profit
EXIT_SUFFIXES = [
    " + Exit:Double",
    " + Exit:Peak",
    " + Exit:WinLossStop",
    " + Exit:ProfitLock",
]


def get_strategy_names(include_exit: bool = False) -> list[str]:
    """Get all available strategy combination names."""
    if not include_exit:
        return BASE_STRATEGIES.copy()

    names = []
    for base in BASE_STRATEGIES:
        for suffix in EXIT_SUFFIXES:
            names.append(base + suffix)
    return names


def create_strategy(
    name: str,
    bankroll: float,
    n_decks: int,
    table_min: int,
    table_max: int,
    h17: bool,
) -> ComposableStrategy:
    """Create a strategy instance from a preset name."""
    parts = name.split(" + ")

    # Parse exit strategy
    exit_strategy = None
    parts_to_remove = []
    for part in parts:
        if part == "Exit:Double":
            exit_strategy = DoubleExitStrategy(bankroll)
            parts_to_remove.append(part)
        elif part == "Exit:Peak":
            exit_strategy = PeakExitStrategy(bankroll)
            parts_to_remove.append(part)
        elif part == "Exit:WinLossStop":
            exit_strategy = WinLossStopExitStrategy(bankroll)
            parts_to_remove.append(part)
        elif part == "Exit:ProfitLock":
            exit_strategy = ProfitLockExitStrategy(bankroll)
            parts_to_remove.append(part)

    for part in parts_to_remove:
        parts.remove(part)

    # Parse counting system and betting spread
    counting_system = NoCounter(n_decks)
    bet_spread = None

    for part in parts:
        if part == "Hi-Lo":
            counting_system = HiLoCounter(n_decks)
        elif part == "Pseudo":
            counting_system = PseudoCounter(n_decks)
        elif part == "Win 1-2-4":
            counting_system = WinStreakCounter(n_decks)
            spread = {
                0: table_min,
                1: table_min * 2,
                2: table_min * 4,
                3: table_min,
                4: table_min * 2,
                5: table_min * 4,
                6: table_min,
                7: table_min * 2,
                8: table_min * 4,
            }
            bet_spread = BetSpread(spread=spread, min_bet=table_min, max_bet=table_min)
        elif part == "Martingale":
            counting_system = LossStreakCounter(n_decks)
            spread = {
                0: table_min,
                1: table_min * 2,
                2: table_min * 4,
                3: table_min * 8,
                4: table_min * 16,
                5: table_min * 32,
            }
            bet_spread = BetSpread(spread=spread, min_bet=table_min, max_bet=table_max)
        elif part == "Linear":
            spread = {
                0: table_min,
                1: table_max * 0.2,
                2: table_max * 0.4,
                3: table_max * 0.6,
                4: table_max * 0.8,
                5: table_max,
            }
            bet_spread = BetSpread(spread=spread, min_bet=table_min, max_bet=table_max)
        elif part == "MinMax":
            spread = {
                0: table_min,
                3: table_max,
            }
            bet_spread = BetSpread(spread=spread, min_bet=table_min, max_bet=table_max)

    return ComposableStrategy(
        bankroll=bankroll,
        playing_strategy=BasicPlayingStrategy(h17=h17),
        counting_system=counting_system,
        bet_spread=bet_spread,
        exit_strategy=exit_strategy,
        min_bet=table_min,
        max_bet=table_max,
    )
