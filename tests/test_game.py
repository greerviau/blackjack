"""Tests for the Blackjack game class - core game logic."""

from core.cards import Card, Deck
from core.game import Blackjack, GameResult
from core.hand import Hand
from core.player import Player


def make_card(rank: str, suit: str = "♠") -> Card:
    """Helper to create a card with correct value."""
    if rank in ["J", "Q", "K"]:
        value = 10
    elif rank == "A":
        value = 11
    else:
        value = int(rank)
    return Card(suit, rank, value)


class MockPlayer(Player):
    """A mock player for testing that allows controlling actions."""

    def __init__(self, bankroll: int = 1000):
        super().__init__(bankroll)
        self.bet_amount = 10
        self.actions_queue = []
        self.continue_playing = True

    def decide_bet(self) -> int:
        return self.bet_amount

    def decide_action(self, valid_actions: list[str]) -> str:
        if self.actions_queue:
            action = self.actions_queue.pop(0)
            if action in valid_actions:
                return action
        return "stand"

    def should_continue_playing(self) -> bool:
        return self.continue_playing

    def end_hand(self, result: GameResult) -> None:
        pass

    def end_round(self, **kwargs) -> None:
        pass


class ControlledDeck(Deck):
    """A deck that deals cards in a specified order for testing."""

    def __init__(self, card_sequence: list[Card]):
        self.n_decks = 1
        self.cards = list(reversed(card_sequence))  # Reverse so pop() gives first card
        self._total_cards = 52 * 8  # Pretend we have a full 8-deck shoe

    def __len__(self) -> int:
        # Return a large number to prevent reshuffle triggering
        return self._total_cards

    def draw(self) -> Card:
        self._total_cards -= 1
        return self.cards.pop()

    def shuffle(self):
        pass  # Don't shuffle - we want controlled order


class TestGameInitialization:
    """Tests for game initialization."""

    def test_default_settings(self):
        """Test default game settings."""
        player = MockPlayer()
        game = Blackjack(player)
        assert game.n_decks == 8
        assert game.table_min == 10
        assert game.table_max == 1000
        assert game.blackjack_payout == 1.5
        assert game.penetration == 0.75
        assert game.h17 is True
        assert game.max_splits == 3

    def test_custom_settings(self):
        """Test custom game settings."""
        player = MockPlayer()
        game = Blackjack(
            player,
            n_decks=6,
            table_min=25,
            table_max=500,
            blackjack_payout=1.2,
            penetration=0.80,
            h17=False,
            max_splits=4,
        )
        assert game.n_decks == 6
        assert game.table_min == 25
        assert game.table_max == 500
        assert game.blackjack_payout == 1.2
        assert game.h17 is False
        assert game.max_splits == 4


class TestDealing:
    """Tests for card dealing."""

    def test_deal_initial_cards(self):
        """Test that initial dealing gives 2 cards to player and dealer."""
        player = MockPlayer()
        game = Blackjack(player)

        # Set up controlled deck
        cards = [
            make_card("5"),  # Player card 1
            make_card("6"),  # Dealer card 1
            make_card("7"),  # Player card 2
            make_card("8"),  # Dealer card 2
        ]
        game.deck = ControlledDeck(cards)
        player.new_hand(10)
        game.dealer_hand = Hand(0)

        game.deal_initial_cards()

        assert len(player.current_hand) == 2
        assert len(game.dealer_hand) == 2

    def test_dealer_up_card(self):
        """Test dealer's up card is accessible."""
        player = MockPlayer()
        game = Blackjack(player)

        cards = [
            make_card("5"),  # Player card 1
            make_card("K"),  # Dealer card 1 (up card)
            make_card("7"),  # Player card 2
            make_card("8"),  # Dealer card 2 (hole card)
        ]
        game.deck = ControlledDeck(cards)
        player.new_hand(10)
        game.dealer_hand = Hand(0)

        game.deal_initial_cards()

        assert game.dealer_up_card.rank == "K"


class TestValidActions:
    """Tests for valid action determination."""

    def test_hit_and_stand_always_available(self):
        """Test hit and stand are always available."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("5"))
        hand.add_card(make_card("6"))

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "hit" in actions
        assert "stand" in actions

    def test_double_available_on_initial_hand(self):
        """Test double is available on initial 2-card hand with sufficient bankroll."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("5"))
        hand.add_card(make_card("6"))

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "double" in actions

    def test_double_not_available_with_three_cards(self):
        """Test double is NOT available after hitting."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("5"))
        hand.add_card(make_card("6"))
        hand.add_card(make_card("2"))  # Third card

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "double" not in actions

    def test_double_not_available_without_bankroll(self):
        """Test double requires sufficient bankroll."""
        player = MockPlayer(bankroll=5)  # Less than bet
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("5"))
        hand.add_card(make_card("6"))

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "double" not in actions

    def test_split_available_on_pair(self):
        """Test split is available on pairs with sufficient bankroll."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("8", "♠"))
        hand.add_card(make_card("8", "♥"))

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "split" in actions

    def test_split_not_available_on_non_pair(self):
        """Test split is NOT available on non-pairs."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("8"))
        hand.add_card(make_card("9"))

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "split" not in actions

    def test_split_not_available_when_max_splits_reached(self):
        """Test split is NOT available when max splits reached."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, max_splits=3)

        hand = Hand(10)
        hand.add_card(make_card("8", "♠"))
        hand.add_card(make_card("8", "♥"))

        actions = game.get_valid_actions(hand, splits_made=3)
        assert "split" not in actions

    def test_split_not_available_without_bankroll(self):
        """Test split requires sufficient bankroll."""
        player = MockPlayer(bankroll=5)  # Less than bet
        game = Blackjack(player)

        hand = Hand(10)
        hand.add_card(make_card("8", "♠"))
        hand.add_card(make_card("8", "♥"))

        actions = game.get_valid_actions(hand, splits_made=0)
        assert "split" not in actions


class TestDealerPlay:
    """Tests for dealer play logic."""

    def test_dealer_hits_on_16(self):
        """Test dealer hits on 16."""
        player = MockPlayer()
        game = Blackjack(player)

        # Dealer has 16, should hit
        game.dealer_hand = Hand(0)
        game.dealer_hand.add_card(make_card("10"))
        game.dealer_hand.add_card(make_card("6"))

        # Next card will be drawn
        game.deck = ControlledDeck([make_card("2")])

        game.dealer_play()
        assert game.dealer_hand.value == 18  # 16 + 2

    def test_dealer_stands_on_hard_17(self):
        """Test dealer stands on hard 17."""
        player = MockPlayer()
        game = Blackjack(player, h17=True)

        game.dealer_hand = Hand(0)
        game.dealer_hand.add_card(make_card("10"))
        game.dealer_hand.add_card(make_card("7"))

        initial_value = game.dealer_hand.value
        game.dealer_play()
        assert game.dealer_hand.value == initial_value  # No change

    def test_dealer_hits_on_soft_17_when_configured(self):
        """Test dealer hits on soft 17 when h17 is True."""
        player = MockPlayer()
        game = Blackjack(player, h17=True)

        game.dealer_hand = Hand(0)
        game.dealer_hand.add_card(make_card("A"))
        game.dealer_hand.add_card(make_card("6"))

        assert game.dealer_hand.value == 17
        assert game.dealer_hand.is_soft is True

        game.deck = ControlledDeck([make_card("3")])
        game.dealer_play()

        # Dealer should have hit: A + 6 + 3 = 20
        assert game.dealer_hand.value == 20

    def test_dealer_stands_on_soft_17_when_configured(self):
        """Test dealer stands on soft 17 when h17 is False."""
        player = MockPlayer()
        game = Blackjack(player, h17=False)

        game.dealer_hand = Hand(0)
        game.dealer_hand.add_card(make_card("A"))
        game.dealer_hand.add_card(make_card("6"))

        initial_len = len(game.dealer_hand)
        game.dealer_play()
        assert len(game.dealer_hand) == initial_len  # No new cards

    def test_dealer_stands_on_18(self):
        """Test dealer stands on 18."""
        player = MockPlayer()
        game = Blackjack(player)

        game.dealer_hand = Hand(0)
        game.dealer_hand.add_card(make_card("10"))
        game.dealer_hand.add_card(make_card("8"))

        initial_len = len(game.dealer_hand)
        game.dealer_play()
        assert len(game.dealer_hand) == initial_len

    def test_dealer_busts(self):
        """Test dealer can bust."""
        player = MockPlayer()
        game = Blackjack(player)

        game.dealer_hand = Hand(0)
        game.dealer_hand.add_card(make_card("10"))
        game.dealer_hand.add_card(make_card("6"))  # 16

        game.deck = ControlledDeck([make_card("K")])  # Will bust to 26
        game.dealer_play()

        assert game.dealer_hand.value == 26
        assert game.dealer_hand.is_busted is True


class TestBlackjackDetection:
    """Tests for blackjack handling in game flow."""

    def test_player_blackjack_pays_correctly(self):
        """Test player blackjack pays 3:2 (1.5x)."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        game = Blackjack(player, blackjack_payout=1.5)

        # Player gets blackjack, dealer doesn't
        cards = [
            make_card("A"),  # Player
            make_card("5"),  # Dealer
            make_card("K"),  # Player (blackjack!)
            make_card("6"),  # Dealer
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, surrenders, wagered = game.play_round()

        # Player should win 1.5x their bet
        expected_winnings = 100 + int(100 * 1.5)  # bet + payout
        assert player.bankroll == initial_bankroll - 100 + expected_winnings
        assert wins == 1
        assert losses == 0

    def test_player_blackjack_pays_6_5(self):
        """Test player blackjack pays 6:5 (1.2x)."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        game = Blackjack(player, blackjack_payout=1.2)

        cards = [
            make_card("A"),  # Player
            make_card("5"),  # Dealer
            make_card("K"),  # Player (blackjack!)
            make_card("6"),  # Dealer
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        game.play_round()

        expected_winnings = 100 + int(100 * 1.2)
        assert player.bankroll == initial_bankroll - 100 + expected_winnings

    def test_dealer_blackjack_player_loses(self):
        """Test dealer blackjack beats player non-blackjack."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        game = Blackjack(player)

        cards = [
            make_card("10"),  # Player
            make_card("A"),  # Dealer
            make_card("9"),  # Player (19)
            make_card("K"),  # Dealer (blackjack!)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll - 100  # Lost the bet
        assert losses == 1
        assert wins == 0

    def test_both_blackjack_is_push(self):
        """Test both player and dealer blackjack is a push."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        game = Blackjack(player)

        cards = [
            make_card("A"),  # Player
            make_card("A"),  # Dealer
            make_card("K"),  # Player (blackjack!)
            make_card("K"),  # Dealer (blackjack!)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll  # No change
        assert pushes == 1
        assert wins == 0
        assert losses == 0


class TestHandResolution:
    """Tests for hand outcome resolution."""

    def test_player_wins_with_higher_value(self):
        """Test player wins with higher value than dealer."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["stand"]
        game = Blackjack(player)

        # Player: 20, Dealer: 17
        cards = [
            make_card("K"),  # Player
            make_card("10"),  # Dealer
            make_card("Q"),  # Player (20)
            make_card("7"),  # Dealer (17)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll + 100  # Won the bet
        assert wins == 1

    def test_player_loses_with_lower_value(self):
        """Test player loses with lower value than dealer."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["stand"]
        game = Blackjack(player)

        # Player: 17, Dealer: 19
        cards = [
            make_card("10"),  # Player
            make_card("10"),  # Dealer
            make_card("7"),  # Player (17)
            make_card("9"),  # Dealer (19)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll - 100  # Lost the bet
        assert losses == 1

    def test_push_returns_bet(self):
        """Test push returns original bet."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["stand"]
        game = Blackjack(player)

        # Player: 18, Dealer: 18
        cards = [
            make_card("10"),  # Player
            make_card("10"),  # Dealer
            make_card("8"),  # Player (18)
            make_card("8"),  # Dealer (18)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll  # No change
        assert pushes == 1

    def test_dealer_bust_player_wins(self):
        """Test player wins when dealer busts."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["stand"]
        game = Blackjack(player)

        # Player: 15 (stands), Dealer: 16 then busts
        cards = [
            make_card("10"),  # Player
            make_card("10"),  # Dealer
            make_card("5"),  # Player (15)
            make_card("6"),  # Dealer (16)
            make_card("K"),  # Dealer draws and busts (26)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll + 100
        assert wins == 1

    def test_player_bust_loses(self):
        """Test player loses when they bust."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["hit"]  # Will bust
        game = Blackjack(player)

        # Player: 15, hits and busts
        cards = [
            make_card("10"),  # Player
            make_card("10"),  # Dealer
            make_card("5"),  # Player (15)
            make_card("6"),  # Dealer (16)
            make_card("K"),  # Player hits and busts (25)
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        assert player.bankroll == initial_bankroll - 100
        assert losses == 1  # Bust is counted as a loss


class TestDoubleDown:
    """Tests for double down action."""

    def test_double_doubles_bet(self):
        """Test double down doubles the bet and draws one card."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["double"]
        game = Blackjack(player)

        # Player: 11, doubles, gets 10 = 21
        cards = [
            make_card("5"),  # Player
            make_card("7"),  # Dealer
            make_card("6"),  # Player (11)
            make_card("10"),  # Dealer (17)
            make_card("10"),  # Player doubles and gets 21
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, surrenders, wagered = game.play_round()

        # Player wagered 200 (100 + 100 double) and won
        assert wagered == 200
        assert player.bankroll == initial_bankroll + 200  # Won 2x bet
        assert wins == 1

    def test_double_only_one_card(self):
        """Test double down only draws one card then stands."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["double", "hit"]  # Hit should be ignored
        game = Blackjack(player)

        # Player: 11
        cards = [
            make_card("5"),  # Player
            make_card("7"),  # Dealer
            make_card("6"),  # Player (11)
            make_card("10"),  # Dealer (17)
            make_card("2"),  # Player doubles (13)
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        # Player should have exactly 3 cards (2 initial + 1 from double)
        assert len(player.hands[0]) == 3


class TestSplit:
    """Tests for split action."""

    def test_split_creates_two_hands(self):
        """Test split creates two separate hands."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["split", "stand", "stand"]
        game = Blackjack(player)

        # Player: pair of 8s
        cards = [
            make_card("8", "♠"),  # Player
            make_card("7"),  # Dealer
            make_card("8", "♥"),  # Player (pair)
            make_card("10"),  # Dealer (17)
            make_card("3"),  # First split hand gets card
            make_card("2"),  # Second split hand gets card
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        assert len(player.hands) == 2

    def test_split_doubles_wager(self):
        """Test split requires additional bet equal to original."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["split", "stand", "stand"]
        game = Blackjack(player)

        cards = [
            make_card("8", "♠"),
            make_card("7"),
            make_card("8", "♥"),
            make_card("10"),
            make_card("10"),  # First hand: 8+10=18
            make_card("10"),  # Second hand: 8+10=18
        ]
        game.deck = ControlledDeck(cards)

        wins, losses, pushes, surrenders, wagered = game.play_round()

        assert wagered == 200  # Original 100 + 100 for split

    def test_split_each_hand_resolved_independently(self):
        """Test each split hand is resolved independently."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["split", "stand", "stand"]
        game = Blackjack(player)

        # First hand wins (19 vs 17), second hand loses (15 vs 17)
        cards = [
            make_card("8", "♠"),  # Player
            make_card("10"),  # Dealer
            make_card("8", "♥"),  # Player (pair)
            make_card("7"),  # Dealer (17)
            make_card("A"),  # First hand: 8+A=19
            make_card("7"),  # Second hand: 8+7=15
        ]
        game.deck = ControlledDeck(cards)

        initial_bankroll = player.bankroll
        wins, losses, pushes, _, _ = game.play_round()

        # Win one (100 + 100), lose one (-100): net +100
        assert wins == 1
        assert losses == 1
        assert player.bankroll == initial_bankroll  # +100 - 100 = 0


class TestBettingLimits:
    """Tests for table betting limits."""

    def test_bet_enforces_table_minimum(self):
        """Test bet is raised to table minimum if too low."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 5  # Below minimum
        player.actions_queue = ["stand"]
        game = Blackjack(player, table_min=10)

        cards = [
            make_card("K"),
            make_card("K"),
            make_card("K"),
            make_card("7"),
        ]
        game.deck = ControlledDeck(cards)

        _, _, _, _, wagered = game.play_round()

        assert wagered == 10  # Enforced to minimum

    def test_bet_enforces_table_maximum(self):
        """Test bet is capped to table maximum if too high."""
        player = MockPlayer(bankroll=10000)
        player.bet_amount = 5000  # Above maximum
        player.actions_queue = ["stand"]
        game = Blackjack(player, table_max=1000)

        cards = [
            make_card("K"),
            make_card("K"),
            make_card("K"),
            make_card("7"),
        ]
        game.deck = ControlledDeck(cards)

        _, _, _, _, wagered = game.play_round()

        assert wagered == 1000  # Capped to maximum

    def test_bet_limited_by_bankroll(self):
        """Test bet is limited by available bankroll."""
        player = MockPlayer(bankroll=50)
        player.bet_amount = 100  # More than bankroll
        player.actions_queue = ["stand"]
        game = Blackjack(player, table_min=10, table_max=1000)

        cards = [
            make_card("K"),
            make_card("K"),
            make_card("K"),
            make_card("7"),
        ]
        game.deck = ControlledDeck(cards)

        _, _, _, _, wagered = game.play_round()

        assert wagered == 50  # Limited by bankroll


class TestDeckPenetration:
    """Tests for deck penetration and reshuffling."""

    def test_reshuffle_at_penetration_point(self):
        """Test deck reshuffles when penetration point is reached."""
        player = MockPlayer(bankroll=1000)
        player.actions_queue = ["stand"]
        game = Blackjack(player, n_decks=1, penetration=0.75)

        # 1 deck = 52 cards, 75% penetration = reshuffle at 13 cards remaining
        # Draw cards until we're below threshold
        while len(game.deck) > 13:
            game.deck.draw()

        # Force a round to trigger reshuffle check
        initial_deck_size = len(game.deck)
        game.play_round()

        # Deck should have been reshuffled (will be close to 52 minus cards dealt)
        assert len(game.deck) > initial_deck_size


class TestHitAction:
    """Tests for hit action."""

    def test_hit_adds_card(self):
        """Test hit adds a card to hand."""
        player = MockPlayer(bankroll=1000)
        player.actions_queue = ["hit", "stand"]
        game = Blackjack(player)

        cards = [
            make_card("5"),  # Player
            make_card("7"),  # Dealer
            make_card("6"),  # Player (11)
            make_card("10"),  # Dealer (17)
            make_card("3"),  # Player hits (14)
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        assert len(player.hands[0]) == 3  # 2 initial + 1 hit

    def test_multiple_hits(self):
        """Test multiple hits in a row."""
        player = MockPlayer(bankroll=1000)
        player.actions_queue = ["hit", "hit", "stand"]
        game = Blackjack(player)

        cards = [
            make_card("2"),  # Player
            make_card("7"),  # Dealer
            make_card("3"),  # Player (5)
            make_card("10"),  # Dealer (17)
            make_card("2"),  # Player hits (7)
            make_card("2"),  # Player hits (9)
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        assert len(player.hands[0]) == 4  # 2 initial + 2 hits


class TestSplitAces:
    """Tests for split aces rules (hit_split_aces and resplit_aces)."""

    def test_split_aces_no_hit_by_default(self):
        """Test that split aces cannot be hit by default (hit_split_aces=False)."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["split", "hit", "hit"]  # Hits should be ignored
        game = Blackjack(player, hit_split_aces=False)

        cards = [
            make_card("A", "♠"),  # Player
            make_card("7"),  # Dealer
            make_card("A", "♥"),  # Player (pair of aces)
            make_card("10"),  # Dealer (17)
            make_card("5"),  # First ace gets one card (16)
            make_card("6"),  # Second ace gets one card (17)
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        # Each split hand should have exactly 2 cards (ace + dealt card)
        assert len(player.hands[0]) == 2
        assert len(player.hands[1]) == 2

    def test_split_aces_only_stand_available(self):
        """Test that only stand is available after splitting aces when hit_split_aces=False."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, hit_split_aces=False)

        # Create a hand that looks like it came from splitting aces
        hand = Hand(100, is_from_split=True)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("5"))

        actions = game.get_valid_actions(hand, splits_made=1)

        assert actions == ["stand"]
        assert "hit" not in actions
        assert "double" not in actions

    def test_split_aces_can_hit_when_allowed(self):
        """Test that split aces can be hit when hit_split_aces=True."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["split", "hit", "stand", "stand"]
        game = Blackjack(player, hit_split_aces=True)

        cards = [
            make_card("A", "♠"),  # Player
            make_card("7"),  # Dealer
            make_card("A", "♥"),  # Player (pair of aces)
            make_card("10"),  # Dealer (17)
            make_card("2"),  # First ace gets card (13)
            make_card("6"),  # Second ace gets card (17)
            make_card("5"),  # First hand hits (18)
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        # First hand should have 3 cards (ace + dealt + hit)
        assert len(player.hands[0]) == 3
        # Second hand should have 2 cards
        assert len(player.hands[1]) == 2

    def test_split_aces_hit_and_double_available_when_allowed(self):
        """Test hit and double are available for split aces when hit_split_aces=True."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, hit_split_aces=True, das=True)

        hand = Hand(100, is_from_split=True)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("5"))

        actions = game.get_valid_actions(hand, splits_made=1)

        assert "hit" in actions
        assert "stand" in actions
        assert "double" in actions

    def test_resplit_aces_allowed_by_default(self):
        """Test that aces can be resplit when resplit_aces=True (default)."""
        player = MockPlayer(bankroll=1000)
        player.bet_amount = 100
        player.actions_queue = ["split", "split", "stand", "stand", "stand"]
        game = Blackjack(player, resplit_aces=True, max_splits=3)

        cards = [
            make_card("A", "♠"),  # Player
            make_card("7"),  # Dealer
            make_card("A", "♥"),  # Player (pair of aces)
            make_card("10"),  # Dealer (17)
            make_card("A", "♦"),  # First ace gets another ace - can resplit
            make_card("6"),  # Second ace gets card
            make_card("10"),  # First re-split ace gets card
            make_card("9"),  # Second re-split ace gets card
        ]
        game.deck = ControlledDeck(cards)

        game.play_round()

        # Should have 3 hands after resplitting
        assert len(player.hands) == 3

    def test_resplit_aces_not_allowed_when_disabled(self):
        """Test that aces cannot be resplit when resplit_aces=False."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, resplit_aces=False)

        # Hand from a split with pair of aces
        hand = Hand(100, is_from_split=True)
        hand.add_card(make_card("A", "♠"))
        hand.add_card(make_card("A", "♥"))

        actions = game.get_valid_actions(hand, splits_made=1)

        assert "split" not in actions

    def test_resplit_aces_available_in_valid_actions(self):
        """Test split is available for ace pair from split when resplit_aces=True."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, resplit_aces=True, max_splits=3)

        hand = Hand(100, is_from_split=True)
        hand.add_card(make_card("A", "♠"))
        hand.add_card(make_card("A", "♥"))

        actions = game.get_valid_actions(hand, splits_made=1)

        assert "split" in actions

    def test_resplit_aces_respects_max_splits(self):
        """Test resplitting aces still respects max_splits limit."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, resplit_aces=True, max_splits=2)

        hand = Hand(100, is_from_split=True)
        hand.add_card(make_card("A", "♠"))
        hand.add_card(make_card("A", "♥"))

        # Already at max splits
        actions = game.get_valid_actions(hand, splits_made=2)

        assert "split" not in actions

    def test_non_ace_pair_from_split_can_still_split(self):
        """Test non-ace pairs from splits can still be split (resplit_aces doesn't affect them)."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, resplit_aces=False, max_splits=3)

        # 8s from a split - should still be splittable
        hand = Hand(100, is_from_split=True)
        hand.add_card(make_card("8", "♠"))
        hand.add_card(make_card("8", "♥"))

        actions = game.get_valid_actions(hand, splits_made=1)

        assert "split" in actions

    def test_initial_ace_pair_can_always_split(self):
        """Test initial (non-split) ace pair can always be split regardless of resplit_aces."""
        player = MockPlayer(bankroll=1000)
        game = Blackjack(player, resplit_aces=False, max_splits=3)

        # Initial hand (not from split) with aces
        hand = Hand(100, is_from_split=False)
        hand.add_card(make_card("A", "♠"))
        hand.add_card(make_card("A", "♥"))

        actions = game.get_valid_actions(hand, splits_made=0)

        assert "split" in actions
