"""
Double bankroll exit strategy

Play until youve doubled your bankroll, then leave
"""

from strategies.exit.base import ExitStrategy


class DoubleExitStrategy(ExitStrategy):
    def should_exit(self, bankroll: float) -> bool:
        """
        Determine if to exit or not

        Returns:
            boolean on whether to exit or not
        """
        return bankroll >= self.starting_bankroll * 2
