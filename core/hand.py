from .cards import Card


class Hand:
    def __init__(self, bet: float, is_from_split: bool = False):
        self.cards = []
        self.bet = float(bet)
        self.is_from_split = is_from_split
        self.is_surrendered = False

    def add_card(self, card: Card):
        self.cards.append(card)

    def __len__(self) -> int:
        return len(self.cards)

    @property
    def value(self) -> int:
        value = 0
        aces = 0

        for card in self.cards:
            value += card.value
            if card.rank == "A":
                aces += 1

        # Convert Aces from 11 to 1 as needed to avoid busting
        while value > 21 and aces > 0:
            value -= 10  # Convert an Ace from 11 to 1 (difference of 10)
            aces -= 1

        return value

    @property
    def is_blackjack(self) -> bool:
        return len(self) == 2 and self.value == 21 and not self.is_from_split

    @property
    def is_busted(self) -> bool:
        return self.value > 21

    @property
    def is_pair(self) -> bool:
        return len(self) == 2 and self.cards[0].rank == self.cards[1].rank

    @property
    def is_soft(self) -> bool:
        """Returns True if the hand is a soft hand (contains an Ace counted as 11)."""
        value = 0
        aces = 0

        for card in self.cards:
            value += card.value
            if card.rank == "A":
                aces += 1

        # Convert Aces from 11 to 1 as needed to avoid busting
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        # A hand is soft if there's still at least one Ace counted as 11
        return aces > 0 and value <= 21

    def __repr__(self):
        string = ""
        for card in self.cards:
            string += f"{card}"
        return string
