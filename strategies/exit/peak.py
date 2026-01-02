from strategies.exit.base import ExitStrategy


class PeakExitStrategy(ExitStrategy):
    def __init__(
        self,
        starting_bankroll: float,
        lock_pct: float = 0.30,
        loss_pct: float = 0.40,
    ):
        super().__init__(starting_bankroll)
        self.lock_value = starting_bankroll * lock_pct
        self.max_drawdown = starting_bankroll * loss_pct

        self.target_bankroll = starting_bankroll + self.lock_value
        self.loss_stop = starting_bankroll - self.max_drawdown

    def should_exit(self, bankroll: float) -> bool:
        if bankroll >= self.target_bankroll:
            # Keep increasing the target and loss stop
            self.target_bankroll = bankroll + self.lock_value
            self.loss_stop = bankroll - self.max_drawdown
        elif bankroll <= self.loss_stop:
            return True
        return False
