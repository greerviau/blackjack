"""
No Counting System - For strategies that don't use card counting.
"""

from .base import CountingSystem


class NoCounter(CountingSystem):
    """A counting system that doesn't count (for non-counting strategies)."""

    def get_true_count(self) -> int:
        """Always return 0 since we're not counting."""
        return 0

    def get_running_count(self) -> int:
        """Always return 0 since we're not counting."""
        return 0
