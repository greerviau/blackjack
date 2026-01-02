from core import Blackjack
from strategies.human_strategy import HumanStrategy

player = HumanStrategy(bankroll=500)
game = Blackjack(
    player,
    n_decks=8,
    table_min=25,
    table_max=500,
    late_surrender=True,
)

game.play()
