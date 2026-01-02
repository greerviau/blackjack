from core import GameResult, Player


class HumanStrategy(Player):
    RESULT_MESSAGES = {
        GameResult.DEALER_BUST: "Dealer Busts - You Win!",
        GameResult.BLACKJACK: "Blackjack! You Win!",
        GameResult.WIN: "You Win!",
        GameResult.PUSH: "Push - It's a Tie",
        GameResult.DEALER_BLACKJACK: "Dealer Blackjack - You Lose",
        GameResult.BUST: "Busted - You Lose",
        GameResult.LOSS: "Dealer Wins - You Lose",
        GameResult.SURRENDER: "You surrendered half of your bet",
    }

    def reset(self):
        super().reset()
        print("\n== Shuffling ==")

    def end_hand(self, result: GameResult):
        message = self.RESULT_MESSAGES.get(result, f"Unknown result: {result}")
        print(f"\n>>> {message} <<<\n")

    def end_round(self, **kwargs):
        print("-" * 30)
        print(
            f"Dealer Final Hand: {self.game.dealer_hand} | {self.game.dealer_hand.value}"
        )
        print("Your hands:")
        for hand in self.hands:
            print(f"  - {hand} | {hand.value}")
        print("-" * 30)

    def decide_bet(self) -> int:
        """Decide how much to bet before the hand is dealt.

        Returns:
            The bet amount
        """
        print(f"\nBankroll: ${self.bankroll}")
        while True:
            bet = (
                input(f"Enter your bet (default ${self.game.table_min}): $")
                or self.game.table_min
            )
            try:
                bet = int(bet)
                if bet > self.bankroll:
                    print("  Not enough bankroll for that bet.")
                elif bet < self.game.table_min:
                    print(f"  Bet must be at least ${self.game.table_min} (table min).")
                elif bet > self.game.table_max:
                    print(f"  Bet cannot exceed ${self.game.table_max} (table max).")
                else:
                    return bet
            except ValueError:
                print(f"  '{bet}' is not a valid number.")

    def decide_action(self, valid_actions: list[str]) -> str:
        """Decide what action to take for the current hand.

        Returns:
            One of: "hit", "stand", "double", "split"
        """
        if len(valid_actions) == 1:
            return valid_actions[0]

        print(f"\nDealer showing: {self.game.dealer_up_card}")
        print(f"Your hand: {self.current_hand}")
        actions_str = " / ".join(valid_actions)
        while True:
            action = input(f"Action [{actions_str}]: ")
            if action in valid_actions:
                return action
            print(f"  '{action}' is not valid. Choose from: {actions_str}")

    def should_continue_playing(self) -> bool:
        """Decide whether to continue playing another round.

        Returns:
            True to continue, False to quit
        """
        return True
        # print()
        # return input("Play another round? (y/n): ").lower() in ["y", "yes"]
