"""
Playing strategies for blackjack.

Determines hit/stand/double/split decisions.
"""

from .base import PlayingStrategy
from .basic import BasicPlayingStrategy

__all__ = [
    "PlayingStrategy",
    "BasicPlayingStrategy",
]
