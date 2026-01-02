import random


class Card:
    def __init__(
        self,
        suit: str,
        rank: str,
        value: int,
    ):
        self.suit = suit
        self.rank = rank
        self.value = value

    def __repr__(self):
        return f"[{self.rank}{self.suit}]"


SUITS = ["♠", "♥", "♦", "♣"]
RANK_POINTS = [
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
    ("6", 6),
    ("7", 7),
    ("8", 8),
    ("9", 9),
    ("10", 10),
    ("J", 10),
    ("Q", 10),
    ("K", 10),
    ("A", 11),
]


class Deck:
    def __init__(self, n_decks: int = 1):
        self.n_decks = n_decks
        self.cards = []
        for _ in range(n_decks):
            for suit in SUITS:
                for rp in RANK_POINTS:
                    self.cards.append(Card(suit, rp[0], rp[1]))

    def __len__(self) -> int:
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()
