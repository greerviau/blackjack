from strategies.exit.base import ExitStrategy


class ProfitLockExitStrategy(ExitStrategy):
    def __init__(
        self,
        starting_bankroll: float,
        lock_pct: float = 0.30,
        loss_pct: float = 0.40,
    ):
        super().__init__(starting_bankroll)
        self.lock_pct = lock_pct
        self.loss_pct = loss_pct
        self.profit_target = starting_bankroll + (starting_bankroll * lock_pct)
        self.leave_target = starting_bankroll + (2 * (starting_bankroll * lock_pct))
        self.loss_stop = starting_bankroll - (starting_bankroll * loss_pct)

    def should_exit(self, bankroll: float) -> bool:
        if bankroll > self.leave_target:
            return True
        elif bankroll >= self.profit_target:
            # Lock in 50% of profit
            profit = bankroll - self.starting_bankroll
            self.loss_stop = self.starting_bankroll + (profit * 0.5)
        elif bankroll <= self.loss_stop:
            return True
        return False
