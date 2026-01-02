from enum import Enum
from typing import Optional

from .cards import Card, Deck
from .hand import Hand
from .player import Player


class GameResult(Enum):
    """Outcomes for a single hand."""

    WIN = "win"
    LOSS = "loss"
    PUSH = "push"
    BLACKJACK = "blackjack"
    DEALER_BLACKJACK = "dealer_blackjack"
    DEALER_BUST = "dealer_bust"
    BUST = "bust"
    SURRENDER = "surrender"

    @property
    def is_win(self) -> bool:
        """Returns True if this result is a player win."""
        return self in (GameResult.WIN, GameResult.BLACKJACK, GameResult.DEALER_BUST)

    @property
    def is_loss(self) -> bool:
        """Returns True if this result is a player loss."""
        return self in (
            GameResult.LOSS,
            GameResult.DEALER_BLACKJACK,
            GameResult.BUST,
            GameResult.SURRENDER,
        )


class Blackjack:
    def __init__(
        self,
        player: Player,
        n_decks: int = 8,
        table_min: int = 10,
        table_max: int = 1000,
        blackjack_payout: float = 1.5,
        penetration: float = 0.75,
        h17: bool = True,
        das: bool = True,
        late_surrender: bool = False,
        max_splits: int = 3,
        hit_split_aces: bool = False,
        resplit_aces: bool = True,
    ):
        """
        Initialize blackjack game.

        Args:
            player: The player
            n_decks: Number of decks in shoe
            table_min: Minimum bet allowed
            table_max: Maximum bet allowed
            blackjack_payout: Blackjack payout multiplier (1.5 for 3:2, 1.2 for 6:5)
            penetration: How deep into shoe before reshuffling (0.75 = 75%)
            h17: If the dealer hits on soft 17
            das: Allow double after splitting
            late_surrender: Allow late surrender (after dealer checks for blackjack)
            max_splits: Maximum number of splits per round
            hit_split_aces: Allow hitting on split aces
            resplit_aces: Allow resplitting aces
        """
        self.deck = Deck(n_decks=n_decks)
        self.deck.shuffle()
        self.player = player
        self.player.join_game(self)
        self.dealer_hand = Hand(0)

        # Initialize counting system
        self.player.reset()

        # Table rules
        self.n_decks = n_decks
        self.table_min = table_min
        self.table_max = table_max
        self.blackjack_payout = blackjack_payout
        self.penetration = penetration
        self.total_cards = n_decks * 52
        self.reshuffle_point = int(self.total_cards * (1 - penetration))
        self.h17 = h17
        self.das = das
        self.late_surrender = late_surrender
        self.max_splits = max_splits
        self.hit_split_aces = hit_split_aces
        self.resplit_aces = resplit_aces

    @property
    def dealer_up_card(self) -> Card:
        return self.dealer_hand.cards[0]

    def get_valid_actions(self, hand: Hand, splits_made: int) -> list[str]:
        """Get valid actions for the current hand state."""
        if hand.value == 21:
            return ["stand"]

        is_ace = hand.cards[0].rank == "A"
        is_pair = hand.is_pair
        can_afford_extra_bet = self.player.bankroll >= hand.bet
        can_split_more = splits_made < self.max_splits

        # Split aces can only stand (unless hit_split_aces is enabled)
        if hand.is_from_split and is_ace and not self.hit_split_aces:
            valid_actions = ["stand"]
            if (
                is_pair
                and can_afford_extra_bet
                and can_split_more
                and self.resplit_aces
            ):
                valid_actions.append("split")
            return valid_actions

        valid_actions = ["hit", "stand"]

        # Double down - only on first two cards with sufficient bankroll
        if len(hand.cards) == 2 and can_afford_extra_bet:
            if not hand.is_from_split or self.das:
                valid_actions.append("double")

        # Split - pairs with enough bankroll and splits remaining
        if is_pair and can_afford_extra_bet and can_split_more:
            # Aces can only be resplit if resplit_aces is enabled
            if not is_ace or not hand.is_from_split or self.resplit_aces:
                valid_actions.append("split")

        # Late surrender - only on initial two cards, not after splitting
        if len(hand.cards) == 2 and not hand.is_from_split and self.late_surrender:
            valid_actions.append("surrender")

        return valid_actions

    def deal_card(self, hand: Hand):
        card = self.deck.draw()
        hand.add_card(card)
        if hasattr(self.player, "counting"):
            self.player.counting.count_card(card)

    def deal_initial_cards(self):
        """Deal two cards to player and dealer."""
        for _ in range(2):
            # Deal to player
            self.deal_card(self.player.current_hand)
            # Deal to dealer
            self.deal_card(self.dealer_hand)

    def dealer_play(self):
        """Dealer draws until reaching 17 or busting."""
        while True:
            # Dealer hits on soft 17
            if self.dealer_hand.value < 17 or (
                self.h17 and self.dealer_hand.value == 17 and self.dealer_hand.is_soft
            ):
                self.deal_card(self.dealer_hand)
            else:
                break

    def play_round(self) -> tuple:
        """Play a single round of blackjack.

        Returns:
            Tuple of (wins, losses, pushes, surrenders, total_wagered)
        """
        splits_made = 0
        self.dealer_hand = Hand(0)
        total_wagered_this_round = 0  # Track all money wagered this round

        # Reshuffle if deck reached penetration point
        if len(self.deck) <= self.reshuffle_point:
            self.deck = Deck(n_decks=self.n_decks)
            self.deck.shuffle()

            # Reset counting system for new shoe
            self.player.reset()

        # Place bet
        bet = self.player.decide_bet()
        # Enforce table limits
        bet = max(self.table_min, min(bet, self.table_max))
        # Can't bet more than bankroll
        bet = min(bet, self.player.bankroll)
        # Reset for new round
        self.player.new_hand(bet)

        self.player.bankroll -= bet
        total_wagered_this_round += bet  # Count initial bet

        # Deal initial cards
        self.deal_initial_cards()

        # Check for dealer blackjack
        if self.dealer_hand.is_blackjack:
            if self.player.current_hand.is_blackjack:
                self.player.bankroll += self.player.current_hand.bet  # Push
                self.player.end_hand(GameResult.PUSH)
                return (0, 0, 1, 0, total_wagered_this_round)
            else:
                # Player loses (already deducted)
                self.player.end_hand(GameResult.DEALER_BLACKJACK)
                return (0, 1, 0, 0, total_wagered_this_round)

        # Check for player blackjack
        if self.player.current_hand.is_blackjack:
            bet = self.player.current_hand.bet
            winnings = bet + bet * self.blackjack_payout
            self.player.bankroll += winnings
            self.player.end_hand(GameResult.BLACKJACK)
            return (1, 0, 0, 0, total_wagered_this_round)

        # Player plays each hand
        while True:
            current_hand = self.player.current_hand
            # Play this hand
            while True:
                valid_actions = self.get_valid_actions(
                    hand=current_hand,
                    splits_made=splits_made,
                )
                action = self.player.decide_action(valid_actions=valid_actions)

                if action == "hit":
                    self.deal_card(current_hand)
                elif action == "stand":
                    break
                elif action == "double":
                    # Deduct additional bet amount
                    bet_amount = current_hand.bet
                    self.player.bankroll -= bet_amount

                    # Track the additional wager if tracker provided
                    total_wagered_this_round += bet_amount

                    # Double the bet for this hand
                    current_hand.bet += bet_amount

                    # Hit once
                    self.deal_card(current_hand)
                    break  # Can only hit once after double
                elif action == "split":
                    splits_made += 1
                    original_hand = self.player.current_hand
                    original_bet = original_hand.bet

                    # Deduct additional bet for second hand
                    self.player.bankroll -= original_bet

                    # Track the additional wager if tracker provided
                    total_wagered_this_round += original_bet

                    # Create two new hands (marked as from split)
                    hand1 = Hand(original_bet, is_from_split=True)
                    hand1.add_card(original_hand.cards[0])
                    self.deal_card(hand1)

                    hand2 = Hand(original_bet, is_from_split=True)
                    hand2.add_card(original_hand.cards[1])
                    self.deal_card(hand2)

                    # Replace original hand and add second hand
                    hand_idx = self.player.current_hand_idx
                    self.player.hands[hand_idx] = hand1
                    self.player.hands.append(hand2)

                    current_hand = self.player.current_hand
                elif action == "surrender":
                    # Player forfeits half the bet
                    current_hand.is_surrendered = True
                    refund = current_hand.bet / 2
                    self.player.bankroll += refund
                    self.player.end_hand(GameResult.SURRENDER)
                    break

                if current_hand.is_busted:
                    self.player.end_hand(GameResult.BUST)
                    break

            if not self.player.has_next_hand:
                break

            self.player.next_hand()

        # Dealer plays if any player hand is still alive
        has_live_hand = any(not h.is_busted for h in self.player.hands)

        if has_live_hand:
            self.dealer_play()

        # Resolve bets
        dealer_value = self.dealer_hand.value if not self.dealer_hand.is_busted else 0
        wins = 0
        losses = 0
        pushes = 0
        surrenders = 0

        # Count busted hands as losses, surrenders separately
        for hand in self.player.hands:
            if hand.is_surrendered:
                surrenders += 1
            elif hand.is_busted:
                losses += 1

        for hand in [
            h for h in self.player.hands if not h.is_busted and not h.is_surrendered
        ]:
            hand_bet = hand.bet

            if self.dealer_hand.is_busted:
                result = GameResult.DEALER_BUST
                self.player.bankroll += hand_bet * 2
                wins += 1
            elif hand.value > dealer_value:
                result = GameResult.WIN
                self.player.bankroll += hand_bet * 2
                wins += 1
            elif hand.value == dealer_value:
                result = GameResult.PUSH
                self.player.bankroll += hand_bet
                pushes += 1
            else:
                result = GameResult.LOSS
                losses += 1

            self.player.end_hand(result)

        return (wins, losses, pushes, surrenders, total_wagered_this_round)

    def play(self, max_rounds: Optional[int] = None) -> dict:
        """
        Play a full session until the player quits or runs out of money.

        Returns:
            Dictionary with session statistics
        """
        starting_bankroll = self.player.bankroll
        rounds_played = 0
        total_wagered = 0
        total_won = 0
        max_bankroll = starting_bankroll
        min_bankroll = starting_bankroll
        hands_played = 0
        hands_won = 0
        hands_lost = 0
        hands_pushed = 0
        hands_surrendered = 0

        while True:
            if max_rounds and rounds_played >= max_rounds:
                break

            initial_bankroll = self.player.bankroll

            # Play one round
            wins, losses, pushes, surrenders, round_wagered = self.play_round()
            self.player.end_round()
            rounds_played += 1
            hands_played += wins + losses + pushes + surrenders
            hands_won += wins
            hands_lost += losses
            hands_pushed += pushes
            hands_surrendered += surrenders

            # Track statistics
            current_bankroll = self.player.bankroll
            max_bankroll = max(max_bankroll, current_bankroll)
            min_bankroll = min(min_bankroll, current_bankroll)

            # Calculate wagered and won
            bankroll_change = self.player.bankroll - initial_bankroll
            total_wagered += round_wagered

            if bankroll_change > 0:
                total_won += bankroll_change

            if (
                not self.player.should_continue_playing()
                or self.player.bankroll < self.table_min
            ):
                break

        # Calculate max drawdown from peak
        max_drawdown = 0
        if max_bankroll > starting_bankroll:
            drawdown_amount = max_bankroll - self.player.bankroll
            max_drawdown = (
                (drawdown_amount / max_bankroll) * 100 if max_bankroll > 0 else 0
            )

        win_rate = (hands_won / hands_played * 100) if hands_played > 0 else 0

        return {
            "starting_bankroll": starting_bankroll,
            "final_bankroll": self.player.bankroll,
            "rounds_played": rounds_played,
            "total_wagered": total_wagered,
            "total_won": total_won,
            "profit": self.player.bankroll - starting_bankroll,
            "max_bankroll": max_bankroll,
            "min_bankroll": min_bankroll,
            "hands_won": hands_won,
            "hands_lost": hands_lost,
            "hands_pushed": hands_pushed,
            "hands_surrendered": hands_surrendered,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
        }
