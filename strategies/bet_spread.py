class BetSpread:
    def __init__(
        self,
        spread: dict[int, int],
        min_bet: int,
        max_bet: int,
    ):
        self.spread = spread
        self.min_bet = min_bet
        self.max_bet = max_bet

    def get_bet(self, value: int) -> float:
        if not self.spread:
            return self.min_bet
        if value <= 0:
            return self.spread.get(value, self.min_bet)
        else:
            return self.spread.get(value, self.max_bet)
