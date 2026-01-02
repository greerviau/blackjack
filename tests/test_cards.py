"""Tests for Card and Deck classes."""

import pytest

from core.cards import RANK_POINTS, SUITS, Card, Deck


class TestCard:
    """Tests for the Card class."""

    def test_card_creation(self):
        """Test that a card is created with correct attributes."""
        card = Card("♠", "A", 11)
        assert card.suit == "♠"
        assert card.rank == "A"
        assert card.value == 11

    def test_card_repr(self):
        """Test card string representation."""
        card = Card("♥", "K", 10)
        assert repr(card) == "[K♥]"

    def test_number_card_values(self):
        """Test that number cards have correct values."""
        for rank, value in [
            ("2", 2),
            ("3", 3),
            ("4", 4),
            ("5", 5),
            ("6", 6),
            ("7", 7),
            ("8", 8),
            ("9", 9),
            ("10", 10),
        ]:
            card = Card("♠", rank, value)
            assert card.value == int(rank) if rank != "10" else 10

    def test_face_card_values(self):
        """Test that face cards are worth 10."""
        for rank in ["J", "Q", "K"]:
            card = Card("♠", rank, 10)
            assert card.value == 10

    def test_ace_initial_value(self):
        """Test that Ace is initially worth 11."""
        card = Card("♠", "A", 11)
        assert card.value == 11


class TestDeck:
    """Tests for the Deck class."""

    def test_single_deck_size(self):
        """Test that a single deck has 52 cards."""
        deck = Deck(n_decks=1)
        assert len(deck) == 52

    def test_multi_deck_size(self):
        """Test that multiple decks have correct number of cards."""
        for n in [2, 4, 6, 8]:
            deck = Deck(n_decks=n)
            assert len(deck) == 52 * n

    def test_deck_contains_all_suits(self):
        """Test that deck contains all four suits."""
        deck = Deck(n_decks=1)
        suits_found = set(card.suit for card in deck.cards)
        assert suits_found == set(SUITS)

    def test_deck_contains_all_ranks(self):
        """Test that deck contains all ranks."""
        deck = Deck(n_decks=1)
        ranks_found = set(card.rank for card in deck.cards)
        expected_ranks = set(rp[0] for rp in RANK_POINTS)
        assert ranks_found == expected_ranks

    def test_draw_removes_card(self):
        """Test that drawing a card removes it from the deck."""
        deck = Deck(n_decks=1)
        initial_size = len(deck)
        card = deck.draw()
        assert len(deck) == initial_size - 1
        assert isinstance(card, Card)

    def test_draw_all_cards(self):
        """Test that all cards can be drawn from deck."""
        deck = Deck(n_decks=1)
        cards_drawn = []
        while len(deck) > 0:
            cards_drawn.append(deck.draw())
        assert len(cards_drawn) == 52
        assert len(deck) == 0

    def test_shuffle_changes_order(self):
        """Test that shuffling changes the order of cards."""
        deck1 = Deck(n_decks=1)
        deck2 = Deck(n_decks=1)

        # Get initial order
        initial_order = [repr(c) for c in deck1.cards]

        # Shuffle one deck
        deck1.shuffle()
        shuffled_order = [repr(c) for c in deck1.cards]

        # Order should be different (statistically almost certain)
        # Note: There's an infinitesimally small chance this could fail
        assert initial_order != shuffled_order

    def test_deck_has_correct_card_distribution(self):
        """Test that deck has exactly 4 of each rank per deck."""
        deck = Deck(n_decks=1)
        rank_counts = {}
        for card in deck.cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        for rank in [rp[0] for rp in RANK_POINTS]:
            assert rank_counts[rank] == 4

    def test_multi_deck_card_distribution(self):
        """Test that multi-deck has correct distribution."""
        n_decks = 6
        deck = Deck(n_decks=n_decks)
        rank_counts = {}
        for card in deck.cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1

        for rank in [rp[0] for rp in RANK_POINTS]:
            assert rank_counts[rank] == 4 * n_decks
