from strategies.exit.base import ExitStrategy


class WinLossStopExitStrategy(ExitStrategy):
    def __init__(
        self,
        starting_bankroll: float,
        target_pct: float = 0.30,
        loss_pct: float = 0.40,
    ):
        super().__init__(starting_bankroll)
        self.target_bankroll = starting_bankroll + (starting_bankroll * target_pct)
        self.loss_stop = starting_bankroll * loss_pct

    def should_exit(self, bankroll: float) -> bool:
        if bankroll >= self.target_bankroll:
            return True
        elif bankroll <= self.loss_stop:
            return True
        return False
