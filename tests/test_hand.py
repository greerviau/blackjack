"""Tests for Hand class - the core hand value calculation logic."""

from core.cards import Card
from core.hand import Hand


def make_card(rank: str, suit: str = "♠") -> Card:
    """Helper to create a card with correct value."""
    if rank in ["J", "Q", "K"]:
        value = 10
    elif rank == "A":
        value = 11
    else:
        value = int(rank)
    return Card(suit, rank, value)


class TestHandValue:
    """Tests for hand value calculation."""

    def test_simple_hand_value(self):
        """Test basic hand value calculation."""
        hand = Hand(bet=10)
        hand.add_card(make_card("5"))
        hand.add_card(make_card("7"))
        assert hand.value == 12

    def test_face_cards_value(self):
        """Test that face cards are worth 10."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        assert hand.value == 20

    def test_ace_as_eleven(self):
        """Test Ace counted as 11 when it doesn't bust."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("6"))
        assert hand.value == 17

    def test_ace_converts_to_one(self):
        """Test Ace converts from 11 to 1 to avoid bust."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("5"))  # 16
        hand.add_card(make_card("K"))  # Would be 26, Ace converts to 1 = 16
        assert hand.value == 16

    def test_multiple_aces_convert(self):
        """Test multiple Aces convert as needed."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("A"))  # 22 -> 12 (one ace converts)
        assert hand.value == 12

    def test_three_aces(self):
        """Test three Aces (would be 33, converts to 13)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("A"))  # 22 -> 12
        hand.add_card(make_card("A"))  # 23 -> 13
        assert hand.value == 13

    def test_four_aces(self):
        """Test four Aces (would be 44, converts to 14)."""
        hand = Hand(bet=10)
        for _ in range(4):
            hand.add_card(make_card("A"))
        assert hand.value == 14

    def test_ace_and_ten_equals_21(self):
        """Test Ace + 10 = 21."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("10"))
        assert hand.value == 21

    def test_complex_hand_with_ace(self):
        """Test complex hand: A + 5 + 5 = 21 (Ace as 11)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("5"))
        hand.add_card(make_card("5"))
        assert hand.value == 21

    def test_complex_hand_ace_converts(self):
        """Test A + 5 + K = 16 (Ace converts to 1)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("5"))
        hand.add_card(make_card("K"))
        assert hand.value == 16

    def test_hand_exactly_21(self):
        """Test various ways to reach exactly 21."""
        # 7 + 7 + 7 = 21
        hand1 = Hand(bet=10)
        for _ in range(3):
            hand1.add_card(make_card("7"))
        assert hand1.value == 21

        # 5 + 6 + K = 21
        hand2 = Hand(bet=10)
        hand2.add_card(make_card("5"))
        hand2.add_card(make_card("6"))
        hand2.add_card(make_card("K"))
        assert hand2.value == 21

    def test_bust_value(self):
        """Test busted hand value is still calculated correctly."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        hand.add_card(make_card("5"))
        assert hand.value == 25


class TestBlackjack:
    """Tests for blackjack detection."""

    def test_ace_and_ten_is_blackjack(self):
        """Test A + 10 is blackjack."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("10"))
        assert hand.is_blackjack is True

    def test_ace_and_jack_is_blackjack(self):
        """Test A + J is blackjack."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("J"))
        assert hand.is_blackjack is True

    def test_ace_and_queen_is_blackjack(self):
        """Test A + Q is blackjack."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("Q"))
        assert hand.is_blackjack is True

    def test_ace_and_king_is_blackjack(self):
        """Test A + K is blackjack."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("K"))
        assert hand.is_blackjack is True

    def test_order_doesnt_matter(self):
        """Test blackjack detection works regardless of card order."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("A"))
        assert hand.is_blackjack is True

    def test_three_cards_totaling_21_not_blackjack(self):
        """Test that 21 with 3+ cards is NOT blackjack."""
        hand = Hand(bet=10)
        hand.add_card(make_card("7"))
        hand.add_card(make_card("7"))
        hand.add_card(make_card("7"))
        assert hand.value == 21
        assert hand.is_blackjack is False

    def test_ace_ace_nine_not_blackjack(self):
        """Test A + A + 9 = 21 is NOT blackjack (3 cards)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("A"))  # Now 12
        hand.add_card(make_card("9"))  # Now 21
        assert hand.value == 21
        assert hand.is_blackjack is False

    def test_two_face_cards_not_blackjack(self):
        """Test K + Q = 20 is not blackjack."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        assert hand.value == 20
        assert hand.is_blackjack is False


class TestBust:
    """Tests for bust detection."""

    def test_under_21_not_busted(self):
        """Test hands under 21 are not busted."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        assert hand.value == 20
        assert hand.is_busted is False

    def test_exactly_21_not_busted(self):
        """Test hands at exactly 21 are not busted."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("K"))
        assert hand.value == 21
        assert hand.is_busted is False

    def test_over_21_is_busted(self):
        """Test hands over 21 are busted."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        hand.add_card(make_card("5"))
        assert hand.value == 25
        assert hand.is_busted is True

    def test_22_is_busted(self):
        """Test 22 is busted."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("6"))
        hand.add_card(make_card("6"))
        assert hand.value == 22
        assert hand.is_busted is True

    def test_ace_conversion_prevents_bust(self):
        """Test that Ace conversion can prevent bust."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("8"))  # 19
        hand.add_card(make_card("5"))  # Would be 24, Ace -> 1, so 14
        assert hand.value == 14
        assert hand.is_busted is False

    def test_multiple_tens_bust(self):
        """Test three 10-value cards bust."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        hand.add_card(make_card("J"))
        assert hand.value == 30
        assert hand.is_busted is True


class TestPair:
    """Tests for pair detection."""

    def test_same_rank_is_pair(self):
        """Test same rank cards are a pair."""
        hand = Hand(bet=10)
        hand.add_card(make_card("8", "♠"))
        hand.add_card(make_card("8", "♥"))
        assert hand.is_pair is True

    def test_different_ranks_not_pair(self):
        """Test different rank cards are not a pair."""
        hand = Hand(bet=10)
        hand.add_card(make_card("8"))
        hand.add_card(make_card("9"))
        assert hand.is_pair is False

    def test_same_value_different_rank_not_pair(self):
        """Test K and Q are NOT a pair (same value, different rank)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("Q"))
        assert hand.is_pair is False

    def test_ace_pair(self):
        """Test two Aces are a pair."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A", "♠"))
        hand.add_card(make_card("A", "♥"))
        assert hand.is_pair is True

    def test_three_cards_not_pair(self):
        """Test three cards even with matching ranks is not a pair."""
        hand = Hand(bet=10)
        hand.add_card(make_card("8"))
        hand.add_card(make_card("8"))
        hand.add_card(make_card("8"))
        assert hand.is_pair is False

    def test_tens_are_pair(self):
        """Test two 10s are a pair."""
        hand = Hand(bet=10)
        hand.add_card(make_card("10", "♠"))
        hand.add_card(make_card("10", "♥"))
        assert hand.is_pair is True


class TestSoftHand:
    """Tests for soft hand detection."""

    def test_ace_with_low_card_is_soft(self):
        """Test Ace + small card is soft."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("6"))
        assert hand.is_soft is True
        assert hand.value == 17

    def test_ace_ten_is_soft(self):
        """Test blackjack (A + 10) is soft."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("K"))
        assert hand.is_soft is True
        assert hand.value == 21

    def test_no_ace_is_hard(self):
        """Test hand without Ace is hard."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        hand.add_card(make_card("7"))
        assert hand.is_soft is False

    def test_ace_converted_is_hard(self):
        """Test hand where Ace converted to 1 is hard."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("5"))  # 16
        hand.add_card(make_card("K"))  # Would bust, Ace -> 1, so 16
        assert hand.value == 16
        assert hand.is_soft is False

    def test_two_aces_one_converted(self):
        """Test A + A = 12 is soft (one Ace still counts as 11)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("A"))
        # Value is 12 (one ace as 11, one as 1)
        assert hand.value == 12
        assert hand.is_soft is True

    def test_soft_17(self):
        """Test soft 17 detection (important for dealer play)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("6"))
        assert hand.value == 17
        assert hand.is_soft is True

    def test_hard_17(self):
        """Test hard 17 detection."""
        hand = Hand(bet=10)
        hand.add_card(make_card("10"))
        hand.add_card(make_card("7"))
        assert hand.value == 17
        assert hand.is_soft is False

    def test_soft_18(self):
        """Test soft 18 (A + 7)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))
        hand.add_card(make_card("7"))
        assert hand.value == 18
        assert hand.is_soft is True

    def test_ace_converts_becomes_hard(self):
        """Test A + 7 + 5 = 13 (Ace converts, becomes hard)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("7"))  # 18 (soft)
        hand.add_card(make_card("5"))  # 23 -> 13 (Ace converts)
        assert hand.value == 13
        assert hand.is_soft is False

    def test_three_cards_still_soft(self):
        """Test A + 2 + 3 = 16 (Still soft with 3 cards)."""
        hand = Hand(bet=10)
        hand.add_card(make_card("A"))  # 11
        hand.add_card(make_card("2"))  # 13 (soft)
        hand.add_card(make_card("3"))  # 16 (soft)
        assert hand.value == 16
        assert hand.is_soft is True


class TestHandBet:
    """Tests for hand bet tracking."""

    def test_initial_bet(self):
        """Test initial bet is set correctly."""
        hand = Hand(bet=25)
        assert hand.bet == 25

    def test_bet_can_be_modified(self):
        """Test bet can be modified (for doubling)."""
        hand = Hand(bet=25)
        hand.bet += 25
        assert hand.bet == 50


class TestHandLength:
    """Tests for hand length tracking."""

    def test_empty_hand(self):
        """Test empty hand has length 0."""
        hand = Hand(bet=10)
        assert len(hand) == 0

    def test_hand_length_after_adding_cards(self):
        """Test hand length increases with cards."""
        hand = Hand(bet=10)
        hand.add_card(make_card("K"))
        assert len(hand) == 1
        hand.add_card(make_card("Q"))
        assert len(hand) == 2
        hand.add_card(make_card("5"))
        assert len(hand) == 3


class TestHandRepr:
    """Tests for hand string representation."""

    def test_hand_repr(self):
        """Test hand string representation."""
        hand = Hand(bet=10)
        hand.add_card(Card("♠", "A", 11))
        hand.add_card(Card("♥", "K", 10))
        assert repr(hand) == "[A♠][K♥]"
